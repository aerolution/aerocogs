import discord
from redbot.core import commands, Config


class Jail(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)
        default_guild = {"jail_channel": None}
        self.config.register_guild(**default_guild)

    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.command()
    async def jail(self, ctx, member: discord.Member, *, reason: str):
        """Jail a user and restrict them to a single specified channel."""
        jail_channel_id = await self.config.guild(ctx.guild).jail_channel()
        if not jail_channel_id:
            await ctx.send("Jail channel not set. Please set it using `setjailchannel` command.")
            return

        jail_channel = ctx.guild.get_channel(jail_channel_id)
        if not jail_channel:
            await ctx.send("Jail channel not found. Please set a valid channel using `setjailchannel` command.")
            return

        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(send_messages=False),
            member: discord.PermissionOverwrite(send_messages=True)
        }
        await jail_channel.set_permissions(member, overwrite=overwrites, reason=reason)
        await ctx.send(f"{member.mention} has been jailed for {reason}.")

    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    @commands.command()
    async def setjailchannel(self, ctx, channel: discord.TextChannel):
        """Set the jail channel for this server."""
        await self.config.guild(ctx.guild).jail_channel.set(channel.id)
        await ctx.send(f"Jail channel has been set to {channel.mention}.")
