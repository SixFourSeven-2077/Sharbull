from discord.ext import tasks, commands
import discord


class BackgroundTasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @tasks.loop(seconds=10)  # <- will do this every 5 seconds
    async def update_presence(self, *args):
        guilds_c = len(self.bot.guilds)
        users_c = len(self.bot.users)
        await self.bot.change_presence(
            activity=discord.Activity(
                name="✉️!!support for support | 🛡️ protecting {} guilds and {} users".format(guilds_c,
                                                                                                      users_c),
                type=discord.ActivityType.playing))
