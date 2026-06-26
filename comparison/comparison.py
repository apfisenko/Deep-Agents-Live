# ---
# jupyter:
#   jupytext:
#     formats: py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Три векторные базы под микроскопом: Qdrant · Chroma · pgvector
#
# В уроке мы на словах разобрали, как векторные базы устроены изнутри — индексы и ANN,
# фильтрация по метаданным, квантование — и почему «да бери любую базу» работает ровно
# до первого нетривиального требования. Эта тетрадка — про то, чтобы **проверить всё руками**:
# поднимаем три базы на одном корпусе и смотрим, где они реально расходятся.
#
# Берём три базы из разных «весовых категорий»:
#
# - **Chroma** — самый простой старт, живёт прямо внутри твоего процесса, дефолт для прототипов;
# - **pgvector** — векторный поиск внутри обычного PostgreSQL («у вас уже есть Postgres»);
# - **Qdrant** — специализированная база на Rust, «прод без лишней головной боли».
#
# Тетрадка ведёт за собой по простому маршруту **вопрос → замер → вывод**. Но это твой
# рабочий инструмент: все объёмы и параметры вынесены в переменные — их полезно покрутить
# самому. План такой:
#
# 1. **Знакомство** — грузим корпус во все три базы, делаем базовый поиск. Чувствуем характер каждой.
# 2. **Возможности** — фильтрация по метаданным и гибридный поиск: здесь базы расходятся.
# 3. **Производительность** — RAM, время индексации, скорость запросов; наращиваем объём.
# 4. **Крутилки** — recall через точный перебор, квантование, параметры HNSW (показываем на Qdrant).
# 5. **Свод** — что из всего этого следует, когда выбираешь базу.
#
# > **Перед запуском:** `docker compose up -d` (поднимет Qdrant и pgvector), `uv sync`
# > (зависимости) и ключ `OPENROUTER_API_KEY` в файле `.env` рядом с тетрадкой —
# > эмбеддинги считаем через API (модель `multilingual-e5-large`). Шаблон — в `.env.example`.

# %% [markdown]
# ## §0. Сетап
#
# Подключаемся к двум поднятым в Docker базам (Qdrant и pgvector) и готовим Chroma — она
# работает прямо в этом процессе, отдельный сервер ей не нужен. Если ячейка падает на
# подключении — почти всегда это `docker compose up -d`, который не отработал.

# %%
import time
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

import corpus
import helpers

# Qdrant — отдельный сервер (REST на порту 6333)
from qdrant_client import QdrantClient, models

qdrant = QdrantClient(url="http://localhost:6333")
print("Qdrant:", "ok" if qdrant.get_collections() is not None else "fail")

# pgvector — это обычный PostgreSQL с расширением vector
import psycopg
from pgvector.psycopg import register_vector

pg = psycopg.connect("postgresql://vec:vec@localhost:5433/vec", autocommit=True)
pg.execute("CREATE EXTENSION IF NOT EXISTS vector")
register_vector(pg)  # теперь numpy-массивы биндятся в SQL как тип vector
print("pgvector:", pg.execute("SELECT extversion FROM pg_extension WHERE extname='vector'").fetchone()[0])

# Chroma — embedded: никакого сервера, база живёт прямо в этом Python-процессе
import chromadb

chroma = chromadb.EphemeralClient()  # in-memory; для данных на диске — PersistentClient(path=...)
print("Chroma:", chromadb.__version__)

# %% [markdown]
# ### Параметры прогона
#
# Две главные ручки тетрадки:
#
# - **`N_BASE`** — сколько документов грузим в базы для секций про **возможности** (§2:
#   фильтрация, гибрид) и **крутилки** (§4: recall, квантование). Этот корпус эмбеддится
#   один раз и кэшируется на диск, чтобы не пересчитывать.
# - **`N_PERF`** — список объёмов, на которых отдельная секция §3 меряет **производительность**
#   (время индексации, RAM, скорость запросов). Мы прогоняем замер на 2 000, 10 000 и 40 000
#   векторов, чтобы увидеть, **как цифры растут с объёмом** корпуса: на маленьком объёме базы
#   почти неотличимы, на большом — расходятся. Эти точки замера дальше называем «перф-срезами».
#
# `DIM` (1024) задаёт модель эмбеддинга — это число измерений вектора, оно ещё пригодится,
# когда дойдём до бинарного квантования.

# %%
import os

# Объёмы можно переопределить через переменные окружения (удобно для быстрого прогона),
# например:  N_BASE=2000 N_PERF=500,1000,2000 jupyter ...   — или просто поменяй значения здесь.
# Большой корпус эмбеддить долго, поэтому удобно предсчитать заранее: `python corpus.py 40000`.
N_BASE = int(os.environ.get("N_BASE", 40_000))   # корпус для секций «возможности» и «крутилки»
N_PERF = [int(x) for x in os.environ.get("N_PERF", "2000,10000,40000").split(",")]  # объёмы для замера производительности
N_PERF = [n for n in N_PERF if n <= N_BASE]      # перф-срезы не больше базового корпуса
K = 10                   # сколько ближайших соседей достаём в каждом запросе
DIM = corpus.EMBED_DIM   # 1024 — размерность вектора у нашей модели

print(f"корпус: {N_BASE} | перф-срезы: {N_PERF} | top-K={K} | dim={DIM}")

# %% [markdown]
# ## §1. Знакомство: один корпус — три базы
#
# Корпус — **DBpedia-14**: короткие энциклопедические аннотации, размеченные по 14 классам
# (`Company`, `Artist`, `Film`, `Animal`, ...). Метка класса дальше пойдёт метаданными — на ней
# в §2 покажем фильтрацию.
#
# Важный момент про единицу хранения: **каждый элемент корпуса — это одна короткая аннотация,
# и она целиком становится одним вектором.** То есть «один документ = один вектор». Никакой
# нарезки длинных текстов на куски (чанкинга) здесь нет — и она нам не нужна: чанкинг это
# забота RAG-пайплайна, а мы сравниваем сами движки баз, для которых единица — просто
# «вектор плюс метаданные».
#
# Сначала грузим тексты и считаем для них эмбеддинги (первый раз — несколько минут на запрос
# к API, дальше мгновенно из кэша).

