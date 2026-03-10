from io import BytesIO
import discord
from discord.ext import commands
import aiohttp

import datetime
import json
import os

#Change this to whatever your source code's link is, if you run a modified version
SOURCE_CODE_URL = "https://github.com/RobbieNeko/UsagiBot"
MODLOG_CHANNEL_ID = 1222257915973599302
REACTION_TRIGGERS: list

if not os.path.isfile("./warnlog.json"):
    with open("./warnlog.json", 'w') as file:
        # Makes sure that the file is initialized with a blank dictionary if not found
        # Actual structure is dict[int, list[str]], where the keys are user IDs
        json.dump({}, file)

if not os.path.isfile("./reactiontriggers.json"):
    with open("./reactiontriggers.json", 'w') as file:
        # Makes sure that the file is initialized with an empty array if not found
        # Actual structure is list[dict[str, str]]
        json.dump([], file)
        REACTION_TRIGGERS = []
else:
    # This is actually probably performance sensitive enough to warrant storing in RAM unless the list of triggers grows big enough to overwhelm the raspberry pi
    with open("./reactiontriggers.json") as file:
        REACTION_TRIGGERS = json.load(file)

with open("./config.json") as file:
    config = json.load(file)
    BOT_TOKEN = config['bot_token']

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="u!", intents=intents)

@bot.tree.command()
async def about(interaction: discord.Interaction):
    """Prints basic 'about' info"""
    info = discord.Embed(title='About UsagiBot')
    info.add_field(name="Developer(s)", value="RosaAeterna (aka NekoRobbie), RibbonTeaDream")
    info.add_field(name="Library", value="Discord.py")
    info.add_field(name="License", value="GNU AGPL v3")
    await interaction.response.send_message(embed=info)

@bot.tree.command()
@discord.app_commands.default_permissions(manage_messages=True)
@discord.app_commands.checks.has_permissions(manage_messages=True)
@discord.app_commands.describe(trigger="Text you want to trigger on in the message")
@discord.app_commands.describe(message="Text you want to react with (optional)")
@discord.app_commands.describe(image="URL to the image you want to react with (optional)")
async def addreactiontrigger(interaction: discord.Interaction, trigger: str, message: str | None = None, image: str | None = None):
    """Adds a trigger to react to specific message content with a predefined message and/or image"""
    newTrigger = {"trigger": trigger, "message": message if message != None else '', 'image': image if image != None else '' }
    with open("./reactiontriggers.json", 'w') as file:
        REACTION_TRIGGERS.append(newTrigger)
        json.dump(REACTION_TRIGGERS, file)
    await interaction.response.send_message(f"Added new trigger for phrase {trigger}!", ephemeral=True)

@bot.tree.command()
@discord.app_commands.default_permissions(ban_members=True)
@discord.app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, user: discord.Member, reason: str | None = None):
    """Bans a user from the guild, sending a DM to them as well as putting it in the mod log"""
    channel = bot.get_channel(MODLOG_CHANNEL_ID)
    if type(channel) == discord.TextChannel:
        await channel.send(f"{user.display_name} has been banned by {interaction.user.display_name}!{f"\n{reason}" if reason != None else ''}")
    await user.send(f"You have been banned from {interaction.guild}!{f"\n{reason}" if reason != None else ''}")
    await user.ban(reason=reason)
    await interaction.response.send_message(f"Banned {user.display_name}!", ephemeral=True)

@bot.tree.command()
@discord.app_commands.default_permissions(kick_members=True)
@discord.app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, user: discord.Member, reason: str | None = None):
    """Kicks a user from the guild, sending a DM to them as well as putting it in the mod log"""
    channel = bot.get_channel(MODLOG_CHANNEL_ID)
    if type(channel) == discord.TextChannel:
        await channel.send(f"{user.display_name} has been kicked by {interaction.user.display_name}!{f"\n{reason}" if reason != None else ''}")
    await user.send(f"You have been kicked from {interaction.guild}!{f"\n{reason}" if reason != None else ''}")
    await user.kick(reason=reason)
    await interaction.response.send_message(f"Kicked {user.display_name}!", ephemeral=True)

