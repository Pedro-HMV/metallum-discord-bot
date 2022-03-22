import re
import logging

# import time
from typing import NoReturn

import discord

from discord import ChannelType as ct, Option
from discord.utils import escape_markdown

import metallum
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
DM = [ct.private, ct.group]
TEST_GUILDS = [879867345475076147]


class Band:
    def __init__(self, band: metallum.Band, albums=True):
        escaped_band = self.escape_band(band)
        self.name: str = escaped_band["name"]
        # print(self.name)
        self.genres: str = escaped_band["genres"]
        # print(self.genres)
        self.status: str = escaped_band["status"]
        # print(self.status)
        self.location: str = escaped_band["location"]
        # print(self.location)
        self.country: str = escaped_band["country"]
        # print(self.country)
        self.formed_in: str = escaped_band["formed_in"]
        # print(self.formed_in)
        self.themes = escaped_band["themes"]
        if albums:
            full_albums = band.albums.search(type="full-length")
            # print("Full albums: " + str(full_albums))
            string_albums: str = (
                "This band has no full-length albums. Check their page below"
                " for other releases."
                if full_albums == []
                else "\n".join(
                    [f"({str(a.year)}) {a.title}" for a in full_albums]
                )
            )
            self.albums = escape_markdown(string_albums)
        # print(self.albums)
        self.url: str = escape_markdown(BASE_URL + band.url)
        # print(self.url)
        self._info: str = "\n\n".join(
            [
                f"__**{self.name}**__",
                f"_GENRES_: {self.genres}",
                f"_LOCATION_: {self.location}, {self.country}",
                f"_FORMED IN_: {self.formed_in}",
                f"_STATUS_: {self.status}",
                f"_THEMES_: {self.themes}",
                (f"_ALBUMS_: \n{self.albums}" if albums else ""),
                f"_PAGE_: {self.url}",
            ]
        ).replace("\n\n\n\n", "\n\n")

    def __str__(self):
        return self._info

    def escape_band(self, band):
        escape_list = list(
            map(
                lambda x: escape_markdown(x),
                [
                    band.name,
                    ", ".join(band.genres),
                    band.status,
                    band.location,
                    band.country,
                    band.formed_in,
                    ", ".join(band.themes),
                ],
            )
        )
        escaped_band = {
            "name": escape_list[0],
            "genres": escape_list[1],
            "status": escape_list[2],
            "location": escape_list[3],
            "country": escape_list[4],
            "formed_in": escape_list[5],
            "themes": escape_list[6],
        }
        return escaped_band


class Search:
    def __init__(self, query: str, strict: bool, albums: bool):
        self.query = query
        self.strict = strict
        self.albums = albums

    def search(self) -> NoReturn:
        # args = self.query.split()
        pass


bot = discord.Bot()


@bot.event
async def on_ready():
    print("Logged on as {0}!".format(bot.user))
    print(f"Running on {[bot.get_guild(int(id)) for id in TEST_GUILDS]}")


@bot.slash_command(guild_ids=TEST_GUILDS, name="test")
async def testing(ctx: discord.ApplicationContext):
    await ctx.respond("I'm working")


@bot.slash_command(guild_ids=TEST_GUILDS, name="metallum")
async def metallum_search(
    ctx: discord.ApplicationContext,
    query: Option(str, "The search you wanna perform", required=True),
    exact: Option(
        bool,
        description=(
            "Wether the search results should match the exact query."
            " Default is 'yes'."
        ),
        default=True,
    ),
    albums: Option(
        bool,
        "Wether to display the bands' full-length albums in the results.",
        default=True,
    ),
):
    if ctx.interaction.channel.type not in DM:
        try:
            send_to = await ctx.interaction.channel.create_thread(
                name=f"/{ctx.command.qualified_name}",
                type=ct.public_thread,
                auto_archive_duration=30,
            )
            await send_to.send(
                content=(
                    f"Band Search: {ctx.command.qualified_name}\nInitiated by:"
                    f" {ctx.author}\n\nStandby for results!  \U0001F916"
                )
            )
        except (
            discord.Forbidden,
            discord.HTTPException,
            discord.InvalidArgument,
        ) as e:
            print(f"Exception in thread handling: {e}")
            await ctx.respond(content="Something went wrong!")
    else:
        send_to = ctx.interaction.channel
    args = query.split()
    if re.search(r"^\d+$", args[0]):

        try:
            result = metallum.band_for_id(args[0])
            if result.id != args[0]:
                raise ValueError
            band = Band(result)
            await send_to.send(f"Found a band with ID: '{args[0]}'\n\n{band}")

        except ValueError as v:
            print(f"ValueError in search: {v}")
        except (
            discord.Forbidden,
            discord.HTTPException,
            discord.InvalidArgument,
        ) as e:
            print(f"Exception sending band_for_id result: {e}")
            await ctx.respond(content="Something went wrong!")


bot.run(BOT_TOKEN)


# if __name__ == "__main__":
#     client = MyClient()
#     client.run(BOT_TOKEN)
#     client.bot.run(BOT_TOKEN)
