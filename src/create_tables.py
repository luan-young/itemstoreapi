import sqlite3

conn = sqlite3.connect('data.db')
cursor = conn.cursor()

create_qry = """
    CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    password TEXT NOT NULL)
"""
cursor.execute(create_qry)

# test_users = [
#     ('Bob', 'asdf'),
#     ('Anne', 'zxcv')
# ]
# test_users_qry = """
#     INSERT INTO users VALUES(NULL, ?, ?)
# """
# cursor.executemany(test_users_qry, test_users)

# result = cursor.execute("SELECT * FROM users")
# for row in result:
#     print(row)

conn.commit()
conn.close()