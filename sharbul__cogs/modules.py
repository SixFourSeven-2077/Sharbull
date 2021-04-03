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