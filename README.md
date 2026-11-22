# UsagiBot

## Overview

UsagiBot is a Discord bot written in Python using Discord.py meant primarily for RibbonTeaDream's community. Usagi is an AI character within RibbonTeaDream's lore, and as such it is only fitting she also shows up as a Discord bot. Due to the nature of this bot, features will primarily be determined by what Ribbon and her community want and can run. As such, this is not a general purpose bot, and is not currently really designed to be used outside of Ribbon's situation.

**However**, this bot can still serve perfectly well as an example of what is possible to do with a Discord bot, and so this repo may still be of interest outside of the community. Additionally, this does not mean we do not welcome third party contributions - Just expect them to be judged primarily on *Ribbon*'s usecase. However, of course, don't forget to keep in mind the [License](LICENSE)  if you're taking code from this.

## Versioning

UsagiBot loosely follows semantic versioning, in particular adopting the style more often seen with packages in Linux distros such as Fedora. In general, it takes the format X.Y.Z-H with the following meanings:
- X is the major version, and denotes any breaking changes (such as commands having different parameters, changes to the format of files, etc.)
- Y is the minor version, and denotes general feature updates within a major version
- Z is the patch version, and denotes primarily two types of changes: regular bugfixes, and organizational changes or similar changes that have no effect on the user of the bot.
- H is the hotfix number, denoting any urgent bugfixes made between patches. Primarily used for the purpose of rapid iteration when a bug can only be caught in live testing.
In general, we don't expect terribly many major version changes.

## Requirements

The provided requirements.txt should have the extra packages beyond the python standard library that you need in order to run the bot. The exact versions of the dependencies are likely irrelevant (they're just what my venv happened to have), but an important note is that the project needs Python 3.13+ no matter what.
