# Upgrading-tty-shell

To check which shell is present in the system
```
cat /etc/shells
```
bash
```
/bin/bash -i
```
sh
```
/bin/sh -i
```
python
```
python -c 'import pty; pty.spwan("/bin/bash")'
```
Perl
```
perl -e 'exec "bin/bash";'
```
Ruby
```
ruby: exe "bin/bash"
```
Perl
```
perl: exec "bin/bash";
```
Lua
```
lua: os.execute('/bin/sh')
```
awk
```
awk 'BEGIN{system("/bin/sh")}'
```
Find
#### using Exec to launch the shell

#### vim
``Vim Escapepermission
## Stabilize Shell
Steps to Stabilize Your Shell- Upgrade to an Interactive Shell
If `python3` is unavailable, try:This gives you job control and allows using built-in commands like `su`.- Set Terminal Type
This ensures compatibility with commands like `clear` and `vim`.- Background the Shell Press:
This suspends the session and returns control to your local shell.- Modify Terminal Settings on Your Local Machine
- `stty raw -echo` disables local echo and allows features like Tab autocompletion, arrow keys, and Ctrl + C.
- `fg` brings the background shell back to the foreground.
- Adjust Terminal Size (Optional)
This ensures proper formatting for commands like `vim` or `less`.
Bonus: Enable a Full TTY Shell If the above steps aren’t enough, try:orThis may further improve terminal capabilities.Last updated 10 months ago
```
find / -name {name of file} -exec /bin/awk 'BEGIN{system("/bin/sh")}'
```

```
find . -exec /bin/sh \; -quit
```

```
vim -c ';!/bin/sh'
```

```
vim
:set shell=/bin/sh
:shell
```

```
ls -la
```

```
python3 -c 'import pty;pty.spawn("/bin/bash")'
```

```
python -c 'import pty;pty.spawn("/bin/bash")'
```

```
export TERM=xterm
```

```
Ctrl + Z
```

```
stty raw -echo; fg
```

```
stty rows 38 columns 116
```

```
script /dev/null -c bash
```

```
reset
```
