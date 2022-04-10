from os import getenv
import traceback

from discord.ext import commands

bot = commands.Bot(command_prefix='!')


@bot.event
async def on_command_error(ctx, error):
    orig_error = getattr(error, "original", error)
    error_msg = ''.join(traceback.TracebackException.from_exception(orig_error).format())
    await ctx.send(error_msg)


@bot.command()
async def 課題(ctx, title, content, simple_date, detail):
    await ctx.send(str(title)+str(content)+str(simple_date))


token = getenv('BOT_TOKEN')
bot.run(token)