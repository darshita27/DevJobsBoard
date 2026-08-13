$ErrorActionPreference = 'Continue'
$scriptDir = "C:\Users\darsh\Documents\dev-jobs-fullstack\backend"

while ($true) {
    & "$scriptDir\run_fetch_jobs.ps1"
    Start-Sleep -Seconds 3600
}
