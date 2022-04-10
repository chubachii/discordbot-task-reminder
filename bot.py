from os import getenv
import traceback

import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.BadArgument):
        embed = discord.Embed(title=":x: 失敗 -BadArgument", description=f"指定された引数がエラーを起こしているため実行出来ません。", timestamp=ctx.message.created_at, color=discord.Colour.red())
        embed.set_footer(text="お困りの場合は、サーバー管理者をメンションしてください。")
        await ctx.send(embed=embed, delete_after=5.0) 
    elif isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        embed = discord.Embed(title=":x: 失敗 -BadArgument", description=f"指定された引数が足りないため実行出来ません。", timestamp=ctx.message.created_at, color=discord.Colour.red())
        embed.set_footer(text="お困りの場合は、サーバー管理者をメンションしてください。")
        await ctx.send(embed=embed) 
    else:
        raise error


@bot.command()
async def 課題(ctx, title, content, simple_date, detail):




    await ctx.send(str(title)+str(content)+str(simple_date))


token = getenv('BOT_TOKEN')
bot.run(token)