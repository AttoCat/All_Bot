import discord
from discord.ext import commands
import random


class Play(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["mr"])
    @commands.is_owner()
    async def memberandom(self, ctx):
        checklist = []
        guild = self.bot.get_guild(711374787892740148)
        bots = guild.get_role(711377288272412723)
        member = guild.members
        for check in member:
            if bots in check.roles:
                continue
            checklist.append(check.discriminator)
        content = random.choice(checklist)
        embed = discord.Embed(
            title=(f"抽選結果"),
            description=f"今回選ばれたのは||{content}||番のユーザーです！",
            color=0x3aee67)
        await ctx.message.delete()
        await ctx.send(embed=embed)

    @commands.command(aliases=["gd"])
    @commands.is_owner()
    async def userdiscriminator(self, ctx, dis: str):
        guild = self.bot.get_guild(711374787892740148)
        member = discord.utils.get(guild.members, discriminator=dis)
        if member == None:
            raise commands.BadArgument()
        else:
            await ctx.message.delete()
            await ctx.send(str(member))

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.NotOwner):
            embed = discord.Embed(
                title="Error",
                description=(
                    f"あなたにこのコマンドを実行する権限がありません！\nYou don't have permission."),
                color=0xff0000)
            await ctx.message.delete()
            await ctx.channel.send(embed=embed, delete_after=10)
            return
        elif isinstance(error, commands.BadArgument):
            embed = discord.Embed(
                title="Error",
                description=(
                    f"不正な引数です！\nInvalid argument passed."),
                color=0xff0000)
            await ctx.message.delete()
            await ctx.channel.send(embed=embed, delete_after=10)
            return
        else:
            embed = discord.Embed(
                title="Error",
                description=(
                    f"不明なエラーが発生しました。\nエラー内容:\n{error}"),
                color=0xff0000)
            await ctx.message.delete()
            await ctx.channel.send(embed=embed, delete_after=10)
            return


def setup(bot):
    bot.add_cog(Play(bot))