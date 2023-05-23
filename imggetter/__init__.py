from .imggetter import PfpGetter

async def setup(bot):
    await bot.add_cog(PfpGetter(bot))
