import json

import discord
from discord.ext import commands


class Triggers:
    def __init__(self, bot):
        self.bot = bot
        with open("triggers.json") as triggers_files:
            try:
                self.triggers = json.load(triggers_files)
            except:
                self.triggers = {}

    async def __local_check(self, ctx):
        permissions = ctx.channel.permissions_for(ctx.me)
        has_role = discord.utils.get(ctx.author.roles, name="Iceteabot Admin")
        return any([all([has_role, permissions.send_messages]), ctx.author.id == 92730223316959232])

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
            with open("triggers.json") as add_file:
                new_dict = json.load(add_file)
                new_dict[word.lower()] = response
                self.triggers[word.lower()] = response
            with open("triggers.json", "w") as save_file:
                json.dump(self.triggers, save_file)
                await ctx.send("Successfully added trigger")
        except Exception as e:
            print(e)

    @trigger.command()
    async def remove(self, ctx, *, word):
        try:
            with open("triggers.json") as add_file:
                new_dict = json.load(add_file)
                del new_dict[word.lower()]
                del self.triggers[word.lower()]
                with open("triggers.json", "w") as save_file:
                    json.dump(self.triggers, save_file)
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

    @commands.command()
    async def nick(self, ctx, newnick):
        await ctx.me.edit(nick=newnick)
        await ctx.send("Success!")

    @commands.command()
    async def reload(self, ctx, target: str):
        ctx.bot.unload_extension(target)
        ctx.bot.load_extension(target)
        await ctx.send("\U0001f44d")


def setup(bot):
    bot.add_cog(Triggers(bot))
