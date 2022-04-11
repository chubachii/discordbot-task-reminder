import os 
import datetime

import discord
from discord.ext import commands, tasks

import psycopg2
import pytz

TOKEN = os.environ.get('BOT_TOKEN')
DATABASE_URL = os.environ.get('DATABASE_URL')
REMIND_CHANNEL_ID = os.environ.get('REMIND_CHANNEL_ID')

REMIND_TIME = '20:00'
TIME_ZONE = pytz.timezone('Asia/Tokyo')
w_list = ['（月）', '（火）', '（水）', '（木）', '（金）', '（土）', '（日）']


bot = commands.Bot(command_prefix='!')
dt_now = datetime.datetime.now()

@tasks.loop(seconds=50)
async def loop():
    await bot.wait_until_ready()
    global dt_now
    dt_now = datetime.datetime.now(TIME_ZONE)

    # リマインダー
    if dt_now.strftime('%H:%M') == REMIND_TIME:
        embed_list = get_tommorw_tasks()
        if not embed_list == None:
            for embed in embed_list:
                channel_remind = bot.get_channel(REMIND_CHANNEL_ID)
                await channel_remind.send(embed=embed)
            
            
    # ステータスメッセージ変更
    if dt_now.strftime('%H:%M') == "00:00":
        n, text = get_today_tasks()
        
        if n > 0:
            await bot.change_presence(status=discord.Status.online, activity=discord.Game(name=text))
        else:
            await bot.change_presence(status=discord.Status.idle, activity=discord.Game(name=text))

@bot.command()
async def 追加(ctx, title, content, date_md, detail='なし'):

    # mm/dd 形式を yyyy-mm-dd に
    deadline = addYtoMD(date_md)

    # インサート正常終了
    if insert(title, content, deadline, detail) is None:
        embed_list = send_tasks(ctx)
        for embed in embed_list:
            await ctx.send(embed=embed)
    
    # ステータスメッセージ更新
    n, text = get_today_tasks()
    if n > 0:
        await bot.change_presence(status=discord.Status.online, activity=discord.Game(name=text))
    else:
        await bot.change_presence(status=discord.Status.idle, activity=discord.Game(name=text))
        
@bot.command()
async def 削除(ctx, title, date_md):
    # mm/dd 形式を yyyy-mm-dd に
    deadline = addYtoMD(date_md)

    try:
        with connect_database() as conn:
            with conn.cursor() as cur:
                # SQLを実行
                cur.execute('DELETE FROM tasks WHERE title = %s AND deadline = %s', (title, deadline,))
            
                # コミットし、変更を確定する
                conn.commit()

                # 一覧の表示
                embed_list = send_tasks(ctx)
                for embed in embed_list:
                    await ctx.send(embed=embed)

    except Exception as ex:
        print(ex)

    # ステータスメッセージ更新
    n, text = get_today_tasks()
    if n > 0:
        await bot.change_presence(status=discord.Status.online, activity=discord.Game(name=text))
    else:
        await bot.change_presence(status=discord.Status.idle, activity=discord.Game(name=text))
       
@bot.command()
async def 表示(ctx):
    embed_list = send_tasks(ctx)
    for embed in embed_list:
        await ctx.send(embed=embed)

@bot.command()
async def テーブル削除(ctx):
    with connect_database() as conn:
        with conn.cursor() as cur:
            # テーブル削除
            cur.execute('''DROP TABLE Tasks''')

            # テーブルを作成する SQL を準備
            sql = '''
                CREATE TABLE Tasks (
                    title TEXT,
                    content TEXT,
                    deadline DATE,
                    detail TEXT
                );
                '''
            # SQLを実行
            cur.execute(sql)

            # コミットし、変更を確定する
            conn.commit()

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        embed = discord.Embed(title="Error -BadArgument", description="引数が足りません", color=discord.Colour.red())
        await ctx.send(embed=embed, delete_after=5.0) 

