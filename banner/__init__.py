from .banner import Banner

async def setup(bot):
   bot.add_cog(Banner(bot))
