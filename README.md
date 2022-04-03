# Metallum Informant Discord
This is the Discord version of the Metallum Informant bot.

A bot that queries the [Encyclopaedia Metallum](www.metal-archives.com)[^1] for metal bands and shows the results to the user.

Also available for Telegram: https://github.com/Pedro-HMV/Metallum-Telegram-Bot.

## Third-party packages
- [Pycord](https://github.com/Pycord-Development/pycord), a Python API wrapper for Discord.
  - At the time of writing this, Discord.py[^2] does not implement all necessary features.
- [python-metallum](https://github.com/Pedro-HMV/python-metallum), a Python API for the Encyclopaedia Metallum.
  - I use my own fork for this, since the original hasn't been maintained in a while and had a broken import[^3].

## Python
Python 3.8 is recommended for guaranteed compatibility.

## Usage
1. The bot must be invited to the Discord server with [this link](https://discord.com/api/oauth2/authorize?client_id=954922759220256850&permissions=309237647360&scope=bot%20applications.commands).
2. Use the `/helper` command to get the [full instructions](#helper-screenshots).
3. Search with `/metallum` and the following parameters:
   - `query:` the text to be searched
   - `exact:` whether results must match the exact query. Must be **True** or **False**.
4. If used within a server, the bot will create a channel thread to dump the results in and avoid polluting the channel.
5. If used in a direct message to the bot, results will be posted in the private conversation.
### Example:
#### command
`/metallum query: black sabbath exact: True`
#### result
```
Black Sabbath

GENRES: Heavy/Doom Metal

LOCATION: Birmingham, West Midlands, England, United Kingdom

FORMED IN: 1969

STATUS: Split-up

THEMES: Doom, Drugs, Life, Death, Religion

ALBUMS: 
(1970) Black Sabbath
(1970) Paranoid
(1971) Master of Reality
(1972) Black Sabbath Vol. 4
(1973) Sabbath Bloody Sabbath
(1975) Sabotage
(1976) Technical Ecstasy
(1978) Never Say Die!
(1980) Heaven and Hell
(1981) Mob Rules
(1983) Born Again
(1986) Seventh Star
(1987) The Eternal Idol
(1989) Headless Cross
(1990) Tyr
(1992) Dehumanizer
(1994) Cross Purposes
(1995) Forbidden
(2013) 13

PAGE: https://metal-archives.com/bands/_/99

1/1
```
## /helper screenshots
![image](https://user-images.githubusercontent.com/85079897/161409476-b59df49d-2f68-459f-bb73-09f8e8488576.png)
![image](https://user-images.githubusercontent.com/85079897/161409499-4f2a756d-7b4d-4f24-8c20-25716902eb0c.png)

[^1]: A website that serves as a database for metal bands.
  https://metal-archives.com.
[^2]: Pycord is a fork of [Discord.py](https://github.com/Rapptz/discord.py), which stopped being maintained for some time and has recently come back.  
  It has some catching up to do, as some of the newer features of Discord are not available there yet.
[^3]: The original python-metallum package can be found [here](https://github.com/lcharlick/python-metallum).  
  The problem is that it hasn't received updates in over a year and has a broken import which raises an error and prevents the whole package from working.  
  So to avoid having to manually fix he issue on every new installation, and especially when deploying, I decided to fork it and use my own fixed version.
