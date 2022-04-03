import re
import logging

from asyncio import shield

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
PRE_M = ":heavy_minus_sign:\n\n"
SUF_M = "\n\n:heavy_minus_sign:"


HELP_STANDARD = (
    ":regional_indicator_h: :regional_indicator_a: :regional_indicator_i:"
    " :regional_indicator_l: :bangbang: \t:metal: :robot:\n\nUse the command"
    " `/metallum` to perform a search.\n\nParameters:\n__query:__ the text"
    " used in the search.\n\n__exact:__ whether to search for the exact query"
    " or not (more info below). Must be either **True** or"
    " **False**.\n\n__**STANDARD SEARCH**__:\n\nWhen the __exact__ parameter"
    " is **True**, searching for 'black sabbath' will only find bands named"
    " EXACTLY 'Black Sabbath' (case-insensitive, though).\n\nHowever, when"
    " __exact__ is **False**, the same search will find all bands with BOTH"
    " 'black' and 'sabbath' in their names, regardless of any other words and"
    " in whatever order, like the band 'Sabbath Black Heretic'.\n\nIf the"
    " first part of the __query__ is a number, you may find a band registered"
    " under that __ID__ on the website, if there's any (the ID is the number"
    " at the end of the band's URL). The search will then continue to look for"
    " bands matching the entire query (including that number) in their"
    " names.\n\nFor example: `/metallum query: 7 sins exact: True` would give"
    " you the band with ID '7', which is 'Entombed' and then search for bands"
    " called '7 Sins' (exact match, in this case).\nNote that searching for"
    " '13' will give you both the band with ID '13' and the band called"
    " '13'.\n\n"
)

HELP_ADVANCED = (
    "__**ADVANCED SEARCH**__:\n\nThe options below only work when"
    " __exact__ is set to **False**...\n\nIn addition to those results"
    " describe above, if you also want bands that contain EITHER 'black' OR"
    " 'sabbath' (not necessarily both), you can search for `black || sabbath`"
    " (or `sabbath || black`, for that matter).\n\nNote, however, that those"
    " words must appear in their entirety in the band's name. Meaning a 'hell'"
    " search won't find 'helloween', for instance.\nBut don't worry, you can"
    " use __asterisks__ as wildcards: `hell*`, `*hell` and `*hell*` are all"
    " valid queries. The asterisk means that the word can be extended by any"
    " amount of characters **in that direction**.\n\nFinally, another thing"
    " you can do is exclude words from the results: `black -sabbath` will find"
    " bands with the word 'black', but exclude those with the word"
    " 'sabbath'.\n\nYou can also combine all of the above, of course!"
)


class Band:
    def __init__(self, band: metallum.Band, albums: bool = True):
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
        self.themes: str = escaped_band["themes"]
        if albums:
            full_albums = band.albums.search(type="full-length")
            # print("Full albums: " + str(full_albums))
            self.albums: str = (
                "This band has no full-length albums. Check their page below"
                " for other releases."
                if full_albums == []
                else "\n".join(
                    [
                        f"**({str(a.year)})** {escape_markdown(a.title)}"
                        for a in full_albums
                    ]
                )
            )
        # print(self.albums)
        self.url: str = escape_markdown(BASE_URL + band.url)
        # print(self.url)
        self._info: str = "\n\n".join(
            [
                f"__**{self.name}**__",
                f"__*GENRES*__: {self.genres}",
                f"__*LOCATION*__: {self.location}, {self.country}",
                f"__*FORMED IN*__: {self.formed_in}",
                f"__*STATUS*__: {self.status}",
                f"__*THEMES*__: {self.themes}",
                (f"__*ALBUMS*__: \n{self.albums}" if albums else ""),
                f"__*PAGE*__: {self.url}",
            ]
        ).replace("\n\n\n\n", "\n\n")

    def __str__(self):
        return self._info

    def escape_band(self, band: metallum.Band):
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
    def __init__(
        self,
        query: str,
        send_to: discord.ApplicationContext.channel,
        strict: bool = True,
        albums: bool = True,
        page_start: int = 0,
    ):
        self.query = query
        self.send_to = send_to
        self.strict = strict
        self.albums = albums
        self.page_start = page_start

    async def search(self) -> NoReturn:
        await shield(
            self.send_to.send(
                PRE_M
                + (
                    "Performing strict search!"
                    if self.strict
                    else (
                        "Performing advanced search:"
                        f" {escape_markdown(self.query)}"
                    )
                )
            )
        )
        try:
            band_list = metallum.band_search(
                self.query, strict=self.strict, page_start=self.page_start
            )
            if not band_list:
                raise IndexError
            await shield(
                self.send_to.send(
                    f"{PRE_M}Found {band_list.result_count} band(s)!\n\nHere"
                    " we go!"
                )
            )
            for i, band_result in enumerate(band_list):
                band = Band(band_result.get(), self.albums)
                band_pos = f"{i+1+self.page_start}/{band_list.result_count}"
                print(band)
                bot_response = "\n\n".join(
                    [
                        str(band),
                        band_pos,
                    ]
                )
                await shield(self.send_to.send(f"{PRE_M}{bot_response}"))
                if (i + 1) % 200 == 0:
                    new_search = Search(
                        self.query,
                        self.send_to,
                        self.strict,
                        self.albums,
                        self.page_start + 200,
                    )
                    await shield(new_search.search())
                    return

        except IndexError:
            await shield(
                self.send_to.send(
                    f"{PRE_M}No band was found. Remember, I only know METAL"
                    " bands! \U0001F918\U0001F916"
                )
            )


