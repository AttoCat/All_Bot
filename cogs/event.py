import discord
from discord.ext import commands


class Event(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.guild = self.bot.get_guild(711374787892740148)
        self.dev = self.guild.get_member(602668987112751125)
        self.rank = self.guild.get_channel(713389883569340436)

    @commands.command()
    async def devdm(self, ctx, naiyou):
        embed = discord.Embed(
            title="メッセージが届きました！",
            description=(
                f"{naiyou}\n送信者:{ctx.author}"),
            color=0x4169e1)
        await self.dev.send(embed=embed)
        embed = discord.Embed(
            title="Done.",
            description=(
                f"正常に送信しました。\nMessage sent successfully. "),
            color=0x4169e1)
        await ctx.channel.send(embed=embed, delete_after=10)
        await ctx.message.delete()

    @commands.Cog.listener()
    async def on_message(self, message):
        mee6 = self.guild.get_member(159985870458322944)
        if message.channel == self.rank:
            if message.author == mee6:
                return
            elif not message.content.startswith("!rank"):
                await message.delete()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        ch = self.guild.get_channel(711375652107976847)
        rule = self.guild.get_channel(711379195992997949)
        yaku = self.guild.get_channel(712410294496002090)
        naiyou = (
            f"{member.mention}さんようこそBOTのすべてへ！\nまずは{rule.mention}でルールを確認し、同意する場合は{yaku.mention}でその他の役職をもらいましょう！")
        embed = discord.Embed(
            title=(f"{member}さんが参加しました！"),
            description=naiyou,
            color=0x3aee67)
        await ch.send(embed=embed)


def setup(bot):
    bot.add_cog(Event(bot))