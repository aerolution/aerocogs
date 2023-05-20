from .jail import Jail

async def setup(bot):
    bot.add_cog(Jail(bot))
