import discord
from discord.ext import commands


class NoAttachmentsFound(commands.CheckFailure):
    pass


def require_attachment():
    def predicate(ctx: commands.Context):
        if ctx.message.attachments:
            return True
        else:
            raise NoAttachmentsFound()

    return commands.check(predicate)


class Administration(commands.Cog):

    async def cog_check(self, ctx):
        return discord.utils.get(ctx.author.roles,
                                 name="ThankBotAdmin") or await ctx.bot.is_owner(ctx.author)

    async def cog_command_error(self, ctx, error):
        error = getattr(error, "original", error)
        if isinstance(error, NoAttachmentsFound):
            return await ctx.send("I could not get any data, did you upload an attachment?")

    @commands.group(name="import")
    @require_attachment()
    async def import_command(self, ctx: commands.Context):
        """Replaces the current database being used with the one uploaded. Make sure to back up before you do this"""
        pass

    @import_command.command(name="triggers")
    async def import_triggers(self, ctx: commands.Context):
        ctx.bot.unload_extension("triggers")
        await ctx.message.attachments[0].save("triggers.json")
        ctx.bot.load_extension("triggers")
        await ctx.send("Imported Successfully")
        pass

    @import_command.command(name="points")
    async def import_points(self, ctx: commands.Context):
        ctx.bot.unload_extension("points")
        await ctx.message.attachments[0].save("points.json")
        ctx.bot.load_extension("points")
        await ctx.send("Imported Successfully")
        pass

    @commands.group(name="export")
    async def export_command(self, ctx: commands.Context):
        """Exports the chosen database"""
        pass

    @export_command.command(name="triggers")
    async def export_triggers(self, ctx: commands.Context):
        try:
            return await ctx.send(file=discord.File("triggers.json"))
        except:
            pass

    @export_command.command(name="points")
    async def export_points(self, ctx: commands.Context):
        try:
            return await ctx.send(file=discord.File("points.json"))
        except:
            pass

    @commands.command()
    async def nick(self, ctx, newnick):
        await ctx.me.edit(nick=newnick)
        await ctx.send("Success!")

    @commands.command()
    async def reload(self, ctx, target: str):
        ctx.bot.reload_extension(target)
        await ctx.send("\U0001f44d")

    @commands.command()
    async def unload(self, ctx, target: str):
        ctx.bot.unload_extension(target)
        await ctx.send("\U0001f44d")

    @commands.command()
    async def load(self, ctx, target: str):
        ctx.bot.load_extension(target)
        await ctx.send("\U0001f44d")


def setup(bot):
    bot.add_cog(Administration())
