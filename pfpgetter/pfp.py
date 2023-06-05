import discord
from discord.ext import commands
import aiohttp
from bs4 import BeautifulSoup

class ProfileHelper(commands.Cog):
    """Fetch profile pictures and banners from Pinterest."""

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def pfpchannel(self, ctx):
        """Set the channel for profile pictures."""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @pfpchannel.command(name="set")
    async def pfpchannel_set(self, ctx, channel: discord.TextChannel):
        # Save the channel ID to the bot's config
        await self.bot.config.channel(ctx.guild).pfp.set(channel.id)
        await ctx.send(f"Profile picture channel set to {channel.mention}")

    @commands.group()
    async def bannerchannel(self, ctx):
        """Set the channel for banners."""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @bannerchannel.command(name="set")
    async def bannerchannel_set(self, ctx, channel: discord.TextChannel):
        # Save the channel ID to the bot's config
        await self.bot.config.channel(ctx.guild).banner.set(channel.id)
        await ctx.send(f"Banner channel set to {channel.mention}")

    @commands.command()
    async def pfp(self, ctx):
        """Fetch a profile picture from Pinterest."""
        pfp_url = "https://www.pinterest.com/awnj0561/for-discord-pfp/"  # Updated Pinterest source
        await self.send_image(ctx, pfp_url, "pfp")

    @commands.command()
    async def banner(self, ctx):
        """Fetch a banner from Pinterest."""
        banner_url = "https://www.pinterest.com/haunteddreamsxd/discord-banners/"  # Updated Pinterest source
        await self.send_image(ctx, banner_url, "banner")
        

    async def send_image(self, ctx, url, image_type):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                html_content = await response.text()
                image_url = self.extract_image_url(html_content)

        if image_url is not None:
            channel_id = await self.bot.config.channel(ctx.guild).get_raw(image_type, default=None)
            if channel_id is not None:
                channel = self.bot.get_channel(channel_id)
                if channel is not None:
                    await channel.send(image_url)
                else:
                    await ctx.send(f"Error: {image_type.capitalize()} channel not found.")
            else:
                await ctx.send(f"Error: {image_type.capitalize()} channel not set.")
        else:
            await ctx.send(f"Error: Could not extract {image_type} image from Pinterest.")

    async def extract_image_url(self, html):
        soup = BeautifulSoup(html, "html.parser")
        image_elements = soup.find_all("img", class_="GrowthUnauthPinImage__Image")

        if image_elements:
            # Select the first image element
            image_element = image_elements[0]
            # Extract the image URL from the 'src' attribute
            image_url = image_element.get("src")
            return image_url
        else:
            return None
