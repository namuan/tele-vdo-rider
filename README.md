## Tube Telegram Rider

Telegram Bot to convert videos to mp3 on your command.
It uses [youtube-dl](https://ytdl-org.github.io/youtube-dl/index.html) so videos from any [supported website](https://ytdl-org.github.io/youtube-dl/supportedsites.html) can be used.

There is a limitation in the current implementation due to restrictions on Telegram bots as it can only send files of any type of up to 50 MB in size.
See https://core.telegram.org/bots/faq#how-do-i-upload-a-large-file for more information.

### Self-Hosting

**Step 1: Setup VPS or use existing server(Raspberry Pi)**

It is pretty simple to set up on a VPS or RaspberryPi (Once you get past installing ffmpeg on it).
Here we will look at setting it up on [Vultr](https://www.vultr.com/?ref=7306977) (Affiliate Link) or [DigitalOcean](https://m.do.co/c/da51ec30754c) (Affiliate Link).

![](docs/20200710215605063_698259815.png)

**Step 2: Clone this project**

```bash
git clone https://github.com/namuan/tele-vdo-rider
```

**Step 3: Checking connectivity**

Once you have the server running, make sure you can connect to it.
It is better to set up a dedicated host entry as below.
Some commands in the `Makefile` assumes that the host entry matches the project directory.

> SideNote: I used to use [poet](https://github.com/awendt/poet) to split ssh files but from [OpenSSH 7.3](http://man.openbsd.org/ssh_config#Include) it supports the `Include` directive to allow multiple ssh config files. 

```
Host tele-vdo-rider
	User root
	HostName xx.xx.xx.xx
	Port 22
	IdentitiesOnly yes
	IdentityFile ~/.ssh/dfiles
```

So if you have the following entry under ~/.ssh. Running the following command will try to connect and ssh to the server.

```bash
$ make ssh
```

Make sure this works before continuing. You may have to enter the Password from the VPS provider (Vultr/DigitalOcean).

**Step 4: Installing dependencies**

We do need to install a couple of dependencies if they are missing from the server.

```
# ssh into server
$ make server
```

This should be enough to run the bot.

**Step 5: Starting up Bot**

**Step 6: Testing if Bot is running**




