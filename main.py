import discord
from discord.ext import commands
from sharbul__cogs import Setup, Mod, User, Events
from AntiSpam import AntiSpamHandler
from AntiSpam.ext import AntiSpamTracker

intents = discord.Intents.default()
intents.members = True

with open("token", "r") as f:  # Token goes in file "token"
    TOKEN = f.read()

bot = commands.Bot(command_prefix="!!", intents=intents)
bot.remove_command("help")
bot.handler = AntiSpamHandler(bot, no_punish=True)
bot.tracker = AntiSpamTracker(bot.handler, 3)
bot.handler.register_extension(bot.tracker)


# Cogs

bot.add_cog(Setup.SetupCommandsCog(bot))
bot.add_cog(Mod.ModCommandsCog(bot))
bot.add_cog(User.UserCommandsCog(bot))
bot.add_cog(Events.EventsCog(bot))

bot.run(TOKEN)

