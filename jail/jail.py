import discord
from discord.ext import commands
from discord.ui import Button, View
from redbot.core import Config
import re
import asyncio
from datetime import datetime, timedelta

class JailView(View):
    def __init__(self, member, reason, jail_time):
        super().__init__()
        self.member = member
        self.reason = reason
        self.jail_time = jail_time

    async def on_timeout(self):
        await self.message.edit(content="Confirmation timeout. Cancelling jail.", view=None)

    @Button(label="Yes", style=discord.ButtonStyle.green)
    async def yes_button(self, button, interaction):
        await self.jail_member(interaction)

    @Button(label="No", style=discord.ButtonStyle.red)
    async def no_button(self, button, interaction):
        await interaction.response.send_message("Jail cancelled.", ephemeral=True)
        await self.message.edit(view=None)

    async def jail_member(self, interaction):
        ctx = await self.bot.get_context(interaction.message)
        author = ctx.author

        jail_channel_id = await self.config.guild(ctx.guild).jail_channel()
        jail_channel = ctx.guild.get_channel(jail_channel_id)

        # Perform the jail action
        channels = ctx.guild.channels
        for channel in channels:
            await channel.set_permissions(self.member, send_messages=False, view_channel=False)

        await jail_channel.set_permissions(self.member, send_messages=True, view_channel=True)

        # Calculate the unjail time
        unjail_time = datetime.utcnow() + self.jail_time

        # Send the confirmation message
        embed = discord.Embed(title="User was Jailed!", color=discord.Color.red())
        embed.add_field(name="User", value=self.member.mention, inline=False)
        embed.add_field(name="Jailed In", value=jail_channel.mention, inline=False)
        embed.add_field(name="Jailed At", value=ctx.message.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
        if self.reason:
            embed.add_field(name="Reason", value=self.reason, inline=False)
        embed.add_field(name="Jail Time", value=str(self.jail_time), inline=False)
        embed.add_field(name="Unjail Time", value=unjail_time.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
        embed.set_footer(text=f"Jailed by: {author}", icon_url=author.display_avatar)

        await interaction.response.send_message(embed=embed, ephemeral=True)
        await self.notify_user(self.member, embed)
        await self.notify_log_channel(ctx.guild, embed)
        await self.message.edit(view=None)

class Jail(commands.Cog):
    """
    Put users in a jail! (Channel.)
    """

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)
        default_guild = {"jail_channel": None, "jail_log_channel": None}
        self.config.register_guild(**default_guild)

    async def notify_user(self, member, embed):
        try:
            await member.send(embed=embed)
        except discord.Forbidden:
            jail_channel_id = await self.config.guild(member.guild).jail_channel()
            jail_channel = member.guild.get_channel(jail_channel_id)
            if jail_channel:
                await jail_channel.send(embed=embed)

    async def notify_log_channel(self, guild, embed):
        log_channel_id = await self.config.guild(guild).jail_log_channel()
        log_channel = guild.get_channel(log_channel_id)
        if log_channel:
            await log_channel.send(embed=embed)

    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.command()
    async def setjailchannel(self, ctx, channel: discord.TextChannel):
        """Set the channel to use for jailing."""
        await self.config.guild(ctx.guild).jail_channel.set(channel.id)
        await ctx.send(f"The jail channel has been set to {channel.mention}.")

    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.command()
    async def setjaillogchannel(self, ctx, channel: discord.TextChannel):
        """Set the channel to use for jail logs."""
        await self.config.guild(ctx.guild).jail_log_channel.set(channel.id)
        await ctx.send(f"The jail log channel has been set to {channel.mention}.")

    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.command()
    async def jail(self, ctx, member: discord.Member, jail_time: commands.clean_content, *, reason: commands.clean_content = ""):
        """Jail a user and restrict them to a single specified channel.
        
        You can optionally specify a jail time after the reason. Examples:
        !jail @user for being bad 1d
        !jail @user for spamming 2h
        """
        time_pattern = r"(\d+)([smhd])"
        match = re.search(time_pattern, jail_time)
        if not match:
            return await ctx.send("Invalid jail time format. Please use a valid format, e.g., `1d` for 1 day, `2h` for 2 hours, etc.")

        quantity, unit = match.groups()
        if unit == "s":
            jail_time_delta = timedelta(seconds=int(quantity))
        elif unit == "m":
            jail_time_delta = timedelta(minutes=int(quantity))
        elif unit == "h":
            jail_time_delta = timedelta(hours=int(quantity))
        elif unit == "d":
            jail_time_delta = timedelta(days=int(quantity))
        else:
            return await ctx.send("Invalid jail time format. Please use a valid format, e.g., `1d` for 1 day, `2h` for 2 hours, etc.")

        jail_channel_id = await self.config.guild(ctx.guild).jail_channel()
        jail_channel = ctx.guild.get_channel(jail_channel_id)

        # Get author
        author = ctx.message.author

        # Create an embed message
        embed = discord.Embed(title="Confirmation", description="Are you sure you want to jail this user?", color=discord.Color.gold())
        embed.add_field(name="User", value=member.mention, inline=False)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Jail Time", value=str(jail_time_delta), inline=False)

        # Send the confirmation message with buttons
        view = JailView(member, reason, jail_time_delta)
        message = await ctx.send(embed=embed, view=view)
        view.message = message

    async def unjail(self, ctx, member: discord.Member, *, reason: str = None):
        """Unjail a user and restore their permissions."""
        # Get all channels in the guild
        channels = ctx.guild.channels

        # Remove permission overwrites for the member in all channels
        for channel in channels:
            await channel.set_permissions(member, overwrite=None)

        # Create an embed message
        embed = discord.Embed(title="User was Unjailed!", color=discord.Color.green())
        embed.add_field(name="User", value=member.mention, inline=False)
        embed.add_field(name="Unjailed By", value=ctx.message.author.mention, inline=False)
        if reason:
            embed.add_field(name="Reason", value=reason, inline=False)
        embed.set_footer(text=f"Unjailed at: {ctx.message.created_at.strftime('%Y-%m-%d %H:%M:%S')}")

        # Send the unjail message
        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.command()
    async def unjail(self, ctx, member: discord.Member, *, reason: commands.clean_content = None):
        """Unjail a user and restore their permissions."""
        await self.unjail(ctx, member, reason=reason)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        jail_channel_id = await self.config.guild(member.guild).jail_channel()
        jail_channel = member.guild.get_channel(jail_channel_id)

        if jail_channel:
            await jail_channel.set_permissions(member, send_messages=False, view_channel=False)
