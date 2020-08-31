# writeup

## Mirai

Mirai was a very simple box\(one of the easiest on htb so the writeup wont be too in depth\) which involved reasearching to find creds and using ssh to gain user, then simply enumerating the files on teh machine to find out information about where the root.txt is stored, we find it to get the root flag

> Skills involved in this box
>
> * enumeration
> * using raspberry pi services

## USER

After the initial nmap scan we find out that the ip is running only ports, TCP on 53, SSH on 22 and HTTP on 80. We visit the website but there is nothing there. We Run a dirbuster to see if there is anything else on the web service.

```text
/admin
```

We visit the admin page and find that its running the raspberry pi network. There is a login page but it takes us nowhere. We do some reasearch into raspberry pies and we try to login in via ssh into the box with default raspberry pi credentials.

```text
pi:raspberry
```

From there we simply just ssh into the box and read the user flag.

## ROOT

After this we can simply run:

```text
sudo -i
```

To become root however the root.txt reads this:

```text
I lost my origonal root.txt! I think i may have a backup on my USB stick
```

We navigate to `/media/usbstick` and read a file called Damnit.txt

```text
Damnit! Sorry man I accidentally deleted your files off the USB stick.
Do you know if there is a way to get them back?
-James
```

We then do a little reasearch and find out we can use the `/dev/sdb` file to recover data we simply run `sudo strings /dev/sdb` and we find the root flag in the output. As i said this box was very simple so it wasnt much of a long writeup but nontheless if you enjoyed please fell to drop me some respect on my profile: [https://www.hackthebox.eu/home/users/profile/246314](https://www.hackthebox.eu/home/users/profile/246314) Thanks.

