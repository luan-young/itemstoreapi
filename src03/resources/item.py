from typing import Optional
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity

from models.item import ItemModel

class Item(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('price',
        type=float,
        required=True,
        help='This field cannot be left blank.'
    )
    parser.add_argument('store_id',
        type=int,
        required=True,
        help='Every item needs a store id.'
    )

    def get(self, name: str):
        try:
            item = ItemModel.find_by_name(name)
        except:
            return {'message': 'Failed when searching for item.'}, 500 # 500: internal server error

        if item:
            return {'item': item.json()}

        return {'message': f'Item {name} not found.'}, 404

    def post(self, name: str):
        try:
            if ItemModel.find_by_name(name):
                return {'message': f'Item {name} already exists.'}, 400 # 400: bad request
        except:
            return {'message': 'Failed when searching for item.'}, 500 # 500: internal server error
            
        req_data = Item.parser.parse_args()
        item = ItemModel(name, req_data['price'], req_data['store_id'])

        try:
            item.save_to_db()
        except:
            return {'message': 'Failed when saving item.'}, 500 # 500: internal server error

        return {'item': item.json()}, 201 # 201: created

    @jwt_required()
    def put(self, name: str):
        req_data = Item.parser.parse_args()

        try:
            item = ItemModel.find_by_name(name)
        except:
            return {'message': 'Failed when searching for item.'}, 500 # 500: internal server error

        if item:
            item.price = req_data['price']
            item.store_id = req_data['store_id']
        else:
            item = ItemModel(name, req_data['price'], req_data['store_id'])

        try:
            item.save_to_db()
        except:
            return {'message': 'Failed when saving item.'}, 500 # 500: internal server error

        return {'item': item.json()}

    @jwt_required(fresh=True)
    def delete(self, name: str):
        claims = get_jwt()
        if not claims['is_admin']:
            return {'message': 'Admin privilege required.'}, 401

        try:
            item = ItemModel.find_by_name(name)
        except:
            return {'message': 'Failed when searching for item.'}, 500 # 500: internal server error

        if not item:
            return {'message': f'Item {name} not found.'}, 404
            
        try:
            item.delete_from_db()
            return {'message': f'Item {name} was removed.'}
        except:
            return {'message': 'Failed when deleting item.'}, 500 # 500: internal server error


class ItemList(Resource):

    @jwt_required(optional=True)
    def get(self):
        user_id = get_jwt_identity()

        try:
            items = [item.json() for item in ItemModel.find_all()]
        except:
            return {'message': 'Failed when searching for items.'}, 500 # 500: internal server error

        if user_id:
            return {'items': items}
        return {
            'items': [item['name'] for item in items],
            'message': 'More data available only to logged in users.'
        }