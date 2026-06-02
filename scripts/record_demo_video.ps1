# Auto record demo -> assets/demo.mp4
# Usage: .\scripts\record_demo_video.ps1
# Optional: -SkipServer when frontend/backend already on 3000/8002

param(
    [switch]$SkipServer
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Assets = Join-Path $Root "assets"
$DemoMp4 = Join-Path $Assets "demo.mp4"
$E2eDir = Join-Path $Root "e2e"

Set-Location $Root

function Test-Url($url) {
    try {
        $r = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 5
        return $r.StatusCode -eq 200
    } catch {
        return $false
    }
}

$frontOk = Test-Url "http://localhost:3000"
$backOk = Test-Url "http://127.0.0.1:8002/health"
Write-Host ">>> frontend :3000 = $frontOk | backend :8002 = $backOk"

if (-not $SkipServer -and (-not $frontOk -or -not $backOk)) {
    Write-Host ">>> playwright webServer will start missing services"
}

Set-Location $E2eDir
if (-not (Test-Path "node_modules")) {
    Write-Host ">>> npm install (e2e)..."
    npm install
}
if (-not (Test-Path "$env:USERPROFILE\AppData\Local\ms-playwright")) {
    Write-Host ">>> playwright install chromium..."
    npx playwright install chromium
}

$env:E2E_SKIP_SERVER = if ($SkipServer -and $frontOk -and $backOk) { "1" } else { "" }

Write-Host ">>> Playwright recording (about 2-4 min)..."
npx playwright test demo-recording.spec.ts --config=playwright.demo.config.ts --project=demo
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Playwright recording failed" -ForegroundColor Red
    exit 1
}

$webm = Get-ChildItem -Path (Join-Path $E2eDir "demo-output") -Recurse -Filter "*.webm" -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

if (-not $webm) {
    $webm = Get-ChildItem -Path (Join-Path $E2eDir "test-results") -Recurse -Filter "video.webm" -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1
}

if (-not $webm) {
    Write-Host "ERROR: no webm file found" -ForegroundColor Red
    exit 1
}

$sizeMb = [math]::Round($webm.Length / 1MB, 2)
Write-Host ">>> source: $($webm.FullName) ($sizeMb MB)"

New-Item -ItemType Directory -Force -Path $Assets | Out-Null

$ffmpeg = Get-Command ffmpeg -ErrorAction SilentlyContinue
if ($ffmpeg) {
    Write-Host ">>> ffmpeg -> mp4..."
    $prevEap = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    & ffmpeg -y -i $webm.FullName -c:v libx264 -pix_fmt yuv420p -movflags +faststart $DemoMp4 *> $null
    $ffmpegOk = $LASTEXITCODE -eq 0
    $ErrorActionPreference = $prevEap
    if (-not $ffmpegOk) {
        Write-Host "WARN: ffmpeg failed, keeping webm" -ForegroundColor Yellow
        Copy-Item $webm.FullName (Join-Path $Assets "demo.webm") -Force
        exit 1
    }
} else {
    Write-Host ">>> ffmpeg not found, copy webm to assets/demo.webm" -ForegroundColor Yellow
    Copy-Item $webm.FullName (Join-Path $Assets "demo.webm") -Force
    Write-Host "    ffmpeg -i assets/demo.webm -c:v libx264 assets/demo.mp4"
    exit 0
}

if (Test-Path $DemoMp4) {
    $outMb = [math]::Round((Get-Item $DemoMp4).Length / 1MB, 2)
    Write-Host ""
    Write-Host "=== Done: $DemoMp4 ($outMb MB) ===" -ForegroundColor Green
} else {
    Write-Host "ERROR: demo.mp4 not created" -ForegroundColor Red
    exit 1
}
