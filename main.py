import discord
from discord.ext import commands
from sharbull__utility.main import seconds_to_text, seconds_to_dhms
from sharbull__db.main import *
from colorama import Fore, Style, init
from datetime import datetime, timedelta
from captcha import image
import random
import string
import asyncio
import os
from AntiSpam import AntiSpamHandler
from AntiSpam.ext import AntiSpamTracker

init()  # windows

intents = discord.Intents.default()
intents.members = True

with open("token", "r") as f:  # Token goes in file "token"
    TOKEN = f.read()

bot = commands.Bot(command_prefix="!!", intents=intents)
bot.remove_command("help")
bot.handler = AntiSpamHandler(bot, no_punish=True)
bot.tracker = AntiSpamTracker(bot.handler, 3)
bot.handler.register_extension(bot.tracker)


async def is_admin(member: discord.Member):
    if member.guild_permissions.administrator is True:
        return True


@bot.event
async def on_ready():
    print(Fore.GREEN + Style.BRIGHT +
          'Successfully connected. [{}]'.format(bot.user))
    pingms = round(bot.latency * 1000)
    print("Commander's latency : " + Fore.YELLOW +
          "{}".format(pingms) + Fore.GREEN + "ms\n" + Style.RESET_ALL)
    guilds_c = len(bot.guilds)
    await bot.change_presence(
        activity=discord.Activity(name="🛡️ protecting {} guilds".format(guilds_c), type=discord.ActivityType.playing))


@bot.event
async def on_message(message):
    msg = message
    add_user(message.author.id)
    await bot.handler.propagate(message)
    if bot.tracker.is_spamming(message):
        log_channel_id, verified_role_id, captcha_level, security_activated = check_guild_setup(message.guild.id)

        points = calculate_reputation(message.author.id)
        message_log = "User {.mention}".format(msg.author) + " - Bad Reputation points : " + str(points) + "\n"
        if points <= 3:
            message_log += "User has been warned"
            description = "{.mention} : stop spamming".format(msg.author)
            increase_user_flag(user_id=msg.author.id, reports_to_add=1)
        elif points <= 10:
            message_log += "User has been muted (removed verified role)"
            description = "{.mention} has been muted for spamming"
            await msg.author.remove_roles(msg.guild.get_role(verified_role_id))
            increase_user_flag(user_id=msg.author.id, mutes_to_add=1)
        elif points <= 30:
            message_log += "User has been kicked"
            description="{.mention} has been kicked for spamming".format(msg.author)
            increase_user_flag(user_id=msg.author.id, kicks_to_add=1)
            await msg.author.kick()
        else:
            message_log += "User has been banned"
            description="{.mention} has been banned for spamming".format(msg.author)
            await msg.author.ban()
            increase_user_flag(user_id=msg.author.id, bans_to_add=1)
        embed = discord.Embed(description=description)
        await msg.channel.send(embed=embed)
        await log(msg.guild.get_channel(log_channel_id), message_log)

        bot.tracker.remove_punishments(message)
    await bot.process_commands(message)


async def log(channel: discord.TextChannel, message: str):
    if channel is not None:
        embed = discord.Embed(title="New Log", description=message, timestamp=datetime.utcnow())
        embed.set_footer(text="Sharbull Security Bot - Timezone : UTC",
                         icon_url="https://cdn0.iconfinder.com/data/icons/small-n-flat/24/678094-shield-512.png")
        await channel.send(embed=embed)
    else:
        print("NO LOGS SETUPED")


