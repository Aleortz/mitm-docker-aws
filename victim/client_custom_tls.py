import requests
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.fernet import Fernet

base_url = "http://10.0.0.10:8080"
payload = b"username=admin&password=university_project_2026"

print("[*] 1. Solicitando Llave Pública RSA...")
res_pub = requests.get(f"{base_url}/public_key")
public_key = serialization.load_pem_public_key(res_pub.content)

print("[*] 2. Generando Llave de Sesión (Fernet)...")
session_key = Fernet.generate_key()
cipher_client = Fernet(session_key)

print("[*] 3. Intercambio de Llaves (RSA)...")
encrypted_key = public_key.encrypt(
    session_key,
    padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
)
requests.post(f"{base_url}/exchange_key", data=encrypted_key)

print("[*] 4. Enviando credenciales cifradas...")
encrypted_payload = cipher_client.encrypt(payload)
res_login = requests.post(f"{base_url}/secure_login", data=encrypted_payload)
print(f"[-] Respuesta inicial: {res_login.status_code}")

print("\n[*] 5. Simulando Ataque Replay (Reenviando el mismo paquete interceptado)...")
res_replay = requests.post(f"{base_url}/secure_login", data=encrypted_payload)
print(f"[-] Respuesta al Replay: {res_replay.status_code} (Esperado: 403)")
