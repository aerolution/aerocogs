from .ytshorts import YTShorts

async def setup(bot):
    await bot.add_cog(YTShorts(bot))
