# Nmap Full Flag

#### Nmap Cheat Sheet
Host Discovery
```
-sL    nmap 192.168.1.1-3 -sL                       # No Scan. List targets only
-sn    nmap 192.168.1.1/24 -sn                      # Disable port scanning
-Pn    nmap 192.168.1.1-5 -Pn               # Disable host discovery. Port scan only
-PS    nmap 192.168.1.1-5 -PS22-25,80       # TCP SYN discovery on ports 22-25,80
-PA    nmap 192.168.1.1-5 -PA22-25,80       # TCP ACK discovery on ports 22-25,80
-PU    nmap 192.168.1.1-5 -PU53                     # UDP discovery on port 53
-PR    nmap 192.168.1.0/24 -PR                      # ARP discovery on local network
-n     nmap 192.168.1.1 -n                          # Never do DNS resolution
```
Target Specification
```
nmap 192.168.1.1                                     # Scan a single IP
nmap 192.168.1.1 192.168.2.1                         # Scan specific IPs
nmap 192.168.1.1-254                                 # Scan a range
nmap scanme.nmap.org                                 # Scan a domain
nmap 192.168.1.0/24                                  # Scan using CIDR notation
-iL     nmap -iL targets.txt                         # Scan targets from a file
-iR     nmap -iR 100                                 # Scan 100 random hosts
--exclude  nmap --exclude 192.168.1.1                # Exclude listed hosts
```
Scan TechniquesPort SpecificationTiming and PerformanceService and Version DetectionOS DetectionFirewall / IDS Evasion and SpoofingNSE ScriptsExample NSE ScriptsWeb App Specific NSE ScriptsAdvanced NSE Script UsageVulnerability Scanning ScriptsOutput OptionsScan Output Analysis & TipsVisit: [StationX Nmap Cheat Sheet](https://www.stationx.net/nmap-cheat-sheet/) for more.Last updated 10 months ago
```
-sS     nmap 192.168.1.1 -sS                         # TCP SYN port scan (Default)
-sT     nmap 192.168.1.1 -sT                         # TCP connect port scan
-sU     nmap 192.168.1.1 -sU                         # UDP port scan
-sA     nmap 192.168.1.1 -sA                         # TCP ACK port scan
-sW     nmap 192.168.1.1 -sW                         # TCP Window port scan
-sM     nmap 192.168.1.1 -sM                         # TCP Maimon port scan
```

```
-p      nmap 192.168.1.1 -p 21                       # Port scan for port 21
-p      nmap 192.168.1.1 -p 21-100                   # Port range
-p      nmap 192.168.1.1 -p U:53,T:21-25,80          # TCP and UDP ports
-p-     nmap 192.168.1.1 -p-                         # All 65535 ports
-p      nmap 192.168.1.1 -p http,https               # Port scan using service names
-F      nmap 192.168.1.1 -F                          # Fast port scan (100 ports)
--top-ports nmap 192.168.1.1 --top-ports 2000        # Top 2000 ports
```

```
nmap -T0             # T0 = Paranoid (very slow, for IDS evasion)
nmap -T1             # T1 = Sneaky (slow)
nmap -T2             # T2 = Polite (slower, uses less bandwidth)
nmap -T3             # T3 = Normal (default)
nmap -T4             # T4 = Aggressive (faster, good for LANs)
nmap -T5             # T5 = Insane (very fast, risk of inaccuracy)
--host-timeout         # Maximum time allowed for one host scan (e.g., 30m, 1h)
--min-rtt-timeout      # Minimum probe timeout based on round-trip time
--max-rtt-timeout      # Maximum probe timeout based on round-trip time
--min-hostgroup        # Minimum number of hosts to scan in parallel
--max-hostgroup        # Maximum number of hosts to scan in parallel
--min-parallelism       # Minimum number of probes to send in parallel
--max-parallelism       # Maximum number of probes to send in parallel
--scan-delay           # Delay between probes (e.g., 1s, 500ms)
--max-scan-delay       # Max allowed delay between probes
--max-retries         # Max number of probe retransmissions per port
--min-rate           # Minimum number of packets per second
--max-rate           # Maximum number of packets per second
```

```
-sV                                # Detect service versions
--version-intensity           # Intensity of detection
--version-light                    # Light and fast scan
--version-all                      # Aggressive detection
-A                                 # OS detection, version detection, scripts, traceroute
```

```
-O                                 # Enable OS detection
--osscan-limit                     # Skip OS scan if conditions not met
--osscan-guess                     # Guess aggressively
--max-os-tries                  # Set max OS detection tries
```

```
-f                                # Fragment packets
--mtu                        # Set MTU
-D                                # Decoy scan
-S                                # Spoof source IP
-g                                # Set source port
--proxies                         # Relay via proxies
--data-length              # Append data
```

```
-sC                                # Default scripts
--script default                   # Same as -sC
--script=banner                    # Run specific script
--script=http*                     # Wildcard match
--script=http,banner               # Multiple scripts
--script "not intrusive"           # Exclude intrusive scripts
--script-args                      # Script arguments
```

```
nmap -Pn --script=http-sitemap-generator scanme.nmap.org
nmap -n -Pn -p 80 --open -sV -vvv --script banner,http-title -iR 1000
nmap -Pn --script=dns-brute domain.com
nmap -n -Pn -vv -O -sV --script smb-* 192.168.1.1
nmap --script whois* domain.com
nmap -p80 --script http-unsafe-output-escaping scanme.nmap.org
nmap -p80 --script http-sql-injection scanme.nmap.org
```

```
nmap -p80 --script http-methods --script-args http-methods.test-all http://target
nmap -p80 --script http-headers http://target
nmap -p80 --script http-auth,http-auth-finder,http-auth-guess http://target
nmap -p80 --script http-enum http://target
nmap -p80 --script http-config-backup http://target
nmap -p80 --script http-userdir-enum http://target
nmap -p80 --script http-vhosts,http-iis-short-name-brute http://target
nmap -p80 --script http-dombased-xss,http-xssed,http-stored-xss,http-csrf 192.168.1.1
```

```
nmap --script-args "userdb=users.txt,passdb=passlist.txt" -p21 ftp.target.com --script ftp-brute
nmap -p445 --script smb-enum-users,smb-enum-shares --script-args smbuser=admin,smbpass=password 192.168.1.100
nmap -p80 --script http-form-brute --script-args http-form-brute.hostname=target.com,http-form-brute.path=/login,http-form-brute.uservar=username,http-form-brute.passvar=password,http-form-brute.failmsg="invalid login" 192.168.1.1
```

```
nmap --script vuln 192.168.1.1
nmap -sV --script vulners 192.168.1.1
nmap -p80 --script http-vuln-cve2015-1635 192.168.1.1
nmap -p80 --script http-vuln-cve2017-5638 192.168.1.1
nmap -p80 --script http-vuln-cve2017-1001000 192.168.1.1
```

```
-oN                            # Normal output
-oX                            # XML output
-oG                            # Grepable output
-oA                          # All formats
--append-output                     # Append to file
-oG -                                # Output to screen (also -oN -, -oX -)
```

```
- Look for open ports with services you can enumerate (e.g., HTTP, SMB, FTP).
- Closed ports still respond; filtered ports are likely firewalled.
- Combine `-sV` and `-A` to gather banners and OS info.
- Use `--reason` to understand why a port is marked as open/closed.
- Save all scans using `-oA` for later grep/parse.
- Use `grep open` or tools like `grepable`, `xsltproc`, or `nmaptocsv` to filter output.
```
