@echo off
REM Setup IPFS for TrueCred development environment

echo Setting up IPFS for TrueCred...

REM Check if IPFS is already installed
where ipfs >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo IPFS not found. Please install IPFS from https://dist.ipfs.io/#go-ipfs
    echo After installation, run 'ipfs init' to initialize your IPFS node.
    echo Then run this script again.
    exit /b 1
)

echo IPFS is installed.

REM Check if IPFS is initialized
ipfs cat /ipfs/QmQPeNsJPyVWPFDVHb77w8G42Fvo15z4bG2X8D2GhfbSXc/readme >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Initializing IPFS...
    ipfs init
    if %ERRORLEVEL% neq 0 (
        echo Failed to initialize IPFS.
        exit /b 1
    )
)

echo IPFS is initialized.

REM Configure CORS for the API
echo Configuring CORS for IPFS API...
ipfs config --json API.HTTPHeaders.Access-Control-Allow-Origin "[\"*\"]"
ipfs config --json API.HTTPHeaders.Access-Control-Allow-Methods "[\"PUT\", \"POST\", \"GET\"]"

REM Start IPFS daemon in the background
echo Checking if IPFS daemon is running...
netstat -ano | find "5001" | find "LISTENING" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Starting IPFS daemon...
    start "" ipfs daemon
    echo Waiting for IPFS daemon to start...
    timeout /t 5 /nobreak
)

echo Testing IPFS connection...
ipfs id >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Failed to connect to IPFS daemon.
    echo Please start the IPFS daemon manually with 'ipfs daemon'
    exit /b 1
)

echo IPFS daemon is running.

echo IPFS setup completed successfully!
echo.
echo You can access the IPFS WebUI at: http://localhost:5001/webui
echo.
echo To stop IPFS daemon later, run: ipfs shutdown
