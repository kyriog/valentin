import os

import discord
from discord_slash import SlashCommand, SlashContext, SlashCommandOptionType
from discord_slash.utils import manage_commands
from dotenv import load_dotenv


load_dotenv()
guild_ids = [int(string) for string in os.getenv("GUILD_IDS", "").split()] or None
intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)
slash = SlashCommand(client, auto_register=True)


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
async def _valentin(ctx: SlashContext, member: discord.Member):
    msg = "{} déclare sa flamme à {} !".format(ctx.author.mention, member.mention)
    await ctx.send(content=msg, allowed_mentions=discord.AllowedMentions(users=True))

client.run(os.getenv("TOKEN"))
