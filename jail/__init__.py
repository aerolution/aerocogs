from .jail import JailCog


async def setup(bot):
    await bot.add_cog(JailCog(bot))
