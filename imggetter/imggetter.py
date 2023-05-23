import discord
from discord import commands, tasks
import aiohttp
import random

class PfpGetter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pfp_channel_id = None
        self.banner_channel_id = None
        self.pfp_keywords = ['discord pfp', 'aesthetic', 'egirl']
        self.banner_keywords = ['banner', 'discord banner']
        self.send_pfp.start()
        self.send_banner.start()

    def cog_unload(self):
        self.send_pfp.cancel()
        self.send_banner.cancel()

    async def fetch_image(self, search_term):
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://www.pinterest.com/search/pins/?q={search_term}') as response:
                if response.status == 200:
                    data = await response.json()
                    images = data['data']['pins']
                    random_image = random.choice(images)
                    return random_image['images']['orig']['url']
                else:
                    return None

    @tasks.loop(minutes=1)
    async def send_pfp(self):
        if self.pfp_channel_id:
            channel = self.bot.get_channel(self.pfp_channel_id)
            search_term = random.choice(self.pfp_keywords)
            image_url = await self.fetch_image(search_term)
            if image_url:
                embed = discord.Embed(title='New Profile Picture', color=0xff69b4)
                embed.set_image(url=image_url)
                await channel.send(embed=embed)

    @tasks.loop(minutes=1)
    async def send_banner(self):
        if self.banner_channel_id:
            channel = self.bot.get_channel(self.banner_channel_id)
            search_term = random.choice(self.banner_keywords)
            image_url = await self.fetch_image(search_term)
            if image_url:
                embed = discord.Embed(title='New Banner', color=0xff69b4)
                embed.set_image(url=image_url)
                await channel.send(embed=embed)

    @commands.command()
    async def set_pfp_channel(self, ctx, channel: discord.TextChannel):
        self.pfp_channel_id = channel.id
        await ctx.send(f'Profile picture channel set to {channel.mention}')

    @commands.command()
    async def set_banner_channel(self, ctx, channel: discord.TextChannel):
        self.banner_channel_id = channel.id
        await ctx.send(f'Banner channel set to {channel.mention}')
