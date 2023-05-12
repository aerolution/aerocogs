import discord
from discord.ext import commands
import requests

class ImageSearch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='img')
    async def image_search(self, ctx, *, query):
        # Replace YOUR_API_KEY with your actual Serpapi API key
        api_key = '576ca028f79b19f902ece71efb97a754fe748944c6ec67046a2d291fa39d942'
        search_engine = 'google'
        search_type = 'images'
        url = f'https://serpapi.com/search.json?q={query}&tbm={search_type}&api_key={api_key}&engine={search_engine}'

        response = requests.get(url).json()
        image_url = response['images_results'][0]['original']
        image_description = response['images_results'][0]['title']
        image_source = response['images_results'][0]['source']

        embed = discord.Embed(title=f'Image of {query} from Google', description=image_description, url=image_source)
        embed.set_image(url=image_url)

        await ctx.send(embed=embed)

def setup(bot):
