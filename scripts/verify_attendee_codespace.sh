#!/usr/bin/env bash
# Health check for an attendee's Codespace. Verifies LangFlow, Phoenix, and KeyBroker
# are reachable, and that the basic plumbing (env vars, mounted files) is in place.
#
# Exits 0 on all-green, 1 on any failure.
set -uo pipefail

GREEN=$'\033[32m'; RED=$'\033[31m'; YELLOW=$'\033[33m'; RESET=$'\033[0m'
fails=0

check() {
    local label="$1"; shift
    if "$@"; then
        printf "  ${GREEN}OK${RESET}     %s\n" "$label"
    else
        printf "  ${RED}FAIL${RESET}   %s\n" "$label"
        fails=$((fails + 1))
    fi
}

note() {
    printf "  ${YELLOW}NOTE${RESET}   %s\n" "$1"
}

http_ok() {
    local url="$1"
    local code
    code=$(curl -sS -o /dev/null -w "%{http_code}" --max-time 5 "$url" 2>/dev/null || echo "000")
    [ "$code" = "200" ]
}

compose_service_running() {
    local service="$1"
    docker compose -f .devcontainer/docker-compose.yml ps --services --status running 2>/dev/null \
        | grep -qx "$service"
}

echo "Codespace health check"
echo "======================"

echo
echo "Environment"
[ -n "${ATTENDEE_ID:-}" ] && check "ATTENDEE_ID set ($ATTENDEE_ID)" true || check "ATTENDEE_ID set" false
[ -n "${ATTENDEE_BROKER_TOKEN:-}" ] && check "ATTENDEE_BROKER_TOKEN set" true || check "ATTENDEE_BROKER_TOKEN set" false
[ -n "${OPENAI_API_KEY_REAL:-}" ] && check "OPENAI_API_KEY_REAL set (real OpenAI calls will work)" true || note "OPENAI_API_KEY_REAL not set — /healthz works but LLM calls will 401"

echo
echo "Files"
check "proxy/tokens.json exists"  test -f proxy/tokens.json
check "docker-compose.yml exists" test -f .devcontainer/docker-compose.yml

echo
echo "Containers"
check "devshell service running"  compose_service_running "devshell"
check "langflow service running"  compose_service_running "langflow"
check "phoenix service running"   compose_service_running "phoenix"
check "keybroker service running" compose_service_running "keybroker"

echo
echo "Endpoints"
check "KeyBroker /healthz"  http_ok "http://localhost:8000/healthz"
check "LangFlow /health"    http_ok "http://localhost:7860/health"
check "Phoenix UI"          http_ok "http://localhost:6006"

echo
if [ "$fails" -eq 0 ]; then
    printf "${GREEN}All checks passed.${RESET}\n"
    exit 0
else
    printf "${RED}%d check(s) failed.${RESET} See docs/troubleshooting.md\n" "$fails"
    exit 1
fi
