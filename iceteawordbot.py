import json
import traceback

from discord.ext import commands

bot = commands.Bot(command_prefix="!", case_insensitive=True)
extensions = ["triggers", "points", "administration"]


@bot.event
async def on_ready():
    print("Ready!")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, (commands.BadArgument, commands.CheckFailure)):
        return
    if sentry:
        sentry.capture('raven.events.Message', message=str(getattr(error, "original", error)), extra={
            'command': ctx.invoked_with,
            "user": str(ctx.author),
            "traceback": traceback.format_tb(error.__traceback__),
            "args": ctx.args[2:]
        })


with open("config.json") as file:
    data = json.load(file)
    token = data['token']
    sentry = None

for ext in extensions:
    bot.load_extension(ext)

if __name__ == '__main__':
    bot.run(token)
