import discord
from discord.ext import commands
from sharbull__db.main import *
from sharbull__utility.main import log, get_prefix, return_info
import string


class UserCommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx, page: str = None):
        footer = "Sharbull Security - Developed by 647"
        icon_url = "https://cdn0.iconfinder.com/data/icons/small-n-flat/24/678094-shield-512.png"
        prefix = get_prefix(self, ctx.message)
        if page == "commands":
            title = "About the commands"
            description = "".join(("``",prefix,"setup`` : Open minimum configuration menu\n - Permission required : administrator\n\n",
            "``",prefix,"mute <Member>`` : Mute a member and report their account to the Sharbull database\n - Permission required : mute members\n\n",
            "``",prefix,"kick <Member>`` : Kick a member and report their account to the Sharbull database\n - Permission required : kick members\n\n",
            "``",prefix,"ban <Member>`` : Ban a member and report their account to the Sharbull database\n - Permission required : ban members\n\n",
            "``",prefix,"alert`` : Toggles ALERT mode (any spamming member will be banned without a warning)\n - Permission required : ban members\n\n",
            "``",prefix,"report <Member> <reason>`` : Report an account to the server and to the Sharbull database\n - Permission required : None\n\n",
            "``",prefix,"flags <Member (optional)>`` : Get the public flags of the user\n - Permission required : None\n\n",
            "``",prefix,"status`` : See the enabled protection features on this server\n - Permission required : None\n\n",
            "``",prefix,"set_prefix <prefix>`` : Sets a new prefix for this bot\n - Permission required : administrator\n\n",
            "You can also tag me instead of using the prefix"))

        elif page == "security":
            title = "About the security"
            description = "".join(("**Automatic flagging**\nSharbull automatically detects if an account is fake or likely to be a ",
                          "selfbot by checking their avatar, creation date, user flags and reports. ",
                          "With this data, a trust score is calculated and further actions may be taken :\n\n",
                          "**Captcha**\nCaptchas are widely used everywhere and have proven to be effective against selfbots, ",
                          "and Sharbull uses 3 levels of protection : \n",
                          "- Level One : Users can join your server without having to complete a challenge.\n",
                          "- Level Two : By looking at the user's flags, Sharbull enables or not the challenge for a suspicious user.\n",
                          "- Level Three : Everyone including clean users will have to complete a challenge.\n\n",
                          "**AntiSpam**\n","An antispam is also included, which automatically flags the user. Depending on their trust ",
                          "score, they may get muted, kicked or even banned.\n\n",
                          "**ALERT mode**\n", "When you enable alert mode, any spamming member will be banned without a warning. ",
                          "(*Sharbull protection services must be enabled first*) ",
                          "Alert mode is automatically enabled when a member reaches the spamming ban treshold. If you want the bot to ignore ",
                          "a channel, block the Read Messages permission of this channel to Sharbull."))
        else:
            title = "Welcome to Sharbull Security Bot!"
            description = "".join(("**What is this bot?**\nSharbull is a ready to use bot deployable in minutes, aimed to filter out ",
                          "selfbot accounts by detecting fake accounts and using a captcha system. ",
                          "With its built-in anti-spam filter this bot will also rate limit humans who flood the chat, as ",
                          "Sharbull has a strict policy on spammers and raiders, zero tolerance is not an option, it's mandatory.\n",
                          "Our bot is using a shared database across all servers in order to detect toxic people before they even ",
                          "join your server.\n\n",
                          "**Main features** \n",
                          "- Togglable Captcha for joining members\n",
                          "- Shared reputation system between all servers\n",
                          "- AntiSpam operating according to the user's rep\n",
                          "- Selfbots detection and flagging system\n\n",
                          "**Usage**\n",
                          "If you are a server administrator and would like to use this bot, start now by using the command ``",prefix,"setup``\n",
                          "Take a look at other commands by sending ``",prefix,"help commands`` or ``",prefix,"help security``\n",
                          "Question? Concerns? Contest a bad reputation? Get the support server link by sending ``",prefix,"support``\n\n",
                          "You can also tag me instead of using the prefix"))

        embed = discord.Embed(title=title, description=description)
        embed.set_footer(text=footer, icon_url=icon_url)
        await ctx.send(embed=embed)

    @commands.cooldown(1, 30, commands.BucketType.guild)
    @commands.guild_only()
    @commands.command()
    async def report(self, ctx, member: discord.User, *args):
        await ctx.message.delete()
        log_channel_id, verified_role_id, captcha_level, security_activated = check_guild_setup(ctx.guild.id)
        message = "✅ Member {.mention} has been reported : ``Reason : {}``\nReporter : {.mention}".format(member, ' '.join(word[0] for word in args),
                                                                                                 ctx.author)
        embed = discord.Embed(description=message)
        await ctx.author.send(embed=embed)
        increase_user_flag(user_id=member.id, reports_to_add=1)
        add_report(member.id, ctx.author.id, str(' '.join(word[0] for word in args)))
        if ctx.guild.get_channel(log_channel_id) is not None:
            await log(ctx.guild.get_channel(log_channel_id), message)

    @commands.command()
    async def support(self, ctx):
        message = "✉️ Get support here : https://discord.gg/RKURYUeX6t"
        embed = discord.Embed(description=message)
        await ctx.send(embed=embed)

    @commands.cooldown(1, 30, commands.BucketType.guild)
    @commands.command()
    async def flags(self, ctx, member:discord.Member = None):
        if member is None:
            member = ctx.author
        add_user(member.id)
        message, trust_score = return_info(member)
        embed = discord.Embed(title="Flags information for user {.name}".format(member),
                              description=message)
        await ctx.send(embed=embed)

    @commands.cooldown(1, 30, commands.BucketType.guild)
    @commands.command()
    async def status(self, ctx):
        log_channel_id, verified_role_id, captcha_level, security_activated = check_guild_setup(ctx.guild.id)
        is_alert = False
        if captcha_level is None:
            captcha_level = 0
        if security_activated is None:
            security_activated = False
        with open('config/alerts.json', 'r') as f:
            alerts = json.load(f)
        try:
            is_alert = alerts[str(ctx.guild.id)]
        except:
            pass

        verified_role = ctx.guild.get_role(verified_role_id)
        is_alert_emoji = "✅ " if is_alert is not False else "❌ "
        verified_emoji = "✅ " if verified_role is not None else "❌ "
        captcha_emoji = "✅ " if captcha_level != 0 else "❌ "
        activated_emoji = "✅ " if security_activated is True else "❌ "

        if verified_role is not None:
            verified_role_fmt = verified_role.mention
        else:
            verified_role_fmt = "No role"
        message = "".join((verified_emoji, "Verified role: ", verified_role_fmt, "\n",
                           captcha_emoji, "Captcha verification level : ", str(captcha_level),"\n",
                           activated_emoji,"Protection enabled : ", str(security_activated), "\n",
                           is_alert_emoji,"ALERT mode enabled : ", str(is_alert)))
        embed = discord.Embed(title="{}'s status".format(ctx.guild.name),
                              description=message)
        await ctx.send(embed=embed)




