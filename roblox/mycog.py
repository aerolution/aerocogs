from redbot.core import commands
import json
import requests
class MyCog(commands.Cog):
    """My custom cog"""

    def __init__(self, bot):
        self.bot = bot
        
        @commands.command()
async def rouser(ctx, username):
 
    users_json = requests.get(f"https://www.roblox.com/search/users/results?keyword={username}&maxRows=1&startIndex=0")
    users = json.loads(users_json.text)
    user_id = users['UserSearchResults'][0]['UserId']
 
 
 
    profile_json = requests.get(f"https://users.roblox.com/v1/users/{user_id}")
    profile = json.loads(profile_json.text)
    display_name = profile["displayName"]
    created_date = profile["created"]
    description = profile["description"]
 
    thumbnail_json = requests.get(f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={user_id}&size=100x100&format=Png&isCircular=false")
    thumbnail = json.loads(thumbnail_json.text)
    thumbnail_url = thumbnail['data'][0]['imageUrl']
 
    embed = discord.Embed(title=f"{username}", url=f"https://www.roblox.com/users/{user_id}/profile", color=0x00b3ff)
    embed.set_author(name="RoUser")
    embed.set_footer(text="Made by AllysonStudiosDev")
 
    embed.add_field(name="id", value=f"{user_id}", inline=False)
    embed.add_field(name="Displayname", value=f"{display_name}", inline=True)
    embed.add_field(name="created", value=f"{created_date}", inline=False)
    embed.add_field(name="description", value=f"{description}", inline=True)
    embed.set_thumbnail(url=f"{thumbnail_url}")
    await ctx.send(embed=embed)
