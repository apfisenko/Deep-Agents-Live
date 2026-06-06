# Task 02: Design tokens и layout shell

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** feat
> **Ветка:** `feat/frontend-2-design-tokens`
> **Spec:** без spec — [design-reference-blue-green.png](../../../../../design-reference-blue-green.png), [architecture.md](../../../../concept/architecture.md)

---

## Цель

Реализовать визуальную систему виджета «Айра»: палитра blue-green, glassmorphism, типографика и оболочка чат-контейнера по design-reference.

---

## Состав работ

- [ ] Изучить `design-reference-blue-green.png`; выписать ключевые цвета (primary, gradient, glass bg)
- [ ] Определить CSS-переменные в `globals.css` (Tailwind 4 `@theme` или `:root`)
- [ ] Градиент фона страницы (blue → green/teal)
- [ ] Стили glassmorphism: `backdrop-blur`, полупрозрачный border, shadow
- [ ] Обновить `app/layout.tsx`: шрифт (Inter или Geist), meta, body classes
- [ ] Создать `components/chat/chat-shell.tsx` — внешний контейнер виджета (rounded-2xl, max-w-md)
- [ ] Самопроверка по критериям DoD
- [ ] (после «ок» пользователя) Создать `summary.md`, обновить sprint README.md

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Фон страницы — blue-green gradient | Визуальное сравнение с design-reference |
| 2 | Контейнер чата — glass effect | backdrop-blur виден на gradient фоне |
| 3 | Акцентные кнопки/chips используют primary token | Inspect CSS variables |
| 4 | Lint проходит | `pnpm lint` |

> Те же команды пользователь выполняет для самостоятельной верификации.

---

## Артефакты

- `frontend/app/globals.css` — design tokens, utility classes
- `frontend/app/layout.tsx` — fonts, metadata «Айра — llmstart.ru»
- `frontend/components/chat/chat-shell.tsx` — оболочка виджета (layout only)

---

## Scope

**Трогаем:** только файлы из списка «Артефакты» + временная demo-страница в `app/page.tsx` для preview shell.

**НЕ трогаем:**
- SSE client, chat logic (задачи 03–05)
- shadcn component internals (только CSS overrides через variables)
- Backend, bot

---

## Риски и допущения

- Допущение: точное pixel-perfect не требуется — достаточно узнаваемого соответствия референсу.
- Риск: shadcn default theme (zinc) конфликтует — override через CSS variables на `:root`.
- Skill `frontend-design` — использовать для палитры и spacing.

---

## Открытые вопросы

- [ ] Нет блокирующих
