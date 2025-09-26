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
Set-Location "C:\Users\Shubham Gupta\GitHub\TrueCred"
# Ensure the repository root is on PYTHONPATH so relative imports (e.g. `config`) resolve
$env:PYTHONPATH = "$PWD"
# Run the app module as a script so app.py's __main__ path-setup runs
python .\backend\app.py

# Note: Frontend should be started separately with: cd frontend && npm run dev