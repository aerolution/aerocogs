import discord
from discord_slash import SlashCommand, SlashContext, ButtonStyle
from discord_slash.utils.manage_commands import create_option
from discord_slash.model import SlashCommandOptionType
from redbot.core import commands, Config
import asyncio
import re
from datetime import timedelta

class Jail(commands.Cog):
    """
    Put users in a jail! (Channel.)
    """

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)
        default_guild = {"jail_channel": None, "jail_log_channel": None}
        self.config.register_guild(**default_guild)
        self.slash = SlashCommand(bot, override_type=True)

    async def notify_log_channel(self, guild, embed):
        log_channel_id = await self.config.guild(guild).jail_log_channel()
        if log_channel_id:
            log_channel = guild.get_channel(log_channel_id)
            if log_channel:
                await log_channel.send(embed=embed)

    async def notify_user(self, member, embed):
        try:
            await member.send(embed=embed)
        except discord.Forbidden:
            jail_channel_id = await self.config.guild(member.guild).jail_channel()
            jail_channel = member.guild.get_channel(jail_channel_id)
            if jail_channel:
                await jail_channel.send(embed=embed)

    def parse_time(self, time_str):
        time_regex = r"(\d+)([smhd])"  # seconds, minutes, hours, days
        matches = re.findall(time_regex, time_str)
        if matches:
            total_seconds = 0
            for value, unit in matches:
                if unit == "s":
                    total_seconds += int(value)
                elif unit == "m":
                    total_seconds += int(value) * 60
                elif unit == "h":
                    total_seconds += int(value) * 3600
                elif unit == "d":
                    total_seconds += int(value) * 86400
            return total_seconds
        return None

    def format_timedelta(self, seconds):
        delta = timedelta(seconds=seconds)
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_parts = []
        if days:
            time_parts.append(f"{days}d")
        if hours:
            time_parts.append(f"{hours}h")
        if minutes:
            time_parts.append(f"{minutes}m")
        if seconds:
            time_parts.append(f"{seconds}s")
        return " ".join(time_parts)

    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.command()
    async def setjailchannel(self, ctx, channel: discord.TextChannel):
        """Set the channel to use as the jail."""
        await self.config.guild(ctx.guild).jail_channel.set(channel.id)
        await ctx.send(f"The jail channel has been set to {channel.mention}.")

    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.command()
    async def setjaillogchannel(self, ctx, channel: discord.TextChannel):
        """Set the channel to use for jail logs."""
        await self.config.guild(ctx.guild).jail_log_channel.set(channel.id)
        await ctx.send(f"The jail log channel has been set to {channel.mention}.")

    async def confirm_action(self, ctx, member, action):
        confirm_embed = discord.Embed(title=f"Are you sure you want to {action} this user?", color=discord.Color.orange())
        confirm_message = await ctx.send(embed=confirm_embed, components=[
            Button(style=ButtonStyle.green, label="Yes"),
            Button(style=ButtonStyle.red, label="No")
        ])

        def check(confirm_ctx):
            return confirm_ctx.author == ctx.author and confirm_ctx.channel == ctx.channel and confirm_ctx.message == confirm_message

        try:
            confirm_ctx = await self.bot.wait_for("button_click", check=check, timeout=30)
            if confirm_ctx.component.label == "Yes":
                return True
            else:
                return False
        except asyncio.TimeoutError:
            return False

    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.command()
    async def jail(self, ctx, member: discord.Member, *, reason: commands.clean_content = ""):
        """Jail a user and restrict them to a single specified channel.

        You can optionally specify a jail time after the reason. Examples:
        !jail @user being bad for 1h
        !jail @user spamming for 30m
        """

        jail_channel_id = await self.config.guild(ctx.guild).jail_channel()
        jail_channel = ctx.guild.get_channel(jail_channel_id)

        # Get author
        author = ctx.message.author

        # Get all channels in the guild
        channels = ctx.guild.channels

        # Deny send messages and view channel permissions in all channels
        for channel in channels:
            await channel.set_permissions(member, send_messages=False, view_channel=False)

        # Allow send messages permission only in the jail channel
        await jail_channel.set_permissions(member, send_messages=True, view_channel=True)

        # Parse the jail time if provided
        jail_time = self.parse_time(reason)
        formatted_reason = reason

        if jail_time:
            formatted_reason = formatted_reason.rsplit(None, 1)[0]  # Remove the time from the reason
            formatted_time = self.format_timedelta(jail_time)
            formatted_reason += f" (Jail time: {formatted_time})"

        # Create an embed message
        embed = discord.Embed(title="User was Jailed!", color=discord.Color.red())
        embed.add_field(name="User", value=member.mention, inline=False)
        embed.add_field(name="Jailed In", value=jail_channel.mention, inline=False)
        embed.add_field(name="Jailed At", value=ctx.message.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
        embed.set_footer(text=f"Jailed by: {author}", icon_url=author.display_avatar)
        if formatted_reason:
            embed.add_field(name="Reason", value=formatted_reason, inline=False)

        confirmation = await self.confirm_action(ctx, member, "jail")
        if confirmation:
            await ctx.send(embed=embed)
            # Send the embed message to the user or jail channel
            await self.notify_user(member, embed)
            # Notify the jail log channel
            await self.notify_log_channel(ctx.guild, embed)
        else:
            await ctx.send("The jail action has been canceled.")

        if jail_time:
            await asyncio.sleep(jail_time)
            await self.unjail(ctx, member, reason="User served their time.")

    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.command()
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
        embed.add_field(name="Unjailed At", value=ctx.message.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
        if reason:
            embed.add_field(name="Reason", value=reason, inline=False)

        # Get the actual command author
        author = ctx.message.author

        embed.set_footer(text=f"Unjailed by: {author}", icon_url=author.display_avatar)

        confirmation = await self.confirm_action(ctx, member, "unjail")
        if confirmation:
            await ctx.send(embed=embed)
            # Send the embed message to the user or jail channel
            await self.notify_user(member, embed)
            # Notify the jail log channel
            await self.notify_log_channel(ctx.guild, embed)
        else:
            await ctx.send("The unjail action has been canceled.")

    @slash.slash(
        name="jail",
        description="Jail a user and restrict them to a single specified channel",
        options=[
            create_option(
                name="member",
                description="The member to jail",
                option_type=SlashCommandOptionType.USER,
                required=True
            ),
            create_option(
                name="reason",
                description="Reason for jailing",
                option_type=SlashCommandOptionType.STRING,
                required=False
            )
        ]
    )
    async def _jail(self, ctx: SlashContext, member: discord.Member, reason: str = ""):
        """Slash command version of the jail command"""
        await self.jail(ctx, member, reason)

    @slash.slash(
        name="unjail",
        description="Unjail a user and restore their permissions",
        options=[
            create_option(
                name="member",
                description="The member to unjail",
                option_type=SlashCommandOptionType.USER,
                required=True
            ),
            create_option(
                name="reason",
                description="Reason for unjailing",
                option_type=SlashCommandOptionType.STRING,
                required=False
            )
        ]
    )
    async def _unjail(self, ctx: SlashContext, member: discord.Member, reason: str = None):
        """Slash command version of the unjail command"""
        await self.unjail(ctx, member, reason=reason)
