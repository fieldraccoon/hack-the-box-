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
Taking a look at `/admin`
