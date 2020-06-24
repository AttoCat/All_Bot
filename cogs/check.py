from janome.tokenizer import Tokenizer
from discord.ext import commands
import discord
import json
import csv
import pandas as pd
import aiofiles


class Check(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.guild = self.bot.get_guild(711374787892740148)
        self.dev = self.guild.get_member(602668987112751125)
        self.nsfw = self.guild.get_channel(713050662774112306)
        await self.ngword()

    async def ngword(self, ch=None, do=None, content=None):
        async with aiofiles.open('allbot.json', 'r') as ng:  # jsonファイルから暴言リストを読み込み
            data = await ng.read()
        scanlist = json.loads(data)
        self.scan = scanlist['henkoulist']
        self.t = Tokenizer(
            "dictionary.csv", udic_type="simpledic", udic_enc="utf8")
        channel = self.bot.get_channel(ch)
        if do == "print":
            print(self.scan)
            kekka = []
            num = 1
            for word in self.scan:
                kekka.append(f"{str(num)}：{word}")
                num += 1
            msg = "\n".join(kekka)
            embed = discord.Embed(
                title="現在のNGワードリスト",
                description=f"{msg}"
            )
            await channel.send(embed=embed, delete_after=10)
            return
        elif do == ("add" or "remove"):
            if do == "add":
                element = "に要素を追加"
                self.scan.append(content)
            else:
                element = "から要素を削除"
                try:
                    print(content)
                    self.scan.remove(content)
                except ValueError:
                    raise commands.BadArgument
            kekka = {'henkoulist': self.scan}
            async with aiofiles.open('allbot.json', 'w') as ng:  # 追加後のリストに内容を置き換え
                await ng.write(json.dumps(kekka, indent=4))  # 書き込み
            embed = discord.Embed(
                title="Done.",
                description=(
                    f"暴言リスト{element}しました。\nOperation complete."),
                color=0x4169e1)
            await channel.send(embed=embed)
            return

    @commands.group()
    @commands.has_role(713321552271376444)
    async def ng(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('このコマンドにはサブコマンドが必要です。')
            return

    @ng.command()
    async def add(self, ctx, content):
        await self.ngword(ch=ctx.channel.id, do="add", content=content)
        return

    @ng.command()
    async def remove(self, ctx, content: str):
        await self.ngword(ch=ctx.channel.id, do="remove", content=content)
        print(content)
        return

    @ng.command()
    async def print(self, ctx):
        await self.ngword(ch=ctx.channel.id, do="print", content=None)
        return

    async def userdict(self, msg, do=None):
        pass

    @commands.Cog.listener()
    async def on_message(self, message):
        member = message.author
        if member.bot:
            return
        elif message.content.startswith("ab!"):
            return
        moji = message.content
        kekka = self.t.tokenize(moji, wakati=True)
        for word in kekka:
            if word in self.scan:
                if message.channel == self.nsfw:
                    return
                kensyutu = kekka.index(word)
                normal = message.guild.get_role(
                    711375295172706313)  # ノーマルメンバー役職
                tyuui = message.guild.get_role(715809531829157938)  # 「注意」役職
                keikoku = message.guild.get_role(715809422148108298)  # 「警告」役職
                seigen = message.guild.get_role(714733639505543222)  # 「制限」役職
                await message.delete()
                embed = discord.Embed(
                    title="Message deleted",
                    description=f"NGワードが含まれていたため、削除しました。",
                    color=0xff0000)
                kensyutu = discord.Embed(
                    title="NGワードを検出",
                    description=f"送信者: {str(message.author)}\n内容:{message.content}",
                    color=0xff0000)
                await message.guild.get_channel(715142539535056907).send(embed=kensyutu)
                if tyuui in member.roles:  # 注意がある場合は警告に変更
                    await member.add_roles(keikoku)
                    await member.remove_roles(tyuui)
                elif keikoku in member.roles:  # 警告がある場合は制限付きに
                    await member.remove_roles(normal)
                    await member.add_roles(seigen)
                    await member.remove_roles(keikoku)
                else:  # 何も持っていなければ注意を
                    await member.add_roles(tyuui)
                await message.channel.send(
                    embed=embed)
                return

    @commands.command(aliases=['ks'])
    @commands.has_role(713321552271376444)
    async def kaiseki(self, ctx, naiyou):
        t = Tokenizer("dictionary.csv", udic_type="simpledic", udic_enc="utf8")
        moji = naiyou
        kekka = t.tokenize(moji, wakati=True)
        await ctx.channel.send(kekka)

    @commands.command(aliases=['da'])
    @commands.is_owner()
    async def dictadd(self, ctx, naiyou, yomi, hinsi):
        with open('dictionary.csv', 'a', encoding='utf8') as f:
            csv_writer = csv.writer(f, lineterminator='\n')
            csv_writer.writerow([naiyou, hinsi, yomi])
        embed = discord.Embed(
            title="Done.",
            description=(
                f"ユーザー辞書に要素を追加しました。\n現在のユーザー辞書は ab!dictprint で確認できます。\nAdd complete."),
            color=0x4169e1)
        await ctx.channel.send(embed=embed, delete_after=10)
        return await ctx.message.delete()

    @commands.command(aliases=['dr'])
    @commands.is_owner()
    async def dictremove(self, ctx, kazu: int):
        df = pd.read_csv("dictionary.csv", header=None)
        df = df.drop(index=df.index[kazu])
        df.to_csv('dictionary.csv', header=False, index=False)
        embed = discord.Embed(
            title="Done.",
            description=(
                f"ユーザー辞書から要素を削除しました。\n現在のユーザー辞書は ab!dictprint で確認できます。\nDelete complete."),
            color=0x4169e1)
        await ctx.channel.send(embed=embed, delete_after=10)
        return await ctx.message.delete()

    @commands.command(aliases=['dp'])
    @commands.has_role(713321552271376444)
    async def dictprint(self, ctx):
        num = 0
        jisyo = []
        with open("dictionary.csv", 'r', encoding="utf8") as f:
            reader = csv.reader(f, delimiter=",")
            for row in reader:
                naiyou = row[0]
                hinsi = row[1]
                yomi = row[2]
                jisyo.append(
                    f"{num}" + f" {naiyou}" +
                    f" {hinsi}" + f" {yomi}")
                num += 1
        msg = "\n".join(jisyo)
        embed = discord.Embed(
            title="現在のユーザー辞書",
            description=f"行  名前  品詞  読み\n{msg}")
        await ctx.channel.send(embed=embed, delete_after=10)
        return await ctx.message.delete()

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            embed = discord.Embed(
                title="Error",
                description=(
                    f"あなたにこのコマンドを実行する権限がありません！\nYou don't have permission."),
                color=0xff0000)
            await ctx.message.delete()
            await ctx.channel.send(embed=embed, delete_after=10)
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title="Error",
                description=f"引数の数が不正です！\nInvalid input.",
                color=0xff0000)
            await ctx.message.delete()
            await ctx.channel.send(embed=embed, delete_after=10)
            return
        elif isinstance(error, commands.NotOwner):
            embed = discord.Embed(
                title="Error",
                description=(
                    f"このコマンドは開発者のみ実行できます。\nCan only be executed by the creator."),
                color=0xff0000)
            await ctx.message.delete()
            await ctx.channel.send(embed=embed, delete_after=10)
            return
        else:
            embed = discord.Embed(
                title="Error",
                description=(
                    f"不明なエラーが発生しました。\nエラー内容:{error}"),
                color=0xff0000)
            await ctx.message.delete()
            await ctx.channel.send(embed=embed)
            return


def setup(bot):
    bot.add_cog(Check(bot))
