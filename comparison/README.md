# Notebook-сравнение: Qdrant · Chroma · pgvector

Это вторая часть практики Темы 4 — **демонстрация**, а не задание с проверкой.
В уроке мы на словах разобрали, как векторные базы устроены изнутри (индексы, фильтрация,
квантование) и чем отличаются. Здесь ты **сам запускаешь** три базы на одном корпусе и
видишь эти отличия своими глазами: где они расходятся по возможностям, по скорости и
ресурсам, и что реально дают «крутилки» из теории.

> **Это не открытая лаборатория.** Notebook ведёт за собой: ставит вопрос → показывает
> замер → делает вывод. Параметры и объёмы вынесены в переменные — их можно (и нужно)
> крутить самому, но сюжет уже выстроен.

## Что внутри

| Файл | Назначение |
|------|------------|
| `comparison.ipynb` | Сам notebook (генерируется из `comparison.py`) |
| `comparison.py` | Исходник notebook в jupytext-формате (его и редактируем) |
| `corpus.py` | Загрузка публичного корпуса + эмбеддинг с кэшем |
| `helpers.py` | Измерительная сантехника: тайминги, RAM, recall@k |
| `docker-compose.yml` | Qdrant + pgvector (Chroma работает embedded, сервер не нужен) |
| `pyproject.toml` | Зависимости (через `uv`) |

## Как запустить

### Linux / macOS

```bash
# 1. Поднять базы (Qdrant + pgvector)
docker compose up -d

# 2. Поставить зависимости и ядро Jupyter
uv sync

# 3. Ключ для эмбеддингов: скопируй .env.example -> .env и впиши OPENROUTER_API_KEY
cp .env.example .env   # затем отредактируй

# 4. (рекомендуется) предсчитать эмбеддинги корпуса один раз
uv run python corpus.py 40000

# 5. Собрать notebook из исходника и открыть
uv run jupytext --to ipynb comparison.py
uv run jupyter lab comparison.ipynb
```

### Windows (Docker в WSL)

На Windows Docker запускается **внутри WSL** — используй `make_u.ps1`, а не прямой вызов
`docker compose` из PowerShell (CLI Docker там может быть недоступен).

```powershell
cd comparison

# Поднять Qdrant + pgvector и проверить порты
.\make_u.ps1 up
.\make_u.ps1 check

# Полный цикл: up + sync + jupyter lab
.\make_u.ps1 start

# Диагностика, если что-то не стартует
.\make_u.ps1 doctor
.\make_u.ps1 ps
```

Остальные шаги (`.env`, `uv sync`, `corpus.py`, jupyter) — те же, через `.\make_u.ps1 sync`,
`.\make_u.ps1 corpus 40000`, `.\make_u.ps1 lab` или напрямую `uv run ...`.

Эмбеддинги считает модель **intfloat/multilingual-e5-large** (1024 измерения, 90+ языков)
через **OpenRouter API** — ничего не качаем локально, нужен только `OPENROUTER_API_KEY`
(стоит копейки: ~$0.01 / 1M токенов). Результат кэшируется в `embeddings_cache/*.npy` —
считается один раз, повторные запуски стартуют мгновенно.

> **Время.** Эмбеддинг корпуса — единственная заметная по времени операция (~15 мин на 40k,
> один раз, дальше из кэша). Объём задаётся `N_BASE` в notebook; индексация и замеры на этом
> объёме — быстрые. Наращивать объём — твоё решение (в notebook сказано, где крутить).

## Корпус

По умолчанию — публичный датасет **DBpedia-14** с готовыми категориями (метки классов идут
как метаданные, на них показываем фильтрацию). Загружается через Hugging Face Hub
(`corpus.py` → `load_dataset("fancyzhx/dbpedia_14")`). Когда появится реальный корпус
курса — подменяется в одном месте (`corpus.py`), остальной notebook не меняется.

### Предупреждение HF Hub: `unauthenticated requests`

В §1 может появиться:

```
Warning: You are sending unauthenticated requests to the HF Hub.
Please set a HF_TOKEN to enable higher rate limits and faster downloads.
```

Это **не ошибка** — `huggingface_hub` напоминает, что датасет качается без токена.
Для публичного DBpedia-14 токен **не обязателен**: скачивание разовое, дальше лежит
в кэше (`~/.cache/huggingface/`). На эмбеддинги это не влияет — они идут через
`OPENROUTER_API_KEY`, а не через HF.

**Исправлять не нужно**, если корпус загрузился и ячейка отработала.

Добавь `HF_TOKEN`, если загрузка падает с rate limit (429), очень медленная или хочешь
убрать предупреждение:

1. Аккаунт на [huggingface.co](https://huggingface.co) → Settings → Access Tokens (Read).
2. В `comparison/.env`:
   ```
   HF_TOKEN=hf_...
   ```

`huggingface_hub` подхватит токен сам, код менять не нужно.

## Подчистить за собой

```bash
docker compose down -v   # остановить базы и удалить тома
```

На Windows: `.\make_u.ps1 down-v`

## Windows + WSL: контейнеры «падают» через минуту

### Симптомы

- §0 в notebook: `ConnectError: [WinError 10061]` на `localhost:6333`
- `.\make_u.ps1 check` сначала OK, через время — timeout на порту 6333
- В логах Qdrant: `SIGTERM received`; pgvector: `received fast shutdown request`

Это **не** краш Qdrant/pgvector и **не** OOM — контейнеры корректно останавливаются
вместе с Docker при **выключении WSL-VM**.

### Причина

`make_u.ps1` вызывает короткие сессии `wsl -e bash -lc "docker compose up -d"`.
Когда команда завершается и активных WSL-процессов не остаётся, WSL 2 **автоматически
гасит VM** (через ~15–60 с). Systemd останавливает `docker.service` → контейнеры
получают SIGTERM, порты 6333/5433 на Windows перестают отвечать.

### Решение (рекомендуется)

Создай `%USERPROFILE%\.wslconfig` и отключи auto-shutdown:

```ini
[wsl2]
vmIdleTimeout=-1
```

Затем перезапусти WSL:

```powershell
wsl --shutdown
wsl
```

После изменения `.wslconfig` перед работой с notebook:

```powershell
.\make_u.ps1 up
.\make_u.ps1 check
```

### Альтернативы

- Держи открытым терминал WSL, пока работаешь с notebook (`wsl` и не закрывай окно).
- Если `check` упал — снова `.\make_u.ps1 up` (не только `check`: после shutdown VM
  контейнеры в статусе Exited и сами не поднимутся).
- Не запускай `.\make_u.ps1 repair` без необходимости — он останавливает **все**
  контейнеры в WSL и перезапускает Docker.

## Windows: §3 и `docker stats`

В §3 RAM Qdrant/pgvector меряется через `docker stats`. Jupyter на Windows не видит
`docker` в PATH (CLI живёт в WSL) → `FileNotFoundError` в `helpers.container_ram_mb`.

`helpers.py` вызывает `wsl -e docker stats ...` автоматически, если `docker` недоступен.
После обновления `helpers.py` **перезапусти kernel** Jupyter (или `%reload_ext autoreload`
+ переимпорт `helpers`), затем заново выполни ячейку §3.

Контейнеры должны быть запущены: `.\make_u.ps1 up`.
