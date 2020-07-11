## Tube Telegram Rider

[![GitHub license](https://img.shields.io/github/license/namuan/tele-vdo-rider.svg)](https://github.com/namuan/tele-vdo-rider/blob/master/LICENSE) [![Twitter Follow](https://img.shields.io/twitter/follow/deskriders_twt.svg?style=social&label=Follow)](https://twitter.com/deskriders_twt)

Telegram Bot to convert videos to mp3 on your command.
It uses [youtube-dl](https://ytdl-org.github.io/youtube-dl/index.html) so videos from any [supported website](https://ytdl-org.github.io/youtube-dl/supportedsites.html) can be used.

![](docs/tele-tube-mobile.gif)

There is a limitation in the current implementation due to restrictions on Telegram bots as it can only send files of any type of up to 50 MB in size.
See https://core.telegram.org/bots/faq#how-do-i-upload-a-large-file for more information.

### Clone project

```bash
git clone https://github.com/namuan/tele-vdo-rider.git
```

### Running it locally

To run it, you'll need to create a new bot using [@botfather](https://t.me/botfather). 
Once your bot is registered, note down the bot token.
Copy `env.cfg.sample` to `env.cfg` and set the token value for `TELEGRAM_BOT_TOKEN` variable.

```bash
cp env.cfg.sample env.cfg
```

Then we'll setup a local `venv` and install all required dependencies to run the bot.
Make sure you have `python3` installed before running the following command.

```bash
make setup
```

We also need to set up `ffmpeg` which is used to convert Video -> MP3.
On a mac, it is as simple as installing with `brew`

```bash
brew install ffmpeg
```

[Instructions](https://ffmpeg.org/download.html) to set up for other platforms.

Next, run the bot

```bash
make run
```

If previous commands worked then this will start the bot. 
Try adding it to on Telegram send a youtube video.
Here is a good one to try.

[The first 20 hours -- how to learn anything | Josh Kaufman | TEDxCSU](https://www.youtube.com/watch?v=5MgBikgcWnY)

### Self-Hosting

Although running locally is fine for testing, you may want to run it in background to avoid any disruptions.
Here is a quick guide to setting it up VPS or RaspberryPi (Once you get past installing ffmpeg on it).

**Step 1: Setup VPS or use existing server(Raspberry Pi)**
Here we will look at setting it up on [Vultr](https://www.vultr.com/?ref=7306977) (Affiliate Link) or [DigitalOcean](https://m.do.co/c/da51ec30754c) (Affiliate Link).

![](docs/20200710215605063_698259815.png)

> Remember to Clean up: Make sure you delete this server if not used to avoid incurring cost. 

**Step 2: Checking connectivity**

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

**Step 3: Installing dependencies**

We do need to install a couple of dependencies if they are missing from the server.

```
# ssh into server
$ make server
```

**Step 4: Starting up Bot**

Again, we'll use the make command to start the bot in a screen session.

```bash
make start
```

The bot is running once the command finishes. Try sending another Youtube video to see it in action.

**Step 5: Testing if Bot is running**

If there is anything wrong, you can see what is going on the server.

```bash
# ssh
make ssh

# check screen sessions
screen -ls

# attach to existing screen session
screen -x tele-vdo-rider

# detach from a session
Ctrl + A then D
```

Once you are detached from a session, you can exit from the server leaving the bot running.

**Step 6: [Optional] Updating Bot**

Run the following command from your local machine, and it should update the bot and restart the session automatically.

```bash
make start
```
