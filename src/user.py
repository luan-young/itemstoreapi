from flask_restful import Resource, reqparse
import sqlite3

class User:

    def __init__(self, _id, username, password):
        self.id = _id
        self.username = username
        self.password = password

    @classmethod
    def get_user_by_name(cls, name):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        qry = 'SELECT id, name, password FROM users WHERE name=?'
        result = cursor.execute(qry, (name,))
        row = result.fetchone()
        user = cls(*row) if row else None

        connection.close()
        return user

    @classmethod
    def get_user_by_id(cls, _id):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        qry = 'SELECT id, name, password FROM users WHERE id=?'
        result = cursor.execute(qry, (_id,))
        row = result.fetchone()
        user = cls(*row) if row else None

        connection.close()
        return user

class UserRegister(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('username',
        type=str,
        required=True,
        help='This field cannot be left blank.'
    )
    parser.add_argument('password',
        type=str,
        required=True,
        help='This field cannot be left blank.'
    )

    def post(self):
        req_data = UserRegister.parser.parse_args()

        if User.get_user_by_name(req_data['username']):
            return {'Message': 'User already exists.'}, 400

        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        qry = 'INSERT INTO users VALUES (NULL, ?, ?)'
        cursor.execute(qry, (req_data['username'], req_data['password']))
        
        connection.commit()
        connection.close()

        return {'Message': 'User created.'}, 201
