import json

import discord
from discord.ext import commands


class Triggers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        try:
            with open("data/triggers.json", "r") as triggers_files:
                try:
                    self.triggers = json.load(triggers_files)
                except:
                    self.triggers = {}
        except FileNotFoundError:
            self.triggers = {}

    async def cog_check(self, ctx):
        permissions = ctx.channel.permissions_for(ctx.me)
        has_role = discord.utils.get(ctx.author.roles, name="Iceteabot Admin")
        return any([all([has_role, permissions.send_messages]), ctx.author.id == 92730223316959232])


    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.author.bot:
            for word in self.triggers:
                if word.lower() in message.content.lower():
                    await message.channel.send(self.triggers[word])

    @commands.group()
    async def trigger(self, ctx):
        pass

    @trigger.command()
    async def add(self, ctx, word, *, response):
        try:
            with open("triggers.json", "w+") as file:
                new_dict = json.load(file)
                new_dict[word.lower()] = response
                self.triggers[word.lower()] = response
                json.dump(self.triggers, file)
                await ctx.send("Successfully added trigger")
        except Exception as e:
            print(e)
            await ctx.send(e, delete_after=10)

    @trigger.command()
    async def remove(self, ctx, *, word):
        try:
            with open("triggers.json", "w+") as file:
                new_dict = json.load(file)
                del new_dict[word.lower()]
                del self.triggers[word.lower()]
                json.dump(self.triggers, file)
                await ctx.send("Successfully removed trigger")
        except Exception as e:
            print(e)

    @trigger.command(name="list")
    async def tlist(self, ctx):
        if len(self.triggers) > 0:
            template = "**{0}** - {1}\n"
            await ctx.send("".join([template.format(word, response) for word, response in self.triggers.items()]))
        else:
            await ctx.send("No triggers")


def setup(bot):
    bot.add_cog(Triggers(bot))
