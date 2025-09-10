# Run development servers for TrueCred
# This script starts both the frontend and backend servers

# Stop on errors
$ErrorActionPreference = "Stop"

Write-Host "Starting TrueCred development environment..." -ForegroundColor Cyan

# Start backend server (Flask)
Write-Host "Starting Flask backend server..." -ForegroundColor Green
Start-Process -FilePath "cmd.exe" -ArgumentList "/c", "cd backend && python app.py"

# Give the backend time to start
Write-Host "Waiting for backend to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Start frontend server (Vite)
Write-Host "Starting Vite frontend server..." -ForegroundColor Green
Start-Process -FilePath "cmd.exe" -ArgumentList "/c", "cd frontend && npm run dev"

Write-Host "`nTrueCred Development Environment" -ForegroundColor Cyan
Write-Host "-----------------------------" -ForegroundColor Cyan
Write-Host "Backend: http://localhost:5000" -ForegroundColor Magenta
Write-Host "Frontend: http://localhost:5173" -ForegroundColor Magenta
Write-Host "`nPress Ctrl+C to stop all servers when done" -ForegroundColor Yellow
Write-Host "Note: You'll need to manually close the opened terminal windows" -ForegroundColor Yellow

# Keep the script running to allow for easy termination of both processes
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
} finally {
    Write-Host "`nShutting down development environment..." -ForegroundColor Cyan
}
