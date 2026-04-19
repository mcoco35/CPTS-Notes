# Protocol Scan

### 🔐 Authentication & Identity

#### LDAP (389, 636)

```
nmap -p 389,636 --script=ldap*
nmap --script "(ldap*) and not brute" -p 389
nmap -p 636 --script=ldap-search,ldap-rootdse
```

#### Kerberos (88)

```
nmap -p 88 --script=krb5-enum-users --script-args="krb5-enum-users.realm='DOMAIN.LOCAL'"
nmap -p 88 --script=krb5-info
```

#### SMB (139, 445)

```
nmap -p 139,445 --script=smb-enum-shares,smb-enum-users,smb-os-discovery,smb-security-mode,smb2-capabilities,smb2-security-mode
nmap --script smb-vuln* -p 445
nmap -p 445 --script=smb-null-session
```

#### RDP (3389)

```
nmap -p 3389 --script=rdp-enum-encryption
nmap -p 3389 --script=rdp-vuln-ms12-020
nmap -p 3389 --script=rdp-ntlm-info
```

#### WinRM (5985, 5986)

### 📱 Network Services

#### FTP (21)

#### SSH (22)

#### Telnet (23)

#### SMTP (25, 465, 587)

#### DNS (53)

#### TFTP (69)

#### POP3 (110, 995)

#### IMAP (143, 993)

#### SNMP (161, 162)

#### R-Services (512, 513, 514)

#### IPMI (623)

#### RSync (873)

#### MSSQL (1433, 1434, 2433)

#### Oracle TNS (1521)

#### NFS (2049)

#### MySQL (3306)

#### PostgreSQL (5432)

#### PostgreSQL Secure (5433)

#### NetBIOS (137, 138)

#### VNC (5900)

#### Redis (6379)

#### Elasticsearch (9200)

#### Memcached (11211)

#### RPCBind (111)

#### SIP (5060)

#### MQTT (1883)

#### RMI (1099)

#### NTP (123)

#### Docker (2375)

#### RabbitMQ (5672)

#### Jenkins (8080)

#### AJP (Apache JServ Protocol - 8009)

#### Kubernetes API Server (6443)

#### CouchDB (5984)

#### VMware (902, 903, 443)

#### TeamViewer (5938)

#### Bacula (9101)

#### X11 (6000)

#### Web Services (80, 443, 8080, 8443)

#### WebDAV (80, 443, 8080)

#### Apache Hadoop (50070)

#### Tomcat (8080, 8443)

#### Zookeeper (2181)

#### Kafka (9092)

#### Varnish (6081)

### 🧰 Other Useful Nmap Scripts

#### Common Nmap Automation & Misc Scripts

#### Brute Force

#### Vulnerability Detection

#### Web Technologies & Frameworks

