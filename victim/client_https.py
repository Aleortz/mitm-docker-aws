import requests

url = "https://10.0.0.10/login"
payload = "username=admin&password=university_project_2026"

# Desactivamos los warnings para el certificado autofirmado del laboratorio
requests.packages.urllib3.disable_warnings()

print("[*] Enviando datos por túnel TLS...")
response = requests.post(url, data=payload, verify=False)
print(f"[-] Respuesta: {response.status_code} - {response.text}")
