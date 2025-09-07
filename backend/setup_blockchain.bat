@echo off
REM Blockchain setup script for TrueCred
echo TrueCred Blockchain Setup
echo =========================

echo Checking environment...

REM Check if .env file exists
if not exist .env (
    echo ERROR: .env file not found. Please create one based on .env.sample
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Create build directory if it doesn't exist
if not exist contracts\build mkdir contracts\build

REM Compile the contract
echo Compiling smart contract...
python contracts\compile_contract.py

REM Ask user if they want to deploy
echo.
echo Do you want to deploy the contract to Goerli testnet? (y/n)
set /p deploy=

if /i "%deploy%"=="y" (
    echo Deploying smart contract to Goerli testnet...
    python contracts\deploy_contract.py --network goerli
    
    echo.
    echo IMPORTANT: Make sure to update your .env file with the new CONTRACT_ADDRESS
    echo.
)

REM Test blockchain connection
echo Testing blockchain connection...
python contracts\test_blockchain.py

echo.
echo Blockchain setup completed!
echo.
