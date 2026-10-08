# Launch Live Service for Apex RiskEngine
$workDir = "c:\Users\Mnvsai\Desktop\Automation"
Set-Location $workDir

# 1. Kill old processes
Get-Process | Where-Object { $_.ProcessName -match "cloudflared" } | Stop-Process -Force -ErrorAction SilentlyContinue

# Verify if port 8000 is listening
$portOk = $false
try {
    $res = Invoke-WebRequest -Uri "http://127.0.0.1:8000" -UseBasicParsing -TimeoutSec 2
    if ($res.StatusCode -eq 200) { $portOk = $true }
} catch {
    $portOk = $false
}

if (-not $portOk) {
    Write-Host "Starting Uvicorn server..."
    Get-Process | Where-Object { $_.ProcessName -match "python" } | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
    Start-Process -FilePath "python" -ArgumentList "-m uvicorn app.main:app --host 127.0.0.1 --port 8000" -WorkingDirectory $workDir -WindowStyle Hidden
    Start-Sleep -Seconds 3
}

# 2. Start Cloudflare Tunnel
$logFile = "$workDir\tunnel.log"
if (Test-Path $logFile) { Remove-Item $logFile -Force }

$cfBin = "C:\Program Files (x86)\cloudflared\cloudflared.exe"
if (-not (Test-Path $cfBin)) {
    $cfBin = "cloudflared"
}

Write-Host "Launching Cloudflare Tunnel with log file: $logFile"
Start-Process -FilePath $cfBin -ArgumentList "tunnel --url http://127.0.0.1:8000 --logfile `"$logFile`"" -WorkingDirectory $workDir -WindowStyle Hidden

# 3. Wait for URL
$publicUrl = ""
for ($i = 0; $i -lt 15; $i++) {
    Start-Sleep -Seconds 1
    if (Test-Path $logFile) {
        $content = Get-Content $logFile -Raw
        if ($content -match "https://([a-zA-Z0-9-]+)\.trycloudflare\.com") {
            $publicUrl = $matches[0]
            break
        }
    }
}

if ($publicUrl) {
    Write-Host "SUCCESS: Live URL is $publicUrl"
    Set-Content -Path "$workDir\LIVE_HOSTED_URL.txt" -Value $publicUrl
    
    # Test HTTP request
    Start-Sleep -Seconds 3
    try {
        $test = Invoke-WebRequest -Uri $publicUrl -UseBasicParsing -TimeoutSec 10
        Write-Host "HTTP Test Status: $($test.StatusCode)"
    } catch {
        Write-Host "HTTP Test Warning: $_"
    }
} else {
    Write-Host "Failed to obtain Cloudflare tunnel URL"
}
