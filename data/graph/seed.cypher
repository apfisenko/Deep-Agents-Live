// GraphRAG catalog seed — sprint-06 task 05 part (a)
// Source: data/b2c/programs/*.md, schema.md
// Idempotent: MERGE only. Re-run safe.

// ---------------------------------------------------------------------------
// 1. Constraints (unique keys on slug / composite — not on name)
// ---------------------------------------------------------------------------

CREATE CONSTRAINT combo_slug IF NOT EXISTS
FOR (n:Combo) REQUIRE n.slug IS UNIQUE;

CREATE CONSTRAINT course_slug IF NOT EXISTS
FOR (n:Course) REQUIRE n.slug IS UNIQUE;

CREATE CONSTRAINT module_key IF NOT EXISTS
FOR (n:Module) REQUIRE (n.courseSlug, n.moduleNumber) IS UNIQUE;

CREATE CONSTRAINT theme_canonical IF NOT EXISTS
FOR (n:Theme) REQUIRE n.canonicalName IS UNIQUE;

CREATE CONSTRAINT audience_slug IF NOT EXISTS
FOR (n:Audience) REQUIRE n.slug IS UNIQUE;

CREATE CONSTRAINT format_slug IF NOT EXISTS
FOR (n:Format) REQUIRE n.slug IS UNIQUE;

CREATE CONSTRAINT level_slug IF NOT EXISTS
FOR (n:Level) REQUIRE n.slug IS UNIQUE;

// ---------------------------------------------------------------------------
// 2. Reference nodes — Level, Format, Audience
// ---------------------------------------------------------------------------

MERGE (l:Level {slug: 'intensive'})
SET l.name = 'интенсив';

MERGE (l:Level {slug: 'intermediate'})
SET l.name = 'средний';

MERGE (l:Level {slug: 'advanced'})
SET l.name = 'продвинутый';

MERGE (f:Format {slug: 'recorded'})
SET f.name = 'в записи';

MERGE (f:Format {slug: 'recorded-with-chat'})
SET f.name = 'в записи + чат-поддержка';

MERGE (f:Format {slug: 'hybrid'})
SET f.name = 'гибрид (live + запись)';

MERGE (f:Format {slug: 'online-live'})
SET f.name = 'онлайн live';

MERGE (a:Audience {slug: 'developers'})
SET a.name = 'Разработчики, ИТ-специалисты, Tech Lead, архитекторы',
    a.description = 'Разработчики, ИТ-специалисты, Tech Lead, архитекторы';

MERGE (a:Audience {slug: 'non-coding-professionals'})
SET a.name = 'Продакты, аналитики, дизайнеры, менеджеры',
    a.description = 'Без ежедневного кодинга';

MERGE (a:Audience {slug: 'leaders-entrepreneurs'})
SET a.name = 'Тимлиды, CTO/CEO, фаундеры, предприниматели',
    a.description = 'Тимлиды, CTO/CEO, фаундеры, предприниматели, фрилансеры, стартаперы';

MERGE (a:Audience {slug: 'ai-engineers'})
SET a.name = 'AI-инженеры с базой LLM/агентов',
    a.description = 'Разработчики и AI-инженеры с базовыми знаниями LLM и агентов';

// ---------------------------------------------------------------------------
// 3. Combo
// ---------------------------------------------------------------------------

MERGE (cb:Combo {slug: 'ai-agents-combo'})
SET cb.name = 'Комбо «ИИ-агенты»: траектория от 0 до эксперта',
    cb.priceRub = 59990,
    cb.sumSeparateRub = 139960,
    cb.discountPct = 57.1,
    cb.sourcePaths = ['data/b2c/programs/ai-agents-combo.md'];

// ---------------------------------------------------------------------------
// 4. Courses — 4 ступени
// ---------------------------------------------------------------------------

MERGE (c:Course {slug: 'ai-coding-intensive-cursor'})
SET c.name = 'Интенсив AI-кодинг ИИ-агентов в Cursor',
    c.stepOrder = 1,
    c.priceRub = 14990,
    c.lessonCount = 4,
    c.legacy = false,
    c.sourcePaths = ['data/b2c/programs/ai-coding-intensive-cursor.md'];

MERGE (c:Course {slug: 'ai-driven-fullstack'})
SET c.name = 'AI-driven Fullstack разработка',
    c.stepOrder = 2,
    c.priceRub = 39990,
    c.lessonCount = 10,
    c.duration = '~1,5 мес.',
    c.legacy = false,
    c.sourcePaths = [
        'data/b2c/programs/ai-driven-fullstack.md',
        'data/b2c/programs/aidd-program.md'
    ];

