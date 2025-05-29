#!/usr/bin/env python3
"""
Render用のスタートアップスクリプト
gunicornがない場合はFlask開発サーバーで起動
"""
import os
import sys
import subprocess

def main():
    port = int(os.environ.get('PORT', 5001))
    
    # gunicornが利用可能か確認
    try:
        subprocess.run(['python', '-m', 'gunicorn', '--version'], 
                      capture_output=True, check=True)
        
        print("Starting with Gunicorn...")
        # Gunicornで起動
        os.chdir('server')
        os.execvp('python', [
            'python', '-m', 'gunicorn',
            '--bind', f'0.0.0.0:{port}',
            'app:app'
        ])
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Gunicorn not found, starting with Flask development server...")
        # Flaskサーバーで起動
        os.chdir('server')
        os.environ['FLASK_ENV'] = 'production'
        os.execvp('python', ['python', 'app.py'])

if __name__ == '__main__':
    main()