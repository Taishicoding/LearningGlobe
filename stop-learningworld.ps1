$ErrorActionPreference = 'Stop'
$projectDir = $PSScriptRoot
$pidFile = Join-Path $env:TEMP 'LearningWorld-8000.pid'

if (-not (Test-Path $pidFile)) {
    Write-Host 'No LearningWorld launcher server was recorded.'
    exit 0
}

$serverId = Get-Content $pidFile -Raw
$process = Get-CimInstance Win32_Process -Filter "ProcessId = $serverId" -ErrorAction SilentlyContinue
if ($process -and $process.CommandLine -like "*http.server*8000*$projectDir*") {
    Stop-Process -Id ([int]$serverId) -Force
    Write-Host 'Stopped LearningWorld.'
}
else {
    Write-Host 'The recorded LearningWorld server is no longer running.'
}
Remove-Item $pidFile -ErrorAction SilentlyContinue
