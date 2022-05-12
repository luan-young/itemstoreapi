from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from marshmallow import ValidationError

from models.item import ItemModel
from schemas.item import ItemSchema

SRV_ERR_SEARCHING = 'Failed while searching for item in DB.'
SRV_ERR_SAVING = 'Failed while saving item in DB.'
SRV_ERR_DELETING = 'Failed while deleting item in DB.'

CL_ERR_NOT_FOUND = 'Item {} not found in DB.'
CL_ERR_ALREADY_EXISTS = 'Item {} already exists in DB.'
CL_ERR_ADMIN_REQUIRED = 'Admin privilege required.'

MSG_DELETED = 'Item {} was removed from DB.'
MSG_MORE_DATA_AVAILABLE_TO_REGISTERD_USER = 'More data available only to logged in users.'

item_schema = ItemSchema()
item_list_schema = ItemSchema(many=True)

class Item(Resource):

    @classmethod
    def get(cls, name: str):
        try:
            item = ItemModel.find_by_name(name)
        except:
            return {'message': SRV_ERR_SEARCHING}, 500 # 500: internal server error

        if item:
            return {'item': item_schema.dump(item)}

        return {'message': CL_ERR_NOT_FOUND.format(name)}, 404
    
    @classmethod
    def post(cls, name: str):
        try:
            if ItemModel.find_by_name(name):
                return {'message': CL_ERR_ALREADY_EXISTS.format(name)}, 400 # 400: bad request
        except:
            return {'message': SRV_ERR_SEARCHING}, 500 # 500: internal server error

        item_json = request.get_json()
        item_json['name'] = name

        try: 
            item_data = item_schema.load(item_json)
        except ValidationError as err:
            return err.messages, 400

        try:
            item_data.save_to_db()
        except:
            return {'message': SRV_ERR_SAVING}, 500 # 500: internal server error

        return {'item': item_schema.dump(item_data)}, 201 # 201: created

    @classmethod
    @jwt_required()
    def put(cls, name: str):
        item_json = request.get_json()

        try:
            item = ItemModel.find_by_name(name)
        except:
            return {'message': SRV_ERR_SEARCHING}, 500 # 500: internal server error

        if item:
            item.price = item_json['price']
            item.store_id = item_json['store_id']
        else:
            item_json['name'] = name
            try: 
                item = item_schema.load(item_json)
            except ValidationError as err:
                return err.messages, 400

        try:
            item.save_to_db()
        except:
            return {'message': SRV_ERR_SAVING}, 500 # 500: internal server error

        return {'item': item_schema.dump(item)}

    @classmethod
    @jwt_required(fresh=True)
    def delete(cls, name: str):
        claims = get_jwt()
        if not claims['is_admin']:
            return {'message': CL_ERR_ADMIN_REQUIRED}, 401

        try:
            item = ItemModel.find_by_name(name)
        except:
            return {'message': SRV_ERR_SEARCHING}, 500 # 500: internal server error

        if not item:
            return {'message': CL_ERR_NOT_FOUND.format(name)}, 404
            
        try:
            item.delete_from_db()
            return {'message': MSG_DELETED.format(name)}
        except:
            return {'message': SRV_ERR_DELETING}, 500 # 500: internal server error


class ItemList(Resource):

    @classmethod
    @jwt_required(optional=True)
    def get(cls):
        user_id = get_jwt_identity()

        try:
            items = item_list_schema.dump(ItemModel.find_all())
        except:
            return {'message': SRV_ERR_SEARCHING}, 500 # 500: internal server error

        if user_id:
            return {'items': items}
        return {
            'items': [item['name'] for item in items],
            'message': MSG_MORE_DATA_AVAILABLE_TO_REGISTERD_USER
        }