MERGE (c:Course {slug: 'ai-coding-agents-base'})
SET c.name = 'AI-driven разработка ИИ-агентов',
    c.stepOrder = 3,
    c.priceRub = 39990,
    c.lessonCount = 11,
    c.duration = '~1,5 мес.',
    c.legacy = false,
    c.sourcePaths = ['data/b2c/programs/ai-coding-agents-base.md'];

MERGE (c:Course {slug: 'deep-agents-advanced'})
SET c.name = 'Deep Agents: продвинутая разработка ИИ-агентов',
    c.stepOrder = 4,
    c.priceRub = 44990,
    c.lessonCount = 12,
    c.duration = '~2 мес.',
    c.legacy = false,
    c.sourcePaths = ['data/b2c/programs/deep-agents-advanced.md'];

// ---------------------------------------------------------------------------
// 5. Modules
// ---------------------------------------------------------------------------

UNWIND [
    {n: 1, title: 'AI-driven подход'},
    {n: 2, title: 'Базовый ИИ-ассистент'},
    {n: 3, title: 'ИИ-продукт с мультимодальными возможностями на локальных моделях'},
    {n: 4, title: 'Автономные ИИ-агенты'}
] AS row
MERGE (m:Module {courseSlug: 'ai-coding-intensive-cursor', moduleNumber: row.n})
SET m.title = row.title;

UNWIND [
    {n: 1, title: 'Основы LLM и AI-кодинг экосистема'},
    {n: 2, title: 'AI-driven разработка Telegram-бота с Cursor'},
    {n: 3, title: 'Системный анализ, проектирование и планирование'},
    {n: 4, title: 'Разработка Backend API-сервиса'},
    {n: 5, title: 'Проектирование и интеграция базы данных'},
    {n: 6, title: 'Frontend-разработка'},
    {n: 7, title: 'Онбординг, работа с legacy и документирование'},
    {n: 8, title: 'DevOps'},
    {n: 9, title: 'CI/CD'},
    {n: 10, title: 'Production-ready: observability и деплой'}
] AS row
MERGE (m:Module {courseSlug: 'ai-driven-fullstack', moduleNumber: row.n})
SET m.title = row.title;

UNWIND [
    {n: 1, title: 'Основы LLM и стандартные API для работы моделями'},
    {n: 2, title: 'AI-driven разработка с ИИ-агентами на примере Cursor'},
    {n: 3, title: 'Мультимодальные возможности и локальный запуск LLM'},
    {n: 4, title: 'RAG с LangChain: от теории к практике'},
    {n: 5, title: 'Мониторинг и оценка качества RAG-систем'},
    {n: 6, title: 'Advanced RAG'},
    {n: 7, title: 'Агенты с LangChain и LangGraph'},
    {n: 8, title: 'Model Context Protocol (MCP)'},
    {n: 9, title: 'Безопасность агентных систем'},
    {n: 10, title: 'Оценка качества агентов'},
    {n: 11, title: 'Переход к мультиагентным системам'}
] AS row
MERGE (m:Module {courseSlug: 'ai-coding-agents-base', moduleNumber: row.n})
SET m.title = row.title;

UNWIND [
    {n: 1, title: 'AI-driven проектирование агентской системы'},
    {n: 2, title: 'AI-кодинг production-ready агента'},
    {n: 3, title: 'Датасет менеджмент'},
    {n: 4, title: 'Векторные базы данных'},
    {n: 5, title: 'Графовые базы данных и GraphRAG'},
    {n: 6, title: 'Мультимодальный RAG'},
    {n: 7, title: 'Продвинутый context-engineering'},
    {n: 8, title: 'Deep Agents: планирование и делегирование'},
    {n: 9, title: 'Evaluation и Red teaming'},
    {n: 10, title: 'Prompt Management'},
    {n: 11, title: 'Мультиагентные паттерны'},
    {n: 12, title: 'Масштабирование агентных систем'}
] AS row
MERGE (m:Module {courseSlug: 'deep-agents-advanced', moduleNumber: row.n})
SET m.title = row.title;

// ---------------------------------------------------------------------------
// 6. INCLUDES — Combo → Course (order on relationship)
// ---------------------------------------------------------------------------

MATCH (cb:Combo {slug: 'ai-agents-combo'})
MATCH (c1:Course {slug: 'ai-coding-intensive-cursor'})
MERGE (cb)-[:INCLUDES {order: 1}]->(c1);

MATCH (cb:Combo {slug: 'ai-agents-combo'})
MATCH (c2:Course {slug: 'ai-driven-fullstack'})
MERGE (cb)-[:INCLUDES {order: 2}]->(c2);

MATCH (cb:Combo {slug: 'ai-agents-combo'})
MATCH (c3:Course {slug: 'ai-coding-agents-base'})
MERGE (cb)-[:INCLUDES {order: 3}]->(c3);

MATCH (cb:Combo {slug: 'ai-agents-combo'})
MATCH (c4:Course {slug: 'deep-agents-advanced'})
MERGE (cb)-[:INCLUDES {order: 4}]->(c4);

