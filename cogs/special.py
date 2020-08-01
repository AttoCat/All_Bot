import discord
from discord.ext import commands
import textwrap
import contextlib
import traceback
import io


class Special(commands.Cog):
    __slots__ = ('client', 'name', '_last_result')

    def __init__(self, client, name=None):
        self.client = client
        self.name = name if name is not None else type(self).__name__
        self._last_result = None

    async def cog_check(self, ctx):
        # シンプルにBOTのオーナーであるか
        return await self.client.is_owner(ctx.author)

    @commands.command(hidden=True)
    async def said(self, ctx, *, arg):
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        await ctx.send(arg)

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

    def get_syntax_error(self, e):
        if e.text is None:
            return f'```py\n{e.__class__.__name__}: {e}\n```'
        return f'```py\n{e.text}'
        f'{"^":>{e.offset}}\n'
        f'{e.__class__.__name__}: {e}```'

    @commands.command(pass_context=True, hidden=True, name='eval')  # 以下コピペ
    async def _eval(self, ctx):
        """Evaluates a code"""

        env = {
            'bot': self.client,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result
        }

        env.update(globals())
        await ctx.send('コマンドを入力してください')
        message = await self.client.wait_for(
            'message', check=lambda m: m.author == ctx.author
            and m.channel == ctx.channel)
        body = self.cleanup_code(message.content)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

        func = env['func']
        try:
            with contextlib.redirect_stdout(stdout):
                ret = await func()
        except Exception:
            value = stdout.getvalue()
            await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\u2705')
            except Exception:
                pass

            if ret is None:
                if value:
                    await ctx.send(f'```py\n{value}\n```')
            else:
                self._last_result = ret
                await ctx.send(f'```py\n{value}{ret}\n```')

    @commands.command()
    async def donate(self, ctx):
        url = "https://www.amazon.co.jp/hz/wishlist"
        "/ls/28QJULCB96QI8?ref_=wl_share"
        embed = discord.Embed(
            title="寄付はこちらから！",
            description=(
                "\n**寄付をしていただけると…**\n"
                "1.AttoCatにものすごく感謝される\n"
                "2.ABACUSがより高性能になる\n"
                "3.要望を優先的にできる\n"
                "  などなど、嬉しいことがいっぱいあります！\n\n"
                "**寄付の方法...**\n"
                "1.欲しいものリストから寄付\n"
                f" [欲しいものリスト]({url})\n"
                "↑にはAttoCatが欲しいものが全て入っています！\n"
                "2.AmazonギフトカードまたはKyashから寄付\n"
                "AttoCat宛にDMでコード（Kyashの場合はリンク）を送ってください！"),
            color=0x4e37fb)
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.NotOwner):
            content = "あなたにこのコマンドを実行する権限がありません！\nYou don't have permission."
        elif isinstance(error, commands.BadArgument):
            content = "不正な引数です！\nInvalid argument passed."
        elif isinstance(error, commands.MissingRequiredArgument):
            content = "想定しない引数が渡されました！\nInvalid input."
        elif isinstance(error, commands.CommandInvokeError):
            if isinstance(error.original, discord.NotFound):
                content = "メッセージが見つかりませんでした！\nMessage not found."
            else:
                f"不明なエラーが発生しました。\nエラー内容：\n{error}"
        elif isinstance(error, commands.TooManyArguments):
            content = "引数の数が不正です！\nInvalid input."
        else:
            content = f"不明なエラーが発生しました。\nエラー内容:\n{error}"
        embed = discord.Embed(
            title="Error", description=content, color=0xff0000)
        await ctx.message.delete()
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Special(bot))
