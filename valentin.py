import io
import logging
import os
import re

import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext, SlashCommandOptionType
from discord_slash.utils import manage_commands
from dotenv import load_dotenv
import i18n
from PIL import Image, ImageDraw, ImageFont


FONT_SIZE = 63
TO_POSITION = (130, 699)
FROM_POSITION = (110, 777)
TEXT_COLOR = "#ef5ba7"
JPEG_QUALITY = 90


logging.basicConfig(level=logging.INFO)
load_dotenv()
i18n.set('filename_format', 'lang.{format}')
i18n.load_path.append('res')
guild_ids = [int(string) for string in os.getenv("GUILD_IDS", "").split()] or None
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=commands.when_mentioned, intents=intents)
slash = SlashCommand(bot, sync_commands=True)
nick_levels = re.compile(r" ([📙🐀⌛💰🐓💀🎣🏆💎🏅][0-9]{1,3})+$")


async def _valentin(ctx: SlashContext, recipient: discord.Member):
    await ctx.respond(eat=True)
    sender = ctx.author
    lang = os.getenv("LANG_{}".format(ctx.guild.id))
    with Image.open("res/templates/{}.jpg".format(lang)) as image:
        font = ImageFont.truetype("res/clegane.ttf", FONT_SIZE)
        draw = ImageDraw.Draw(image)
        sender_display_name = nick_levels.sub("", sender.display_name)
        recipient_display_name = nick_levels.sub("", recipient.display_name)
        draw.text(FROM_POSITION, sender_display_name, fill=TEXT_COLOR, font=font)
        draw.text(TO_POSITION, recipient_display_name, fill=TEXT_COLOR, font=font)

        with io.BytesIO() as tempio:
            image.save(tempio, "jpeg", quality=JPEG_QUALITY)
            tempio.seek(0)
            msg = i18n.t(
                "%{sender}’s heart burns for %{recipient}!",
                sender=sender.mention,
                recipient=recipient.mention,
                locale=lang
            )
            await ctx.send(
                content=msg,
                allowed_mentions=discord.AllowedMentions(users=True),
                file=discord.File(tempio, filename="flameheart.jpg")
            )
    lover_role = ctx.guild.get_role(int(os.getenv("ROLE_{}".format(ctx.guild.id))))
    try:
        if lover_role not in sender.roles:
            await sender.add_roles(lover_role)
        if lover_role not in recipient.roles:
            await recipient.add_roles(lover_role)
    except discord.Forbidden:
        logging.warning("Cannot add lover role for guild {}".format(repr(ctx.guild)))

for guild_id in guild_ids:
    lang = os.getenv("LANG_{}".format(guild_id))
    i18n.set('locale', lang)
    slash.add_slash_command(
        cmd=_valentin,
        name=i18n.t("valentine"),
        description=i18n.t("Declare your burning heart to another member!"),
        options=[manage_commands.create_option(
            name=i18n.t("member"),
            description=i18n.t("Member whom your heart burns to"),
            option_type=SlashCommandOptionType.USER,
            required=True
        )],
        guild_ids=[guild_id]
    )

bot.run(os.getenv("TOKEN"))
