# Repara schema após stamp incorreto — NÃO usar stamp manual.
# Uso: .\scripts\migrate-legacy.ps1

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host ">> Alembic upgrade head (inclui repair 26 se pendente)..." -ForegroundColor Cyan
docker compose exec -T api alembic upgrade head
docker compose restart api
Start-Sleep 3

try {
    $h = Invoke-RestMethod http://localhost:8000/health -TimeoutSec 5
    Write-Host "API: $($h.status) | DB: $($h.database)" -ForegroundColor Green
} catch {
    Write-Host "API ainda com problema — veja: docker compose logs api --tail 40" -ForegroundColor Red
}
