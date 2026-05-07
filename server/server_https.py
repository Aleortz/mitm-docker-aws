from http.server import BaseHTTPRequestHandler, HTTPServer
import ssl

class SecureHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers['Content-Length'])
        data = self.rfile.read(length).decode('utf-8')
        print(f"[*] Datos descifrados de forma segura: {data}")
        
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Login HTTPS Exitoso")

print("[*] Servidor HTTPS (Fase II) en puerto 443...")
httpd = HTTPServer(('0.0.0.0', 443), SecureHandler)
# Requiere generar cert.pem y key.pem previamente
httpd.socket = ssl.wrap_socket(httpd.socket, keyfile="key.pem", certfile="cert.pem", server_side=True)
httpd.serve_forever()
