# Preparation

## 🏆 OSCP Preparation
- 📝 OSCP GuideIntroduction
- Exam Structure
- Exam RequirementsDocumentation
- Exploit Code
- Documentation Rules
- Exam Restrictions
- Exam Connection
- Exam Control Panel
- Report Submission
- Results

## OSCP+ Certification Exam Guide

### 📑 Introduction
The OSCP+ exam simulates a real network inside a private VPN with several vulnerable machines. You have 23 hours and 45 minutes to complete the exam. After that, you'll have another 24 hours to upload your documentation.All exams are proctored. Review the proctoring manual and FAQ here:
https://help.offsec.com/hc/en-us/sections/360008126631-Proctored-Exams
### 🔧 Exam Structure

#### Total Score: 100 points (minimum 70 to pass)
- 3 standalone machines (60 points total)20 points per machine:10 points for initial access
- 10 points for privilege escalation
- 1 Active Directory (AD) set with 3 machines (40 points total)You are given an initial user and password, simulating a breach scenario.
- Scoring:10 points for machine 1
- 10 points for machine 2
- 20 points for machine 3

#### Examples of passing combinations:
- 40 points in AD + 3 `local.txt` flags (70 points)
- 40 points in AD + 2 `local.txt` + 1 `proof.txt` (70 points)
- 20 points in AD + 3 `local.txt` + 2 `proof.txt` (70 points)
- 10 points in AD + 3 fully compromised standalone machines (70 points)
🔄 Evaluation Order:
The order in which you document machines in your report determines their evaluation order.
### 📝 Exam Requirements

#### 📚 Documentation
You must write a professional report detailing the exploitation process for each target.Must include:- All executed commands
- Screenshots showing `local.txt` and `proof.txt`
- Shell output showing the target IP address
- Step-by-step instructions that can be replicated

#### 📋 Exploit Code
If you used an unmodified exploit, only provide the URL. If modified, include:- The modified code
- Original exploit URL
- Shellcode generation commands (if applicable)
- Explanation of the changes

#### 🎨 Documentation Rules
- All `local.txt` and `proof.txt` flags must be shown in screenshots with the IP visible
- Use an interactive shell (`cat` or `type`) to display flags
- In Windows, you must be `SYSTEM`, `Administrator`, or an administrator-level user
- In Linux, you must be `root`

#### 🔒 Exam Restrictions
Not allowed:- Automated exploitation tools (SQLmap, Nessus, Metasploit Pro, etc.)
- Spoofing (ARP, DNS, NBNS, etc.)
- AI or chatbots (ChatGPT, OffSec KAI, etc.)
- Downloading files from the exam environment
Metasploit can only be used on one machine, and not for pivoting.Allowed tools: `Nmap`, `Nikto`, `Burp Free`, `DirBuster`, among others.
### 💻 Exam Connection
- Download the connection pack from the link in your exam email
- Extract the files:
- Connect to the VPN with OpenVPN:
- Enter the username and password provided in the email

### 🛠️ Exam Control Panel
From the panel, you can:- Submit flags
- Revert machines (up to 24 reverts, resettable once)
- View each machine's specific objectives

### 📃 Report Submission
Submission checklist:- PDF format named `OSCP-OS-XXXXX-Exam-Report.pdf`
- Compressed `.7z` archive without password: `OSCP-OS-XXXXX-Exam-Report.7z`
- Maximum size: 200MB
- Upload at: [https://upload.offsec.com](https://upload.offsec.com/)
- Verify MD5 hash after uploading
Commands to generate and verify:
### Results
You will receive your results via email within 10 business days.If additional info is required, you must provide it within 24 hours of the request.
For technical issues during the exam, contact:
Live Chat: https://chat.offsec.comEmail: help@offsec.com
### 🎯 Machines List
https://docs.google.com/spreadsheets/u/1/d/1dwSMIAPIam0PuRBkCiDI88pU3yzrqqHkDtBngUHNCw8/htmlview?pli=1#
https://docs.google.com/spreadsheets/u/0/d/18weuz_Eeynr6sXFQ87Cd5F0slOj9Z6rt/htmlview#Last updated 11 months ago- [🏆 OSCP Preparation](#oscp-preparation)
- [OSCP+ Certification Exam Guide](#oscp-certification-exam-guide)
- [📑 Introduction](#introduction)
- [🔧 Exam Structure](#exam-structure)
- [💻 Exam Connection](#exam-connection)
- [🛠️ Exam Control Panel](#exam-control-panel)
- [📃 Report Submission](#report-submission)
- [Results](#results)
- [🎯 Machines List](#machines-list)

```
tar xvfj exam-connection.tar.bz2
```

```
sudo openvpn OS-XXXXXX-OSCP.ovpn
```

```
sudo 7z a OSCP-OS-XXXXX-Exam-Report.7z OSCP-OS-XXXXX-Exam-Report.pdf
md5sum OSCP-OS-XXXXX-Exam-Report.7z
```
