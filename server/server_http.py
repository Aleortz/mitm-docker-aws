from http.server import BaseHTTPRequestHandler, HTTPServer

class SimpleHTTPHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        # Evidencia forense de la vulnerabilidad
        print(f"[!] DATA RECEIVED (CLEARTEXT): {post_data}")
        
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Login successful (Vulnerable)")

if __name__ == '__main__':
    print("[*] Server HTTP started on port 80...")
    HTTPServer(('0.0.0.0', 80), SimpleHTTPHandler).serve_forever()