@bot.event
async def on_member_join(member):
    log_channel_id, verified_role_id, captcha_level, security_activated = check_guild_setup(member.guild.id)
    if security_activated is None or member.bot is True:
        return False

    add_user(member.id)
    captcha_fails, mutes, reports, kicks, bans = check_user_flags(member.id)
    trust_score = 14
    now = datetime.now()
    created_at = member.created_at
    time_since_creation = now - created_at
    time_since_creation = time_since_creation.total_seconds()
    time_since_creation_fmt = seconds_to_text(time_since_creation)

    message = "**New member joined** : " + member.mention + "\nAccount created :" + time_since_creation_fmt + \
              "\n\n**Noticeable flags** :\n"

    # trust
    days, hours, minutes, seconds = seconds_to_dhms(time_since_creation)
    if days < 1:
        message += " 	🚩 Account was created less than a day ago\n"
        trust_score -= 3
    if member.avatar_url == member.default_avatar_url:
        message += " 	🚩 Account has no custom avatar\n"
        trust_score -= 2
    if member.public_flags.hypesquad is False:
        message += "⚠️ Account has no HypeSquad Team\n"
        trust_score -= 1
    if member.premium_since is None:
        message += "⚠️ Account has no Nitro active sub\n"
        trust_score -= 1
    if member.public_flags.partner is False:
        message += "⚠️ Account has no partner badge\n"
        trust_score -= 1
    if member.public_flags.early_supporter is False:
        message += "⚠️ Account has no early supporter badge\n"
        trust_score -= 1
    if captcha_fails > 3:
        message += "⚠️ Account has failed the captcha **{}** times\n".format(captcha_fails)
        trust_score -= 1
    if mutes > 3:
        message += " 	🚩 Account has been muted **{}** times\n".format(mutes)
        trust_score -= 1
    if reports > 2:
        message += " 	🚩 Account has been reported **{}** times\n".format(reports)
        trust_score -= 1
    if kicks > 2:
        message += " 	🚩 Account has been kicked **{}** times\n".format(kicks)
        trust_score -= 1
    if bans > 1:
        message += " 	🚩 Account has been banned **{}** times\n".format(bans)
        trust_score -= 1

    message += ("🔍 Trust score is **" + str(trust_score) + "**/14")

    await log(member.guild.get_channel(log_channel_id), message)

    if captcha_level == 2 and trust_score > 9:
        await log(member.guild.get_channel(log_channel_id), "Trust score is high enough, captcha skipped")
        await member.add_roles(member.guild.get_role(verified_role_id))
        return True
    if captcha_level == 1:
        await log(member.guild.get_channel(log_channel_id), "Captcha level is set to ONE, skipped")
        try:
            await member.add_roles(member.guild.get_role(verified_role_id))
        except:
            pass
        return True

    string_to_guess = ""
    for char in range(6):
        char = random.choice(string.ascii_lowercase)
        string_to_guess += char
    image_data = image.ImageCaptcha(width=280, height=90).generate_image(string_to_guess)
    image_data.save("captcha/" + str(member.id) + ".png")
    embed = discord.Embed(title="Greetings, welcome to **{}**".format(member.guild.name),
                          description="Please complete the following captcha to continue.\n" +
                                      "You have 60 seconds to reply or your access will be denied." +
                                      "\nThere are only **lowercase** letters."  # in bold because ppl cant read
                          )
    embed.set_thumbnail(url=member.guild.icon_url)
    embed.set_footer(
        text="Sharbull Security Guard",
        icon_url="https://cdn0.iconfinder.com/data/icons/small-n-flat/24/678094-shield-512.png"
    )
    await member.send(
        embed=embed
    )

    await member.send(file=discord.File("captcha/" + str(member.id) + ".png"))

    def check(message):
        return message.content == string_to_guess and message.channel == message.author.dm_channel

    try:
        message = await bot.wait_for('message', timeout=60.0, check=check)
    except asyncio.TimeoutError:
        embed = discord.Embed(
            title="Time exceeded, verification has failed.",
            description="You have been kicked from **{}**.\n".format(member.guild.name) +
                        "You may try again by rejoining the server."
        )
        embed.set_thumbnail(url=member.guild.icon_url)
        embed.set_footer(
            text="Sharbull Security Guard",
            icon_url="https://cdn0.iconfinder.com/data/icons/small-n-flat/24/678094-shield-512.png"
        )
        await member.dm_channel.send(embed=embed)
        await member.kick(reason="User failed Captcha verification")
        increase_user_flag(user_id=member.id, captcha_fails_to_add=1)
    else:
        embed = discord.Embed(
            title="Verification successful",
            description="Welcome to **{}**".format(member.guild.name)
        )
        embed.set_thumbnail(url=member.guild.icon_url)
        embed.set_footer(
            text="Sharbull Security Guard",
            icon_url="https://cdn0.iconfinder.com/data/icons/small-n-flat/24/678094-shield-512.png"
        )
        await member.dm_channel.send(embed=embed)
        await member.add_roles(member.guild.get_role(verified_role_id))
    os.remove("captcha/" + str(member.id) + ".png")


