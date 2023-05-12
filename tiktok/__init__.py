import httpx
from .tiktok import fyp

def setup(bot):
    bot.add_cog(fyp(bot))
