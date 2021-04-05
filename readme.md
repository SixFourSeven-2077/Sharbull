# Sharbull
## What is this bot?
Sharbull is a ready to use bot deployable in minutes, aimed to filter out selfbot accounts by detecting fake accounts and using a captcha system. With its built-in anti-spam filter this bot will also rate limit humans who flood the chat, as Sharbull has a strict policy on spammers and raiders, zero tolerance is not an option, it's mandatory.
Our bot is using a shared database across all servers in order to detect toxic people before they even join your server.

### Main features
- Togglable Captcha for joining members
- Shared reputation system between all servers
- AntiSpam operating according to the user's rep
- Selfbots detection and flagging system

### Usage
If you are a server administrator and would like to use this bot, start now by using the command !!setup
Take a look at other commands by sending !!help commands or !!help security
Question? Concerns? Contest a bad reputation? Get the support server link by sending !!support

## Security
### Automatic flagging
Sharbull automatically detects if an account is fake or likely to be a selfbot by checking their avatar, creation date, user flags and reports. With this data, a trust score is calculated and further actions may be taken :

### Captcha
Captchas are widely used everywhere and have proven to be effective against selfbots, and Sharbull uses 3 levels of protection :
- Level One : Users can join your server without having to complete a challenge.
- Level Two : By looking at the user's flags, Sharbull enables or not the challenge for a suspicious user.
- Level Three : Everyone including clean users will have to complete a challenge.

### AntiSpam
An antispam is also included, which automatically flags the user. Depending on their trust score, they may get muted, kicked or even banned.

### ALERT mode
When you enable alert mode, any spamming member will be banned without a warning. (Sharbull protection services must be enabled first) Alert mode is automatically enabled when a member reaches the spamming ban treshold. If you want the bot to ignore a channel, block the Read Messages permission of this channel to Sharbull.

## Installation
**Requires Python 3.8 or later**

- Make a new virtual environment and activate it
- Install the dependencies : `pip install -r requirements`
- Create a new file named "token" in the main directory in which you will copypaste your bot's token
- Run the bot with `python main.py`


### Discord Bot
This project is currently running as a public bot, you can invite it here : https://discordapp.com/api/oauth2/authorize?client_id=827467138361065503&permissions=8&scope=bot

Question? Concerns? Contest a bad reputation? Go to the support server here : https://discord.gg/RKURYUeX6t

If you want to help the project, consider buying me a coffee here: https://en.tipeee.com/yzu-vpn