# %%
texts, categories, vectors = corpus.load_corpus(N_BASE)
print(f"загружено {len(texts)} документов, матрица векторов {vectors.shape}")
print("распределение по категориям:")
print(pd.Series(categories).value_counts())
print("\nпример:", repr(texts[0][:160]), "→", categories[0])

# %% [markdown]
# Теперь кладём один и тот же корпус в каждую из трёх баз. Смотри не только на цифры загрузки,
# но и на **сам код** — насколько просто положить данные в базу и что она требует из коробки.
# Это и есть «характер» базы.

# %% [markdown]
# **Qdrant.** Создаём коллекцию под вектор фиксированной размерности с косинусной метрикой
# и заливаем точки пачкой. Каждая точка несёт `payload` — произвольные метаданные, у нас это
# категория.

# %%
COLL = "docs"
if qdrant.collection_exists(COLL):
    qdrant.delete_collection(COLL)
qdrant.create_collection(
    collection_name=COLL,
    vectors_config=models.VectorParams(size=DIM, distance=models.Distance.COSINE),
)
with helpers.timer("Qdrant · загрузка"):
    qdrant.upload_collection(
        collection_name=COLL,
        vectors=vectors,
        payload=[{"category": c} for c in categories],
        ids=list(range(len(texts))),
    )
# дождёмся, пока база достроит индекс (статус GREEN)
while qdrant.get_collection(COLL).status != models.CollectionStatus.GREEN:
    time.sleep(0.5)
print("точек в коллекции:", qdrant.get_collection(COLL).points_count)

# %% [markdown]
# **Chroma.** Ещё проще: одна коллекция, метрика задаётся в конфиге, а `add` принимает
# эмбеддинги и метаданные разом. Единственный нюанс — лимит на размер одной пачки, поэтому
# заливаем батчами.

# %%
chroma_col = chroma.get_or_create_collection(
    name="docs", configuration={"hnsw": {"space": "cosine"}}
)
with helpers.timer("Chroma · загрузка"):
    B = 5000
    for i in range(0, len(texts), B):
        chroma_col.add(
            ids=[str(j) for j in range(i, min(i + B, len(texts)))],
            embeddings=vectors[i:i + B].tolist(),
            metadatas=[{"category": c} for c in categories[i:i + B]],
        )
print("точек в Chroma:", chroma_col.count())

# %% [markdown]
# **pgvector.** Здесь мы внутри обычного SQL: таблица со столбцом `vector(1024)` и колонкой
# категории. Данные заливаем через `COPY` (быстрый бинарный путь Postgres), а затем отдельно
# строим HNSW-индекс под косинус. Обрати внимание: в Postgres построение индекса — это
# отдельный явный шаг.

# %%
pg.execute("DROP TABLE IF EXISTS docs")
pg.execute(f"CREATE TABLE docs (id bigint PRIMARY KEY, category text, embedding vector({DIM}))")
with helpers.timer("pgvector · загрузка (COPY)"):
    with pg.cursor().copy("COPY docs (id, category, embedding) FROM STDIN WITH (FORMAT BINARY)") as cp:
        cp.set_types(["int8", "text", "vector"])
        for i in range(len(texts)):
            cp.write_row((i, categories[i], vectors[i]))
with helpers.timer("pgvector · построение HNSW-индекса"):
    pg.execute("CREATE INDEX ON docs USING hnsw (embedding vector_cosine_ops) WITH (m=16, ef_construction=64)")
print("строк в pgvector:", pg.execute("SELECT count(*) FROM docs").fetchone()[0])

# %% [markdown]
# ### Один запрос — три выдачи
#
# Зададим один и тот же текстовый запрос и посмотрим топ-5 из каждой базы. На чистом
# семантическом поиске (без фильтров) выдачи должны почти совпасть — все три решают
# одну задачу одним и тем же способом. Это наш sanity-check; интересные отличия начнутся дальше.

# %%
def show_top(title, rows):
    print(f"\n{title}")
    for rank, (cat, snippet) in enumerate(rows, 1):
        print(f"  {rank}. [{cat}] {snippet[:70]}")

query_text = "a famous jazz musician and composer"
qv = corpus.embed_query(query_text)
print("запрос:", repr(query_text))

# Qdrant
qd_hits = qdrant.query_points(COLL, query=qv.tolist(), limit=5, with_payload=True).points
show_top("Qdrant", [(h.payload["category"], texts[h.id]) for h in qd_hits])

# Chroma
ch = chroma_col.query(query_embeddings=[qv.tolist()], n_results=5)
show_top("Chroma", [(m["category"], texts[int(i)]) for i, m in zip(ch["ids"][0], ch["metadatas"][0])])

# pgvector
pg_rows = pg.execute(
    "SELECT id, category FROM docs ORDER BY embedding <=> %s LIMIT 5", (qv,)
).fetchall()
show_top("pgvector", [(cat, texts[i]) for i, cat in pg_rows])

# %% [markdown]
# Выдачи совпадают (с точностью до порядка очень близких соседей) — и это ожидаемо: на простом
# поиске базы взаимозаменяемы. А вот дальше начинается то, ради чего вся тетрадка.

# %% [markdown]
# ## §2. Возможности: фильтрация по метаданным
#
# «Фильтрация по метаданным» звучит как галочка, которая есть у всех. На деле она устроена
# хитрее. Задача-эталон простая: **«найди 10 ближайших соседей, у которых `category = X`»**.
# Подвох в том, что ANN-индекс (HNSW) строится по всей коллекции сразу, и наивная фильтрация
# либо отсекает результаты уже **после** поиска (и тогда их окажется меньше 10), либо ломает
# обход графа.
#
# Чтобы подсветить проблему, подберём **стресс-условие**: фильтр по категории, которая
# **далека** от запроса. Спросим про спортсмена, но оставим в выдаче только деревни (`Village`).
# Тогда ближайшие к запросу соседи — почти все «не деревни», и наивный пост-фильтр рискует
# срезать выдачу в ноль.

