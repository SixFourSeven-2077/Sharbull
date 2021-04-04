import discord
from discord.ext import commands
from sharbul__cogs import Setup, Mod, User, Events, Errors
from AntiSpam import AntiSpamHandler
from AntiSpam.ext import AntiSpamTracker
from sharbull__utility.main import get_prefix

intents = discord.Intents.default()
intents.members = True

with open("token", "r") as f:  # Token goes in file "token"
    TOKEN = f.read()

def when_mentioned_or_function(func):
    def inner(bot, message):
        r = func(bot, message)
        prefixes = commands.when_mentioned(bot, message)
        prefixes.append(r)
        return prefixes
    return inner


bot = commands.Bot(command_prefix=when_mentioned_or_function(get_prefix), intents=intents)

bot.remove_command("help")
bot.handler = AntiSpamHandler(bot, no_punish=True)
bot.tracker = AntiSpamTracker(bot.handler, 3)
bot.handler.register_extension(bot.tracker)


# Cogs

bot.add_cog(Errors.ErrorCog(bot))
bot.add_cog(Setup.SetupCommandsCog(bot))
bot.add_cog(Mod.ModCommandsCog(bot))
bot.add_cog(User.UserCommandsCog(bot))
bot.add_cog(Events.EventsCog(bot))

bot.run(TOKEN)

