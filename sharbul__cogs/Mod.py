import discord
from discord.ext import commands
from sharbull__db.main import *
from sharbull__utility.main import log


class ModCommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.bot_has_permissions(administrator=True)
    @commands.has_permissions(mute_members=True)
    @commands.guild_only()
    @commands.command()
    async def mute(self, ctx, member: discord.Member):
        log_channel_id, verified_role_id, captcha_level, security_activated = check_guild_setup(ctx.guild.id)
        await member.remove_roles(ctx.guild.get_role(verified_role_id))
        message = "✅ Member {.mention} has been muted (removed {.mention})".format(member,
                                                                                   ctx.guild.get_role(
                                                                                       verified_role_id))
        embed = discord.Embed(description=message)
        await ctx.send(embed=embed)
        increase_user_flag(user_id=member.id, mutes_to_add=1)
        await log(ctx.guild.get_channel(log_channel_id), message)

    @commands.bot_has_permissions(administrator=True)
    @commands.has_permissions(kick_members=True)
    @commands.guild_only()
    @commands.command()
    async def kick(self, ctx, member: discord.Member):
        log_channel_id, verified_role_id, captcha_level, security_activated = check_guild_setup(ctx.guild.id)
        message = "✅ Member {.mention} has been kicked".format(member)
        embed = discord.Embed(description=message)
        await ctx.send(embed=embed)
        await member.kick()
        increase_user_flag(user_id=member.id, kicks_to_add=1)
        await log(ctx.guild.get_channel(log_channel_id), message)

    @commands.bot_has_permissions(administrator=True)
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    @commands.command()
    async def ban(self, ctx, member: discord.Member):
        log_channel_id, verified_role_id, captcha_level, security_activated = check_guild_setup(ctx.guild.id)
        message = "✅ Member {.mention} has been banned".format(member)
        embed = discord.Embed(description=message)
        await ctx.send(embed=embed)
        await member.ban()
        increase_user_flag(user_id=member.id, bans_to_add=1)
        await log(ctx.guild.get_channel(log_channel_id), message)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        message = ""
        if isinstance(error, commands.BotMissingPermissions):
            message = "⚠️The bot must be an administrator in order to protect the guild."
        elif isinstance(error, commands.NoPrivateMessage):
            message = "⚠️Please use this command in a guild channel."
        elif isinstance(error, commands.MissingPermissions):
            message = "⚠️You do not have enough privileges to do that."
        elif isinstance(error, commands.BadArgument):
            message = "⚠️Wrong command argument."
        elif isinstance(error, commands.MissingRequiredArgument):
            message = "⚠️Missing command argument."
        else:
            message = "⚠️Unknown error"
            raise error
        embed = discord.Embed(description=message)
        await ctx.send(embed=embed)