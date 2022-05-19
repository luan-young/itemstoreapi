from flask import g, request, url_for
from flask_restful import Resource
from flask_jwt_extended import create_access_token, create_refresh_token

from oa import github
from models.user import UserModel


class GithubLogin(Resource):

    @classmethod
    def get(cls):
        return github.authorize(callback=url_for('github.authorize', _external=True))


class GithubAuthorize(Resource):

    @classmethod
    def get(cls):
        resp = github.authorized_response()
        if resp is None or resp.get('access_token') is None:
            return {
                'error': request.args['error'],
                'error_description': request.args['error_description']
            }, 500

        g.access_token = resp['access_token']
        github_user = github.get('user')
        github_username = github_user.data['login']
        
        # of course, we should be using something really unique instead of username (as a different user but with the same
        # username could be already registered in), like the user email from github.
        # we could also keep track of the method used to register and assign a random username if the username already
        # exists (this user will be using hithub to login anyways), and allow the user to change the username later.
        user = UserModel.find_by_name(github_username)
        if not user:
            user = UserModel(username=github_username, password=None)
            user.save_to_db()

        access_token = create_access_token(identity=user.id, fresh=True)
        refresh_token = create_refresh_token(user.id)
        return {
            'access_token': access_token,
            'refresh_token': refresh_token
        }, 200