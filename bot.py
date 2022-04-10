from os import getenv
import traceback

from discord.ext import commands

bot = commands.Bot(command_prefix='!')


@bot.event
async def on_command_error(ctx, error): await ctx.send("構文エラー")


@bot.command()
async def 課題(ctx, title, content, simple_date, detail):
    await ctx.send(str(title)+str(content)+str(simple_date))


token = getenv('BOT_TOKEN')
bot.run(token)