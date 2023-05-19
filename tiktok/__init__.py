from .tiktok import TikTokFYP


async def setup(bot):
    await bot.add_cog(fyp(bot))

