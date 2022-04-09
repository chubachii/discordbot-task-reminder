# データ保存用のテーブルを作成する
import sqlite3

dbname = 'task.db'

# データベースに接続
conn = sqlite3.connect(dbname)

# カーソルオブジェクトを作成
cur = conn.cursor()

# テーブルの削除
#cur.execute("""DROP TABLE tasks""")

# テーブルを作成
cur.execute("""CREATE TABLE tasks(
    id        INTEGER PRIMARY KEY,   
    title     STRING,                
    content   STRING,               
    deadline  DATE,                   
    detail    STRING           
    )""")

# データベースにコミット
conn.commit()

# 切断
cur.close()
conn.close()