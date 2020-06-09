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

