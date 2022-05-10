import imp
from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt

from models.user import UserModel
from blocklist import users_logged_out_jwt_ids

_user_parser = reqparse.RequestParser()
_user_parser.add_argument('username',
    type=str,
    required=True,
    help='This field cannot be left blank.'
)
_user_parser.add_argument('password',
    type=str,
    required=True,
    help='This field cannot be left blank.'
)

class UserRegister(Resource):

    def post(self):
        req_data = _user_parser.parse_args()

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
    def get(cls, user_id: int):
        try:
            user = UserModel.find_by_id(user_id)
        except:
            return {'message': 'Failed when searching for user.'}, 500 # 500: internal server error

        if user:
            return {'user': user.json()}
            
        return {'message': f'User {user_id} not found.'}, 404

    @classmethod
    def delete(cls, user_id: int):
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


class UserLogin(Resource):

    @classmethod
    def post(cls):
        req_data = _user_parser.parse_args()

        user = UserModel.find_by_name(req_data['username'])

        if user and user.password == req_data['password']: # change comparison for a safe comparison like hmac.compare_digest()
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)
            return {
                'access_token': access_token,
                'refresh_token': refresh_token
            }, 200
        
        return {'message': 'Invalid credentials.'}, 401


class UserLogout(Resource):

    @jwt_required()
    def post(self):
        jti = get_jwt()['jti']
        # instead of users_logged_out_jwt_ids, should be keep the revoked tokens in database,
        # and should clean the tokens from database when the tokens have expired
        users_logged_out_jwt_ids.add(jti)
        return {'message': 'User logged out.'}


class TokenRefresh(Resource):

    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {'access_token': new_token}