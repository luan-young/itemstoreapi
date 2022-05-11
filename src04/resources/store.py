from flask_restful import Resource

from models.store import StoreModel

SRV_ERR_SEARCHING = 'Failed while searching for store in DB.'
SRV_ERR_SAVING = 'Failed while saving store in DB.'
SRV_ERR_DELETING = 'Failed while deleting store in DB.'

CL_ERR_NOT_FOUND = 'Store {} not found in DB.'
CL_ERR_ALREADY_EXISTS = 'Store {} already exists in DB.'

MSG_DELETED = 'Store {} was removed from DB.'

class Store(Resource):

    @classmethod
    def get(cls, name: str):
        try:
            store = StoreModel.find_by_name(name)
        except:
            return {'message': SRV_ERR_SEARCHING}, 500 # 500: internal server error

        if store:
            return {'store': store.json()}

        return {'message': CL_ERR_NOT_FOUND.format(name)}, 404

    @classmethod
    def post(cls, name: str):
        try:
            if StoreModel.find_by_name(name):
                return {'message': CL_ERR_ALREADY_EXISTS.format(name)}, 400 # 400: bad request
        except:
            return {'message': SRV_ERR_SEARCHING}, 500 # 500: internal server error
            
        store = StoreModel(name)

        try:
            store.save_to_db()
        except:
            return {'message': SRV_ERR_SAVING}, 500 # 500: internal server error

        return {'store': store.json()}, 201 # 201: created

    @classmethod
    def delete(cls, name: str):
        try:
            store = StoreModel.find_by_name(name)
        except:
            return {'message': SRV_ERR_SEARCHING}, 500 # 500: internal server error

        if not store:
            return {'message': CL_ERR_NOT_FOUND.format(name)}, 404

        try:
            store.delete_from_db()
            return {'message': MSG_DELETED.format(name)}
        except:
            return {'message': SRV_ERR_DELETING}, 500 # 500: internal server error


class StoreList(Resource):

    @classmethod
    def get(cls):
        try:
            return {'stores': [store.json() for store in StoreModel.find_all()]}
        except:
            return {'message': SRV_ERR_SEARCHING}, 500 # 500: internal server error