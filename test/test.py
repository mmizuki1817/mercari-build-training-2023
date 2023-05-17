import sqlite3

db = 'items.db'
connect = sqlite3.connect(db)
cursor = connect.cursor()

cursor.execute('INSERT INTO items(id) values("jacket")')

connect.commit()
cursor.close()
connect.close()
