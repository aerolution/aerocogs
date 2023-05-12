import discord
from discord.ext import commands
import requests
import json

class Lock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.locked_channels = set()

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx):
        if ctx.channel.id in self.locked_channels:
            await ctx.send("Channel is already locked.")
            return

        # Update permissions to deny sending messages for everyone
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)

        # Get lock GIF using GIPHY API
        response = requests.get(f"https://api.giphy.com/v1/gifs/random?api_key=rw40QaZ5L4AG1eJ1DK0PzgyYckMisIjQ&tag=lock")
        gif_data = json.loads(response.text)
        gif_url = gif_data["data"]["image_original_url"]

        # Create embed message with lock GIF
        embed = discord.Embed()
        embed.title = "Channel Locked"
        embed.description = "This channel has been temporarily locked."
        embed.set_image(url=gif_url)
        await ctx.send(embed=embed)

        self.locked_channels.add(ctx.channel.id)

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx):
        if ctx.channel.id not in self.locked_channels:
            await ctx.send("Channel is not locked.")
            return

        # Update permissions to allow sending messages for everyone
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)

        embed = discord.Embed()
        embed.title = "Channel Unlocked"
        embed.description = "This channel has been unlocked."
        await ctx.send(embed=embed)

        self.locked_channels.remove(ctx.channel.id)

def setup(bot):
    bot.add_cog(Lock(bot))

