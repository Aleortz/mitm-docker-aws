import requests
import time

url = "http://10.0.0.10/login"
payload = "username=admin&password=university_project_2026"

print("[*] Enviando datos en texto plano...")
response = requests.post(url, data=payload)
print(f"[-] Respuesta: {response.status_code} - {response.text}")