// ---------------------------------------------------------------------------
// 7. RECOMMENDED_BEFORE — prerequisite chain (order on relationship)
// ---------------------------------------------------------------------------

MATCH (a:Course {slug: 'ai-coding-intensive-cursor'})
MATCH (b:Course {slug: 'ai-driven-fullstack'})
MERGE (a)-[:RECOMMENDED_BEFORE {order: 1}]->(b);

MATCH (a:Course {slug: 'ai-driven-fullstack'})
MATCH (b:Course {slug: 'ai-coding-agents-base'})
MERGE (a)-[:RECOMMENDED_BEFORE {order: 2}]->(b);

MATCH (a:Course {slug: 'ai-coding-agents-base'})
MATCH (b:Course {slug: 'deep-agents-advanced'})
MERGE (a)-[:RECOMMENDED_BEFORE {order: 3}]->(b);

// ---------------------------------------------------------------------------
// 8. HAS_MODULE — Course → Module
// ---------------------------------------------------------------------------

UNWIND [
    {course: 'ai-coding-intensive-cursor', nums: range(1, 4)},
    {course: 'ai-driven-fullstack', nums: range(1, 10)},
    {course: 'ai-coding-agents-base', nums: range(1, 11)},
    {course: 'deep-agents-advanced', nums: range(1, 12)}
] AS batch
UNWIND batch.nums AS moduleNumber
MATCH (c:Course {slug: batch.course})
MATCH (m:Module {courseSlug: batch.course, moduleNumber: moduleNumber})
MERGE (c)-[:HAS_MODULE]->(m);

// ---------------------------------------------------------------------------
// 9. HAS_LEVEL — Course → Level
// ---------------------------------------------------------------------------

MATCH (c:Course {slug: 'ai-coding-intensive-cursor'})
MATCH (l:Level {slug: 'intensive'})
MERGE (c)-[:HAS_LEVEL]->(l);

MATCH (c:Course {slug: 'ai-driven-fullstack'})
MATCH (l:Level {slug: 'intermediate'})
MERGE (c)-[:HAS_LEVEL]->(l);

MATCH (c:Course {slug: 'ai-coding-agents-base'})
MATCH (l:Level {slug: 'intermediate'})
MERGE (c)-[:HAS_LEVEL]->(l);

MATCH (c:Course {slug: 'deep-agents-advanced'})
MATCH (l:Level {slug: 'advanced'})
MERGE (c)-[:HAS_LEVEL]->(l);

// ---------------------------------------------------------------------------
// 10. HAS_FORMAT — Course → Format
// ---------------------------------------------------------------------------

MATCH (c:Course {slug: 'ai-coding-intensive-cursor'})
MATCH (f:Format {slug: 'recorded'})
MERGE (c)-[:HAS_FORMAT]->(f);

MATCH (c:Course {slug: 'ai-driven-fullstack'})
MATCH (f:Format {slug: 'recorded-with-chat'})
MERGE (c)-[:HAS_FORMAT]->(f);

MATCH (c:Course {slug: 'ai-coding-agents-base'})
MATCH (f:Format {slug: 'hybrid'})
MERGE (c)-[:HAS_FORMAT]->(f);

MATCH (c:Course {slug: 'deep-agents-advanced'})
MATCH (f:Format {slug: 'online-live'})
MERGE (c)-[:HAS_FORMAT]->(f);

// ---------------------------------------------------------------------------
// 11. TARGETS — Course → Audience
// ---------------------------------------------------------------------------

MATCH (c:Course {slug: 'ai-coding-intensive-cursor'})
MATCH (a:Audience {slug: 'non-coding-professionals'})
MERGE (c)-[:TARGETS]->(a);

MATCH (c:Course {slug: 'ai-coding-intensive-cursor'})
MATCH (a:Audience {slug: 'leaders-entrepreneurs'})
MERGE (c)-[:TARGETS]->(a);

MATCH (c:Course {slug: 'ai-coding-intensive-cursor'})
MATCH (a:Audience {slug: 'developers'})
MERGE (c)-[:TARGETS]->(a);

MATCH (c:Course {slug: 'ai-driven-fullstack'})
MATCH (a:Audience {slug: 'developers'})
MERGE (c)-[:TARGETS]->(a);

MATCH (c:Course {slug: 'ai-coding-agents-base'})
MATCH (a:Audience {slug: 'developers'})
MERGE (c)-[:TARGETS]->(a);

MATCH (c:Course {slug: 'deep-agents-advanced'})
MATCH (a:Audience {slug: 'developers'})
MERGE (c)-[:TARGETS]->(a);

MATCH (c:Course {slug: 'deep-agents-advanced'})
MATCH (a:Audience {slug: 'ai-engineers'})
MERGE (c)-[:TARGETS]->(a);
