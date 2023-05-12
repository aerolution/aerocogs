from .tiktok import fyp

self.session = aiohttp.ClientSession()

async def setup(bot):
    await bot.add_cog(fyp(bot))
