import discord
from sharbull__db.main import *
from datetime import datetime, timedelta


def get_prefix(client, message):
    with open('config/customprefixes.json', 'r') as f:
        prefixes = json.load(f)
    try:
        return prefixes[str(message.guild.id)]
    except KeyError:
        return "!!"


def seconds_to_text(secs):
    days, hours, minutes, seconds = seconds_to_dhms(secs)
    result = ("{0} day{1}, ".format(days, "s" if days!=1 else "") if days else "") + \
    ("{0} hour{1}, ".format(hours, "s" if hours!=1 else "") if hours else "") + \
    ("{0} minute{1}, ".format(minutes, "s" if minutes!=1 else "") if minutes else "") + \
    ("{0:.2f} second{1} ago".format(seconds, "s" if seconds!=1 else "") if seconds else "")
    return result


def seconds_to_dhms(secs):
    days = secs//86400
    hours = (secs - days*86400)//3600
    minutes = (secs - days*86400 - hours*3600)//60
    seconds = secs - days*86400 - hours*3600 - minutes*60
    return days, hours, minutes, seconds


async def log(channel: discord.TextChannel, message: str):
    if channel is not None:
        embed = discord.Embed(title="New Log", description=message, timestamp=datetime.utcnow())
        embed.set_footer(text="Sharbull Security Bot - Timezone : UTC",
                         icon_url="https://cdn0.iconfinder.com/data/icons/small-n-flat/24/678094-shield-512.png")
        await channel.send(embed=embed)
    else:
        print("NO LOGS SETUPED")


