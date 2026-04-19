# Login-brute-forcing

#### What is Brute Forcing?
A trial-and-error method used to crack passwords, login credentials, or encryption keys by systematically trying every possible combination of characters.
#### Factors Influencing Brute Force Attacks
- Complexity of the password or key
- Computational power available to the attacker
- Security measures in place

#### How Brute Forcing Works
- Start: The attacker initiates the brute force process.
- Generate Possible Combination: The software generates a potential password or key combination.
- Apply Combination: The generated combination is attempted against the target system.
- Check if Successful: The system evaluates the attempted combination.
- Access Granted (if successful): The attacker gains unauthorized access.
- End (if unsuccessful): The process repeats until the correct combination is found or the attacker gives up.

#### Types of Brute Forcing
Attack TypeDescriptionBest Used WhenSimple Brute ForceTries every possible character combination in a set.No prior information about the password.Dictionary AttackUses a pre-compiled list of common passwords.The password is likely weak or common.Hybrid AttackCombines brute force and dictionary attacks.Target uses modified common passwords.Credential StuffingUses leaked credentials from other breaches.Target may reuse passwords.Password SprayingAttempts common passwords across many accounts.Account lockout policies are in place.Rainbow Table AttackUses precomputed tables of password hashes.Cracking a large number of password hashes.Reverse Brute ForceTargets a known password against multiple usernames.Password reuse is suspected.Distributed Brute ForceDistributes attempts across multiple machines.Password is complex, and one machine isn't enough.
#### Default Credentials
DeviceUsernamePasswordLinksys RouteradminadminNetgear RouteradminpasswordTP-Link RouteradminadminCisco RouterciscociscoUbiquiti UniFi APubntubnt
#### Brute-Forcing Tools
Hydra- Fast network login cracker.
- Supports numerous protocols.
- Uses parallel connections for speed.
- Flexible and adaptable.
Examples:Medusa- Fast, massively parallel, modular login brute-forcer.
- Supports a wide array of services.
Examples:
#### Custom Wordlists
Username AnarchyCUPP (Common User Passwords Profiler)
#### Password Policy Filtering
Policy RequirementGrep Regex PatternExplanationMinimum Length (8 characters)grep -E '^.{8,}$' wordlist.txtAt least 8 characters long.At Least One Uppercase Lettergrep -E '[A-Z]' wordlist.txtContains uppercase letters.At Least One Lowercase Lettergrep -E '[a-z]' wordlist.txtContains lowercase letters.At Least One Digitgrep -E '[0-9]' wordlist.txtContains digits.At Least One Special Charactergrep -E '[!@#$%^&*()_+-=[]{};':",.<>/?]' wordlist.txtContains special characters.No Consecutive Repeated Charactersgrep -E '(.)\1' wordlist.txtAvoids repeated characters.Exclude Common Patternsgrep -v -i 'password' wordlist.txtExcludes common patterns.Exclude Dictionary Wordsgrep -v -f dictionary.txt wordlist.txtExcludes dictionary words.Combination of Requirementsgrep -E '^.{8,}$' wordlist.txtgrep -E '[A-Z]'Last updated 10 months ago
```
hydra [-l LOGIN|-L FILE] [-p PASS|-P FILE] [-C FILE] -m MODULE [service://server[:PORT][/OPT]]
```

```
hydra -l admin -P /path/to/password_list.txt ftp://192.168.1.100
hydra -l root -P /path/to/password_list.txt ssh://192.168.1.100
hydra -l admin -P /path/to/password_list.txt 127.0.0.1 http-post-form "/login.php:user=^USER^&pass=^PASS^:F=incorrect"
```

```
medusa [-h host|-H file] [-u username|-U file] [-p password|-P file] [-C file] -M module [OPT]
```

```
medusa -h 192.168.1.100 -u admin -P passwords.txt -M ssh
medusa -h 192.168.1.100 -U users.txt -P passwords.txt -M ftp -t 5
medusa -h 192.168.1.100 -u admin -P passwords.txt -M rdp
```

```
username-anarchy Jane Smith
username-anarchy -i names.txt
username-anarchy -a --country us
username-anarchy -l
username-anarchy -f format1,format2
username-anarchy -@ example.com
username-anarchy --case-insensitive
```

```
cupp -i
cupp -w profiles.txt
cupp -l
```