def send_tasks(ctx):
    # 締切の遅い順に日付を取得
    with connect_database() as conn:
        with conn.cursor() as cur:
            deadlines = []
            cur.execute('SELECT * FROM Tasks ORDER BY deadline DESC')
            for row in cur:
                deadlines.append(row[2])

            cur.execute('SELECT * FROM Tasks ORDER BY deadline DESC')
            embed_list = []
            for i, row in enumerate(cur):
                deadline = row[2]
                
                if deadline.year < dt_now.year or (deadline.month < dt_now.month and (deadline.year != dt_now.year+1)) or (deadline.year == dt_now.year and deadline.month == dt_now.month and deadline.day < dt_now.day):
                    # 課題なし
                    if i == 0:
                        embed_list.append(discord.Embed(title = "課題はありません", color=0xffecd5))
                        return embed_list
                    continue 
                
                if i == 0 or deadlines[i-1] != deadline:
                    ## 曜日取得
                    day_t = deadline.weekday()
                    embed=discord.Embed(title = str(deadline.month) + ' / ' + str(deadline.day) + w_list[day_t], color=0xffecd5)

                embed.add_field(name='・' + row[0] + '  :  ' + row[1] + '\n　詳細  :  ' + row[3], value=" - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -", inline=False)
                
                if i == len(deadlines)-1 or deadlines[i+1] != deadline:
                    embed_list.append(embed)    
            return embed_list

def connect_database():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    return conn

def insert(title, content, deadline, detail):

    try:
        with connect_database() as conn:
            with conn.cursor() as cur:
                # SQLを実行
                cur.execute('INSERT INTO tasks (title, content, deadline, detail) VALUES (%s, %s, %s, %s)', (title, content, deadline, detail,))
            
                # コミットし、変更を確定する
                conn.commit()

                return None
        
    except Exception as ex:
        return ex
 
def addYtoMD(date_md):

    md = date_md.split('/') # 月と日に分割
    if dt_now.month > int(md[0]): y = dt_now.year + 1
    else: y = dt_now.year

    date = str(y) + '-' + str(md[0]) + '-' + str(md[1])  # yyyy-mm-dd形式
    date_ymd = datetime.datetime.strptime(date, '%Y-%m-%d').date()
    return date_ymd

def get_tommorw_tasks():

    t = dt_now + datetime.timedelta(1)
    tomorrow = str(t.year) + '-' + str(t.month) + '-' + str(t.day)  # yyyy-mm-dd形式

    with connect_database() as conn:
        with conn.cursor() as cur:

            tasks = []
            cur.execute('SELECT * FROM Tasks WHERE deadline = %s', (tomorrow,))
            for row in (cur):
                tasks.append(row)

            if len(tasks) != 0:
                embed_list = []
                for i, row in enumerate(tasks):
                    deadline = row[2]
                
                    if i == 0:
                        ## 曜日取得
                        day_t = deadline.weekday()
                        embed=discord.Embed(title = "【 リマインド 】 明日が締切の課題があります", description = str(deadline.month) + ' / ' + str(deadline.day) + w_list[day_t], color=0xff0000)

                    embed.add_field(name='・' + row[0] + '  :  ' + row[1] + '\n　詳細  :  ' + row[3], value=" - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -", inline=False)
                    
                    if i == len(tasks)-1:
                        embed_list.append(embed)
                        return embed_list

            else: return None

def get_today_tasks():
    date = str(dt_now.year) + '-' + str(dt_now.month) + '-' + str(dt_now.day)  # yyyy-mm-dd形式
    date_ymd = datetime.datetime.strptime(date, '%Y-%m-%d').date()

    text = "エラー"
    n = 0
    with connect_database() as conn:
        with conn.cursor() as cur:

            tasks = []
            cur.execute('SELECT * FROM Tasks WHERE deadline = %s', (date,))
            for row in (cur):
                tasks.append(row)

            n = len(tasks)

            text = "今日 " + w_list[date_ymd.weekday()] + "が締切の課題 : " + str(n)

    return n, text

loop.start()
bot.run(TOKEN)