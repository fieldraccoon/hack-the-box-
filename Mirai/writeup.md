# Mirai

Mirai was a very simple box(one of the easiest on htb so the writeup wont be too in depth) which involved reasearching to find creds and using ssh to gain user, then simply enumerating the files on teh machine to find out information about where the root.txt is stored, we find it to get the root flag

>Skills involved in this box
- enumeration
- using raspberry pi services

After the initial nmap scan we find out that the ip is running only ports, TCP on 53, SSH on 22 and HTTP on 80.
We visit the website but there is nothing there. We Run a dirbuster to see if there is anything else on the web service.
```
/admin
```
We visit the admin page and find that its running the raspberry pi network. There is a login page but it takes us nowhere.
We do some reasearch into raspberry pies and we try to login in via ssh into the box with default raspberry pi credentials.
```
pi:raspberry
```
From there we simply just ssh into the box and read the user flag
