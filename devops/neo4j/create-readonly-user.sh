#!/usr/bin/env bash
# Create text2cypher runtime user (sprint-06).
# Community Edition: CREATE USER only (no RBAC — see devops/README.md).
# Run via: make graph-init-readonly / .\make.ps1 graph-init-readonly

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

load_neo4j_env() {
  local file key value
  for file in .env.example .env; do
    [[ -f "$file" ]] || continue
    while IFS= read -r line || [[ -n "$line" ]]; do
      line="${line%%#*}"
      line="${line%"${line##*[![:space:]]}"}"
      [[ -z "$line" || "$line" != *=* ]] && continue
      key="${line%%=*}"
      value="${line#*=}"
      case "$key" in
        NEO4J_USER|NEO4J_PASSWORD|NEO4J_READONLY_USER|NEO4J_READONLY_PASSWORD)
          if [[ -z "${!key:-}" ]]; then
            export "$key=$value"
          fi
          ;;
      esac
    done <"$file"
  done
}

load_neo4j_env

: "${NEO4J_USER:?NEO4J_USER is required (see .env.example)}"
: "${NEO4J_PASSWORD:?NEO4J_PASSWORD is required (see .env.example)}"
: "${NEO4J_READONLY_USER:?NEO4J_READONLY_USER is required}"
: "${NEO4J_READONLY_PASSWORD:?NEO4J_READONLY_PASSWORD is required}"

echo "Creating user '$NEO4J_READONLY_USER' (Neo4j Community — no custom roles)..."

docker compose exec -T neo4j cypher-shell \
  -u "$NEO4J_USER" \
  -p "$NEO4J_PASSWORD" \
  "CREATE USER \`$NEO4J_READONLY_USER\` IF NOT EXISTS SET PASSWORD '$NEO4J_READONLY_PASSWORD' CHANGE NOT REQUIRED;"

echo "Verifying login for '$NEO4J_READONLY_USER'..."

docker compose exec -T neo4j cypher-shell \
  -u "$NEO4J_READONLY_USER" \
  -p "$NEO4J_READONLY_PASSWORD" \
  "RETURN 1 AS ok;"

cat <<EOF

OK: user '$NEO4J_READONLY_USER' created and login verified.

NOTE (Neo4j Community Edition):
  RBAC (CREATE ROLE / GRANT) is not available — all users have admin privileges.
  Guardrail #1 on dev: separate credentials for text2cypher (not admin password).
  Write blocking: app-layer guardrails in task 07 (regex, LIMIT, timeout).

  For Enterprise / Aura with RBAC, see: devops/neo4j/init-readonly-enterprise.cypher
EOF
