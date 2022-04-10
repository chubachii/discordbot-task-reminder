import os 

import discord
from discord.ext import commands

import redis

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        embed = discord.Embed(title="Error -BadArgument", description="引数が足りません", color=discord.Colour.red())
        await ctx.send(embed=embed, delete_after=5.0) 


@bot.command()
async def 課題(ctx, title, content, simple_date, detail):

    conn = connect_redis()
    task = conn.set('title', title)
    result = conn.get('title')




    await ctx.send(str(result))
    await ctx.send('a')


token = os.environ.get('BOT_TOKEN')
bot.run(token)


def connect_redis():
    return redis.from_url(
        url=os.environ.get('REDIS_URL'),
        decode_responses=True,
    )