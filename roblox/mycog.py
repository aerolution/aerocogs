from redbot.core import commands

class MyCog(commands.Cog):
    """My custom cog"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def roblox(ctx, username):

 carros_json=requests.get(f"https://api.roblox.com/users/get-by-u...{username}")
 carros=json.loads(carros_json.text)
 test = (carros["Id"])
 #image
 carro_json2=requests.get(f"https://users.roblox.com/v1/users/{test}/status")
 carro2=json.loads(carro_json2.text)
 test2 = (carro2["status"])

 #display
 displayname2=requests.get(f"https://users.roblox.com/v1/users/{test}")
 displayname3=json.loads(displayname2.text)
 displayname4 = (displayname3["displayName"])
 #created
 date1=requests.get(f"https://users.roblox.com/v1/users/{test}")
 date2=json.loads(date1.text)
 date3 = (date2["created"])

 #description
 desc1=requests.get(f"https://users.roblox.com/v1/users/{test}")
 desc2=json.loads(desc1.text)
 desc3 = (desc2["description"])