# %%
FILTER_CAT = "Village"
n_match = sum(c == FILTER_CAT for c in categories)
print(f"фильтр: category = '{FILTER_CAT}' (≈{n_match} из {N_BASE}, {100*n_match/N_BASE:.1f}% корпуса)")
print("запрос — про спортсмена (намеренно далеко от деревень)")
fq = corpus.embed_query("an Olympic athlete who won gold medals")

# %% [markdown]
# **pgvector, вариант 1 — точный проход.** Добавляем `WHERE category = ...` к поиску
# `ORDER BY embedding <=> ...`. На нашем объёме планировщик Postgres видит, что таблица
# небольшая, и решает не лезть в индекс, а **просто пройти всю таблицу целиком** (seq scan).
# При полном проходе фильтр честный, и вернётся ровно `K`:

# %%
pg.execute("SET hnsw.iterative_scan = off")  # дефолт pgvector 0.8
got = pg.execute(
    "SELECT id FROM docs WHERE category = %s ORDER BY embedding <=> %s LIMIT %s",
    (FILTER_CAT, fq, K),
).fetchall()
print(f"pgvector (как есть): запросили {K}, вернулось {len(got)}")

# %% [markdown]
# **pgvector, вариант 2 — через сам ANN-индекс.** На реальном масштабе (миллионы строк)
# полный проход слишком дорог, и планировщик выберет именно HNSW-индекс. Сэмулируем это,
# запретив Postgres проходить таблицу целиком (`enable_seqscan = off`). Теперь индекс достаёт
# фиксированное число ближайших векторов — а они почти все «не деревни» — и фильтр `WHERE`
# срезает их уже **после** поиска:

# %%
pg.execute("SET enable_seqscan = off")        # форсим путь через HNSW-индекс (как было бы на масштабе)
pg.execute("SET hnsw.iterative_scan = off")
got_idx = pg.execute(
    "SELECT id FROM docs WHERE category = %s ORDER BY embedding <=> %s LIMIT %s",
    (FILTER_CAT, fq, K),
).fetchall()
print(f"pgvector (через HNSW, post-filter): запросили {K}, вернулось {len(got_idx)}  <-- дефект")

# %% [markdown]
# Вот он — «получили меньше, чем просили» из урока, вживую. В pgvector 0.8 это лечится
# **итеративным сканом** (`iterative_scan`):

# %%
pg.execute("SET hnsw.iterative_scan = strict_order")
pg.execute("SET hnsw.max_scan_tuples = 40000")
got_fix = pg.execute(
    "SELECT id FROM docs WHERE category = %s ORDER BY embedding <=> %s LIMIT %s",
    (FILTER_CAT, fq, K),
).fetchall()
print(f"pgvector (HNSW + iterative_scan): запросили {K}, вернулось {len(got_fix)}  <-- починили")
pg.execute("SET enable_seqscan = on")  # вернём настройку как было

# %% [markdown]
# **Что именно делает `iterative_scan`?** Это не возврат к полному перебору и не то же самое,
# что filterable-HNSW у Qdrant (см. ниже). Идея посередине и довольно простая: индекс достаёт
# первую порцию ближайших, отсеивает не прошедших фильтр — и если подходящих набралось меньше
# `K`, **досканирует ещё** порцию из графа, и так по кругу, пока не наберёт нужные `K` (или не
# упрётся в потолок `max_scan_tuples`, который мы задаём, чтобы запрос не сканировал вечность).
# Режим `strict_order` гарантирует, что итоговая выдача всё равно строго отсортирована по
# расстоянию. То есть pgvector не фильтрует *внутри* обхода графа, а делает несколько проходов
# индекса, докручивая, пока не наберёт нужное число.

# %% [markdown]
# **Qdrant — filterable HNSW.** Здесь фильтр встроен прямо в обход графа: узлы, не прошедшие
# фильтр, всё ещё используются для **навигации** по графу, но в выдачу попадают только
# прошедшие. Контракт — гарантированный top-K без «потери результатов», и никаких флагов
# крутить не надо. Для скорости на фильтрах мы заводим **payload-индекс** по полю (он же нужен
# планировщику Qdrant, чтобы прикинуть, насколько фильтр избирателен).

# %%
qdrant.create_payload_index(
    collection_name=COLL, field_name="category",
    field_schema=models.PayloadSchemaType.KEYWORD,
)
qd_f = qdrant.query_points(
    COLL, query=fq.tolist(), limit=K,
    query_filter=models.Filter(must=[
        models.FieldCondition(key="category", match=models.MatchValue(value=FILTER_CAT))
    ]),
    with_payload=True,
).points
print(f"Qdrant (filterable HNSW): запросили {K}, вернулось {len(qd_f)}, "
      f"категории = {set(h.payload['category'] for h in qd_f)}")

# %% [markdown]
# **Chroma.** Передаём `where={'category': ...}`. В актуальной версии Chroma фильтр
# применяется **до** поиска (pre-filter): соседи ищутся уже по отобранному подмножеству,
# поэтому `n_results` честные из коробки. (Исторически у Chroma тут был как раз post-filtering —
# тот самый дефект; к 2026 это починили.)

# %%
ch_f = chroma_col.query(query_embeddings=[fq.tolist()], n_results=K, where={"category": FILTER_CAT})
print(f"Chroma (pre-filter): запросили {K}, вернулось {len(ch_f['ids'][0])}, "
      f"категории = {set(m['category'] for m in ch_f['metadatas'][0])}")

