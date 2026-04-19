# Web-attacks-to-the-point

I. HTTP Verb TamperingHTTP Methods:- HEAD
- PUT
- DELETE
- OPTIONS
- PATCH
Curl Command for HTTP Methods:
```
curl -X OPTIONS
```
II. IDOR (Insecure Direct Object References)Identification Techniques:- Inspect URL parameters and APIs.
- Analyze AJAX calls.
- Check for reference hashing/encoding.
- Compare user roles for access control discrepancies.
Common Commands:
```
echo -n 'string' | md5sum
echo -n 'string' | base64
```
III. XXE (XML External Entity Injection)Common XXE Payloads:IV. Additional Tools- Burp Suite for testing HTTP methods and identifying IDORs.
- Amass for passive DNS enumeration.
- Shodan for discovering exposed services.
- TheHarvester for gathering information from public sources.
- Censys for advanced reconnaissance.
Last updated 10 months ago
```

">
">
```
