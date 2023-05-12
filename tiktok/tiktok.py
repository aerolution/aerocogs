import discord
from redbot.core import commands
from tikapi import TikAPI, ValidationException, ResponseException

class TikTokUser(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = "hnxoYBFNO7uQFUpmRkiPNmb3Rr11YJYerx7clmfc7mHRpPWS"
        self.user_account_key = "2y4qLDFxAcxujMjazkQNzQKUhvGv43U1LmSyF6KYOytngcNw"

    @commands.command()
    async def tiktokuser(self, ctx):
        """Fetches information about a TikTok user."""
        try:
            api = TikAPI(self.api_key)
            user = api.user(accountKey=self.user_account_key)
            response = user.info()
            response_json = response.json()
            user_info = f"Username: {response_json['itemInfos'][0]['itemStruct']['author']['uniqueId']}\n" \
                        f"Full Name: {response_json['itemInfos'][0]['itemStruct']['author']['nickname']}\n" \
                        f"Bio: {response_json['itemInfos'][0]['itemStruct']['author']['signature']}\n" \
                        f"Following: {response_json['itemInfos'][0]['itemStruct']['authorStats']['followingCount']}\n" \
                        f"Followers: {response_json['itemInfos'][0]['itemStruct']['authorStats']['followerCount']}\n" \
                        f"Total Likes: {response_json['itemInfos'][0]['itemStruct']['authorStats']['heartCount']}"

            await ctx.send(user_info)
        except ValidationException as e:
            await ctx.send(f"Validation error: {e}, {e.field}")
        except ResponseException as e:
            await ctx.send(f"Response error: {e}, {e.response.status_code}")
        except Exception as e:
            await ctx.send(f"Error fetching user info: {e}")


