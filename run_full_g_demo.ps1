$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

$Python = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    Write-Error "Missing .venv Python at $Python. Create the environment first; see REPRODUCE_FULL_G.md."
}

& $Python --version

if ($env:OPENROUTER_API_KEY) {
    Write-Host "OPENROUTER_API_KEY is set in this shell, but this launcher will not use it."
}

$Url = "http://127.0.0.1:8765/?demo=full_g_reviewer"
Write-Host "Starting local Full-G reviewer demo."
Write-Host "No cloud services, paid APIs, or model calls are used by this launcher."
Write-Host "Open: $Url"
& $Python -m nowmind.demo.web --host 127.0.0.1 --port 8765
