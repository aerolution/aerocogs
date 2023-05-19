import discord
from redbot.core import commands
from ttapi import TikTokApi

class TikTokFYP(commands.Cog):
    """Gets a random video from TikTok's For You Page"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def tiktokfyp(self, ctx):
        """Gets a random video from TikTok's For You Page"""
        api = TikTokApi()
        results = api.trending()
        video = results[0]

        embed = discord.Embed(title=f"{video['text']}", url=f"https://www.tiktok.com/@{video['author']['uniqueId']}/video/{video['id']}")
        
        # Set thumbnail
        embed.set_thumbnail(url=video["author"]["avatarThumb"])
        
        # Add author attribution
        embed.set_author(name=video["author"]["uniqueId"], url=f"https://www.tiktok.com/@{video['author']['uniqueId']}")
        
        # Set video views and likes
        embed.add_field(name="Views", value=f"{video['stats']['playCount']:,}")
        embed.add_field(name="Likes", value=f"{video['stats']['diggCount']:,}")
        
        # Set image
        embed.set_image(url=video["video"]["originCover"])
        
        await ctx.send(embed=embed)

