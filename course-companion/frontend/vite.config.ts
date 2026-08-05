import { defineConfig, type ProxyOptions } from "vite";
import react from "@vitejs/plugin-react";

// CORS решаем Vite-прокси (как в deployment-cookbook): браузер ходит только
// на origin фронта, дальше dev-сервер Vite перекидывает на Agent Server :2024.
const upstream: ProxyOptions = {
  target: process.env.LANGGRAPH_PROXY_TARGET ?? "http://127.0.0.1:2024",
  changeOrigin: true,
  // проверка домашки — минуты, дефолтных таймаутов прокси не хватает
  timeout: 600_000,
  proxyTimeout: 600_000,
};

// Поллер фоновых проверок ходит на сервер ЧЕКЕРА («результат пришёл сам»).
// Отдельный прокси-путь решает CORS и делает адрес чекера конфигурацией фронта:
// co-deployed — не задавать (тот же сервер, что companion), распил —
// CHECKER_PROXY_TARGET=http://127.0.0.1:2025.
const checkerUpstream: ProxyOptions = {
  ...upstream,
  target:
    process.env.CHECKER_PROXY_TARGET ??
    process.env.LANGGRAPH_PROXY_TARGET ??
    "http://127.0.0.1:2024",
};

// Drill-endpoint (A2UI-формы, канал 2 из таблицы каналов README практики):
// вмонтирован в companion-сервер
// через http.app в langgraph.json, т.е. по умолчанию тот же :2024. Фолбэк
// «отдельный процесс на :8123» — DRILL_PROXY_TARGET=http://127.0.0.1:8123,
// код фронта при этом не меняется.
const drillUpstream: ProxyOptions = {
  ...upstream,
  target:
    process.env.DRILL_PROXY_TARGET ??
    process.env.LANGGRAPH_PROXY_TARGET ??
    "http://127.0.0.1:2024",
};

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // клиент использует apiUrl = origin + "/api/langgraph"
      "/api/langgraph": {
        ...upstream,
        rewrite: (path) => path.replace(/^\/api\/langgraph/, ""),
      },
      "/api/checker": {
        ...checkerUpstream,
        rewrite: (path) => path.replace(/^\/api\/checker/, ""),
      },
      // /api/drill/a2ui -> <drill upstream>/drill/a2ui
      "/api/drill": {
        ...drillUpstream,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
      // SDK может резолвить часть путей от корня — зеркалируем их тоже
      "/threads": upstream,
      "/runs": upstream,
      "/assistants": upstream,
      "/ok": upstream,
      "/info": upstream,
    },
  },
});
