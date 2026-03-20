#!/usr/bin/env python3
"""WebDoom MVP - Simple HTTP Server with logging"""

import http.server
import socketserver
import os
import json
from datetime import datetime

PORT = 8000
LOG_FILE = "game.log"


class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        super().end_headers()

    def do_POST(self):
        if self.path == "/log":
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode("utf-8"))
                entry = f"[{data['time']}] {data['msg']}\n"
                with open(LOG_FILE, "a") as f:
                    f.write(entry)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"status":"ok"}')
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass


os.chdir(os.path.dirname(os.path.abspath(__file__)))

with open(LOG_FILE, "w") as f:
    f.write(f"[{datetime.now().isoformat()}] Server started\n")

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Server running at http://localhost:{PORT}")
    print(f"Game log: {os.path.abspath(LOG_FILE)}")
    httpd.serve_forever()
