# Hashcat Word lists and Rules

## Recommended General Large Word lists
Word ListLinkAllInOne[https://weakpass.com/all-in-one](https://weakpass.com/all-in-one)Rockyou2021[https://weakpass.com/wordlist/1943](https://weakpass.com/wordlist/1943)Weakpass_3a[https://weakpass.com/wordlist/1948](https://weakpass.com/wordlist/1948)Top2Billion-probable-v2[https://weakpass.com/wordlist/1858](https://weakpass.com/wordlist/1858)
## Recommended General Medium Word lists
Word ListLinkhk_hlm_founds[https://weakpass.com/wordlist/1256](https://weakpass.com/wordlist/1256)RP4[https://weakpass.com/wordlist/914](https://weakpass.com/wordlist/914)Ignis[https://weakpass.com/wordlist/1935](https://weakpass.com/wordlist/1935)Top29Million-probable-v2[https://weakpass.com/wordlist/1857](https://weakpass.com/wordlist/1857)SkullSecurityComp[https://weakpass.com/wordlist/671](https://weakpass.com/wordlist/671)
## Specific Word lists
Word ListUse caseLinkKerberoast_pwsSPN cracking[https://gist.github.com/The-Viper-One/a1ee60d8b3607807cc387d794e809f0b](https://gist.github.com/The-Viper-One/a1ee60d8b3607807cc387d794e809f0b)weakpass_3w8-24 characters[https://weakpass.com/wordlist/1950](https://weakpass.com/wordlist/1950)weakpass_3pContains only printable characters[https://weakpass.com/wordlist/1949](https://weakpass.com/wordlist/1949)
## Word list from cracked hashes
Locate pot-filePlace the cracked hash passwords into its own word list.
## Word list from website scraping

## Recommended Rules

#### NSA Rules
Github: [https://github.com/NSAKEY/nsa-rules](https://github.com/NSAKEY/nsa-rules)
#### OneRuleToRuleThemAllStill
An updated and improved variation of the popular OneRuleToRuleThemAll rule set. This updated rule set should provide the same effective crackrate as OneRule with a reduction in total cracking time.Blog Post: [https://in.security/2023/01/10/oneruletorulethemstill-new-and-improved/](https://in.security/2023/01/10/oneruletorulethemstill-new-and-improved/)Github: [https://github.com/stealthsploit/OneRuleToRuleThemStill](https://github.com/stealthsploit/OneRuleToRuleThemStill)
#### Unic0rn28 Hashcat Rules
Github: [https://github.com/Unic0rn28/hashcat-rules](https://github.com/Unic0rn28/hashcat-rules)
## Brute Force Mask

## Reviewing cracked passwords
Hashcat can display credentials in [Username]:[Password] format. Adjust the command below to match the correct method for the hashfile and the --outfile-format value to whichever looks best. For NTLM and Secretsdump the command below should work fine.![](../../~gitbook/image.md)Last updated 10 months ago- [Recommended General Large Word lists](#recommended-general-large-word-lists)
- [Recommended General Medium Word lists](#recommended-general-medium-word-lists)
- [Specific Word lists](#specific-word-lists)
- [Word list from cracked hashes](#word-list-from-cracked-hashes)
- [Word list from website scraping](#word-list-from-website-scraping)
- [Recommended Rules](#recommended-rules)
- [Brute Force Mask](#brute-force-mask)
- [Reviewing cracked passwords](#reviewing-cracked-passwords)

```
find / -name hashcat.potfile 2> /dev/null
```

```
cat [PotFile] | sed 's/[^:]*://' > CrackedHashesWordlist.txt
```

```
cewl [URL] -d 3 -m 5 --with-numbers | tee Wordlists/CewlWordList.txt
```

```
git clone https://github.com/NSAKEY/nsa-rules.git
```

```
git clone https://github.com/stealthsploit/OneRuleToRuleThemStill.git
```

```
git clone https://github.com/Unic0rn28/hashcat-rules.git
```

```
hashcat -m 13100 -O -a3 ?a?a?a?a?a?a?a?a --increment # Bruteforce all upto 8 characters
```

```
hashcat -m 1000 SecretsDump.txt --show --username --outfile-format 2 | sort
```
