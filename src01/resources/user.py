from flask_restful import Resource, reqparse
import sqlite3

from models.user import UserModel

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

        if UserModel.get_user_by_name(req_data['username']):
            return {'message': 'User already exists.'}, 400

        connection = sqlite3.connect('data01.db')
        cursor = connection.cursor()

        qry = 'INSERT INTO users VALUES (NULL, ?, ?)'
        cursor.execute(qry, (req_data['username'], req_data['password']))
        
        connection.commit()
        connection.close()

        return {'message': 'User created.'}, 201
