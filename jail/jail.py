from discord.ext import commands
from discord.utils import get

class Jail(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def jail(self, ctx, member: commands.MemberConverter):
        server_id = 1093594511076249701
        role_id = 1098752253449486416

        if ctx.guild.id == server_id:
            role = get(ctx.guild.roles, id=role_id)
            if role is not None:
                await member.add_roles(role)
                await ctx.send(f"{member.mention} has been jailed.")
            else:
                await ctx.send(f"Role with ID {role_id} not found.")
        else:
            await ctx.send(f"This command can only be used in the server with ID {server_id}.")
