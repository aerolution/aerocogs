import discord

from redbot.core import commands
import json
import requests

class MyCog(commands.Cog):
    """A Roblox cog"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def roblox(self, ctx, username):

        users_json = requests.get(f"https://www.roblox.com/search/users/results?keyword={username}&maxRows=1&startIndex=0")
        users = json.loads(users_json.text)

        if not users['UserSearchResults']:
            await ctx.send(f"Sorry, no user was found with the username {username}.")
            return

        if len(users['UserSearchResults']) < 1 :
            await ctx.send(f"Sorry, no user was found with the username {username}.")
            return

        user_id = users['UserSearchResults'][0]['UserId']

        profile_json = requests.get(f"https://users.roblox.com/v1/users/{user_id}")
        profile = json.loads(profile_json.text)
        display_name = profile["displayName"]
        created_date = profile["created"]
        description = profile["description"]

        thumbnail_json = requests.get(f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={user_id}&size=100x100&format=Png&isCircular=false")
        thumbnail = json.loads(thumbnail_json.text)
        thumbnail_url = thumbnail['data'][0]['imageUrl']

        embed = discord.Embed(title=f"{display_name}", url=f"https://www.roblox.com/users/{user_id}/profile",
                              description=description,
                              color=0x00b3ff)
        embed.set_author(name="Roblox")
        embed.add_field(name="Username", value=f"{display_name}", inline=False)
        embed.add_field(name="ID", value=f"{user_id}", inline=True)
        embed.add_field(name="Date created", value=f"{created_date}", inline=False)
        embed.set_thumbnail(url=thumbnail_url)
        await ctx.send(embed=embed)

# Register the cog
def setup(bot):
    bot.add_cog(MyCog(bot))
