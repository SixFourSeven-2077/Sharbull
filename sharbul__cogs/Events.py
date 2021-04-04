import discord
from discord.ext import commands
from sharbull__utility.main import seconds_to_text, seconds_to_dhms, log
from sharbull__db.main import *
from sharbul__cogs import Tasks
from colorama import Fore, Style, init
from datetime import datetime, timedelta
from captcha import image
import random
import string
import asyncio
import os
from AntiSpam import AntiSpamHandler
from AntiSpam.ext import AntiSpamTracker


class EventsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(Fore.GREEN + Style.BRIGHT +
              'Successfully connected. [{}]'.format(self.bot.user))
        pingms = round(self.bot.latency * 1000)
        print("Commander's latency : " + Fore.YELLOW +
              "{}".format(pingms) + Fore.GREEN + "ms\n" + Style.RESET_ALL)

        if len(self.bot.guilds) < 20:
            for server in self.bot.guilds:
                print(server.name,server.id)
        Tasks.BackgroundTasks.update_presence.start(self)



    @commands.Cog.listener()
    async def on_message(self, message):
        msg = message
        add_user(message.author.id)
        await self.bot.handler.propagate(message)
        if self.bot.tracker.is_spamming(message):
            log_channel_id, verified_role_id, captcha_level, security_activated = check_guild_setup(message.guild.id)
            points = calculate_reputation(message.author.id)
            message_log = "User {.mention}".format(msg.author) + " - Bad Reputation points : " + str(points) + "\n"
            if points <= 3:
                message_log += "User has been warned"
                description = "{.mention} : stop spamming".format(msg.author)
                increase_user_flag(user_id=msg.author.id, reports_to_add=1)
            elif points <= 10:
                message_log += "User has been muted (removed verified role)"
                description = "{.mention} has been muted for spamming".format(message.author)
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
            if security_activated is not None:
                await msg.channel.send(embed=embed)
            if msg.guild.get_channel(log_channel_id) is not None:
                await log(msg.guild.get_channel(log_channel_id), message_log)
            self.bot.tracker.remove_punishments(message)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        now = datetime.now().strftime("%Y %m %d - %H:%M:%S")
        print(now, "New captcha started for", member.id)
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
            if member.guild.get_role(verified_role_id) is not None:
                await member.add_roles(member.guild.get_role(verified_role_id))
            return True
        if captcha_level == 1:
            await log(member.guild.get_channel(log_channel_id), "Captcha level is set to ONE, skipped")
            if member.guild.get_role(verified_role_id) is not None:
                await member.add_roles(member.guild.get_role(verified_role_id))
            return True

        string_to_guess = ""
        for char in range(6):
            char = random.choice(string.ascii_lowercase)
            string_to_guess += char
        image_data = image.ImageCaptcha(width=280, height=90).generate_image(string_to_guess)
        image_data.save("captcha/" + str(member.id) + ".png")
        embed = discord.Embed(title="Greetings, welcome to **{}**".format(member.guild.name),
                              description="Please complete the following captcha to continue.\n" +
                                          "You have **60** seconds to reply or your access will be denied." +
                                          "\nTHERE ARE ONLY **LOWERCASE** LETTERS (no numbers)."  # in bold because ppl cant read
                              )
        embed.set_thumbnail(url=member.guild.icon_url)
        embed.set_footer(
            text="Sharbull Security Guard - This server enforces a high security verification",
            icon_url="https://cdn0.iconfinder.com/data/icons/small-n-flat/24/678094-shield-512.png"
        )
        file = discord.File("captcha/" + str(member.id) + ".png", filename="image.png")
        embed.set_image(url="attachment://image.png")
        await member.send(
            embed=embed,
            file=file
        )

        #await member.send(file=discord.File("captcha/" + str(member.id) + ".png"))

        def check(message):
            return message.content == string_to_guess and message.channel == message.author.dm_channel

        try:
            message = await self.bot.wait_for('message', timeout=60.0, check=check)
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