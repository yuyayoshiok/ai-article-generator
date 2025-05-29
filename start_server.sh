#!/bin/bash
set -e

echo "=== Render Startup Script ==="
echo "Current directory: $(pwd)"
echo "Contents: $(ls -la)"

if [ -d "server" ]; then
    echo "Server directory found"
    echo "Server contents: $(ls -la server/)"
    
    if [ -f "server/app.py" ]; then
        echo "app.py found, starting server..."
        cd server
        echo "Changed to server directory: $(pwd)"
        python app.py
    else
        echo "ERROR: server/app.py not found"
        exit 1
    fi
else
    echo "ERROR: server directory not found"
    echo "Available directories:"
    ls -la
    exit 1
fi