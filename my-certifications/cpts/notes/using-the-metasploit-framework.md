# Using-the-metasploit-framework

#### MSFconsole Commands
- Show all exploits:

```
show exploits
```
- Show all payloads:

```
show payloads
```
- Show all auxiliary modules:

```
show auxiliary
```
- Search for a module:

```
search
```
- Load information about a specific module:

```
info
```
- Load an exploit or module:

```
use
```
- Load an exploit by index number:

```
use
```
- Set Local Host IP (LHOST):

```
set LHOST
```
- Set Remote Host IP (RHOST):
- Set a specific option value:
- Set a global option value:
- Display available options for a module:
- Display supported platforms for the exploit:
- Specify the target index:
- Set the desired payload:
- Display advanced options for a module:
- Automatically migrate to another process after exploitation:
- Check if a target is vulnerable:
- Execute the module or exploit:
- Run the exploit in the background:
- Run without interacting with the session:
- Specify a payload encoder:
- Display help for the exploit command:
- List available sessions:
- List sessions with verbose details:
- Run a script on all live sessions:
- Kill all active sessions:
- Run a command across all sessions:
- Upgrade a shell to a Meterpreter session:
- Create a new database:
- Connect to an existing database:
- Use Nmap and store results in the database:
- Delete the current database:

#### Meterpreter Commands
- Display Meterpreter help:
- Run a Meterpreter script:
- Show target system information:
- List files and directories:
- Load the privilege extension:
- List running processes:
- Migrate to a specific process by ID:
- Load incognito functions:
- List user tokens:
- List group tokens:
- Impersonate a token:
- Steal a process token:
- Stop token impersonation:
- Attempt privilege escalation to SYSTEM:
- Drop into an interactive shell:
- Run a command interactively:
- Revert to the original user:
- Interact with the registry:
- Switch to another desktop:
- Capture a screenshot:
- Upload a file to the target:
- Download a file from the target:
- Start keylogging:
- Dump captured keystrokes:
- Stop keylogging:
- Get available privileges:
- Take control of input devices:
- Background the current session:
- Dump password hashes:
- Load the sniffer module:
- List network interfaces:
- Start sniffing on an interface:
- Dump captured packets:
- Stop packet sniffing:
- Clear event logs:
- Modify file timestamps:
- Reboot the target machine:

```
set RHOST
```

```
set
```

```
setg
```

```
show options
```

```
show targets
```

```
set target
```

```
set payload
```

```
show advanced
```

```
set autorunscript migrate -f
```

```
check
```

```
exploit
```

```
exploit -j
```

```
exploit -z
```

```
exploit -e
```

```
exploit -h
```

```
sessions -l
```

```
sessions -v
```

```
sessions -s
```

```
sessions -K
```

```
sessions -c
```

```
sessions -u
```

```
db_create
```

```
db_connect
```

```
db_nmap
```

```
db_destroy
```

```
help
```

```
run
```

```
sysinfo
```

```
ls
```

```
use priv
```

```
ps
```

```
migrate
```

```
use incognito
```

```
list_tokens -u
```

```
list_tokens -g
```

```
impersonate_token
```

```
steal_token
```

```
drop_token
```

```
getsystem
```

```
shell
```

```
execute -f  -i
```

```
rev2self
```

```
reg
```

```
setdesktop
```

```
screenshot
```

```
upload
```

```
download
```

```
keyscan_start
```

```
keyscan_dump
```

```
keyscan_stop
```

```
getprivs
```

```
uictl enable
```

```
background
```

```
hashdump
```

```
use sniffer
```

```
sniffer_interfaces
```

```
sniffer_start
```

```
sniffer_dump
```

```
sniffer_stop
```

```
clearev
```

```
timestomp
```

```
reboot
```