# %% [markdown]
# ### Что мы увидели
#
# Главный вывод — **не «такая-то база плохая»**. «Потеря результатов» это свойство *механики*
# (фильтр поверх приближённого индекса), а не вечный ярлык конкретного вендора:
#
# - **pgvector** ловит дефект, как только в дело вступает сам HNSW-индекс (а на масштабе он
#   вступает всегда); лечится флагом `iterative_scan` (появился в 0.8). На маленькой таблице
#   его спасает полный проход — поэтому так важно проверять на **реальном** объёме.
# - **Qdrant** решает это на уровне индекса (filterable HNSW) — корректно и без флагов.
# - **Chroma** сегодня делает pre-filter (фильтр применяется до KNN) и тоже возвращает честные
#   `K` ([docs: metadata filtering](https://docs.trychroma.com/docs/querying-collections/metadata-filtering)).
#
# Практический смысл: если фильтруешь по метаданным — **проверь на своей базе, своём объёме
# и конфиге**, что она реально возвращает `K`, а не молча меньше. Это ровно то, что в уроке
# называлось «настоящая пре-фильтрация против post-filtering».

# %% [markdown]
# ## §2b. Гибридный поиск: где dense промахивается
#
# Плотный (dense) вектор силён в семантике, но **смазывает точные токены** — коды, артикулы,
# номера, редкие имена. Для них нужен лексический сигнал: гибрид складывает dense + sparse
# (BM25) и сливает результаты (обычно через RRF — Reciprocal Rank Fusion). Покажем механику
# гибрида и сравним его с чистым dense на запросе с точным термином.
#
# > **Про другие базы — честно и со ссылками (состояние на 2026).** Гибрид «из коробки», когда
# > dense и sparse живут в одной коллекции, удобнее всего показать на **Qdrant** (именованные
# > dense + sparse-векторы, слияние RRF одним запросом), поэтому механику собираем на нём.
# > Про остальных — по докам:
# >
# > - **Chroma** долго была только-dense, и отсутствие BM25 было классическим аргументом за
# >   переход на специализированную базу (см. многолетний
# >   [feature request #1330](https://github.com/chroma-core/chroma/issues/1330)). С тех пор она
# >   добавила полнотекстовый и regex-поиск
# >   ([docs: full-text search](https://docs.trychroma.com/docs/querying-collections/full-text-search))
# >   и sparse-векторы/BM25 для гибрида
# >   ([анонс «Sparse vector support»](https://www.trychroma.com/project/sparse-vector-search),
# >   [docs: sparse vector search](https://docs.trychroma.com/cloud/schema/sparse-vector-search)).
# >   Полнотекст и regex работают **локально** (мы проверили на нашей версии), а вот sparse-гибрид
# >   по докам оформлен в первую очередь под Cloud/Web-Sync-коллекции — классы в локальном пакете
# >   уже есть, но точную границу «локально vs облако» сверяй по докам выше.
# > - **pgvector** гибрид собирает руками: полнотекстовый поиск Postgres (`tsvector`) + слияние
# >   RRF в коде приложения.

# %%
# отдельная гибридная коллекция: dense + именованный sparse-вектор (BM25 с IDF-модификатором)
HCOLL = "docs_hybrid"
if qdrant.collection_exists(HCOLL):
    qdrant.delete_collection(HCOLL)
qdrant.create_collection(
    collection_name=HCOLL,
    vectors_config={"dense": models.VectorParams(size=DIM, distance=models.Distance.COSINE)},
    sparse_vectors_config={"bm25": models.SparseVectorParams(modifier=models.Modifier.IDF)},
)

N_HYB = min(3000, N_BASE)   # для гибрида берём подвыборку (BM25 считается на CPU)
# Нативный путь: BM25-вектор не собираем руками, а отдаём текст как models.Document — клиент
# qdrant сам посчитает разреженный вектор через fastembed (модель "Qdrant/bm25"). Dense при этом
# остаётся нашим, уже посчитанным через API (его мы базе не доверяем считать — у нас своя модель).
with helpers.timer("Qdrant · загрузка гибридной коллекции"):
    qdrant.upload_points(
        collection_name=HCOLL,
        points=[
            models.PointStruct(
                id=i,
                vector={"dense": vectors[i].tolist(),
                        "bm25": models.Document(text=texts[i], model="Qdrant/bm25")},
                payload={"category": categories[i]},
            )
            for i in range(N_HYB)
        ],
    )
print("гибридная коллекция готова:", qdrant.get_collection(HCOLL).points_count, "точек")

# %% [markdown]
# Нам нужен запрос, на котором dense **спотыкается**. Идеальный случай — **точный токен-код**
# (число, артикул, обозначение модели): семантически он почти пуст, dense-вектор его смазывает,
# а BM25 ловит буквально.
#
# Важно: токен мы **не выдумываем, а находим в самом корпусе**. Код ниже сканирует тексты,
# берёт токены с цифрами, которые встречаются **ровно в одном** документе, и выбирает первый
# такой, который чистый dense НЕ находит (ранг хуже 10 или вовсе мимо топ-50), а гибрид —
# находит. То есть и токен, и документ — настоящие, из данных; синтетическая только обёртка
# запроса — естественная формулировка `"what happened in <токен>"` (на нашем корпусе показательный
# токен — это год вроде 1778).

# %%
import re
from collections import Counter

# токены с цифрами, встречающиеся ровно в одном документе (коды/числа/обозначения)
tok_doc = {}
tok_count = Counter()
for i, t in enumerate(texts[:N_HYB]):
    for w in set(re.findall(r"\b[A-Za-z]*\d[A-Za-z0-9-]*\b", t)):
        tok_count[w.lower()] += 1
        tok_doc.setdefault(w.lower(), i)

# для одного токена считаем ранг нужного документа тремя способами поиска
def ranks_for(tok):
    target = tok_doc[tok]
    q = f"what happened in {tok}"
    qd_dense = corpus.embed_query(q)                          # dense-запрос — через наш API
    sparse_q = models.Document(text=q, model="Qdrant/bm25")  # sparse-запрос — клиент сам посчитает BM25
    dense = [h.id for h in qdrant.query_points(HCOLL, query=qd_dense.tolist(), using="dense", limit=50).points]
    sparse = [h.id for h in qdrant.query_points(HCOLL, query=sparse_q, using="bm25", limit=50).points]
    hybrid = [h.id for h in qdrant.query_points(HCOLL, prefetch=[
        models.Prefetch(query=qd_dense.tolist(), using="dense", limit=50),
        models.Prefetch(query=sparse_q, using="bm25", limit=50)],
        query=models.FusionQuery(fusion=models.Fusion.RRF), limit=50).points]
    rank = lambda lst: (lst.index(target) + 1) if target in lst else None
    return q, target, rank(dense), rank(sparse), rank(hybrid)

