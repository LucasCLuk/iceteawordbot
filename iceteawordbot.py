import json
import traceback

import raven
from discord.ext import commands
from raven_aiohttp import AioHttpTransport

bot = commands.Bot(command_prefix="!", case_insensitive=True)
bot.triggers = {}
extensions = ["triggers", "points"]


@bot.event
async def on_ready():
    if len(bot.triggers) == 0:
        with open("triggers.json") as triggers:
            bot.triggers = json.load(triggers)
    print("Ready!")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, (commands.BadArgument, commands.CheckFailure)):
        return
    sentry.capture('raven.events.Message', message=str(getattr(error, "original", error)), extra={
        'command': ctx.invoked_with,
        "user": str(ctx.author),
        "traceback": traceback.format_tb(error.__traceback__),
        "args": ctx.args[2:]
    })


@bot.event
async def on_message(message):
    if not message.author.bot or message.guild is None:
        ctx = await bot.get_context(message)
        if ctx.valid:
            return await bot.invoke(ctx)
        for word in bot.triggers:
            if word.lower() in message.content.lower():
                await message.channel.send(bot.triggers[word])


with open("config.json") as file:
    data = json.load(file)
    token = data['token']
    sentry = raven.Client(transport=AioHttpTransport, dsn=data['sentry'])

for ext in extensions:
    bot.load_extension(ext)

bot.run(token)
