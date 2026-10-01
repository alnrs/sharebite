#!/usr/bin/env python3
"""Run the frontend preview from the extracted project root and open a browser."""
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
import os,sys,webbrowser,threading
ROOT=Path(__file__).resolve().parents[1]
os.chdir(ROOT)
try:
    server=ThreadingHTTPServer(('127.0.0.1',5500),SimpleHTTPRequestHandler)
except OSError:
    server=ThreadingHTTPServer(('127.0.0.1',0),SimpleHTTPRequestHandler)
# Use localhost rather than 127.0.0.1: AWS API and S3 CORS require an exact origin match.
url=f'http://localhost:{server.server_port}/index.html'
print('\n ShareBite preview is starting: '+url)
print(' Keep this window OPEN while using the site. Close with Ctrl+C.\n')
threading.Timer(1.0,lambda:webbrowser.open(url)).start()
try:server.serve_forever()
except KeyboardInterrupt: print('\nStopping ShareBite preview.')
finally:server.server_close()
