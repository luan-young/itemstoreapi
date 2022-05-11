from flask import request
from flask_restful import Resource
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from marshmallow import ValidationError

from models.user import UserModel
from schemas.user import UserSchema
from blocklist import users_logged_out_jwt_ids

SRV_ERR_SEARCHING = 'Failed while searching for user in DB.'
SRV_ERR_CREATING = 'Failed while creating user in DB.'
SRV_ERR_DELETING = 'Failed while deleting user in DB.'

CL_ERR_NOT_FOUND = 'User {} not found in DB.'
CL_ERR_ALREADY_EXISTS = 'User {} already exists in DB.'
CL_ERR_INVALID_CREDENTIALS = 'Invalid credentials.'

MSG_CREATED = 'User {} was created in DB.'
MSG_DELETED = 'User {} was removed from DB.'
MSG_LOGGED_OUT = 'User logged out.'

user_schema = UserSchema()

class UserRegister(Resource):

    @classmethod
    def post(cls):
        try:
            user_data = user_schema.load(request.get_json())
        except ValidationError as err:
            return err.messages, 400

        try:
            if UserModel.find_by_name(user_data['username']):
                return {'message': CL_ERR_ALREADY_EXISTS.format(user_data['username'])}, 400

            user = UserModel(**user_data)
            user.save_to_db()
        except:
            return {'message': SRV_ERR_CREATING}, 500

        return {'message': MSG_CREATED.format(user_data['username'])}, 201


class User(Resource):

    @classmethod
    def get(cls, user_id: int):
        try:
            user = UserModel.find_by_id(user_id)
        except:
            return {'message': SRV_ERR_SEARCHING}, 500 # 500: internal server error

        if user:
            return {'user': user_schema.dump(user)}, 200
            
        return {'message': CL_ERR_NOT_FOUND.format(user_id)}, 404

    @classmethod
    def delete(cls, user_id: int):
        try:
            user = UserModel.find_by_id(user_id)
        except:
            return {'message': SRV_ERR_SEARCHING}, 500 # 500: internal server error

        if not user:
            return {'message': CL_ERR_NOT_FOUND.format(user_id)}, 404

        try:
            user.delete_from_db()
            return {'message': MSG_DELETED.format(user_id)}
        except:
            return {'message': SRV_ERR_DELETING}, 500 # 500: internal server error


class UserLogin(Resource):

    @classmethod
    def post(cls):
        try:
            user_data = user_schema.load(request.get_json())
        except ValidationError as err:
            return err.messages, 400

        user = UserModel.find_by_name(user_data['username'])

        if user and user.password == user_data['password']: # change comparison for a safe comparison like hmac.compare_digest()
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)
            return {
                'access_token': access_token,
                'refresh_token': refresh_token
            }, 200
        
        return {'message': CL_ERR_INVALID_CREDENTIALS}, 401


class UserLogout(Resource):

    @classmethod
    @jwt_required()
    def post(cls):
        jti = get_jwt()['jti']
        # instead of users_logged_out_jwt_ids, should be keep the revoked tokens in database,
        # and should clean the tokens from database when the tokens have expired
        users_logged_out_jwt_ids.add(jti)
        return {'message': MSG_LOGGED_OUT}


class TokenRefresh(Resource):

    @classmethod
    @jwt_required(refresh=True)
    def post(cls):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {'access_token': new_token}