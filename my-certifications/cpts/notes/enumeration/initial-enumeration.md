# Initial Enumeration

## Scanning

#### NMAP TCP quick

```
sudo nmap -Pn -v -sS -sV -sC -oN tcp-quick.nmap IP
```

#### NMAP TCP Full

```
sudo nmap -Pn -sS --stats-every 3m --max-retries 1 --max-scan-delay 20 --defeat-rst-ratelimit -T4 -p1-65535 -oN tcp-full.nmap -sV IP
```

#### NMAP TCP - Repeat if extra ports found

```
sudo nmap -Pn -v -sS -A -oN tcp-extra.nmap -p PORTS IP
```

#### NMAP UDP quick

```
sudo nmap -Pn -v -sU -sV --top-ports=30 -oN udp-quick.nmap IP
```

#### NMAP UDP 1000

```
sudo nmap -Pn --top-ports 1000 -sU --stats-every 3m --max-retries 1 -T4 -oN udp-1000.nmap IP
```

#### NMAP UDP - Repeat if extra ports found

```
sudo nmap -Pn -sU -A -oN udp-extra.nmap -p PORTS IP
```

#### ICMP Sweep

```
fping -a -g 10.10.10.0/24 2>/dev/null
```

#### ARP Scan (Local Network)

## Enumeration

#### FTP - Port 21

#### SSH - Port 22

#### Telnet - Port 23

#### SMTP - Port 25

#### POP - PORT 110

#### DNS - Port 53

#### Kerberos - Port 88

## Indication that it's a DC

#### Netbios - Port 139

#### RPC - PORT 135

#### LDAP - Ports 389,636,3268,326

#### SNMP - Port 161

#### Oracle - Port 1521

#### MySQL - Port 3306

#### WEB - PORT 80 / 443
NMAP WebChecksDirbGobusterNiktowhatweb / wappalyzerwpscan (WordPress)
#### SMB - Ports
NMAP vuln scriptsCheck for Null loginsConnect to a share with Null sessionImpacket ToolsCheck permissions on a connect shareMount share on local machineList share with credentialsRecursively list all files in shareWith smbclient (recurse downloads all files)Upload / Download specific files
#### NFS - Port 2049

#### TFTPD - UDP 69

## Automation Tools

#### AutoRecon

#### NmapAutomator

## Finding exploits

