from flask_restful import Resource, reqparse
from flask_jwt import  jwt_required
import sqlite3

from models.item import ItemModel

class Item(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('price',
        type=float,
        required=True,
        help='This field cannot be left blank.'
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
        new_item = ItemModel(name, req_data['price'])

        try:
            new_item.insert()
        except:
            return {'message': 'Failed when saving item.'}, 500 # 500: internal server error

        return {'item': new_item.json()}, 201 # 201: created

    def put(self, name):
        req_data = Item.parser.parse_args()

        try:
            existing_item = ItemModel.find_by_name(name)
        except:
            return {'message': 'Failed when searching for item.'}, 500 # 500: internal server error

        if existing_item:
            try:
                existing_item.update(req_data['price'])
                return {'item': existing_item.json()}, 200
            except:
                return {'message': 'Failed when updating item.'}, 500 # 500: internal server error
        else:
            try:
                new_item = ItemModel(name, req_data['price'])
                new_item.insert()
                return {'item': new_item.json()}, 201 # 201: created
            except:
                return {'message': 'Failed when saving item.'}, 500 # 500: internal server error

    @jwt_required()
    def delete(self, name):
        try:
            item = ItemModel.find_by_name(name)
        except:
            return {'message': 'Failed when searching for item.'}, 500 # 500: internal server error

        if item:
            try:
                item.remove()
            except:
                return {'message': 'Failed when deleting item.'}, 500 # 500: internal server error
        return {'message': f'Item {name} was removed.'}

class ItemList(Resource):
    def get(self):
        connection = sqlite3.connect('data01.db')
        cursor = connection.cursor()

        qry = "SELECT name, price FROM items"
        result = cursor.execute(qry)
        items = [{'name': row[0], 'price': row[1]} for row in result]
        connection.close()

        return {'items': items}