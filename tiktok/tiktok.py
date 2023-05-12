import discord
from redbot.core import commands
from tikapi import TikAPI, ValidationException, ResponseException

class fyp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api = TikAPI("hnxoYBFNO7uQFUpmRkiPNmb3Rr11YJYerx7clmfc7mHRpPWS")
        self.user = self.api.user(accountKey="2y4qLDFxAcxujMjazkQNzQKUhvGv43U1LmSyF6KYOytngcNw")

    @commands.command()
    async def videoinfo(self, ctx, video_id: str):
        """Fetches video information from TikTok."""
        try:
            response = self.user.posts.video(id=video_id)
            video_info = response.json()
            if "id" in video_info:
                embed = discord.Embed(title="TikTok Video Information")
                embed.add_field(name="Video ID", value=video_info["id"], inline=False)
                embed.add_field(name="Description", value=video_info["desc"], inline=False)
                embed.add_field(name="Likes", value=video_info["stats"]["diggCount"], inline=True)
                embed.add_field(name="Shares", value=video_info["stats"]["shareCount"], inline=True)
                embed.add_field(name="Comments", value=video_info["stats"]["commentCount"], inline=True)
                embed.add_field(name="Plays", value=video_info["stats"]["playCount"], inline=True)
                await ctx.send(embed=embed)
            else:
                await ctx.send("Video information not found.")
        except ValidationException as e:
            await ctx.send(f"Validation error: {e}, field: {e.field}")
        except ResponseException as e:
            await ctx.send(f"Response error: {e}, status code: {e.response.status_code}")

def setup(bot):
    bot.add_cog(TikTok(bot))
