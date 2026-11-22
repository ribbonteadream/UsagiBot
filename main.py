import discord
from discord.ext import commands
import aiohttp

import datetime
import json
import os

# Wildcard because we want to import all the helper functions
from helper_functions import *

"""
The main code for the bot.
The primary contents here should be commands and bot setup.
Helper functions should generally not go here, and should instead go in helper_functions.py
"""

#Change this to whatever your source code's link is, if you run a modified version
SOURCE_CODE_URL = "https://github.com/RobbieNeko/UsagiBot"
MODLOG_CHANNEL_ID = 1222257915973599302
REACTION_TRIGGERS: list
USAGI_COLOR: discord.Color = discord.Color.from_rgb(33, 26, 54) # Taken from her hair

if not os.path.isfile("./warnlog.json"):
    with open("./warnlog.json", 'w') as file:
        # Makes sure that the file is initialized with a blank dictionary if not found
        # Actual structure is dict[str, list[str]], where the keys are user IDs
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

# Class added for customizability, namely the setup hook override
class UsagiBot(commands.Bot):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def setup_hook(self):
        # Sets things up, namely the global session
        self.session = aiohttp.ClientSession()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = UsagiBot(command_prefix="u!", intents=intents)

@bot.tree.command()
async def about(interaction: discord.Interaction):
    """Prints basic 'about' info"""
    info = discord.Embed(title='About UsagiBot')
    info.add_field(name="Developer(s)", value="RosaAeterna (aka NekoRobbie), RibbonTeaDream")
    info.add_field(name="Library", value="Discord.py")
    info.add_field(name="License", value="GNU AGPL v3")
    info.add_field(name="Version", value="0.0.3-0")
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
    REACTION_TRIGGERS.append(newTrigger)
    with open("./reactiontriggers.json", 'w') as file:
        json.dump(REACTION_TRIGGERS, file)
    await interaction.response.send_message(f"Added new trigger for phrase {trigger}!", ephemeral=True)

@bot.tree.command()
@discord.app_commands.default_permissions(ban_members=True)
@discord.app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, user: discord.Member, reason: str | None = None):
    """Bans a user from the guild, sending a DM to them as well as putting it in the mod log"""
    author = interaction.user
    if (type(author) == discord.Member):
        if(author.roles[-1] <= user.roles[-1]):
            await interaction.response.send_message(f"You do not have the ability to ban {user.display_name}!", ephemeral=True)
            return
    channel = bot.get_channel(MODLOG_CHANNEL_ID)
    if type(channel) == discord.TextChannel:
        embed = modlogEmbed("ban", user, interaction.user, reason)
        await channel.send(embed=embed)
    try:
        await user.send(f"You have been banned from {interaction.guild}!{f"\n{reason}" if reason != None else ''}")
    except:
        print(f"Could not DM {user.name}")
    await user.ban(reason=reason)
    await interaction.response.send_message(f"Banned {user.display_name}!", ephemeral=True)

@bot.tree.command()
@discord.app_commands.default_permissions(moderate_members=True)
@discord.app_commands.checks.has_permissions(moderate_members=True)
async def cleartimeout(interaction: discord.Interaction, user: discord.Member):
    """Clears the timeout for the given user. (Idempotent)"""
    await user.timeout(None)
    await interaction.response.send_message(f"Cleared timeout for {user.display_name}")

@bot.tree.command()
@discord.app_commands.default_permissions(moderate_members=True)
@discord.app_commands.checks.has_permissions(moderate_members=True)
async def clearwarnings(interaction: discord.Interaction, user: discord.Member):
    """Clears the warnings for the given user. (Idempotent)"""
    # We're doing this old-school style because it looks cleaner when you have to do it this way
    log = open("./warnlog.json")
    data = json.load(log)
    log.close()
    log = open("./warnlog.json", 'w')
    # This even works if they aren't already in the log, so is extremely idempotent
    data[str(user.id)] = []
    json.dump(data, log)
    log.close()
    
    await interaction.response.send_message(f"Cleared warnings for {user.display_name}")

@bot.tree.command()
@discord.app_commands.default_permissions(kick_members=True)
@discord.app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, user: discord.Member, reason: str | None = None):
    """Kicks a user from the guild, sending a DM to them as well as putting it in the mod log"""
    author = interaction.user
    if (type(author) == discord.Member):
        if(author.roles[-1] <= user.roles[-1]):
            await interaction.response.send_message(f"You do not have the ability to ban {user.display_name}!", ephemeral=True)
            return
    channel = bot.get_channel(MODLOG_CHANNEL_ID)
    if type(channel) == discord.TextChannel:
        embed = modlogEmbed("kick", user, interaction.user, reason)
        await channel.send(embed=embed)
    try:
        await user.send(f"You have been kicked from {interaction.guild}!{f"\n{reason}" if reason != None else ''}")
    except:
        print(f"Could not DM {user.name}")
    await user.kick(reason=reason)
    await interaction.response.send_message(f"Kicked {user.display_name}!", ephemeral=True)

