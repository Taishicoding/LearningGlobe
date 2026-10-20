$ErrorActionPreference = 'Stop'
$projectDir = $PSScriptRoot
$baseUrl = 'http://127.0.0.1:8000'
$pidFile = Join-Path $env:TEMP 'LearningWorld-8000.pid'
$stdoutLog = Join-Path $env:TEMP 'LearningWorld-server.log'
$stderrLog = Join-Path $env:TEMP 'LearningWorld-server-error.log'

function Test-LearningWorld {
    try {
        $page = Invoke-WebRequest -Uri "$baseUrl/index.html" -UseBasicParsing -TimeoutSec 2
        return $page.Content.Contains('<title>LearningWorld')
    }
    catch {
        return $false
    }
}

if (Test-LearningWorld) {
    Start-Process $baseUrl
    exit 0
}

$pythonCommand = Get-Command py.exe -ErrorAction SilentlyContinue
if ($pythonCommand) {
    $pythonPath = (& py -3 -c 'import sys; print(sys.executable)' 2>$null | Select-Object -First 1)
}
else {
    $pythonCommand = Get-Command python.exe -ErrorAction SilentlyContinue
    if (-not $pythonCommand) {
        Write-Host 'Python 3 was not found. Install Python from python.org, then try again.' -ForegroundColor Red
        Read-Host 'Press Enter to close'
        exit 1
    }
    $pythonPath = $pythonCommand.Source
}

if (-not $pythonPath -or -not (Test-Path $pythonPath)) {
    Write-Host 'Python 3 was not found. Install Python from python.org, then try again.' -ForegroundColor Red
    Read-Host 'Press Enter to close'
    exit 1
}

$arguments = '-m http.server 8000 --bind 127.0.0.1 --directory "{0}"' -f $projectDir
$server = Start-Process -FilePath $pythonPath -ArgumentList $arguments -WindowStyle Hidden -PassThru `
    -RedirectStandardOutput $stdoutLog -RedirectStandardError $stderrLog
Set-Content -Path $pidFile -Value $server.Id

for ($attempt = 0; $attempt -lt 30; $attempt++) {
    if (Test-LearningWorld) {
        Start-Process $baseUrl
        exit 0
    }
    if ($server.HasExited) { break }
    Start-Sleep -Milliseconds 200
}

Remove-Item $pidFile -ErrorAction SilentlyContinue
Write-Host "Could not start LearningWorld at $baseUrl. Check $stderrLog for details." -ForegroundColor Red
Read-Host 'Press Enter to close'
exit 1
