# Smoke read-only pos-start-all: infra + login + fluxo home -> coleta -> venda (via API).
#
# Uso:
#   .\scripts\smoke.ps1
#   $env:SMOKE_USER = 'Super_Brotare'; $env:SMOKE_PASS = '***'; .\scripts\smoke.ps1
#   .\scripts\dev.ps1 start-all -Smoke
#
# Env:
#   API_BASE          default http://localhost:8000
#   WEB_BASE          default http://localhost:5173
#   SMOKE_USER        default Super_Brotare
#   SMOKE_PASS        obrigatorio (nao commitar); fallback demo.admin se ausente
#   SMOKE_TIMEOUT_SEC default 120
#   SMOKE_SKIP_FRONT  1 = nao espera o Vite (:5173)

param(
    [switch]$SkipFront
)

$ErrorActionPreference = 'Stop'

$ApiRoot = if ($env:API_BASE) { $env:API_BASE.TrimEnd('/') } else { 'http://localhost:8000' }
$ApiV1 = if ($ApiRoot -match '/api/v1$') { $ApiRoot } else { "$ApiRoot/api/v1" }
$WebBase = if ($env:WEB_BASE) { $env:WEB_BASE.TrimEnd('/') } else { 'http://localhost:5173' }
$TimeoutSec = if ($env:SMOKE_TIMEOUT_SEC) { [int]$env:SMOKE_TIMEOUT_SEC } else { 120 }
$SmokeUser = if ($env:SMOKE_USER) { $env:SMOKE_USER } else { 'Super_Brotare' }
$SkipFrontCheck = $SkipFront -or ($env:SMOKE_SKIP_FRONT -eq '1')

function Write-Step($msg) {
    Write-Host ">> $msg" -ForegroundColor Cyan
}

function Assert-Ok($label, $condition, $detail = '') {
    if (-not $condition) {
        $extra = if ($detail) { " ($detail)" } else { '' }
        throw "FAIL: $label$extra"
    }
    Write-Host "OK:   $label" -ForegroundColor Green
}

function Wait-Until {
    param(
        [string]$Label,
        [scriptblock]$Test,
        [int]$TimeoutSeconds = 120,
        [int]$IntervalSeconds = 2
    )
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    $attempt = 0
    while ((Get-Date) -lt $deadline) {
        $attempt++
        try {
            $result = & $Test
            if ($result) {
                Write-Host "OK:   $Label (tentativa $attempt)" -ForegroundColor Green
                return $result
            }
        }
        catch {
            # proxima tentativa
        }
        Start-Sleep -Seconds $IntervalSeconds
    }
    throw "TIMEOUT: $Label apos ${TimeoutSeconds}s"
}

function Get-HttpStatus($Uri, $Headers = $null) {
    try {
        $params = @{ Uri = $Uri; Method = 'Get'; UseBasicParsing = $true; TimeoutSec = 15 }
        if ($Headers) { $params.Headers = $Headers }
        $r = Invoke-WebRequest @params
        return [int]$r.StatusCode
    }
    catch {
        if ($_.Exception.Response) { return [int]$_.Exception.Response.StatusCode }
        throw
    }
}

function New-FormBody([hashtable]$Fields) {
    $parts = @()
    foreach ($key in $Fields.Keys) {
        $parts += ('{0}={1}' -f [uri]::EscapeDataString([string]$key), [uri]::EscapeDataString([string]$Fields[$key]))
    }
    return ($parts -join '&')
}

Write-Host ""
Write-Host "=== SisViNa smoke (read-only) ===" -ForegroundColor White
Write-Host "API: $ApiV1 | Web: $WebBase | User: $SmokeUser"
Write-Host ""

Write-Step 'Aguardando API /health'
Wait-Until -Label 'API /health' -TimeoutSeconds $TimeoutSec -Test {
    $h = Invoke-RestMethod -Uri "$ApiRoot/health" -TimeoutSec 5
    return ($h.status -eq 'ok' -and $h.database -eq 'connected')
} | Out-Null

if (-not $SkipFrontCheck) {
    Write-Step 'Aguardando front (:5173)'
    Wait-Until -Label 'Front Vite' -TimeoutSeconds $TimeoutSec -Test {
        return (Get-HttpStatus $WebBase) -eq 200
    } | Out-Null
}

$SmokePass = $env:SMOKE_PASS
if (-not $SmokePass) {
    Write-Host "AVISO: SMOKE_PASS nao definido - usando demo.admin (dev)" -ForegroundColor Yellow
    $SmokeUser = 'demo.admin'
    $SmokePass = 'Senha!@#'
}

Write-Step "Login ($SmokeUser)"
$login = Invoke-RestMethod -Method Post -Uri "$ApiV1/auth/login" `
    -ContentType 'application/x-www-form-urlencoded' `
    -Body (New-FormBody @{ username = $SmokeUser; password = $SmokePass }) `
    -TimeoutSec 15
Assert-Ok 'Login retornou token' ($null -ne $login.access_token -and $login.access_token.Length -gt 20)

$Headers = @{ Authorization = "Bearer $($login.access_token)" }

Write-Step 'Fluxo login -> home -> coleta -> venda'

$checks = @(
    @{ Label = 'GET /auth/me (login)';            Uri = "$ApiV1/auth/me" },
    @{ Label = 'GET /dashboard/resumo (home)';    Uri = "$ApiV1/dashboard/resumo" },
    @{ Label = 'GET /coletas-sementes/ (coleta)'; Uri = "$ApiV1/coletas-sementes/?limit=5" },
    @{ Label = 'GET /lotes-sementes/ (coleta)';   Uri = "$ApiV1/lotes-sementes/?limit=5" },
    @{ Label = 'GET /vendas/ (vendas)';           Uri = "$ApiV1/vendas/?limit=5" },
    @{ Label = 'GET /estoques/resumo (pipeline)'; Uri = "$ApiV1/estoques/resumo" }
)

foreach ($c in $checks) {
    $status = Get-HttpStatus -Uri $c.Uri -Headers $Headers
    Assert-Ok $c.Label ($status -eq 200) "HTTP $status"
}

$resumo = Invoke-RestMethod -Uri "$ApiV1/dashboard/resumo" -Headers $Headers -TimeoutSec 15
Assert-Ok 'Home /dashboard/resumo JSON' ($null -ne $resumo.especies -or $null -ne $resumo.mudas_ativas)

$coletas = Invoke-RestMethod -Uri "$ApiV1/coletas-sementes/?limit=500" -Headers $Headers -TimeoutSec 15
$vendas = Invoke-RestMethod -Uri "$ApiV1/vendas/?limit=500" -Headers $Headers -TimeoutSec 15
$cCount = @($coletas).Count
$vCount = @($vendas).Count
Write-Host "INFO: coletas=$cCount vendas=$vCount mudas_ativas=$($resumo.mudas_ativas)" -ForegroundColor DarkGray

Write-Host ""
Write-Host "Smoke passou - stack pronta para uso." -ForegroundColor Cyan
Write-Host ""
