#!/usr/bin/env bash
# Testes negativos RBAC — token de usuário consulta deve receber 403 em mutações.
# Uso: TOKEN=<jwt> ./scripts/test_permissions.sh
#      ou: ./scripts/test_permissions.sh  (faz login com CONSULTA_USER/CONSULTA_PASS)

set -euo pipefail

API_BASE="${API_BASE:-http://localhost:8000/api/v1}"
CONSULTA_USER="${CONSULTA_USER:-consulta}"
CONSULTA_PASS="${CONSULTA_PASS:-Consulta@123}"

if [[ -z "${TOKEN:-}" ]]; then
  echo ">> Login como ${CONSULTA_USER}..."
  TOKEN=$(curl -sf -X POST "${API_BASE%/api/v1}/api/v1/auth/login" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=${CONSULTA_USER}&password=${CONSULTA_PASS}" \
    | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
fi

AUTH=(-H "Authorization: Bearer ${TOKEN}" -H "Content-Type: application/json")

fail() { echo "FAIL: $1 (HTTP $2, esperado 403)"; exit 1; }
pass() { echo "OK:   $1 → 403"; }

# --- Mutações (devem falhar) ---
code=$(curl -s -o /dev/null -w "%{http_code}" -X POST "${API_BASE}/vendas/" \
  "${AUTH[@]}" -d '{"id_comprador":1,"itens":[]}')
[[ "$code" == "403" ]] && pass "POST /vendas/" || fail "POST /vendas/" "$code"

code=$(curl -s -o /dev/null -w "%{http_code}" -X POST "${API_BASE}/insumos/" \
  "${AUTH[@]}" -d '{"nome":"Teste RBAC","tipo":"Fertilizante","unidade":"kg"}')
[[ "$code" == "403" ]] && pass "POST /insumos/" || fail "POST /insumos/" "$code"

code=$(curl -s -o /dev/null -w "%{http_code}" -X POST "${API_BASE}/pragas/tipos" \
  "${AUTH[@]}" -d '{"nome":"Praga Teste"}')
[[ "$code" == "403" ]] && pass "POST /pragas/tipos" || fail "POST /pragas/tipos" "$code"

code=$(curl -s -o /dev/null -w "%{http_code}" -X PUT "${API_BASE}/funcionarios/1" \
  "${AUTH[@]}" -d '{"perfis":["admin"]}')
[[ "$code" == "403" ]] && pass "PUT /funcionarios/1 (escalação)" || fail "PUT /funcionarios/1" "$code"

code=$(curl -s -o /dev/null -w "%{http_code}" -X PATCH "${API_BASE}/auth/me" \
  "${AUTH[@]}" -d '{"perfis":["admin"]}')
# PATCH /me aceita body mas ignora perfis — deve ser 200, não escala
[[ "$code" == "200" ]] && pass "PATCH /auth/me (ignora perfis, 200)" || fail "PATCH /auth/me" "$code"

# --- Leitura bloqueada (users.view) ---
code=$(curl -s -o /dev/null -w "%{http_code}" -X GET "${API_BASE}/funcionarios/" "${AUTH[@]}")
[[ "$code" == "403" ]] && pass "GET /funcionarios/ (sem users.view)" || fail "GET /funcionarios/" "$code"

# --- Leitura permitida ---
code=$(curl -s -o /dev/null -w "%{http_code}" -X GET "${API_BASE}/vendas/" "${AUTH[@]}")
[[ "$code" == "200" ]] && pass "GET /vendas/ (consulta.view)" || fail "GET /vendas/ deveria ser 200" "$code"

code=$(curl -s -o /dev/null -w "%{http_code}" -X GET "${API_BASE}/dashboard/financeiro" "${AUTH[@]}")
[[ "$code" == "200" ]] && pass "GET /dashboard/financeiro" || fail "GET /dashboard/financeiro" "$code"

echo ""
echo "Todos os testes negativos passaram."
