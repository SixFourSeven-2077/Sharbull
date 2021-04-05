import discord
from discord.ext import commands
from sharbull__utility.main import seconds_to_text, seconds_to_dhms, log, return_info
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
            increase_user_flag(user_id=msg.author.id, reports_to_add=1, bypass_cooldown=True)
            alert_activated = False
            with open('config/alerts.json', 'r') as f:
                alerts = json.load(f)
            try:
                alert_activated = alerts[str(message.guild.id)]
                if alert_activated is False:
                    pass
                else:
                    points = 99
            except:
                pass

            message_log = "User {.mention}".format(msg.author) + " - Bad Reputation points : " + str(points) + "\n"
            if points <= 3:
                message_log += "User has been warned"
                description = "{.mention} : stop spamming - warns before mute : {}".format(msg.author, 3-points)
            elif points <= 6:
                message_log += "User has been muted (removed verified role)"
                description = "{.mention} has been muted for spamming - warns before kick : {} ".format(message.author, 6-points)
                await msg.author.remove_roles(msg.guild.get_role(verified_role_id))
                increase_user_flag(user_id=msg.author.id, mutes_to_add=1)
            elif points <= 9:
                message_log += "User has been kicked"
                description="{.mention} has been kicked for spamming - warns before ban : {}".format(msg.author, 12-points)
                increase_user_flag(user_id=msg.author.id, kicks_to_add=1)
                await msg.author.kick(reason="Spamming")
            else:
                alert_message = ""
                if alert_activated is True:
                    alert_message = "- ALERT Mode is activated"

                message_log += "User has been banned"
                description="{.mention} has been banned for spamming {} - **ALERT mode has been enabled**, any spamming member will be banned without a warning".format(msg.author, alert_message)
                alerts[str(message.guild.id)] = True
                with open('config/alerts.json', 'w') as f:
                    json.dump(alerts, f, indent=4)

                await msg.author.ban(reason="Spamming", delete_message_days=1)
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


        message = "**New member joined** : " + member.mention + "\n"

        message, trust_score = return_info(member, message)

        await log(member.guild.get_channel(log_channel_id), message)


        if captcha_level == 2 and trust_score > 9:
            await log(member.guild.get_channel(log_channel_id), "{.mention}'s trust score is high enough, captcha skipped".format(member))
            if member.guild.get_role(verified_role_id) is not None:
                await member.add_roles(member.guild.get_role(verified_role_id))
            return True
        if captcha_level == 1:
            await log(member.guild.get_channel(log_channel_id), "Captcha is disabled, skipped verification")
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
        try:
            await member.send(
                embed=embed,
                file=file
            )
        except:
            if log_channel_id is not None:
                message = ("⚠️ Error! Could not send captcha verification, {.mention}'s DM are closed. User is waiting for manual approval.".format(
                    member
                ))
                await log(member.guild.get_channel(log_channel_id), message)
                return False
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
            try:
                await member.dm_channel.send(embed=embed)
            except:
                if log_channel_id is not None:
                    message = ("⚠️ Error! Could not send captcha verification, {.mention}'s DM are closed.".format(
                        member
                    ))
                    await log(member.guild.get_channel(log_channel_id), message)
            await member.add_roles(member.guild.get_role(verified_role_id))
        os.remove("captcha/" + str(member.id) + ".png")