# SisViNa — Docker (único fluxo oficial, projeto sisvina na raiz)
param(
    [Parameter(Position = 0)]
    [ValidateSet('start', 'start-all', 'start-demo', 'stop', 'restart-api', 'migrate', 'logs', 'ps', 'smoke', 'help')]
    [string]$Command = 'help',
    [switch]$Smoke
)

function Invoke-Smoke {
    & "$PSScriptRoot\smoke.ps1"
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

function Ensure-Network {
    $exists = docker network ls -q -f "name=^viveiro_network$"
    if (-not $exists) {
        Write-Host ">> Criando rede viveiro_network..." -ForegroundColor Cyan
        docker network create viveiro_network | Out-Null
    }
}

function Invoke-Compose([string[]]$Args) {
    & docker compose @Args
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

function Stop-Orphans {
    # Containers antigos (compose modular / container_name fixo) — remoção única na migração
    foreach ($name in @('viveiro_api', 'viveiro_web', 'viveiro_site', 'viveiro_postgres', 'viveiro_pgadmin', 'viveiro-site')) {
        docker rm -f $name 2>$null | Out-Null
    }
    foreach ($proj in @('bd_viveiro', 'sisvina-infra', 'sisvina-api', 'sisvina-web', 'sisvina-site')) {
        docker compose -p $proj down 2>$null | Out-Null
    }
}

switch ($Command) {
    'start' {
        Stop-Orphans
        Ensure-Network
        Invoke-Compose up, -d, --build, postgres, api
        Start-Sleep -Seconds 2
        Invoke-Compose exec, -T, api, alembic, upgrade, head
        Write-Host "OK — API http://localhost:8000/docs | Front: npm run dev em sistema-viveiro-nativas" -ForegroundColor Green
    }
    'start-all' {
        Stop-Orphans
        Ensure-Network
        Invoke-Compose --profile, docker-web, --profile, site, up, -d, --build, postgres, api, web, site
        Start-Sleep -Seconds 3
        Invoke-Compose exec, -T, api, alembic, upgrade, head
        Write-Host "OK — app :5173 | site :3000 | API :8000/docs" -ForegroundColor Green
        if ($Smoke) { Invoke-Smoke }
    }
    'start-demo' {
        Stop-Orphans
        Ensure-Network
        Invoke-Compose --profile, docker-web, --profile, site, --profile, tools, up, -d, --build
        Start-Sleep -Seconds 3
        Invoke-Compose exec, -T, api, alembic, upgrade, head
        Write-Host "OK — app :5173 | API :8000 | site :3000 | PgAdmin :5050" -ForegroundColor Green
    }
    'stop' {
        Invoke-Compose --profile, docker-web, --profile, site, --profile, tools, down
        Write-Host "Stack parada. Dados do Postgres preservados (volume postgres_data)." -ForegroundColor Yellow
    }
    'restart-api' {
        Invoke-Compose up, -d, --build, --force-recreate, api
        Write-Host "API recriada (le .env atualizado)." -ForegroundColor Green
    }
    'migrate' {
        Invoke-Compose exec, -T, api, alembic, upgrade, head
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Falhou? Banco legado: .\scripts\migrate-legacy.ps1" -ForegroundColor Yellow
        }
    }
    'logs' {
        Invoke-Compose logs, -f, api, web
    }
    'ps' {
        Invoke-Compose ps
    }
    'smoke' {
        Invoke-Smoke
    }
    default {
        Write-Host @"
SisViNa — dev.ps1 (Docker oficial)

  .\scripts\dev.ps1 start       Postgres + API
  .\scripts\dev.ps1 start-all   + front Vue + site marketing (:5173 + :3000)
  .\scripts\dev.ps1 start-all -Smoke   sobe stack e roda smoke read-only
  .\scripts\dev.ps1 smoke       valida API (login, home, coleta, venda)
  .\scripts\dev.ps1 start-demo  + PgAdmin (:5050) — mesmo stack do start-all
  .\scripts\dev.ps1 stop        para tudo (mantem dados)
  .\scripts\dev.ps1 restart-api recria API apos editar .env
  .\scripts\dev.ps1 migrate     alembic upgrade head
  .\scripts\dev.ps1 logs        api + web
  .\scripts\dev.ps1 ps

Front recomendado (sem Docker): cd sistema-viveiro-nativas && npm run dev

Docs: docs/DEV_DOCKER.md
"@
    }
}
