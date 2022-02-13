import io
import logging
import os
import re

import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext, SlashCommandOptionType
from discord_slash.error import DuplicateCommand
from discord_slash.utils import manage_commands
from dotenv import load_dotenv
import i18n
from PIL import Image, ImageDraw, ImageFont


FONT_SIZE = 63
POSITIONS = {
    "fr": {"from": (110, 777), "to": (130, 699)},
    "es": {"from": (110, 777), "to": (130, 699)},
    "it": {"from": (110, 777), "to": (80, 699)},
}
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
slash = SlashCommand(bot)
nick_levels = re.compile(r" ([📙🐀⌛💰🐓💀🎣🏆💎🏅][0-9]{1,3})+$")
font_unavailable_chars = re.compile(r"[^A-Za-z0-9 !#$%&\'\(\)*+,\-̣\./:;?@\[\\\]\^\{\}\ ­ÀÁÂÃÄÅÇÈÉÊËÌÍÎÏÑÒÓÔÕÖØÙÚÛÜÝßàáâãäåçèéêëìíîïñòóôõöøùúûüýÿ\‘\’]")


@bot.event
async def on_ready():
    connectors = {}
    for guild_id in guild_ids:
        lang = os.getenv("LANG_{}".format(guild_id))
        i18n.set('locale', lang)
        cmd_name = i18n.t("valentine")
        member_i18n = i18n.t("member")
        try:
            connectors[cmd_name].add(member_i18n)
        except KeyError:
            connectors[cmd_name] = set()
            connectors[cmd_name].add(member_i18n)
        logging.info(f"Register command /{cmd_name} for guild #{guild_id}")
        await manage_commands.add_slash_command(
            bot_id=bot.user.id,
            bot_token=os.getenv("TOKEN"),
            guild_id=guild_id,
            cmd_name=cmd_name,
            description=i18n.t("Declare your burning heart to another member!"),
            options=[manage_commands.create_option(
                name=member_i18n,
                description=i18n.t("Member whom your heart burns to"),
                option_type=SlashCommandOptionType.USER,
                required=True
            )]
        )
    for cmd_name, connector_list in connectors.items():
        connector = {c: "recipient" for c in connector_list}
        slash.add_slash_command(
            cmd=_valentin,
            name=cmd_name,
            connector=connector
        )


async def _valentin(ctx: SlashContext, recipient: discord.Member):
    sender = ctx.author
    lang = os.getenv("LANG_{}".format(ctx.guild.id))
    msg = i18n.t(
        "%{sender}’s heart burns for %{recipient}!",
        sender=sender.mention,
        recipient=recipient.mention,
        locale=lang
    )
    await ctx.send(content=msg, allowed_mentions=discord.AllowedMentions(users=True))
    with Image.open("res/templates/{}.jpg".format(lang)) as image:
        font = ImageFont.truetype("res/clegane.ttf", FONT_SIZE)
        draw = ImageDraw.Draw(image)
        sender_display_name = nick_levels.sub("", sender.display_name)
        sender_display_name = font_unavailable_chars.sub("", sender_display_name)
        sender_display_name = sender_display_name.strip()
        recipient_display_name = nick_levels.sub("", recipient.display_name)
        recipient_display_name = font_unavailable_chars.sub("", recipient_display_name)
        recipient_display_name = recipient_display_name.strip()
        draw.text(POSITIONS[lang]["from"], sender_display_name, fill=TEXT_COLOR, font=font)
        draw.text(POSITIONS[lang]["to"], recipient_display_name, fill=TEXT_COLOR, font=font)

        with io.BytesIO() as tempio:
            image.save(tempio, "jpeg", quality=JPEG_QUALITY)
            tempio.seek(0)
            # discord-py-slash-command tricks to edit original message
            ctx.responded = False
            ctx.deferred = True
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


bot.run(os.getenv("TOKEN"))
