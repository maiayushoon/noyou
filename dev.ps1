# ─────────────────────────────────────────────────────────────────────────────
# NoYou — one-command dev launcher (Windows / PowerShell)
#   Starts the FastAPI backend on :8000 and the Next.js dashboard on :3002,
#   each in its own window. Frees those ports first so nothing drifts.
#
#   Run:   .\dev.ps1        (or double-click dev.bat)
#   Stop:  close the two spawned windows (or Ctrl+C in each)
# ─────────────────────────────────────────────────────────────────────────────
$ErrorActionPreference = "SilentlyContinue"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path

function Free-Port([int]$port) {
  Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue |
    Select-Object -ExpandProperty OwningProcess -Unique |
    ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }
}

Write-Host ""
Write-Host "  NoYou dev launcher" -ForegroundColor Magenta
Write-Host "  ------------------" -ForegroundColor DarkGray
Write-Host "  Freeing ports 8000 (API) and 3002 (dashboard)..." -ForegroundColor DarkGray
Free-Port 8000
Free-Port 3002
Start-Sleep -Milliseconds 800

# --- Backend: FastAPI on :8000 (auto-reload, scoped to backend/) ---
$py = Join-Path $root "backend\venv\Scripts\python.exe"
if (-not (Test-Path $py)) {
  Write-Host "  ! backend venv not found. Run: cd backend; python -m venv venv; venv\Scripts\activate; pip install -r requirements.txt" -ForegroundColor Yellow
  exit 1
}
Write-Host "  Starting backend   -> http://localhost:8000" -ForegroundColor Cyan
Start-Process -FilePath $py `
  -ArgumentList "-m","uvicorn","app.main:app","--app-dir","backend","--reload","--reload-dir","backend","--port","8000" `
  -WorkingDirectory $root

# --- Dashboard: Next.js dev on :3002 ---
$fe = Join-Path $root "frontend"
if (-not (Test-Path (Join-Path $fe "node_modules"))) {
  Write-Host "  Installing dashboard deps (first run)..." -ForegroundColor DarkGray
  Start-Process -FilePath "cmd.exe" -ArgumentList "/c","npm install" -WorkingDirectory $fe -Wait
}
Write-Host "  Starting dashboard -> http://localhost:3002" -ForegroundColor Cyan
Start-Process -FilePath "cmd.exe" -ArgumentList "/k","npm run dev" -WorkingDirectory $fe

Start-Sleep -Seconds 2
Write-Host ""
Write-Host "  NoYou is starting up:" -ForegroundColor Green
Write-Host "    Dashboard : http://localhost:3002   (demo@noyou.app / demo12345)"
Write-Host "    API       : http://localhost:8000   (docs at /docs)"
Write-Host ""
Write-Host "  Two windows opened (backend + dashboard). Close them to stop." -ForegroundColor DarkGray