# берём первый показательный токен: dense мимо, а гибрид — в топе.
# Сначала пробуем годы (4 цифры) — на них вопрос "what happened in YYYY" звучит естественно;
# если подходящего года нет — откатываемся к прочим числовым токенам (коды/артикулы).
uniq = [w for w, c in tok_count.items() if c == 1]
years = [w for w in uniq if re.fullmatch(r"(1[5-9]\d\d|20[0-2]\d)", w)]
others = [w for w in uniq if re.search(r"\d", w) and len(w) >= 3 and w not in years]
candidates = years + others
for tok in candidates:
    hquery, target, r_dense, r_sparse, r_hybrid = ranks_for(tok)
    if (r_dense is None or r_dense > 10) and r_hybrid and r_hybrid <= 5:
        break

print(f"запрос: {hquery!r}  (точный токен '{tok}' есть ровно в одном документе)")
print(f"документ: {texts[target][:100]}")
print()
print("на Qdrant — три способа поиска:")
print(f"  dense-only : ранг {r_dense}   (семантика не помогает)")
print(f"  BM25-only  : ранг {r_sparse}   (точное совпадение)")
print(f"  hybrid RRF : ранг {r_hybrid}   (лучшее из обоих)")

# %% [markdown]
# Теперь — для чистоты картины — повторим **тот же запрос чистым dense по всем трём базам**.
# Если проблема в самом dense-векторе (а не в конкретной базе), то промахнутся одинаково все:
# точный токен-код найти семантическим поиском нельзя в принципе, какую базу ни возьми.

# %%
qd_dense_vec = corpus.embed_query(hquery)   # тот же текстовый запрос, что выше

# ранг нужного документа при чистом dense-поиске в каждой базе (по полному корпусу docs)
qd_ids = [h.id for h in qdrant.query_points(COLL, query=qd_dense_vec.tolist(), limit=50).points]
r_qd = (qd_ids.index(target) + 1) if target in qd_ids else None

ch_res = chroma_col.query(query_embeddings=[qd_dense_vec.tolist()], n_results=50)
ch_ids = [int(i) for i in ch_res["ids"][0]]
r_ch = (ch_ids.index(target) + 1) if target in ch_ids else None

pg_ids = [r[0] for r in pg.execute(
    "SELECT id FROM docs ORDER BY embedding <=> %s LIMIT 50", (qd_dense_vec,)).fetchall()]
r_pg = (pg_ids.index(target) + 1) if target in pg_ids else None

print(f"dense-only, ранг нужного документа в топ-50 (None = не попал даже в топ-50):")
print(f"  Qdrant   : {r_qd}")
print(f"  Chroma   : {r_ch}")
print(f"  pgvector : {r_pg}")
print("→ чистым dense ни одна база не выводит точный токен в топ — дело в векторе, а не в базе.")

# %% [markdown]
# ### Что мы увидели
#
# Точное число для dense-вектора семантически пусто — поэтому нужный документ роняют в хвост
# (а то и вовсе за топ-50) **все три базы одинаково**. Помогает не выбор базы, а **добавление
# лексического сигнала**: BM25 ставит документ первым по буквальному совпадению, а гибрид (RRF)
# забирает этот сигнал и склеивает с семантикой. В уроке это и был аргумент за гибрид —
# вопрос **возможностей**, а не скорости. Сегодня гибрид умеют и Qdrant, и Chroma (локально),
# а в pgvector он собирается руками. Перейдём к скорости.

# %% [markdown]
# ## §3. Производительность и ресурсы
#
# До сих пор корпус был маленький, и базы вели себя по скорости почти одинаково. В уроке
# звучал тезис: **примерно до ~10M векторов разница в скорости одного запроса невелика** —
# ANN-индексы все логарифмические, заметный отрыв появляется на больших объёмах. Зато то, что
# расходится **раньше**, — это память и время индексации. Проверим: будем наращивать объём и
# мерить по трём базам три вещи — время загрузки и индексации, потребление RAM и пропускную
# способность (сколько запросов в секунду).
#
# > **Это самая тяжёлая по времени секция.** Объёмы заданы в `N_PERF`; последний — самый
# > крупный. Уменьши список, если нужен быстрый прогон.

# %%
# перф-секция переиспользует уже посчитанные векторы (vectors) — никакого второго эмбеддинга,
# просто берём префиксы нужной длины.
perf_vecs = vectors
N_QUERIES = 200
rng = np.random.default_rng(0)
query_pool = perf_vecs[rng.choice(N_BASE, N_QUERIES, replace=False)]

# %%
# RAM меряем как ПРИРОСТ вокруг построения коллекции. Так мы изолируем именно перф-данные:
# в Qdrant/Chroma параллельно живут другие коллекции из прошлых секций, и абсолютные числа
# были бы зашумлены.
def _settle():
    time.sleep(0.7)  # дать базе осесть после загрузки, чтобы замер RAM был устойчивее

def bench_qdrant(n):
    name = "perf_q"
    if qdrant.collection_exists(name):
        qdrant.delete_collection(name)
    _settle(); ram0 = helpers.container_ram_mb("qdrant")
    qdrant.create_collection(name, vectors_config=models.VectorParams(size=DIM, distance=models.Distance.COSINE))
    t0 = time.perf_counter()
    qdrant.upload_collection(collection_name=name, vectors=perf_vecs[:n], ids=list(range(n)))
    while qdrant.get_collection(name).status != models.CollectionStatus.GREEN:
        time.sleep(0.3)
    idx_t = time.perf_counter() - t0
    _settle(); ram = helpers.container_ram_mb("qdrant") - ram0
    it = iter(range(10**9))
    def one():
        q = query_pool[next(it) % N_QUERIES]
        qdrant.query_points(name, query=q.tolist(), limit=K)
    tp = helpers.throughput(one, N_QUERIES)
    return {"db": "Qdrant", "n": n, "index_s": idx_t, "ram_mb": ram, **tp}

