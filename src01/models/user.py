import sqlite3

class UserModel:

    def __init__(self, _id, username, password):
        self.id = _id
        self.username = username
        self.password = password

    @classmethod
    def get_user_by_name(cls, name):
        connection = sqlite3.connect('data01.db')
        cursor = connection.cursor()

        qry = 'SELECT id, name, password FROM users WHERE name=?'
        result = cursor.execute(qry, (name,))
        row = result.fetchone()
        user = cls(*row) if row else None

        connection.close()
        return user

    @classmethod
    def get_user_by_id(cls, _id):
        connection = sqlite3.connect('data01.db')
        cursor = connection.cursor()

        qry = 'SELECT id, name, password FROM users WHERE id=?'
        result = cursor.execute(qry, (_id,))
        row = result.fetchone()
        user = cls(*row) if row else None

        connection.close()
        return user