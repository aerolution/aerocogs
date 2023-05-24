import discord
from discord.ext import commands
import re
from datetime import datetime, timedelta
from redbot.core import Config, checks, commands
import asyncio

class Jail(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)
        default_guild = {
            "jail_channel": None,
            "logs_channel": None
        }
        self.config.register_guild(**default_guild)

    def parse_duration(self, duration_str):
        match = re.match(r"(\d+)([dhm])", duration_str)
        if not match:
            return None

        value, unit = match.groups()
        value = int(value)

        if unit == "d":
            return timedelta(days=value)
        elif unit == "h":
            return timedelta(hours=value)
        elif unit == "m":
            return timedelta(minutes=value)

    async def create_embed(self, title, description, fields, thumbnail_url=None):
        embed = discord.Embed(title=title, description=description, color=discord.Color.blue())
        for field in fields:
            embed.add_field(name=field["name"], value=field["value"], inline=field.get("inline", False))

        if thumbnail_url:
            embed.set_thumbnail(url=thumbnail_url)

        return embed

    async def confirmation(self, ctx, embed):
        message = await ctx.send(embed=embed)

        components = [
            [
                discord.ui.button(style=discord.ButtonStyle.green, label="Yes"),
                discord.ui.button(style=discord.ButtonStyle.red, label="No")
            ]
        ]

        def check(interaction):
            return interaction.user == ctx.author and interaction.message == message

        try:
            interaction = await self.bot.wait_for("interaction", check=check, timeout=60)
        except asyncio.TimeoutError:
            await message.edit(content="Confirmation timed out.", components=[])
            return False

        await interaction.response.defer()

        if interaction.component.label == "Yes":
            await message.edit(content="Confirmed.", components=[])
            return True
        else:
            await message.edit(content="Cancelled.", components=[])
            return False

    @commands.group()
    @checks.admin_or_permissions(manage_roles=True)
    async def jailset(self, ctx):
        """Jail settings"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @jailset.command(name="channel")
    async def jailset_channel(self, ctx, channel: discord.TextChannel):
        """Set the jail channel"""
        await self.config.guild(ctx.guild).jail_channel.set(channel.id)
        embed = await self.create_embed("Jail Channel Set", f"Jail channel set to {channel.mention}", [])
        await ctx.send(embed=embed)

    @jailset.command(name="logs")
    async def jailset_logs(self, ctx, channel: discord.TextChannel):
        """Set the logs channel"""
        await self.config.guild(ctx.guild).logs_channel.set(channel.id)
        embed = await self.create_embed("Logs Channel Set", f"Logs channel set to {channel.mention}", [])
        await ctx.send(embed=embed)

    @commands.command()
    @checks.admin_or_permissions(manage_roles=True)
    async def jail(self, ctx, member: discord.Member, duration: str = None, *, reason: str = "No reason provided"):
        """Jail a user"""
        jail_channel_id = await self.config.guild(ctx.guild).jail_channel()
        jail_channel = ctx.guild.get_channel(jail_channel_id)
        if not jail_channel:
            embed = await self.create_embed("Error", "Jail channel not set. Please set it using `!jailset channel`.", [])
            await ctx.send(embed=embed)
            return

        duration_td = self.parse_duration(duration) if duration else None
        unjail_time = datetime.utcnow() + duration_td if duration_td else None

        fields = [
            {"name": "Jailed User", "value": member.mention},
            {"name": "Moderator", "value": ctx.author.mention},
            {"name": "Jail Channel", "value": jail_channel.mention},
            {"name": "Jailed At", "value": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")},
            {"name": "Duration", "value": duration if duration else "Indefinite"},
            {"name": "Reason", "value": reason}
        ]
        embed = await self.create_embed("User Jailed!", "Are you sure you want to jail this user?", fields, thumbnail_url=member.display_avatar)
        confirmed = await self.confirmation(ctx, embed)

        if not confirmed:
            return

        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            member: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        await jail_channel.set_permissions(member, overwrite=overwrites)

        for channel in ctx.guild.channels:
            if channel != jail_channel:
                await channel.set_permissions(member, overwrite=discord.PermissionOverwrite(read_messages=False, send_messages=False))

        embed = await self.create_embed("User Jailed!", reason, fields, thumbnail_url=member.display_avatar)
        await ctx.send(embed=embed)

        if unjail_time:
            await discord.utils.sleep_until(unjail_time)
            await self.unjail_user(ctx, member)

    async def unjail_user(self, ctx, member: discord.Member):
        jail_channel_id = await self.config.guild(ctx.guild).jail_channel()
        jail_channel = ctx.guild.get_channel(jail_channel_id)
        if not jail_channel:
            return

        await jail_channel.set_permissions(member, overwrite=None)

        for channel in ctx.guild.channels:
            if channel != jail_channel:
                await channel.set_permissions(member, overwrite=None)

    @commands.command()
    @checks.admin_or_permissions(manage_roles=True)
    async def unjail(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        """Unjail a user"""
        fields = [
            {"name": "Unjailed User", "value": member.mention},
            {"name": "Moderator", "value": ctx.author.mention},
            {"name": "Reason", "value": reason}
        ]
        embed = await self.create_embed("User Unjailed!", "Are you sure you want to unjail this user?", fields, thumbnail_url=member.display_avatar)
        confirmed = await self.confirmation(ctx, embed)

        if not confirmed:
            return

        await self.unjail_user(ctx, member)
        embed = await self.create_embed("User Unjailed!", f"{member.mention} has been unjailed.", fields)
        await ctx.send(embed=embed)