- [📱 Network Services](#network-services)
- [🧰 Other Useful Nmap Scripts](#other-useful-nmap-scripts)

```
nmap -p 5985,5986 --script=http-windows-enum
nmap -p 5985,5986 --script=winrm-enum-users
```

```
nmap -p 21 --script=ftp-anon,ftp-bounce,ftp-syst,ftp-vsftpd-backdoor,ftp-proftpd-backdoor,ftp-libopie
```

```
nmap -p 22 --script=ssh-hostkey,ssh-auth-methods,sshv1,ssh2-enum-algos,ssh-brute
```

```
nmap -p 23 --script=telnet-encryption,telnet-ntlm-info
```

```
nmap -p 25,465,587 --script=smtp-commands,smtp-enum-users,smtp-open-relay,smtp-ntlm-info
```

```
nmap -p 53 --script=dns-zone-transfer,dns-nsid,dns-service-discovery,dns-recursion,dns-cache-snoop,dns-random-srcport
```

```
nmap -sU -p 69 --script=tftp-enum
```

```
nmap -p 110,995 --script=pop3-capabilities,pop3-brute
```

```
nmap -p 143,993 --script=imap-capabilities,imap-brute
```

```
nmap -sU -p 161,162 --script=snmp-info,snmp-interfaces,snmp-processes,snmp-win32-services,snmp-brute,snmp-sysdescr
```

```
nmap -p 512,513,514 --script=rpcinfo
```

```
nmap -p 623 --script=ipmi-version,ipmi-cipher-zero
```

```
nmap -p 873 --script=rsync-list-modules
```

```
nmap -p 1433,1434,2433 --script=ms-sql-info,ms-sql-empty-password,ms-sql-dump-hashes,ms-sql-brute,ms-sql-config
```

```
nmap -p 1521 --script=oracle-tns-version,oracle-sid-brute
```

```
nmap -p 2049 --script=nfs-ls,nfs-statfs,nfs-showmount,nfs-acls
```

```
nmap -p 3306 --script=mysql-info,mysql-users,mysql-databases,mysql-empty-password,mysql-query,mysql-brute,mysql-dump-hashes
```

```
nmap -p 5432 --script=pgsql-brute,pgsql-databases,pgsql-users
nmap -p 5432 --script=pgsql-enum
```

```
nmap -p 5433 --script=pgsql-info
```

```
nmap -p 137,138 --script=nbstat,smb-os-discovery,smb-enum-shares,smb-enum-users
```

```
nmap -p 5900 --script=vnc-info,vnc-title,vnc-brute
```

```
nmap -p 6379 --script=redis-info,redis-brute
```

```
nmap -p 9200 --script=http-elasticsearch-head,http-title,http-methods,http-headers
```

```
nmap -p 11211 --script=memcached-info
```

```
nmap -sU -sT -p 111 --script=rpcinfo
```

```
nmap -sU -p 5060 --script=sip-methods,sip-enum-users
```

```
nmap -p 1883 --script=mqtt-subscribe,mqtt-connect
```

```
nmap -p 1099 --script=rmi-dumpregistry,rmi-vuln-classloader
```

```
nmap -sU -p 123 --script=ntp-info,ntp-monlist
```

```
nmap -p 2375 --script=docker-version
```

```
nmap -p 5672 --script=rabbitmq-info
```

```
nmap -p 8080 --script=http-jenkins-info,http-headers,http-title
# Common Vulnerabilities: Anonymous Access, Script Console Exposure
```

```
nmap -p 8009 --script=ajp-methods,ajp-headers,ajp-auth
# Common Exploit: Ghostcat CVE-2020-1938 (File Inclusion via AJP)
```

```
nmap -p 6443 --script=http-kubernetes-info,http-headers,http-title
# Check for: Unauthorized access, misconfigured kubelet, exposed dashboard
```

```
nmap -p 5984 --script=http-couchdb-info,http-title,http-headers
# Common Exploits: CVE-2017-12635 & CVE-2017-12636 (Remote Code Execution)
```

```
nmap -p 902,903,443 --script=vmware-version
```

```
nmap -p 5938 --script=teamviewer-info
```

```
nmap -p 9101 --script=bacula-info
```

```
nmap -p 6000 --script=x11-access
```

```
nmap -p 80,443,8080,8443 --script=http-title,http-methods,http-enum,http-headers,http-server-header,http-auth-finder,http-vuln*
```

```
nmap -p 80,443,8080 --script=http-webdav-scan
```

```
nmap -p 50070 --script=http-hadoop-info
```

```
nmap -p 8080,8443 --script=http-tomcat-manager,http-tomcat-users
```

```
nmap -p 2181 --script=zookeeper-info
```

```
nmap -p 9092 --script=kafka-info
```

```
nmap -p 6081 --script=http-headers,http-title
```

```
nmap --script=default,safe
nmap -p- --min-rate=10000 -T4   # Fast full port scan
nmap -sV --version-all -p    # Aggressive service detection
nmap -sC -sV   # Default scripts and version detection
nmap -Pn -n -sS -p- -T4   # Stealth SYN scan without DNS resolution
```

```
nmap -p 21,22,23,25,80,110,143,443,3306,5432,6379,8080 --script brute
```

```
nmap --script vuln
nmap -p 80,443 --script=http-vuln*
nmap -p 445 --script=smb-vuln*
```

```
nmap -p 80,443 --script=http-headers,http-title,http-methods,http-enum,http-php-version,http-aspnet-debug,http-wordpress-enum,http-drupal-enum
```
