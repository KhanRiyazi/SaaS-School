import sqlite3

conn = sqlite3.connect("url_shortener.db")
conn.row_factory = sqlite3.Row  # 👈 important
cursor = conn.cursor()

cursor.execute("SELECT * FROM url_mappings")
rows = cursor.fetchall()

for row in rows:
    print(dict(row))  # 👈 clean output

conn.close()