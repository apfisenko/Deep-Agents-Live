# Task 01: Frontend scaffold

> **Sprint:** [../../README.md](../../README.md)
> **Тип:** feat
> **Ветка:** `feat/frontend-1-scaffold`
> **Spec:** без spec — [architecture.md](../../../../concept/architecture.md), [api-contracts.md](../../../../concept/api-contracts.md)

---

## Цель

Инициализировать `frontend/`: Next.js 16 App Router, pnpm, Tailwind CSS 4, shadcn/ui, TypeScript strict и базовая структура каталогов.

---

## Состав работ

- [ ] Создать `frontend/` через `pnpm create next-app@latest` (App Router, TS, Tailwind, ESLint, src dir — по согласованию, без `src/` если совпадает с architecture)
- [ ] Зафиксировать версии: Next.js 16.x, React 19.x в `package.json`
- [ ] Инициализировать shadcn/ui (`pnpm dlx shadcn@latest init`); добавить Button, Input, ScrollArea
- [ ] Настроить `tsconfig.json`: `strict: true`, запрет `any`
- [ ] Создать каталоги `components/chat/`, `lib/` (пустые или с `.gitkeep`)
- [ ] Добавить `frontend/.gitignore` (node_modules, .next)
- [ ] Настроить ESLint + Prettier (если не включены create-next-app)
- [ ] Самопроверка по критериям DoD
- [ ] (после «ок» пользователя) Создать `summary.md`, обновить sprint README.md

---

## Критерии готовности (DoD)

| # | Критерий | Способ проверки |
|---|----------|-----------------|
| 1 | Зависимости устанавливаются | `cd frontend && pnpm install` |
| 2 | Dev-сервер на `:3000` | `pnpm dev` |
| 3 | shadcn Button импортируется | `import { Button } from "@/components/ui/button"` |
| 4 | Lint проходит | `pnpm lint` |
| 5 | Typecheck проходит | `pnpm exec tsc --noEmit` |

> Те же команды пользователь выполняет для самостоятельной верификации.

---

## Артефакты

- `frontend/package.json` — зависимости и scripts
- `frontend/tsconfig.json` — strict TypeScript
- `frontend/next.config.ts` — конфиг Next.js
- `frontend/app/layout.tsx` — root layout (минимальный)
- `frontend/app/page.tsx` — заглушка «Deep Agents Live»
- `frontend/components/ui/button.tsx` — shadcn
- `frontend/components/ui/input.tsx` — shadcn
- `frontend/components/ui/scroll-area.tsx` — shadcn
- `frontend/components/chat/.gitkeep` — каталог компонентов чата
- `frontend/lib/.gitkeep` — каталог утилит

---

## Scope

**Трогаем:** только файлы из списка «Артефакты».

**НЕ трогаем:**
- Backend, bot, docker-compose
- Design tokens и chat UI (задачи 02–05)
- Makefile / make.ps1 (задача 06)
- `.env` (только чтение; правки `.env.example` — задача 06)

---

## Риски и допущения

- Допущение: Tailwind CSS 4 через create-next-app или ручная настройка `@tailwindcss/postcss` — следовать актуальному шаблону Next 16.
- Риск: конфликт `PORT` в `.env.example` (сейчас 3001) — исправляется в задаче 06; scaffold использует default `:3000`.
- Допущение: alias `@/` для imports — стандарт shadcn.

---

## Открытые вопросы

- [ ] Нет блокирующих — стек зафиксирован в conventions и architecture.md
