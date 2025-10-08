#!/usr/bin/env python3

import json
import time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import os

class ChatServer(BaseHTTPRequestHandler):
    messages = []
    message_lock = threading.Lock()
    
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/messages':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            with self.message_lock:
                response = json.dumps(self.messages[-50:])  # Last 50 messages
            self.wfile.write(response.encode())
            
        elif parsed_path.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "healthy", "timestamp": datetime.now().isoformat()}).encode())
            
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")
    
    def do_POST(self):
        if self.path == '/message':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                message_data = json.loads(post_data.decode())
                
                # Validate required fields
                if all(key in message_data for key in ['user', 'message', 'timestamp']):
                    with self.message_lock:
                        self.messages.append({
                            'user': message_data['user'],
                            'message': message_data['message'],
                            'timestamp': message_data['timestamp'],
                            'server_received': datetime.now().isoformat()
                        })
                    
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "success"}).encode())
                else:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Missing fields"}).encode())
                    
            except json.JSONDecodeError:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())
                
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")
    
    def do_OPTIONS(self):
        # Handle CORS preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        # Custom log format with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{timestamp} - {format % args}")

def run_server(port=8080):
    server_address = ('', port)
    httpd = HTTPServer(server_address, ChatServer)
    print(f"🚀 Chat server running on port {port}")
    print(f"📡 Endpoints:")
    print(f"   GET  /messages  - Get recent messages")
    print(f"   POST /message   - Send a message")
    print(f"   GET  /health    - Health check")
    print(f"⏰ Server started at: {datetime.now().isoformat()}")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server shutting down...")
    finally:
        httpd.server_close()

if __name__ == '__main__':
    run_server()
