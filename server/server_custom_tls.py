from http.server import BaseHTTPRequestHandler, HTTPServer
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.fernet import Fernet
import json

# 1. Generación de llaves RSA (4096-bit recomendado para producción, 2048 para lab)
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_pem = private_key.public_key().public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

cipher_server = None
seen_tokens = set() # Bóveda Anti-Replay

class CustomTLSHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/public_key':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(public_pem)

    def do_POST(self):
        global cipher_server, seen_tokens
        length = int(self.headers['Content-Length'])
        data = self.rfile.read(length)

        if self.path == '/exchange_key':
            session_key = private_key.decrypt(
                data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            cipher_server = Fernet(session_key)
            self.send_response(200)
            self.end_headers()

        elif self.path == '/secure_login':
            # --- MITIGACIÓN REPLAY ATTACK ---
            token_hash = hash(data)
            if token_hash in seen_tokens:
                print("[!!!] SECURITY ALERT: REPLAY OR TAMPERING DETECTED")
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b"Forbidden: Replay Attack")
                return

            try:
                decrypted = cipher_server.decrypt(data).decode()
                seen_tokens.add(token_hash)
                print(f"[*] Secure Decryption Success: {decrypted}")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"Login successful (Secured)")
            except Exception:
                print("[!] SECURITY ALERT: DECRYPTION FAILED")
                self.send_error(400)

if __name__ == '__main__':
    print("[*] Custom TLS Server started on port 8080...")
    HTTPServer(('0.0.0.0', 8080), CustomTLSHandler).serve_forever()
