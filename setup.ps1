$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
Write-Host 'LocalCoder RTX setup' -ForegroundColor Cyan
if (-not (Get-Command py -ErrorAction SilentlyContinue)) { throw 'Install Python 3.10+ with the Windows py launcher: https://www.python.org/downloads/' }
& py -3 -c "import sys; assert sys.version_info >= (3,10), 'Python 3.10+ required'"
if ($LASTEXITCODE -ne 0) { throw 'Python check failed' }
if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) { throw 'Install and open Ollama: https://ollama.com/download/windows' }
try { Invoke-RestMethod http://127.0.0.1:11434/api/tags | Out-Null } catch { throw 'Open Ollama first, then rerun setup.' }
$model = & py -3 -c "from localcoder.config import Settings; print(Settings.auto().model)"
Write-Host "Downloading $model (one-time internet connection required)"
& ollama pull $model
if ($LASTEXITCODE -ne 0) { throw 'Model download failed. Retry setup.' }
Write-Host 'Ready. Double-click start_ui.bat' -ForegroundColor Green
