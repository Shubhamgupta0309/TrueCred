# TrueCred Development Startup Script
# This script starts all required services for development

Write-Host "Starting TrueCred Development Environment..." -ForegroundColor Green

# Function to start a service in background
function Start-Service {
    param([string]$Name, [string]$Command, [string]$WorkingDir)
    Write-Host "Starting $Name..." -ForegroundColor Yellow
    $process = Start-Process -FilePath "powershell.exe" -ArgumentList "-Command `"$Command`"" -WorkingDirectory $WorkingDir -NoNewWindow -PassThru
    return $process
}

# Start Ganache (Blockchain)
$ganacheProcess = Start-Service -Name "Ganache" -Command "npx ganache --port 9545" -WorkingDir "C:\Users\Shubham Gupta\GitHub\TrueCred\backend\truffle"

# Start IPFS Daemon
$ipfsProcess = Start-Service -Name "IPFS Daemon" -Command "`$env:IPFS_PATH = '$PWD\.ipfs'; .\ipfs daemon" -WorkingDir "C:\Users\Shubham Gupta\GitHub\TrueCred\backend"

# Wait a bit for services to start
Start-Sleep -Seconds 10

# Start Backend
Write-Host "Starting Backend..." -ForegroundColor Yellow
Set-Location "C:\Users\Shubham Gupta\GitHub\TrueCred\backend"
python app.py

# Note: Frontend should be started separately with: cd frontend && npm run dev