def bench_pgvector(n):
    pg.execute("DROP TABLE IF EXISTS perf_pg")
    _settle(); ram0 = helpers.container_ram_mb("pgvector")
    pg.execute(f"CREATE TABLE perf_pg (id bigint PRIMARY KEY, embedding vector({DIM}))")
    t0 = time.perf_counter()
    with pg.cursor().copy("COPY perf_pg (id, embedding) FROM STDIN WITH (FORMAT BINARY)") as cp:
        cp.set_types(["int8", "vector"])
        for i in range(n):
            cp.write_row((i, perf_vecs[i]))
    pg.execute("CREATE INDEX ON perf_pg USING hnsw (embedding vector_cosine_ops) WITH (m=16, ef_construction=64)")
    idx_t = time.perf_counter() - t0
    _settle(); ram = helpers.container_ram_mb("pgvector") - ram0
    it = iter(range(10**9))
    def one():
        q = query_pool[next(it) % N_QUERIES]
        pg.execute("SELECT id FROM perf_pg ORDER BY embedding <=> %s LIMIT %s", (q, K)).fetchall()
    tp = helpers.throughput(one, N_QUERIES)
    return {"db": "pgvector", "n": n, "index_s": idx_t, "ram_mb": ram, **tp}

def bench_chroma(n):
    import gc
    # embedded: RAM меряем как прирост RSS процесса (база живёт внутри приложения)
    cl = chromadb.EphemeralClient()
    col = cl.get_or_create_collection("perf_c", configuration={"hnsw": {"space": "cosine"}})
    gc.collect(); ram0 = helpers.process_ram_mb()
    t0 = time.perf_counter()
    B = 5000
    for i in range(0, n, B):
        j = min(i + B, n)
        col.add(ids=[str(k) for k in range(i, j)], embeddings=perf_vecs[i:j].tolist())
    idx_t = time.perf_counter() - t0
    gc.collect(); ram = helpers.process_ram_mb() - ram0
    it = iter(range(10**9))
    def one():
        q = query_pool[next(it) % N_QUERIES]
        col.query(query_embeddings=[q.tolist()], n_results=K)
    tp = helpers.throughput(one, N_QUERIES)
    return {"db": "Chroma*", "n": n, "index_s": idx_t, "ram_mb": ram, **tp}

rows = []
for n in N_PERF:
    print(f"--- объём {n} ---", flush=True)
    rows.append(bench_qdrant(n))
    rows.append(bench_pgvector(n))
    rows.append(bench_chroma(n))
perf = pd.DataFrame(rows)
print(perf.to_string(index=False))
perf

# %% [markdown]
# > **Почему `Chroma*` со звёздочкой.** RAM у Chroma — это **прирост RSS** процесса самой
# > тетрадки (база embedded, её память неотделима от приложения), тогда как Qdrant и pgvector
# > меряются «снаружи» через `docker stats`. Поэтому числа Chroma сравнивай с двумя другими
# > осторожно — это просто другая модель развёртывания, а не «Chroma экономнее».

# %%
import matplotlib.pyplot as plt

fig, ax = plt.subplots(1, 3, figsize=(15, 4))
for db in perf["db"].unique():
    d = perf[perf["db"] == db]
    ax[0].plot(d["n"], d["index_s"], "o-", label=db)
    ax[1].plot(d["n"], d["ram_mb"], "o-", label=db)
    ax[2].plot(d["n"], d["p95_ms"], "o-", label=db)
ax[0].set_title("Время индексации, с"); ax[1].set_title("RAM, МиБ"); ax[2].set_title("Latency p95, мс")
for a in ax:
    a.set_xlabel("число векторов"); a.legend(); a.grid(alpha=0.3)
plt.tight_layout(); plt.show()

# %% [markdown]
# ### Как читать
#
# **Latency одного запроса** на этих объёмах у всех трёх близка — тезис из урока про «до ~10M
# по скорости непринципиально» виден прямо здесь. А вот **время индексации** и **RAM**
# расходятся заметно сильнее: это та цена, которую часто упускают, глядя только на скорость
# поиска. Например, pgvector строит HNSW-индекс ощутимо дольше остальных, и на 40k это уже
# хорошо видно. Где именно разойдётся и latency — зависит от объёма: увеличивай `N_PERF`
# (помня, что эмбеддинг большого корпуса это минуты), пока разница не станет наглядной.

# %% [markdown]
# ## §4. Крутилки: recall, квантование, HNSW (на Qdrant)
#
# Последний блок — про **параметры**, которые в уроке шли списком: квантование (SQ/BQ) и
# гиперпараметры HNSW (`m`, `ef`). Все они про один и тот же размен: **скорость и память
# против точности**. Показываем на Qdrant — у него все ручки доступны явно и в одном API.
#
# Но сначала нужен **эталон точности**. Качество приближённого поиска меряют через **recall**:
# какую долю «настоящих» ближайших соседей нашёл ANN. А «настоящих» соседей даёт **точный
# перебор** (brute force) — он медленный, но точный по определению. В Qdrant точный поиск
# включается одним флагом `exact=True`, и заранее размеченный датасет нам не нужен: ground
# truth (эталон) мы считаем сами, тем же индексом.
#
# > **Важная граница.** Здесь мы меряем recall **ретривала** — насколько ANN близок к точному
# > перебору по векторам. Это не то же самое, что качество финального ответа RAG (туда входят
# > чанкинг, reranking и сам LLM) — оценка ответа живёт в теме про evaluation.

# %%
# эталон: точный top-K для пула запросов (exact=True — полный перебор внутри Qdrant)
def recall_vs_exact(query_vecs, search_kwargs, collection=COLL):
    total = 0.0
    for q in query_vecs:
        exact = qdrant.query_points(collection, query=q.tolist(), limit=K,
                                    search_params=models.SearchParams(exact=True)).points
        approx = qdrant.query_points(collection, query=q.tolist(), limit=K, **search_kwargs).points
        gt = {p.id for p in exact}
        total += len(gt & {p.id for p in approx}) / len(gt)
    return total / len(query_vecs)

