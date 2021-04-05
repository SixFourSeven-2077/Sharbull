import discord
from discord.ext import commands


class ErrorCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        message = ""
        if isinstance(error, commands.BotMissingPermissions):
            message = "⚠️The bot must have the following permissions : "\
                      "- Mute Members\n"\
                      "- Kick Members\n"\
                      "- Ban Members\n"\
                      "- Manage Messages\n"\
                      "- Basic privileges such as : View and Send Messages, Add reactions, View Channels etc..."
        elif isinstance(error, commands.NoPrivateMessage):
            message = "⚠️Please use this command in a guild channel."
        elif isinstance(error, commands.MissingPermissions):
            message = "⚠️You do not have enough privileges to do that."
        elif isinstance(error, commands.BadArgument):
            message = "⚠️Wrong command argument."
        elif isinstance(error, commands.MissingRequiredArgument):
            message = "⚠️Missing command argument."
        elif isinstance(error, commands.CommandOnCooldown):
            target = "You are"
            if error.cooldown.type == commands.BucketType.guild:
                target = "The guild is"
            message = "⚠️{} being rate limited, please try again in **{}** seconds".format(target, round(error.retry_after))
        else:
            message = "⚠️Unknown error"
            raise error
        embed = discord.Embed(description=message)
        await ctx.send(embed=embed)