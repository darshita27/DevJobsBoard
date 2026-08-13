$ErrorActionPreference = 'Continue'

$backendDir = "C:\Users\darsh\Documents\dev-jobs-fullstack\backend"
$logDir = Join-Path $backendDir "logs"
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }
$logFile = Join-Path $logDir "fetch_jobs.log"

$start = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Add-Content -Path $logFile -Value "`n----- Run started $start -----"

$output = & "$backendDir\venv\Scripts\python.exe" "$backendDir\manage.py" fetch_jobs 2>&1
$exitCode = $LASTEXITCODE
$output | Out-File -FilePath $logFile -Append -Encoding utf8

$end = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Add-Content -Path $logFile -Value "----- Run finished $end (exit $exitCode) -----"