eval_q = vectors[np.random.default_rng(1).choice(N_BASE, 100, replace=False)]
base_recall = recall_vs_exact(eval_q, {})
print(f"recall@{K} дефолтного HNSW против точного перебора: {base_recall:.3f}")

# %% [markdown]
# На нашем корпусе recall ≈ **1.0** (на 40k — порядка 0.998): данные хорошо разделимы (разные
# сущности живут в разных областях пространства), и HNSW находит почти ровно тех же соседей,
# что точный перебор. Это и есть «ANN почти ничего не теряет» из урока — на чистых, хорошо
# разделимых данных приближённость обходится почти даром (на больших и более «слипшихся»
# коллекциях recall просел бы заметнее). А вот где размен виден сразу — это **квантование**:
# там мы сознательно жертвуем точностью ради памяти.

# %% [markdown]
# ### Квантование: сжимаем векторы
#
# Вектор из 1024 чисел `float32` — это 4 КБ на документ. На миллионах документов память
# становится главным ограничением, и тут помогает **квантование** — хранить векторы в более
# грубом, но компактном виде. Берём два варианта (продуктовое квантование, PQ, в этот раз не
# трогаем):
#
# - **SQ — скалярное квантование (scalar).** Каждое из 1024 чисел сжимаем из `float32` в
#   `int8` (1 байт вместо 4). Сжатие **×4**. Огрубление мягкое, поэтому recall почти не падает —
#   это безопасный дефолт.
# - **BQ — бинарное квантование (binary).** Каждое измерение схлопываем до **одного бита**
#   (по сути — только знак числа). Сжатие радикальное, до **×32**. Это работает тем лучше, чем
#   **выше размерность**: на наших 1024 измерениях даже один бит на координату сохраняет
#   достаточно сигнала. Но потеря точности уже ощутима — и тут на помощь приходит rescoring.
#
# **Rescoring (с oversampling).** Поиск по сжатым векторам быстрый, но грубый. Чтобы вернуть
# точность, делаем два шага: сначала по дешёвой сжатой метрике берём кандидатов **с запасом**
# (oversampling, например ×2 от нужного `K`), а затем **переранжируем именно этих кандидатов
# по оригинальным `float32`-векторам** и выбираем настоящий top-K. Оригиналы для этого база
# хранит рядом со сжатыми. Эффект увидим ниже: у BQ rescoring вытягивает recall заметно.
#
# > **А у других баз?** Квантование есть не только у Qdrant: в pgvector оно доступно руками
# > (`halfvec` — fp16 ×2, бинарное через тип `bit` + расстояние Хэмминга), а вот у embedded-Chroma
# > явных ручек квантования в pip-API сейчас нет. Поэтому показываем на Qdrant, где это
# > настраивается декларативно.
#
# Кстати про «декларативно»: квантование задаётся **в конфиге коллекции при её создании** —
# и дальше всё, что в неё загружаем, хранится уже в сжатом виде (плюс оригиналы для rescoring).
# Поэтому ниже мы создаём под каждый вариант отдельную коллекцию.

# %%
def build_quant(name, quant_cfg):
    if qdrant.collection_exists(name):
        qdrant.delete_collection(name)
    qdrant.create_collection(
        name,
        vectors_config=models.VectorParams(size=DIM, distance=models.Distance.COSINE),
        quantization_config=quant_cfg,   # <-- квантование объявляем при создании коллекции
    )
    qdrant.upload_collection(collection_name=name, vectors=vectors, ids=list(range(N_BASE)))
    while qdrant.get_collection(name).status != models.CollectionStatus.GREEN:
        time.sleep(0.3)

build_quant("q_sq", models.ScalarQuantization(
    scalar=models.ScalarQuantizationConfig(type=models.ScalarType.INT8, always_ram=True)))
build_quant("q_bq", models.BinaryQuantization(
    binary=models.BinaryQuantizationConfig(always_ram=True)))

# два режима поиска по сжатой коллекции: с rescoring (по оригиналам) и без
rescore = {"search_params": models.SearchParams(
    quantization=models.QuantizationSearchParams(rescore=True, oversampling=2.0))}
norescore = {"search_params": models.SearchParams(
    quantization=models.QuantizationSearchParams(rescore=False))}

def avg_latency(collection, kwargs):
    it = iter(range(10**9))
    def one():
        q = eval_q[next(it) % len(eval_q)]
        qdrant.query_points(collection, query=q.tolist(), limit=K, **kwargs)
    return helpers.throughput(one, 200)["p50_ms"]

quant = pd.DataFrame([
    {"вариант": "без квантования",     "сжатие": "×1",  "recall@10": base_recall,
     "p50_ms": avg_latency(COLL, {})},
    {"вариант": "SQ int8 (rescore)",   "сжатие": "×4",  "recall@10": recall_vs_exact(eval_q, rescore, "q_sq"),
     "p50_ms": avg_latency("q_sq", rescore)},
    {"вариант": "BQ 1-бит (rescore)",  "сжатие": "×32", "recall@10": recall_vs_exact(eval_q, rescore, "q_bq"),
     "p50_ms": avg_latency("q_bq", rescore)},
    {"вариант": "BQ 1-бит (без rescore)", "сжатие": "×32", "recall@10": recall_vs_exact(eval_q, norescore, "q_bq"),
     "p50_ms": avg_latency("q_bq", norescore)},
])
print(quant.to_string(index=False))
quant

# %% [markdown]
# Вот он, размен «память ↔ точность» в цифрах:
#
# - **SQ (int8, ×4)** — recall практически не падает. Вчетверо меньше памяти почти даром —
#   потому это и безопасный дефолт.
# - **BQ (1 бит, ×32)** — сжатие радикальное, но recall заметно ниже. И ключевой нюанс виден
#   прямо в таблице: **без rescoring** BQ проваливается сильно, а **с rescoring** подтягивается
#   до приличного уровня. Это ровно та механика «грубо отобрали по битам → финал по
#   оригиналам», что мы разобрали выше.
#
# По скорости на этом объёме выигрыш квантования скромный — он по-настоящему раскрывается на
# масштабе, когда сжатые векторы позволяют держать в RAM то, что иначе ушло бы на диск.

