#!/usr/bin/env python3
"""
Render用のスタートアップスクリプト
"""
import os
import sys
import subprocess

def main():
    port = int(os.environ.get('PORT', 5001))
    
    print(f"Starting server on port {port}")
    print("Python path:", sys.executable)
    print("Current directory:", os.getcwd())
    
    # まずgunicornの再インストールを試行
    try:
        print("Installing gunicorn...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'gunicorn==21.2.0'], 
                      check=True)
        print("Gunicorn installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install gunicorn: {e}")
    
    # gunicornが利用可能か確認
    try:
        result = subprocess.run([sys.executable, '-m', 'gunicorn', '--version'], 
                              capture_output=True, check=True, text=True)
        print(f"Gunicorn version: {result.stdout.strip()}")
        
        print("Starting with Gunicorn...")
        # Gunicornで起動
        os.chdir('server')
        os.execvp(sys.executable, [
            sys.executable, '-m', 'gunicorn',
            '--bind', f'0.0.0.0:{port}',
            '--workers', '1',
            '--timeout', '120',
            'app:app'
        ])
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Gunicorn failed: {e}")
        print("Starting with Flask development server...")
        # Flaskサーバーで起動
        os.chdir('server')
        os.environ['FLASK_ENV'] = 'production'
        os.environ['PORT'] = str(port)
        os.execvp(sys.executable, [sys.executable, 'app.py'])

if __name__ == '__main__':
    main()