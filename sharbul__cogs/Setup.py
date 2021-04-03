import discord
from discord.ext import commands
from sharbull__db.main import *


class SetupCommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.bot_has_permissions(administrator=True)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    @commands.command()
    async def setup(self, ctx):
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
    @commands.command()
    async def set_log_channel(self, ctx):
        add_guild(ctx.guild.id)
        set_guild_setting(ctx.guild.id, new_log_channel_id=ctx.channel.id)
        message = "✅ {.mention} is now your logging channel".format(ctx.channel)
        embed = discord.Embed(description=message)
        await ctx.send(embed=embed)

    @commands.bot_has_permissions(administrator=True)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    @commands.command()
    async def set_verified_role(self, ctx, role: discord.Role):
        add_guild(ctx.guild.id)
        set_guild_setting(ctx.guild.id, new_verified_role_id=role.id)
        message = "✅ {.mention} is now your verified role".format(role)
        embed = discord.Embed(description=message)
        await ctx.send(embed=embed)

    @commands.bot_has_permissions(administrator=True)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    @commands.command()
    async def set_captcha_level(self, ctx, level: int):
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
    @commands.command()
    async def activate(self, ctx):
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
