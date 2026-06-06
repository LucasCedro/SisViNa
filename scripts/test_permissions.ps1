# Testes negativos RBAC — usuário consulta deve receber 403 em mutações.
# Uso: .\scripts\test_permissions.ps1
# Env: $env:API_BASE, $env:CONSULTA_USER, $env:CONSULTA_PASS, $env:TOKEN

$ErrorActionPreference = "Stop"
$ApiBase = if ($env:API_BASE) { $env:API_BASE } else { "http://localhost:8000/api/v1" }
$ConsultaUser = if ($env:CONSULTA_USER) { $env:CONSULTA_USER } else { "consulta" }
$ConsultaPass = if ($env:CONSULTA_PASS) { $env:CONSULTA_PASS } else { "Consulta@123" }

function Assert-Status($Label, $Expected, $Actual) {
    if ($Actual -ne $Expected) {
        throw "FAIL: $Label (HTTP $Actual, esperado $Expected)"
    }
    Write-Host "OK:   $Label → $Expected" -ForegroundColor Green
}

$Token = $env:TOKEN
if (-not $Token) {
    Write-Host ">> Login como $ConsultaUser..."
    $loginBody = "username=$ConsultaUser&password=$ConsultaPass"
    $login = Invoke-RestMethod -Method Post -Uri "$ApiBase/auth/login" `
        -ContentType "application/x-www-form-urlencoded" -Body $loginBody
    $Token = $login.access_token
}

$Headers = @{ Authorization = "Bearer $Token" }

function Invoke-Status($Method, $Uri, $Body = $null) {
    try {
        if ($Body) {
            Invoke-WebRequest -Method $Method -Uri $Uri -Headers $Headers `
                -ContentType "application/json" -Body ($Body | ConvertTo-Json) -UseBasicParsing | Out-Null
            return 200
        }
        Invoke-WebRequest -Method $Method -Uri $Uri -Headers $Headers -UseBasicParsing | Out-Null
        return 200
    }
    catch {
        return [int]$_.Exception.Response.StatusCode
    }
}

Assert-Status "POST /vendas/" 403 (Invoke-Status Post "$ApiBase/vendas/" @{ id_comprador = 1; itens = @() })
Assert-Status "POST /insumos/" 403 (Invoke-Status Post "$ApiBase/insumos/" @{ nome = "Teste RBAC"; tipo = "Fertilizante"; unidade = "kg" })
Assert-Status "POST /pragas/tipos" 403 (Invoke-Status Post "$ApiBase/pragas/tipos" @{ nome = "Praga Teste" })
Assert-Status "PUT /funcionarios/1" 403 (Invoke-Status Put "$ApiBase/funcionarios/1" @{ perfis = @("admin") })
Assert-Status "PATCH /auth/me (ignora perfis)" 200 (Invoke-Status Patch "$ApiBase/auth/me" @{ perfis = @("admin") })
Assert-Status "GET /funcionarios/" 403 (Invoke-Status Get "$ApiBase/funcionarios/")
Assert-Status "GET /vendas/" 200 (Invoke-Status Get "$ApiBase/vendas/")
Assert-Status "GET /dashboard/financeiro" 200 (Invoke-Status Get "$ApiBase/dashboard/financeiro")

Write-Host "`nTodos os testes negativos passaram." -ForegroundColor Cyan
