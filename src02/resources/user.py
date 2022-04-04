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
            if UserModel.get_user_by_name(req_data['username']):
                return {'message': 'User already exists.'}, 400

            user = UserModel(req_data['username'], req_data['password'])
            user.save_to_db()
        except:
            return {'message': 'Failed while creating user.'}, 500

        return {'message': 'User created.'}, 201
