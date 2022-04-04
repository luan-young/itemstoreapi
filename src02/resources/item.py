from flask_restful import Resource, reqparse
from flask_jwt import  jwt_required

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

    def get(self, name):
        try:
            item = ItemModel.find_by_name(name)
        except:
            return {'message': 'Failed when searching for item.'}, 500 # 500: internal server error

        if item:
            return {'item': item.json()}
        return {'message': f'Item {name} not found.'}, 404

    def post(self, name):
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

    def put(self, name):
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

    @jwt_required()
    def delete(self, name):
        try:
            item = ItemModel.find_by_name(name)
        except:
            return {'message': 'Failed when searching for item.'}, 500 # 500: internal server error

        if item:
            try:
                item.delete_from_db()
            except:
                return {'message': 'Failed when deleting item.'}, 500 # 500: internal server error
        return {'message': f'Item {name} was removed.'}


class ItemList(Resource):
    def get(self):
        return {'items': [item.json() for item in ItemModel.find_all()]}