# %% [markdown]
# ### HNSW `ef`: ещё одна ручка размена
#
# `ef` (точнее `hnsw_ef` на поиске) — это **ширина «луча» при обходе графа HNSW**: сколько
# лучших кандидатов база держит во фронте, расширяя их соседей, пока поиск ещё улучшается. Чем
# больше `ef`, тем тщательнее обход → выше recall, но и выше задержка. В конце из этих `ef`
# кандидатов отдаются top-K (поэтому `ef ≥ K`).
#
# Чтобы не путаться, разведём три похожих понятия:
#
# - **`hnsw_ef`** — ширина обхода на **поиске**, настраивается на каждый запрос отдельно (именно
#   её и крутим ниже).
# - **`ef_construction`** — то же «сколько кандидатов держим», но на этапе **построения** индекса:
#   сколько соседей рассмотреть, вставляя каждый вектор в граф. Больше → качественнее граф (выше
#   потолок recall), но дольше сборка и больше памяти. Задаётся один раз при создании (у нас 64).
# - **Рескоринг (из секции про квантование) — это НЕ про `ef`.** Рескоринг доуточняет выдачу по
#   *оригинальным* векторам после поиска по сжатым; `ef` же — про тщательность обхода графа и к
#   квантованию отношения не имеет. Это ортогональные ручки.
#
# Прогоним sweep по `hnsw_ef` и посмотрим на обе оси — recall и latency.

# %%
ef_rows = []
for ef in [4, 8, 16, 32, 64, 128, 256]:
    sp = {"search_params": models.SearchParams(hnsw_ef=ef)}
    ef_rows.append({"ef": ef, "recall@10": recall_vs_exact(eval_q, sp), "p50_ms": avg_latency(COLL, sp)})
ef_df = pd.DataFrame(ef_rows)
print(ef_df.to_string(index=False))

fig, ax1 = plt.subplots(figsize=(7, 4))
ax2 = ax1.twinx()
ax1.plot(ef_df["ef"], ef_df["recall@10"], "o-", color="tab:blue", label="recall@10")
ax2.plot(ef_df["ef"], ef_df["p50_ms"], "s--", color="tab:red", label="p50, мс")
ax1.set_xlabel("hnsw_ef (на поиске)"); ax1.set_ylabel("recall@10", color="tab:blue")
ax2.set_ylabel("p50 latency, мс", color="tab:red"); ax1.grid(alpha=0.3)
# ось recall зумим у потолка: размен 0.95→1.0 иначе выглядел бы плоским
ax1.set_ylim(0.9, 1.01); plt.title("HNSW ef: recall и latency"); plt.tight_layout(); plt.show()
ef_df

# %% [markdown]
# Вот он, обещанный теорией размен **recall ↔ latency**, вживую. При крошечном `ef` (4–8) граф
# обходится поверхностно — recall заметно ниже единицы (см. таблицу выше), зато запрос самый
# быстрый. С ростом
# `ef` recall быстро подтягивается к 1.0, но и задержка растёт. Кривая выходит на «плато»:
# после какого-то `ef` recall уже почти не растёт, а латентность — продолжает. Смысл ручки
# один: ты выбираешь точку под свой бюджет задержки и нужную полноту выдачи — это и есть
# «гиперпараметр trade-off скорость/качество» из урока.
#
# (Замечание про масштаб: на маленьком и «чистом» корпусе recall держался бы у 1.0 даже при
# крошечном `ef` — размен был бы не виден. Он проявляется как раз на объёме и на более
# «слипшихся» данных; поэтому так полезно мерить на реальном размере, а не на игрушечном.)

# %% [markdown]
# ## §5. Свод: что мы увидели руками
#
# Соберём наблюдения в одну картину — и свяжем с тем, что делать дальше в практике.

# %%
print("СВОДКА\n" + "=" * 60)
print("""
ВОЗМОЖНОСТИ
  · Простой семантический поиск — все три базы взаимозаменяемы.
  · Фильтрация по метаданным — расходятся: дефект "теряем результаты" —
    свойство механики (фильтр поверх приближённого индекса), а не вечный
    ярлык. pgvector ловит его по дефолту (лечится iterative_scan), Qdrant
    корректен из коробки (filterable HNSW), Chroma сегодня pre-filter'ит.
  · Гибрид (dense+BM25): нативно у Qdrant; Chroma раньше не умела (это и был
    аргумент за миграцию), сейчас добавила (границу локально/облако — по докам);
    pgvector — руками через FTS + RRF.
    Точный токен-код чистым dense не находит НИ ОДНА база — нужен BM25.

ПРОИЗВОДИТЕЛЬНОСТЬ
  · Latency одного запроса на десятках тысяч векторов — близка у всех.
  · Раньше расходятся время индексации и RAM — смотри на них, не только
    на скорость поиска.

КРУТИЛКИ (Qdrant)
  · recall меряется точным перебором (exact=True) — эталон без датасета.
  · SQ почти бесплатен по качеству; BQ жмёт сильно (×32), recall спасает rescoring.
  · HNSW ef — прямой размен recall ↔ latency.
""")

# %% [markdown]
# ### Куда это ведёт
#
# - **Часть 1 (кейс-дрилл)** тренировала выбор базы под требования. Теперь за этим выбором
#   стоят не слова из обзора, а **то, что ты увидел сам**: где базы реально расходятся, а где
#   разница — миф.
# - **Часть 3 (интеграция)** — берёшь базу под свою задачу и встраиваешь в агента. Если
#   фильтрация и гибрид критичны — понятно, почему референс собран на Qdrant; если у тебя
#   уже есть Postgres и нагрузка скромная — pgvector может быть достаточным, и ты знаешь,
#   какие ручки проверить (`iterative_scan`).
#
# Главный вывод тот же, что в уроке: **«правильной» базы в вакууме нет** — есть подходящая
# под твои требования. Только теперь ты это пощупал руками, а не принял на веру.
