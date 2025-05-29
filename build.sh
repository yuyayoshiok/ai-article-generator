#!/bin/bash
set -o errexit  # exit on error

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies and build React app
cd client
npm install
npm run build
cd ..

echo "Build completed successfully!"