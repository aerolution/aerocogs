import discord
import requests
import json
from discord.ext import commands

class Lock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="lock")
    async def lock_channel(self, ctx):
        # Get the lock GIF from the GIPHY API
        api_key = "rw40QaZ5L4AG1eJ1DK0PzgyYckMisIjQ"
        url = f"http://api.giphy.com/v1/gifs/random?api_key={api_key}&tag=lock"
        response = requests.get(url)
        json_data = json.loads(response.text)
        gif_url = json_data["data"]["images"]["original"]["url"]

        # Send an embed message with the lock GIF
        embed = discord.Embed(title="🔒 Channel Locked", color=discord.Color.red())
        embed.set_image(url=gif_url)
        embed.set_footer(text=f"Locked by {ctx.author.name}")
        await ctx.send(embed=embed)

        # Lock the channel
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)

def setup(bot):
    bot.add_cog(Lock(bot))
