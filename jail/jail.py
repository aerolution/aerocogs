import discord
from discord.ext import commands
from datetime import datetime, timedelta
from re import search
from redbot.core import Config

class Jail(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)
        default_guild = {
            "jail_channel": None,
            "logs_channel": None
        }
        self.config.register_guild(**default_guild)

    async def duration_to_seconds(self, duration):
        match = search(r"(\d+d)?(\d+h)?(\d+m)?(\d+s)?", duration)
        days, hours, minutes, seconds = [int(x[:-1]) if x else 0 for x in match.groups()]
        return timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds).total_seconds()

    async def jail_user(self, guild, user, jail_channel):
        for channel in guild.channels:
            if channel.id != jail_channel.id:
                await channel.set_permissions(user, view_channel=False, send_messages=False)

    async def unjail_user(self, guild, user):
        for channel in guild.channels:
            await channel.set_permissions(user, overwrite=None)

    @commands.group()
    async def jailset(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Invalid subcommand. Use `jailset channel` or `jailset logs`.")

    @jailset.command()
    async def channel(self, ctx, channel: discord.TextChannel):
        await self.config.guild(ctx.guild).jail_channel.set(channel.id)
        embed = discord.Embed(title="Jail Channel Set", description=f"Jail channel set to {channel.mention}.", color=discord.Color.blue())
        await ctx.send(embed=embed)

    @jailset.command()
    async def logs(self, ctx, channel: discord.TextChannel):
        await self.config.guild(ctx.guild).logs_channel.set(channel.id)
        embed = discord.Embed(title="Logs Channel Set", description=f"Logs channel set to {channel.mention}.", color=discord.Color.blue())
        await ctx.send(embed=embed)

    @commands.command()
    async def jail(self, ctx, user: discord.Member, duration: str = None, *, reason: str = None):
        if duration:
            duration_seconds = await self.duration_to_seconds(duration)
            unjail_time = datetime.utcnow() + timedelta(seconds=duration_seconds)
        else:
            unjail_time = None

        jail_channel_id = await self.config.guild(ctx.guild).jail_channel()
        jail_channel = ctx.guild.get_channel(jail_channel_id)

        embed = discord.Embed(title=f"Are you sure you want to jail {user.display_name}?", color=discord.Color.red())
        embed.add_field(name="Jail reason", value=reason or "No reason provided")
        embed.add_field(name="Jailed in", value=jail_channel.mention)
        embed.add_field(name="Jailed for", value=duration or "Indefinitely")
        embed.set_thumbnail(url=user.display_avatar)

        confirm_view = ConfirmView()
        confirm_message = await ctx.send(embed=embed, view=confirm_view)

        await confirm_view.wait()
        if confirm_view.value:
            await self.jail_user(ctx.guild, user, jail_channel)

            embed = discord.Embed(title=f"{user.display_name} was jailed", color=discord.Color.red())
            embed.add_field(name="Jail reason", value=reason or "No reason provided")
            embed.add_field(name="Jailed in", value=jail_channel.mention)
            embed.add_field(name="Jailed at", value=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
            embed.add_field(name="Jailed for", value=duration or "Indefinitely")
            embed.add_field(name="Moderator", value=ctx.author.display_name)
            embed.set_thumbnail(url=ctx.author.display_avatar)

            logs_channel_id = await self.config.guild(ctx.guild).logs_channel()
            logs_channel = ctx.guild.get_channel(logs_channel_id)
            await logs_channel.send(embed=embed)

            await confirm_message.edit(embed=discord.Embed(title=f"{user.display_name} was jailed", color=discord.Color.green()))
        else:
            await confirm_message.edit(embed=discord.Embed(title="Jail cancelled", color=discord.Color.green()))

    @commands.command()
    async def unjail(self, ctx, user: discord.Member, *, reason: str = None):
        embed = discord.Embed(title=f"Are you sure you want to unjail {user.display_name}?", color=discord.Color.green())
        embed.add_field(name="Unjail reason", value=reason or "No reason provided")
        embed.set_thumbnail(url=user.display_avatar)

        confirm_view = ConfirmView()
        confirm_message = await ctx.send(embed=embed, view=confirm_view)

        await confirm_view.wait()
        if confirm_view.value:
            await self.unjail_user(ctx.guild, user)

            embed = discord.Embed(title=f"{user.display_name} was unjailed", color=discord.Color.green())
            embed.add_field(name="Unjail reason", value=reason or "No reason provided")
            embed.add_field(name="Unjailed at", value=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
            embed.add_field(name="Moderator", value=ctx.author.display_name)
            embed.set_thumbnail(url=ctx.author.display_avatar)

            logs_channel_id = await self.config.guild(ctx.guild).logs_channel()
            logs_channel = ctx.guild.get_channel(logs_channel_id)
            await logs_channel.send(embed=embed)

            await confirm_message.edit(embed=discord.Embed(title=f"{user.display_name} was unjailed", color=discord.Color.green()))
        else:
            await confirm_message.edit(embed=discord.Embed(title="Unjail cancelled", color=discord.Color.green()))

class ConfirmView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=30.0)
        self.value = None

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def yes(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = True
        self.stop()

    @discord.ui.button(label="No", style=discord.ButtonStyle.red)
    async def no(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = False
        self.stop()
