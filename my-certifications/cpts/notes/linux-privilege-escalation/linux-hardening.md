# Linux-hardening

#### Ubuntu/Debian (unattended-upgrades)

```
sudo apt update
sudo apt upgrade
sudo apt install unattended-upgrades
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

#### Red Hat/CentOS (yum-cron)

```
sudo yum update
sudo yum install yum-cron
sudo systemctl enable yum-cron
sudo systemctl start yum-cron
```

#### Find SUID binaries

```
find / -perm -4000 2>/dev/null
```

#### Find world-writable files/directories

```
find / -perm -o+w -type f 2>/dev/null
find / -perm -o+w -type d 2>/dev/null
```

#### Check cron jobs (root)

```
sudo crontab -l
```

#### Check cron jobs (user)

#### Check sudo privileges

#### Check home directories

#### Check bash history

#### Check for custom libraries (example)

#### Remove unnecessary packages (example)

#### SELinux status

#### List users

#### List groups

#### Check login attempts

#### Password policy (example)

#### Rotate passwords (example)

#### Check /etc/security/opasswd (example)

#### Clone Lynis

#### Run Lynis audit

## Key Hardening Practices:
- Updates and Patching:Importance: Addresses known vulnerabilities.
- Tools: `unattended-upgrades` (Debian/Ubuntu), `yum-cron` (Red Hat).
- Best Practices: Automate updates, prioritize security patches.
- Configuration Management:Importance: Secures system settings.
- Practices:Audit file permissions (SUID, writable).
- Use absolute paths in cron and sudo.
- Secure credentials.
- Clean up user directories and bash history.
- Secure custom libraries.
- Remove unnecessary packages/services.
- Implement SELinux (or AppArmor).
- User Management:Importance: Controls user access.
- Practices:Limit user and admin accounts.
- Log and monitor logon attempts.
- Enforce strong password policies.
- Restrict group memberships.
- Implement the principle of least privilege for sudo.
- Audit:Importance: Regularly assess security posture.
- Practices:Perform security and configuration checks.
- Use security baselines (DISA STIGs).
- Follow compliance frameworks (ISO27001, PCI-DSS, HIPAA).
- Use auditing tools (Lynis).
- Automation:Importance: Improves efficiency and consistency.
- Tools: Puppet, SaltStack, Zabbix, Nagios.
- Practices:Automate configuration checks and remediation.
- Use checksum verification for sensitive binaries.
Lynis Auditing Tool:- Purpose: Performs security audits and provides hardening tips.
- Usage: `./lynis audit system`.
- Features:Warnings and suggestions.
- Hardening index.
- Detailed scan report.
- Importance: Provides a good base line security audit.
Key Enhancements and Considerations:- Security Baselines: Emphasize the importance of using established security benchmarks.
- Principle of Least Privilege: Reinforce the importance of granting only necessary permissions.
- Log Monitoring: Stress the importance of centralized log monitoring for detecting suspicious activity.
- File Integrity Monitoring: Highlight the value of tools that detect unauthorized file changes.
- Automation Security: Be aware of the security risks that come with automation. If automation tools are not secured properly, they can become an attack vector.
- Regular Penetration Testing: Emphasize that audits are not a replacement for regular penetration testing.
- Container Security: More information could be given about how to harden containers.
- Kernel Hardening: More information could be given about kernel hardening best practices.
- Network Hardening: More information could be given about network hardening best practices.
- Security awareness training: Emphasize the importance of security awareness training for all users.

```
crontab -l
```

```
sudo -l
```

```
ls -la ~
```

```
cat ~/.bash_history
```

```
ldd
```

```
sudo apt remove  # or sudo yum remove
```

```
sestatus
```

```
cat /etc/passwd
```

```
cat /etc/group
```

```
sudo cat /var/log/auth.log # or sudo journalctl -u sshd.service
```

```
sudo cat /etc/login.defs
```

```
sudo passwd
```

```
sudo cat /etc/security/opasswd
```

```
git clone https://github.com/CISOfy/lynis.git
cd lynis
```

```
sudo ./lynis audit system
```
