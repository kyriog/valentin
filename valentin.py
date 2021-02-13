import io
import logging
import os
import re

import discord
from discord_slash import SlashCommand, SlashContext, SlashCommandOptionType
from discord_slash.utils import manage_commands
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont


FONT_SIZE = 63
TO_POSITION = (130, 699)
FROM_POSITION = (110, 777)
TEXT_COLOR = "#ef5ba7"
JPEG_QUALITY = 90


load_dotenv()
guild_ids = [int(string) for string in os.getenv("GUILD_IDS", "").split()] or None
intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)
slash = SlashCommand(client, auto_register=True)
nick_levels = re.compile(r" ([📙🐀⌛💰🐓💀🎣🏆💎🏅][0-9]{1,3})+$")


@slash.slash(
    name="valentin",
    description="Déclarez votre flamme à un autre membre !",
    options=[manage_commands.create_option(
        name="membre",
        description="Membre à qui déclarer votre flamme",
        option_type=SlashCommandOptionType.USER,
        required=True
    )],
    guild_ids=guild_ids,

)
async def _valentin(ctx: SlashContext, recipient: discord.Member):
    await ctx.send(5)
    sender = ctx.author
    with Image.open("res/template.jpg") as image:
        font = ImageFont.truetype("res/clegane.ttf", FONT_SIZE)
        draw = ImageDraw.Draw(image)
        sender_display_name = nick_levels.sub("", sender.display_name)
        recipient_display_name = nick_levels.sub("", recipient.display_name)
        draw.text(FROM_POSITION, sender_display_name, fill=TEXT_COLOR, font=font)
        draw.text(TO_POSITION, recipient_display_name, fill=TEXT_COLOR, font=font)

        with io.BytesIO() as tempio:
            image.save(tempio, "jpeg", quality=JPEG_QUALITY)
            tempio.seek(0)
            msg = "{} déclare sa flamme à {} !".format(sender.mention, recipient.mention)
            await ctx.channel.send(
                content=msg,
                allowed_mentions=discord.AllowedMentions(users=True),
                file=discord.File(tempio, filename="flameheart.jpg")
            )
    lover_role = ctx.guild.get_role(int(os.getenv("ROLE_ID")))
    try:
        if lover_role not in sender.roles:
            await sender.add_roles(lover_role)
        if lover_role not in recipient.roles:
            await recipient.add_roles(lover_role)
    except discord.Forbidden:
        logging.warning("Cannot add lover role for guild {}".format(repr(ctx.guild)))

client.run(os.getenv("TOKEN"))
