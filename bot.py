import os
import sys
import traceback

import discord
import psutil
from discord.ext import commands
from raven import Client
from raven_aiohttp import AioHttpTransport

client = Client(transport=AioHttpTransport)

bot = commands.Bot(command_prefix=commands.when_mentioned_or(os.getenv('discord_prefix', "!")), case_insensitive=True)
extensions = ["triggers", "points", "administration"]


@bot.event
async def on_ready():
    print(f"Successfully logged in as {bot.user}\n" +
          f"Using version {discord.__version__} of discord.py\n" +
          f"Using {psutil.Process().memory_full_info().uss / 1024 ** 2} of ram\n" +
          f"loaded {len(bot.extensions)} cogs\n" +
          f"{'-' * 15}")


@bot.event
async def on_command_error(ctx, error):
    error = getattr(error, "original", error)
    if isinstance(error, (commands.BadArgument, commands.CheckFailure)):
        return
    if sentry_token:
        client.capture('raven.events.Message', message=str(error), extra={
            'command': ctx.invoked_with,
            "user": str(ctx.author),
            "traceback": traceback.format_tb(error.__traceback__),
            "args": ctx.args[2:]
        })
    else:
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


token = os.getenv('discord_token')
sentry_token = os.getenv('sentry_token')

for ext in extensions:
    bot.load_extension(ext)

if __name__ == '__main__':
    bot.run(token)
