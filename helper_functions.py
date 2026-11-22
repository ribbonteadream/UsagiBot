import discord
import aiohttp

from io import BytesIO

"""
Helper functions to keep main.py clean.
Generally, if you're using something in multiple places (or expect to in the future), then it should go here.
Particularly useful for hiding away aiohttp logic.
"""

Image = discord.File

def modlogEmbed(type: str, user: discord.Member | discord.User, moderator: discord.Member | discord.User, reason: str | None) -> discord.Embed:
    if reason is None:
        reason = "No reason specified"
    color : discord.Color
    match type:
        case "ban":
            color = discord.Color.red()
        case "kick":
            color = discord.Color.orange()
        case _:
            color = discord.Color.yellow()

    embedBody = f"**Member:** {user.name} ({user.mention})\n**Moderator:** {moderator.display_name}\n**Reason:** {reason}"
    return discord.Embed(title=f"{type}: {user.display_name}", colour=color, description=embedBody)

async def getImageFromURL(session: aiohttp.ClientSession, url: str, name: str = "image") -> Image | None:
    """Handles getting an image from a URL. Does not support video files."""
    async with session.get(url) as response:
        if (response.status == 200):
            mimeType = response.headers.get("content-type")
            if (mimeType is None):
                print(f"getImageFromURL: URL {url} did not return a content type!")
                return None
            fileCategory, fileType = mimeType.split('/')
            if (fileCategory != "image"):
                print(f"getImageFromURL: URL {url} did not return an image!")
                return None
            buffer = BytesIO(await response.read())
            filename = name + "." + fileType
            return discord.File(fp=buffer, filename=filename)
        else:
            print(f"getImageFromURL: URL {url} returned HTTP {response.status}!")
            return None
        