@bot.tree.command()
@discord.app_commands.default_permissions(moderate_members=True)
@discord.app_commands.checks.has_permissions(moderate_members=True)
async def listwarnings(interaction: discord.Interaction, user: discord.Member):
    """Lists the past warnings for the user in question"""
    with open("./warnlog.json") as log:
        data: dict = json.load(log)
        warnings: list = data.get(str(user.id), [])
    if len(warnings) == 0:
        await interaction.response.send_message(f"{user.display_name} does not have any warnings!")
    else:
        response = f"{user.display_name} has {len(warnings)} warnings:"
        for warning in warnings:
            response += '\n' + warning
        await interaction.response.send_message(response)

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
async def source(interaction: discord.Interaction):
    """Get a link to the source code!"""
    await interaction.response.send_message(f"Here's my source code!\n{SOURCE_CODE_URL}")

@bot.tree.command()
@discord.app_commands.default_permissions(moderate_members=True)
@discord.app_commands.checks.has_permissions(moderate_members=True)
@discord.app_commands.describe(length="The integer number of minutes you want to time someone out for")
async def timeout(interaction: discord.Interaction, user: discord.Member, length: int, reason: str | None = None):
    """Applies a timeout to the user in the guild, sending a DM to them as well as putting it in the mod log"""
    author = interaction.user
    if (type(author) == discord.Member):
        if(author.roles[-1] <= user.roles[-1]):
            await interaction.response.send_message(f"You do not have the ability to timeout {user.display_name}!", ephemeral=True)
            return
    delta = datetime.timedelta(minutes=int(length))
    channel = bot.get_channel(MODLOG_CHANNEL_ID)
    if type(channel) == discord.TextChannel:
        embed = modlogEmbed("timeout", user, interaction.user, reason)
        await channel.send(embed=embed)
    try:
        await user.send(f"You have been timed out from {interaction.guild} for {length} minute(s)!{f"\n{reason}" if reason != None else ''}")
    except:
        print(f"Could not DM {user.name}")
    await user.timeout(delta, reason=reason)
    await interaction.response.send_message(f"Timed out {user.display_name} for {length} minute(s)!", ephemeral=True)

@bot.tree.command()
@discord.app_commands.default_permissions(moderate_members=True)
@discord.app_commands.checks.has_permissions(moderate_members=True)
async def warn(interaction: discord.Interaction, user: discord.Member, reason: str):
    """Warns a user in the guild, sending a DM to them as well as putting it in the mod log. Also logs the warning in a file to keep track."""
    channel = bot.get_channel(MODLOG_CHANNEL_ID)
    if type(channel) == discord.TextChannel:
        embed = modlogEmbed("warn", user, interaction.user, reason)
        await channel.send(embed=embed)
    try:
        await user.send(f"You have been warned in {interaction.guild}!\n{reason}")
    except:
        print(f"Could not DM {user.name}")
    # This is TECHNICALLY blocking, but async file handling doesn't really work
    # And this is being run on a single core system so threaded approaches probably don't work any better
    file = open("./warnlog.json")
    js: dict = json.load(file)
    file.close()
    warnings: list[str] = js.get(str(user.id), [])
    warnings.append(reason)
    js[str(user.id)] = warnings
    file = open("./warnlog.json", 'w')
    json.dump(js, file)
    file.close()
    await interaction.response.send_message(f"Warned {user.display_name}!", ephemeral=True)
    
@bot.event
async def on_message(message: discord.Message):
    # Do not recursively trigger ourselves, or get triggered by other bots
    if message.author.bot:
        return
    # Handle actual commands, because this is probably eating the normal way to define them
    if message.content.startswith("u!"):
        if message.content == "u!sync":
            print("Attempting to sync slash commands")
            # Only the owner(s) should be able to do this
            # Necessary for slash commands to populate
            if bot.is_owner(message.author):
                await bot.tree.sync()
        return

    # Handles reaction triggers
    # Only the first found trigger occurs
    for trigger in REACTION_TRIGGERS:
        if trigger["trigger"] in message.content:
            text: str | None = None if trigger["message"] == '' else trigger["message"]
            if trigger["image"] != '':
                file = await getImageFromURL(bot.session, trigger["image"], "reaction")
                if (file != None):
                    await message.channel.send(content=text, file=file)
                    return
            await message.channel.send(content=text)
            return

# Add custom status!
@bot.event
async def on_ready():
    print('USAGI online!')
    await bot.change_presence(activity=discord.CustomActivity(name='Patrolling the celestia library! | <3 to you all!', emoji='⭐'))

bot.run(BOT_TOKEN)
