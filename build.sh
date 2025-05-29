#!/bin/bash
set -o errexit  # exit on error

echo "=== Python Build Phase ==="
# Install Python dependencies
pip install -r requirements.txt

# Verify Flask installation
echo "=== Verifying Flask Installation ==="
python -c "import flask; print(f'Flask version: {flask.__version__}')"

echo "=== Node.js Build Phase ==="
# Install Node.js dependencies and build React app
cd client
npm install
npm run build
cd ..

echo "=== Build completed successfully! ==="