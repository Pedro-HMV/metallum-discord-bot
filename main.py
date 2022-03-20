# import re
import logging

# import time
# from typing import NoReturn

import discord
from discord.ext import commands

# import metallum
from decouple import config

logger = logging.getLogger("discord")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(
    filename="discord.log", encoding="utf-8", mode="w"
)
handler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
logger.addHandler(handler)

BOT_TOKEN = config("BOT_TOKEN")
BASE_URL = "https://metal-archives.com/"
BAND_SEP = "\n\n" + "*" * 30 + "\n\n"
DM = ["private", "group"]



class MyClient(discord.Client):
    bot = commands.Bot(command_prefix="/")

    async def on_ready(self):
        print("Logged on as {0}!".format(self.user))

    @bot.command()
    async def band(self, ctx):
        if ctx.channel.type not in DM:
            ctx.channel.


client = MyClient()
client.run("my token goes here")
