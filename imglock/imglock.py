import discord
from redbot.core import commands, Config


class ImgLock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567891)
        default_guild = {"imglock_channel": None}
        self.config.register_guild(**default_guild)

    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    @commands.command()
    async def imglock(self, ctx, channel: discord.TextChannel):
        """Set the channel to restrict to image-only messages."""
        await self.config.guild(ctx.guild).imglock_channel.set(channel.id)
        await ctx.send(f"The image lock channel has been set to {channel.mention}.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        imglock_channel_id = await self.config.guild(message.guild).imglock_channel()
        if message.channel.id == imglock_channel_id and not message.attachments:
            await message.delete()
            warning_msg = await message.channel.send(
                f"{message.author.mention}, this channel is restricted to image-only messages."
            )
            await warning_msg.delete(delay=5)
