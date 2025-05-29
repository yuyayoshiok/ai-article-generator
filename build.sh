#!/bin/bash
set -o errexit  # exit on error

echo "=== Python Build Phase ==="
# Install Python dependencies
pip install -r requirements.txt

# Verify gunicorn installation
echo "=== Verifying Gunicorn Installation ==="
python -m pip show gunicorn
python -c "import gunicorn; print(f'Gunicorn version: {gunicorn.__version__}')"

echo "=== Node.js Build Phase ==="
# Install Node.js dependencies and build React app
cd client
npm install
npm run build
cd ..

echo "=== Build completed successfully! ==="