@bot.command()
async def help(ctx, page: str = None):
    footer = "Sharbull Security - Developed by 647"
    icon_url = "https://cdn0.iconfinder.com/data/icons/small-n-flat/24/678094-shield-512.png"
    if page == "commands":
        title = "About the commands",
        description = "``!!setup`` : Open minimum configuration menu\n - Permission required : administrator\n\n"
        "``!!mute <Member>`` : Mute a member and report their account to the Sharbull database\n - Permission required : mute members\n\n"
        "``!!kick <Member>`` : Kick a member and report their account to the Sharbull database\n - Permission required : kick members\n\n"
        "``!!ban <Member>`` : Ban a member and report their account to the Sharbull database\n - Permission required : ban members\n\n" \
        "``!!report <Member> <reason>`` : Report an account to the server and to the Sharbull database\n - Permission required : None\n\n"

    elif page == "security":
        title = "About the security"
        description = "Sharbull automatically detects if an account is fake or likely to be a " \
                      "selfbot by checking their avatar, creation date, user flags and reports. " \
                      "With this data, a trust score is calculated and further actions may be taken." \
                      "An antispam is also included, which automatically flags the user. Depending on their trust " \
                      "score, they may get muted, kicked or even banned. "
    else:
        title = "Welcome to Sharbull Security Bot!"
        description = "Sharbull is a ready to use bot deployable in minutes, aimed to filter out " \
                      "selfbot accounts by detecting fake accounts and using a captcha system. " \
                      "With its built-in anti-spam filter this bot will also rate limit humans who flood the chat, as " \
                      "Sharbull has a strict policy on spammers and raiders, zero tolerance is not an option, it's mandatory.\n" \
                      "Our bot is using a shared database across all servers in order to detect toxic people before they even " \
                      "join your server.\n\n" \
                      "If you are a server administrator, you can start by using the command ``!!setup``\n" \
                      "Take a look at other commands by sending ``!!help commands`` or ``!!help security``"

    embed = discord.Embed(title=title, description=description)
    embed.set_footer(text=footer, icon_url=icon_url)
    await ctx.send(embed=embed)


@commands.bot_has_permissions(administrator=True)
@commands.has_permissions(administrator=True)
@commands.guild_only()
@bot.command()
async def setup(ctx):
    add_guild(ctx.guild.id)
    log_channel_id, verified_role_id, captcha_level, security_activated = check_guild_setup(ctx.guild.id)
    log_emoji = "✅ " if log_channel_id is not None else "❌ "
    verified_emoji = "✅ " if verified_role_id is not None else "❌ "
    captcha_emoji = "✅ " if captcha_level is not None else "❌ "
    activated_emoji = "✅ " if security_activated is not None else "❌ "
    embed = discord.Embed(title="Welcome to Sharbull Security Bot!",
                          description="In order to initially setup Sharbull, you will have to execute a few steps:\n\n" +
                                      "**1.** " + log_emoji + "``!!set_log_channel`` in a text channel you want the logs to be posted in.\n\n" +
                                      "**2.** " + verified_emoji + "``!!set_verified_role @a_role`` replace @a_role by the role you want users to get when they get approved by the bot\n\n" +
                                      "**3.** Edit channels permissions to restrict access to Verified users only.\n\n" +
                                      "**4.** " + captcha_emoji + "``!!set_captcha_level <level (1, 2, or 3)>`` to setup captcha policy (learn more with ``!!help security``\n" +
                                      " > Level ``1`` : No captcha verification\n" +
                                      " > Level ``2`` : Captcha verification for suspicious users only\n" +
                                      " > Level ``3`` : Captcha verification for everyone\n\n" +
                                      "**5.** " + activated_emoji + "``!!activate`` to start security services"
                          )
    await ctx.send(embed=embed)


