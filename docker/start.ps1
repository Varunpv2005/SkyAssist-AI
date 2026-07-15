Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

if (-not (Test-Path "docker\.env")) {
    Copy-Item "docker\.env.example" "docker\.env"
    Write-Host "Created docker\.env from example — update SECRET_KEY before production use."
}

docker compose --profile ai up -d --build

Write-Host "SKYASSIST AI is starting..."
Write-Host "  Frontend:  http://localhost"
Write-Host "  Backend:   http://localhost:8000"
Write-Host "  API docs:  http://localhost:8000/docs"
