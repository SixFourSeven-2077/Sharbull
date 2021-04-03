import discord
from discord.ext import commands


class ErrorCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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