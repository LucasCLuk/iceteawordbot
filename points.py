import json
import typing

import discord
from discord.ext import commands, tasks


def thankbot():
    def predicate(ctx):
        return discord.utils.get(ctx.author.roles, name="ThankBotAdmin") or ctx.author.id == 92730223316959232

    return commands.check(predicate)


class MyUser:

    def __init__(self, **kwargs):
        self._points = kwargs.get("points", 0)
        self._tokens = kwargs.get("tokens", 0)
        self.users_thanked = kwargs.get("users_thanked", [])

    @property
    def points(self):
        return round(self._points, 2)

    @points.setter
    def points(self, value):
        self._points = value

    @property
    def tokens(self):
        return round(self._tokens, 2)

    @tokens.setter
    def tokens(self, value):
        self._tokens = value

    @property
    def serialize(self) -> dict:
        return {"points": self._points, "tokens": self._tokens, "users_thanked": self.users_thanked}

    def can_thank(self, target_id: int) -> bool:
        return self.tokens - 1 > -1 and target_id not in self.users_thanked

    def refresh(self, max_tokens, lose_points):
        self.users_thanked = []
        self.tokens = max_tokens
        if self.points - lose_points < 0:
            self.points = 0
        else:
            self.points -= lose_points

    def thank_user(self, target_id, target):
        self.users_thanked.append(target_id)
        self.tokens -= 1
        target.points += 1


class Points(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        try:
            with open("data/points.json", "r") as file:
                try:
                    self.data = json.load(file)
                except:
                    self.data = {}
        except FileNotFoundError:
            self.data = {}
        if self.data:
            self.users = {int(uid): MyUser(**data) for uid, data in
                          self.data.pop("users").items()}  # type: typing.Dict[str,MyUser]
        else:
            self.users = {}
        self.database_manager.start()

    def cog_unload(self):
        self.database_manager.cancel()

    async def cog_check(self, ctx):
        return ctx.guild

    async def cog_command_error(self, ctx, error):
        pass

    @property
    def maxtokens(self):
        return self.data.get('max_tokens')

    @maxtokens.setter
    def maxtokens(self, value):
        self.data['max_tokens'] = value

    @property
    def losepoints(self):
        return self.data.get('lose_points')

    @losepoints.setter
    def losepoints(self, value):
        self.data['lose_points'] = value

    @property
    def maxpoints(self):
        return self.data.get('max_points')

    @maxpoints.setter
    def maxpoints(self, value):
        self.data['max_points'] = value

    async def on_member_remove(self, member: discord.Member):
        self.users.pop(member.id, None)
        self.save_database()

    def add_user(self, user_id) -> MyUser:
        self.users[user_id] = MyUser(tokens=self.maxtokens)
        self.save_database()
        return self.users[user_id]

    def thank_member(self, thanker_id, thankee_id):
        thanker = self.users.get(thanker_id)
        thankee = self.users.get(thankee_id)
        if thanker is not None and thankee is not None:
            if thanker.can_thank(thankee_id) and thanker.points + 1 < self.maxpoints:
                thanker.thank_user(thankee_id, thankee)
                return True
            else:
                return False
        return False

    def save_database(self):
        with open("points.json", "w+") as file:
            data = {
                "max_tokens": self.maxtokens,
                "lose_points": self.losepoints,
                "max_points": self.maxpoints,
                "users": {str(uid): data.serialize for uid, data in self.users.items()}
            }
            json.dump(data, file, indent=2)

    @tasks.loop(hours=24)
    async def database_manager(self):
        for user in self.users.values():
            user.refresh(self.maxtokens, self.losepoints)
            self.save_database()

    @database_manager.before_loop
    async def before_database_manager(self):
        await self.bot.wait_until_ready()

    @thankbot()
    @commands.command(name="maxtokens")
    async def max_tokens(self, ctx, amount: int = 5):
        async with ctx.typing():
            self.maxtokens = amount
            for user in self.users.values():
                user.tokens = user.tokens if user.tokens < amount else amount
            self.save_database()
            await ctx.send(":thumbsup:", delete_after=20)

    @thankbot()
    @commands.command(name="maxpoints")
    async def max_points(self, ctx, amount: int = 100):
        async with ctx.typing():
            self.maxpoints = amount
            for user in self.users.values():
                user.points = user.points if user.points < amount else amount
            self.save_database()
            await ctx.send(":thumbsup:", delete_after=20)

    @thankbot()
    @commands.command(name="losepoints")
    async def lose_points(self, ctx, amount: int = 0.2):
        async with ctx.typing():
            self.losepoints = amount
            self.save_database()
            await ctx.send(":thumbsup:", delete_after=20)

    @commands.command()
    async def thank(self, ctx, target: discord.Member = None):
        author = self.users.get(ctx.author.id)
        if target is None and author is None:
            author = self.add_user(ctx.author.id)
        target_data = self.users.get(target.id)
        if target_data is None:
            return await ctx.send("The member can not receive thank points, because they have not used !points yet.")
        if target == ctx.author:
            return await ctx.send("Cannot thank yourself!")
        try:
            thanked = self.thank_member(ctx.author.id, target.id)
        except:
            return await ctx.send("I could not find that member in my database :(")
        self.save_database()
        if thanked:
            try:
                await ctx.author.send(f"You awarded a token to {target}\n"
                                      f"You have {author.tokens} left")
            except:
                pass
            try:
                await target.send(f"You've received a Thank Point from {ctx.author}\n"
                                  f"You have {target_data.points} Total.")
            except:
                pass
        else:
            await ctx.send(f"You have already awarded a token to {target} for today.")

    @thank.error
    async def thank_error(self, ctx, error):
        error = getattr(error, "orginal", error)
        if isinstance(error, commands.BadArgument):
            await ctx.send("Unable to find member", delete_after=10)

    @commands.command()
    async def points(self, ctx):
        user_data = self.users.get(ctx.author.id)
        if user_data is None:
            user_data = self.add_user(ctx.author.id)
        try:
            await ctx.author.send(f"Your Thank Points total: **{user_data.points}**\n"
                                  f"You have **{user_data.tokens}** available to give\n"
                                  f"Use {ctx.prefix}thank @member to give someone a token")
        except:
            pass

    @commands.command(name="leaders")
    @commands.cooldown(10, 5)
    @thankbot()
    async def leaderboard(self, ctx):
        if not self.users:
            return await ctx.send("No data found")
        data = sorted(self.users, key=lambda user: self.users[user].points, reverse=True)[:20]

        def get_string(user):
            target = ctx.guild.get_member(user)
            return f"{target.display_name} : **{self.users[user].points}** Points"

        await ctx.send("\n".join([get_string(user) for user in data if ctx.guild.get_member(user)]))


def setup(bot):
    bot.add_cog(Points(bot))
