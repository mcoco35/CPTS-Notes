# Scan-network-with-nmap

### Nmap Scan

```
nmap -sn $ip
```
Disable port scanning (only host discovery)
Use this to check if hosts are up without scanning their ports.
```
nmap -sn -PS $ip
```
SYN Ping
Sends a SYN packet to check if the host responds.
```
nmap -sn -PA $ip
```
TCP ACK Ping
Useful for detecting hosts behind firewalls that block ICMP.
```
nmap -T4 -sS -p- $ip
```
Full SYN scan with aggressive timing
Scans all ports using a SYN scan with a faster timing template (T4).
```
nmap -sC -sV --script={name_of_script} -p- -T4 $ip
```
Run script with version detection
Runs a specific Nmap script while detecting versions of services.
```
nmap -Pn -sA -p-
```
ACK scan for firewall analysis
Determines which ports are filtered or unfiltered by firewalls.
```
nmap -Pn -sS -sV -p- --data-length 200 -D $gatewayip,$gatewayip $ip
```
Decoy scan with packet padding
Uses decoys to obscure the real scanner and adds random data to packets.
### 🔹 Flags for Better Results

#### 🚀 Scan Types
- `-sA` → TCP ACK scan
- `-sS` → TCP SYN scan
- `-sT` → TCP connect scan

#### 🔍 Host & Network Discovery
- `PE` → Ping scan using ICMP ECHO request
- `--disable-arp-ping` → Disable ARP ping

#### 📡 Packet Handling & Output
- `--packet-trace` → Show all packets sent and received
- `--reason` → Display the reason for specific results

#### 🔢 Port Scanning
- `--top-ports=10` → Scan the top 10 most frequent ports
- `-p22` → Scan a specific port (e.g., port 22)
- `-F` → Scan the top 100 ports

#### 🛡️ Spoofing & Stealth Techniques
- `-D RND:5` → Generate 5 random decoy IP addresses
- `-S <IP>` → Set a specific source IP address
- `-e tun0` → Send requests through a specific network interface
- `--source-port 53` → Scan using a specific source port (e.g., `53`)

### 🎯 Optimizing Nmap Scans
Reducing scan time can help evade IDS detection, while increasing speed may appear suspicious.
#### 🕒 Timing & Performance Tweaks
- `--host-timeout 5s` → Set a timeout for each host (e.g., 5 seconds)
- `--scan-delay 5s` → Delay between scan attempts (e.g., 5 seconds)
- `--initial-rtt-timeout 50ms` → Set the initial RTT timeout
- `--max-rtt-timeout 100ms` → Set the max RTT timeout

### 📂 Nmap Output Formats
- `-oN <filename>` → Save as normal text file
- `-oX <filename>` → Save as XML file
- `-oS <filename>` → Save as script (for Metasploit)
- `-oA <basename>` → Save in all formats (`.nmap`, `.xml`, `.gnmap`)
