# Фронт — третий сервис compose: тот же Vite dev-сервер, что и при портовом
# запуске (никакой отдельной «прод-сборки» — учебный стенд, честно dev).
# Прокси-цели (companion/checker) приходят env-переменными из compose —
# vite.config.ts читает их при старте.

FROM node:22-slim

WORKDIR /app

COPY package.json package-lock.json ./
# --legacy-peer-deps обязателен: @a2ui/markdown-it@0.0.4 требует peer
# @a2ui/web_core@^0.9.2 при актуальном 0.10.1 (грабли экосистемы A2UI)
RUN npm ci --legacy-peer-deps

COPY index.html tsconfig.json vite.config.ts ./
COPY src ./src

EXPOSE 5173
# --host 0.0.0.0: dev-сервер Vite по умолчанию слушает localhost —
# снаружи контейнера был бы невидим
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