- [Enumeration](#enumeration)
- [Indication that it's a DC](#indication-that-its-a-dc)
- [Automation Tools](#automation-tools)
- [Finding exploits](#finding-exploits)

```
arp-scan -l
```

```
# Check for FTP version vulns
# Check for Anonymous login
# Check for Read access
# Check for Web root or root directories of any other accessible service
# Check for write access
```

```
# Check for SSH version vulns
# Check for User enumeration if necessary
# Check if host key was seen somewhere else
# Check if it prompts for a password - means password login is allowed for some users
nmap -sV --script=ssh-hostkey -p22 IP
# Bruteforce if necessary with CeWL, Hydra, Patator, Crowbar, MSF (if port gets filtered, there's defense mechanisms - fail2ban)
```

```
# Connect and check for service running
```

```
# Check for SMTP vulns
# Check version with HELO / HELLO
```

```
# Connect using telnet
user
pass
LIST - to list emails
RETR  - To retrieve emails
```

```
# Might indicate a domain controller on Windows
# Check for zone transfer
```

```
kerbrute userenum --dc IP -d DOMAIN users.txt
GetNPUsers.py domain.local/ -usersfile users.txt -no-pass
```

```
nmblookup -A IP
nbtscan IP
# On older hosts, this port serves SMB / SAMBA, scan by adding 'client min protocol = LANMAN1' to GLOBAL setting in /etc/samba/smb.conf or by using --option='client min protocol'=LANMAN1 with smbclient
```

```
sudo nmap -sS -Pn -sV --script=rpcinfo.nse -p135 0
rpcinfo IP
rpcclient -U "" -N [ip]
```

```
sudo nmap -sS -Pn -sV --script=ldap* -p389,636,3268,3269
```

```
snmpwalk -v2c -c public IP
snmp-check IP
onesixtyone -c community.txt IP
sudo nmap -sU -sV -p 161 --script snmp* IP
snmpenum -t IP -c public
```

```
tnscmd10g version -h IP
nmap -sV --script=oracle-tns-version -p1521 IP
odat tnscmd -s IP --ping
odat all -s IP -p 1521
odat sidguesser -s IP
```

```
mysql -h IP -u root -p
nmap -sV --script=mysql* -p3306 IP
hydra -L users.txt -P passwords.txt mysql://IP
mysql -h IP -u root
```

```
sudo nmap -Pn -sC -p80,443
```

```
# Browse the webapp
# Check for usernames, keywords
# Check Web server vulns
# Check for Cgi's shellshock
# Check Certificates for hostname
# Check robots.txt
# Check sitemap.xml
# Check for known software - View source
# Check for default credentials
# Check for input validation - SQLi
# Check for OS Command execution
# Check for LFI / RFI
```

```
dirb IP
dirb with -X extensions based on web technology, .php,.asp,.txt,.jsp
dirb IP -a  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'
```

```
gobuster dir --url IP --wordlist /usr/share/seclists/Discovery/Web-Content/big.txt
gobuster dir --url IP --wordlist /usr/share/seclists/Discovery/Web-Content/big.txt -k -a 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'
```

```
nikto -host IP
```

```
whatweb http://IP
wappalyzer http://IP
```

```
wpscan --url http://IP --enumerate u
```

```
sudo nmap -Pn --script=smb-proto* -p139,445
sudo nmap -Pn --script=smb-os-discovery.nse -p139,445
sudo nmap -Pn --script=smb-enum* -p139,445
sudo nmap -Pn --script=smb-vuln* -p139,445
nmap -p 445 -vv --script=smb-vuln-cve2009-3103.nse,smb-vuln-ms06-025.nse,smb-vuln-ms07-029.nse,smb-vuln-ms08-067.nse,smb-vuln-ms10-054.nse,smb-vuln-ms10-061.nse,smb-vuln-ms17-010.nse
crackmapexec smb IP -u '' -p '' --shares
```

```
nmap --script smb-enum-shares -p 139,445
smbclient -L \\ip\ -N
smbclient -m=SMB2 -L \\Hostname\ -N
```

```
smbclient \\IP\$Admin -N
smbmap -H IP
smbmap -u DoesNotExists -H IP
enum4linux -a IP
```

```
impacket-smbclient -no-pass IP
impacket-lookupsid domain/username:password@ip
```

```
smb: \> showacls # enable acl listing
smb: \> dir # list directories with acls
```

```
sudo mount -t cifs //10.10.10.134/SHARENAME ~/path/to/mount_directory
```

```
smbmap -u USERNAME -p PASSWORD -d DOMAIN.TLD -H
```

```
smbmap -R -H
smbmap -R Replication -H
```

```
smbclient ///Replication
smb: \> recurse ON
smb: \> prompt OFF
smb: \> mget *
```

```
smbmap -H  --download 'Replication\active.htb\
smbmap -H  --upload test.txt SHARENAME/test.txt
```

```
showmount -e IP
mount -t nfs -o vers=3 10.1.1.1:/home/ ~/home
mount -t nfs4 -o proto=tcp,port=2049 127.0.0.1:/srv/Share mountpoint
```

```
tftp client to connect
atftp is a better client
Can be used to read system files, MSSQL password mdf file
```

```
autorecon IP
```

```
./NmapAutomator.sh IP All
```

```
# Search on EDB and searchsploit
# Check each service on CVE details for RCE / LFI / RFI / SQLI issues
# Google search the with the service banner
searchsploit apache 2.4.49
searchsploit -x path/to/exploit
```