bot = discord.Bot()


@bot.event
async def on_ready():
    print("Logged on as {0}!".format(bot.user))


@bot.slash_command(
    name="helper",
    description="Learn how to search!",
)
async def helper(ctx: discord.ApplicationContext):
    await shield(ctx.respond(HELP_STANDARD))
    await shield(ctx.respond(HELP_ADVANCED))


@bot.slash_command(
    name="metallum",
    description="Use /helpers for instructions!",
)
async def metallum_search(
    ctx: discord.ApplicationContext,
    query: Option(str, "The search you wanna perform", required=True),
    exact: Option(
        bool,
        description=(
            "Whether the search results should match the exact query."
            " True or False."
        ),
    ),
):
    try:
        print(
            "\n\n"
            + "*" * 10
            + f"\n\nSearch by: {ctx.author}\nQuery: {query}\nExact:"
            f" {exact}\nData: {ctx.interaction.data}\n\n"
            + "*" * 10
            + "\n\n"
        )
    except Exception as e:
        print(f"Debug exception: {e}")
    try:
        send_to = await shield(
            ctx.interaction.channel.create_thread(
                name=f"Metallum search, query='{query}', exact={exact}",
                type=ct.public_thread,
                auto_archive_duration=60,
            )
        )
        await shield(
            ctx.respond(
                "Search initiated, please refer to the thread:"
                f" {send_to.mention}"
            )
        )
        await shield(
            send_to.send(
                f"{ctx.author} used: `/metallum query: '{query}'"
                f" exact: '{exact}'` \n\nStandby for results!  \U0001F916"
            )
        )
    except (
        discord.Forbidden,
        discord.HTTPException,
        discord.InvalidArgument,
    ) as e:
        print(f"Exception in thread handling: {e}")
        await shield(ctx.respond("Something went wrong!"))
        send_to = ctx.interaction.channel
    except AttributeError as ae:
        print(f"Thread attribute error: {ae}")
        send_to = ctx.interaction.channel
        await shield(ctx.respond("Search initialized!"))

    args = query.split()
    if re.search(r"^\d+$", args[0]):
        try:
            result = metallum.band_for_id(args[0])
            if result.id != args[0]:
                raise ValueError
            band = Band(result)
            print(band)
            await send_to.send(
                f"{PRE_M}Found a band with ID: '{args[0]}'\n\n{band}"
            )
        except ValueError as v:
            print(f"ValueError in search: {v}")
        except (
            discord.Forbidden,
            discord.HTTPException,
            discord.InvalidArgument,
        ) as e:
            print(f"Exception sending band_for_id result: {e}")
    name_search = Search(query, send_to, exact)
    await shield(name_search.search())
    try:
        await shield(
            ctx.interaction.edit_original_message(
                content=(
                    "Search **completed**, please refer to the thread:"
                    f" {send_to.mention}"
                )
            )
        )
    except Exception as e:
        print(f"Failed to edit response: {e}")


bot.run(BOT_TOKEN)