@commands.bot_has_permissions(administrator=True)
@commands.has_permissions(administrator=True)
@commands.guild_only()
@bot.command()
async def set_log_channel(ctx):
    add_guild(ctx.guild.id)
    set_guild_setting(ctx.guild.id, new_log_channel_id=ctx.channel.id)
    message = "✅ {.mention} is now your logging channel".format(ctx.channel)
    embed = discord.Embed(description=message)
    await ctx.send(embed=embed)


@commands.bot_has_permissions(administrator=True)
@commands.has_permissions(administrator=True)
@commands.guild_only()
@bot.command()
async def set_verified_role(ctx, role: discord.Role):
    add_guild(ctx.guild.id)
    set_guild_setting(ctx.guild.id, new_verified_role_id=role.id)
    message = "✅ {.mention} is now your verified role".format(role)
    embed = discord.Embed(description=message)
    await ctx.send(embed=embed)


@commands.bot_has_permissions(administrator=True)
@commands.has_permissions(administrator=True)
@commands.guild_only()
@bot.command()
async def set_captcha_level(ctx, level: int):
    add_guild(ctx.guild.id)
    if level < 1:
        level = 1
    if level > 3:
        level = 3
    set_guild_setting(ctx.guild.id, new_captcha_level=level)
    message = "✅ Captcha level has been set to **{}**".format(level)
    embed = discord.Embed(description=message)
    await ctx.send(embed=embed)


@commands.bot_has_permissions(administrator=True)
@commands.has_permissions(administrator=True)
@commands.guild_only()
@bot.command()
async def activate(ctx):
    log_channel_id, verified_role_id, captcha_level, security_activated = check_guild_setup(ctx.guild.id)

    if log_channel_id is None or verified_role_id is None or captcha_level is None:
        message = "⚠️Please perform the initial steps to setup your protection (``!!setup``)"
        embed = discord.Embed(description=message)
        await ctx.send(embed=embed)
    else:
        set_guild_setting(ctx.guild.id, new_security_activated=True)
        message = "✅ Protection is now enabled"
        embed = discord.Embed(description=message)
        await ctx.send(embed=embed)


@commands.bot_has_permissions(administrator=True)
@commands.has_permissions(mute_members=True)
@commands.guild_only()
@bot.command()
async def mute(ctx, member: discord.Member):
    log_channel_id, verified_role_id, captcha_level, security_activated = check_guild_setup(ctx.guild.id)
    await member.remove_roles(ctx.guild.get_role(verified_role_id))
    message = "✅ Member {.mention} has been muted (removed {.mention})".format(member,
                                                                               ctx.guild.get_role(verified_role_id))
    embed = discord.Embed(description=message)
    await ctx.send(embed=embed)
    increase_user_flag(user_id=member.id, mutes_to_add=1)
    await log(ctx.guild.get_channel(log_channel_id), message)


@commands.bot_has_permissions(administrator=True)
@commands.has_permissions(kick_members=True)
@commands.guild_only()
@bot.command()
async def kick(ctx, member: discord.Member):
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
@bot.command()
async def ban(ctx, member: discord.Member):
    log_channel_id, verified_role_id, captcha_level, security_activated = check_guild_setup(ctx.guild.id)
    message = "✅ Member {.mention} has been banned".format(member)
    embed = discord.Embed(description=message)
    await ctx.send(embed=embed)
    await member.ban()
    increase_user_flag(user_id=member.id, bans_to_add=1)
    await log(ctx.guild.get_channel(log_channel_id), message)


@commands.bot_has_permissions(administrator=True)
@commands.has_permissions(ban_members=True)
@commands.guild_only()
@bot.command()
async def report(ctx, member: discord.User, *, reason):
    await ctx.message.delete()
    log_channel_id, verified_role_id, captcha_level, security_activated = check_guild_setup(ctx.guild.id)
    message = "✅ Member {.mention} has been reported : ``{}``\nReporter : {.mention}".format(member, reason,
                                                                                             ctx.author.id)
    embed = discord.Embed(description=message)
    await ctx.author.send(embed=embed)
    increase_user_flag(user_id=member.id, reports_to_add=1)
    add_report(member.id, ctx.author.id, str(reason))
    await log(ctx.guild.get_channel(log_channel_id), message)


@bot.event
async def on_command_error(ctx, error):
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


bot.run(TOKEN)