@bot.tree.command()
@discord.app_commands.default_permissions(manage_messages=True)
@discord.app_commands.checks.has_permissions(manage_messages=True)
@discord.app_commands.describe(trigger="The text which triggers the reaction you want to delete")
async def removereactiontrigger(interaction: discord.Interaction, trigger: str):
    """Removes a trigger to react to specific message content with a predefined message and/or image"""
    for item in REACTION_TRIGGERS:
        if trigger == item["trigger"]:
            REACTION_TRIGGERS.remove(item)
            with open("./reactiontriggers.json", 'w') as file:
                json.dump(REACTION_TRIGGERS, file)
            await interaction.response.send_message("Removed the specified trigger!", ephemeral=True)
            return
    await interaction.response.send_message("Could not find the specified trigger!", ephemeral=True)

@bot.tree.command()
@discord.app_commands.default_permissions(moderate_members=True)
@discord.app_commands.checks.has_permissions(moderate_members=True)
async def timeout(interaction: discord.Interaction, user: discord.Member, length: datetime.timedelta, reason: str | None = None):
    """Applies a timeout to the user in the guild, sending a DM to them as well as putting it in the mod log"""
    channel = bot.get_channel(MODLOG_CHANNEL_ID)
    if type(channel) == discord.TextChannel:
        await channel.send(f"{user.display_name} has been timed out for {length.total_seconds()} seconds by {interaction.user.display_name}!{f"\n{reason}" if reason != None else ''}")
    await user.send(f"You have been timed out from {interaction.guild} for {length.total_seconds()} seconds!{f"\n{reason}" if reason != None else ''}")
    await user.timeout(length, reason=reason)
    await interaction.response.send_message(f"Timed out {user.display_name} for {length.total_seconds()} seconds!", ephemeral=True)

@bot.tree.command()
@discord.app_commands.default_permissions(moderate_members=True)
@discord.app_commands.checks.has_permissions(moderate_members=True)
async def warn(interaction: discord.Interaction, user: discord.Member, reason: str):
    """Warns a user in the guild, sending a DM to them as well as putting it in the mod log. Also logs the warning in a file to keep track."""
    channel = bot.get_channel(MODLOG_CHANNEL_ID)
    if type(channel) == discord.TextChannel:
        await channel.send(f"{user.display_name} has been warned by {interaction.user.display_name}!\n{reason}")
    await user.send(f"You have been warned in {interaction.guild}!\n{reason}")
    # This is TECHNICALLY blocking, but async file handling doesn't really work
    # And this is being run on a single core system so threaded approaches probably don't work any better
    with open("./warnlog.json", 'r+') as file:
        js = json.load(file)
        warnings: list[str] = js[user.id]
        warnings.append(reason)
        js[user.id] = warnings
        json.dump(js, file)
    await interaction.response.send_message(f"Warned {user.display_name}!", ephemeral=True)

@bot.command()
async def sync(ctx):
    # Only the owner(s) should be able to do this
    # Necessary for slash commands to populate
    if bot.is_owner(ctx.author):
        await bot.tree.sync()

@bot.event
async def on_message(message: discord.Message):
    # Handles reaction triggers
    # Only the first found trigger occurs
    for trigger in REACTION_TRIGGERS:
        if trigger["trigger"] in message.content:
            text: str | None = None if trigger["message"] == '' else trigger["message"]
            if trigger["image"] != '':
                async with aiohttp.ClientSession() as session:
                    async with session.get(trigger["image"]) as response:
                        buffer = BytesIO(await response.read())
                        file = discord.File(fp=buffer, filename="reaction.png")
                await message.channel.send(content=text, file=file)
                return
            else:
                await message.channel.send(content=text)
                return

bot.run(BOT_TOKEN)