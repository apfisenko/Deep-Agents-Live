#!/usr/bin/env bash
# Статус compose-стека: контейнеры + restart/uptime + HTTP-probe с хоста (WSL).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

fail=0

echo "=== docker compose ps ==="
docker compose ps -a

running_count="$(docker compose ps --status running -q 2>/dev/null | wc -l | tr -d ' ')"
exited_count="$(docker compose ps -a --status exited -q 2>/dev/null | wc -l | tr -d ' ')"

if [[ "$running_count" -eq 0 && "$exited_count" -gt 0 ]]; then
  echo ""
  echo "HINT: контейнеры остановлены (Exited/SIGTERM). Запустите: .\\make.ps1 compose-ensure"
  echo "      Не используйте make stop / make.ps1 stop при compose — это убивает docker-proxy."
  echo "      Docker Desktop: отключите Settings → General → Resource Saver (иначе VM может паузить контейнеры)."
  fail=1
fi

echo ""
echo "=== uptime / restarts ==="
ids="$(docker compose ps -aq 2>/dev/null || true)"
if [[ -z "$ids" ]]; then
  echo "(нет контейнеров — сначала compose-up)"
else
  while IFS= read -r id; do
    [[ -z "$id" ]] && continue
    docker inspect --format='{{.Name}} status={{.State.Status}} exit={{.State.ExitCode}} restarts={{.RestartCount}} started={{.State.StartedAt}} health={{if .State.Health}}{{.State.Health.Status}}{{else}}n/a{{end}}' "$id"
  done <<< "$ids"
fi

probe() {
  local name="$1"
  local url="$2"
  local code
  code="$(curl -s -o /dev/null -w '%{http_code}' --connect-timeout 3 "$url" 2>/dev/null || true)"
  code="${code:-000}"
  code="${code//$'\r'/}"
  code="${code//$'\n'/}"
  if [[ "$code" =~ ^[23][0-9][0-9]$ ]]; then
    echo "OK   $name  $url  HTTP $code"
  else
    echo "FAIL $name  $url  HTTP ${code:-000}"
    fail=1
  fi
}

echo ""
echo "=== HTTP probe (localhost) ==="
if [[ "$running_count" -eq 0 ]]; then
  echo "SKIP HTTP probe — нет running-контейнеров"
  fail=1
else
  probe "frontend :5173" "http://127.0.0.1:5173/"
  probe "companion :2024/info" "http://127.0.0.1:2024/info"
  probe "checker :2025/info" "http://127.0.0.1:2025/info"
fi

exit "$fail"
