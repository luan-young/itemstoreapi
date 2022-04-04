from flask_restful import Resource

from models.store import StoreModel

class Store(Resource):

    def get(self, name):
        try:
            store = StoreModel.find_by_name(name)
        except:
            return {'message': 'Failed when searching for store.'}, 500 # 500: internal server error

        if store:
            return {'store': store.json()}

        return {'message': f'Store {name} not found.'}, 404

    def post(self, name):
        try:
            if StoreModel.find_by_name(name):
                return {'message': f'Store {name} already exists.'}, 400 # 400: bad request
        except:
            return {'message': 'Failed when searching for store.'}, 500 # 500: internal server error
            
        store = StoreModel(name)

        try:
            store.save_to_db()
        except:
            return {'message': 'Failed when saving store.'}, 500 # 500: internal server error

        return {'store': store.json()}, 201 # 201: created

    def delete(self, name):
        try:
            store = StoreModel.find_by_name(name)
        except:
            return {'message': 'Failed when searching for store.'}, 500 # 500: internal server error

        if not store:
            return {'message': f'Store {name} not found.'}, 404

        try:
            store.delete_from_db()
            return {'message': f'Store {name} was removed.'}
        except:
            return {'message': 'Failed when deleting store.'}, 500 # 500: internal server error


class StoreList(Resource):

    def get(self):
        try:
            return {'stores': [store.json() for store in StoreModel.find_all()]}
        except:
            return {'message': 'Failed when searching for stores.'}, 500 # 500: internal server error