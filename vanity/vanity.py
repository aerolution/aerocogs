import asyncio
from redbot.core import commands
import os
import discord

class VanityChecker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.vanity_list = self.load_vanity_list()
        self.channel_id = 1115063675632484452
        self.check_interval = 3600  # Check every hour (in seconds)
        self.bot.loop.create_task(self.check_vanities())

    def load_vanity_list(self):
        # Load your extremely long list of words from a file or an external source
        # For example, you can load a text file with one word per line
        file_path = os.path.join(os.path.dirname(__file__), 'word_list.txt')
        with open(file_path, "r") as f:
            words = [line.strip() for line in f.readlines()]
        return words


    async def check_vanities(self):
    await self.bot.wait_until_ready()
    while not self.bot.is_closed():
        for vanity in self.vanity_list:
            if await self.is_vanity_free(vanity):
                await self.log_vanity(vanity)
        await asyncio.sleep(self.check_interval)

            
async def is_vanity_free(self, vanity):
    try:
        invite = await self.bot.fetch_invite(f"https://discord.gg/{vanity}")
    except discord.NotFound:
        # The invite was not found, which means the vanity URL is available
        return True
    else:
        # The invite was found, which means the vanity URL is not available
        return False

    async def log_vanity(self, vanity):
        channel = self.bot.get_channel(self.channel_id)
        if channel:
            await channel.send(f"This vanity is free: https://discord.gg/{vanity}")
