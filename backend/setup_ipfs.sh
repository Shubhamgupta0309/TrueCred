#!/bin/bash
# Setup IPFS for TrueCred development environment

echo "Setting up IPFS for TrueCred..."

# Check if IPFS is already installed
if ! command -v ipfs &> /dev/null; then
    echo "IPFS not found. Please install IPFS from https://dist.ipfs.io/#go-ipfs"
    echo "After installation, run 'ipfs init' to initialize your IPFS node."
    echo "Then run this script again."
    exit 1
fi

echo "IPFS is installed."

# Check if IPFS is initialized
if ! ipfs cat /ipfs/QmQPeNsJPyVWPFDVHb77w8G42Fvo15z4bG2X8D2GhfbSXc/readme &> /dev/null; then
    echo "Initializing IPFS..."
    ipfs init
    if [ $? -ne 0 ]; then
        echo "Failed to initialize IPFS."
        exit 1
    fi
fi

echo "IPFS is initialized."

# Configure CORS for the API
echo "Configuring CORS for IPFS API..."
ipfs config --json API.HTTPHeaders.Access-Control-Allow-Origin '["*"]'
ipfs config --json API.HTTPHeaders.Access-Control-Allow-Methods '["PUT", "POST", "GET"]'

# Start IPFS daemon in the background
echo "Checking if IPFS daemon is running..."
if ! lsof -i :5001 | grep LISTEN &> /dev/null; then
    echo "Starting IPFS daemon..."
    ipfs daemon &
    echo "Waiting for IPFS daemon to start..."
    sleep 5
fi

echo "Testing IPFS connection..."
if ! ipfs id &> /dev/null; then
    echo "Failed to connect to IPFS daemon."
    echo "Please start the IPFS daemon manually with 'ipfs daemon'"
    exit 1
fi

echo "IPFS daemon is running."

echo "IPFS setup completed successfully!"
echo
echo "You can access the IPFS WebUI at: http://localhost:5001/webui"
echo
echo "To stop IPFS daemon later, run: ipfs shutdown"
