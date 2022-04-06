from flask_restful import Resource, reqparse

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

        try:
            if UserModel.find_by_name(req_data['username']):
                return {'message': 'User already exists.'}, 400

            user = UserModel(req_data['username'], req_data['password'])
            user.save_to_db()
        except:
            return {'message': 'Failed while creating user.'}, 500

        return {'message': 'User created.'}, 201


class User(Resource):

    @classmethod
    def get(cls, user_id):
        try:
            user = UserModel.find_by_id(user_id)
        except:
            return {'message': 'Failed when searching for user.'}, 500 # 500: internal server error

        if user:
            return {'user': user.json()}
            
        return {'message': f'User {user_id} not found.'}, 404

    @classmethod
    def delete(cls, user_id):
        try:
            user = UserModel.find_by_id(user_id)
        except:
            return {'message': 'Failed when searching for user.'}, 500 # 500: internal server error

        if not user:
            return {'message': f'User {user_id} not found.'}, 404

        try:
            user.delete_from_db()
            return {'message': f'User {user_id} was removed.'}
        except:
            return {'message': 'Failed when deleting user.'}, 500 # 500: internal server error