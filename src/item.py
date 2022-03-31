from multiprocessing import connection
from flask_restful import Resource, reqparse
from flask_jwt import  jwt_required
import sqlite3

class Item(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('price',
        type=float,
        required=True,
        help='This field cannot be left blank.'
    )

    @classmethod
    def find_by_name(cls, name):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        qry = "SELECT name, price FROM items WHERE name=?"
        result = cursor.execute(qry, (name,))
        row = result.fetchone()
        connection.close()

        if row:
            return {'item': {'name': row[0], 'price': row[1]}}

    @classmethod
    def insert(cls, item):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        qry = "INSERT INTO items VALUES (?, ?)"
        cursor.execute(qry, (item['name'], item['price']))
        
        connection.commit()
        connection.close()

    @classmethod
    def update(cls, item):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        qry = "UPDATE items SET price=? WHERE name=?"
        cursor.execute(qry, (item['price'], item['name']))
        
        connection.commit()
        connection.close()

    @classmethod
    def remove(cls, name):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        qry = "DELETE FROM items WHERE name=?"
        cursor.execute(qry, (name,))
        
        connection.commit()
        connection.close()

    def get(self, name):
        try:
            item = self.find_by_name(name)
        except:
            return {'message': 'Failed when searching for item.'}, 500 # 500: internal server error

        if item:
            return item
        return {'message': f'Item {name} not found.'}, 404

    def post(self, name):
        try:
            if self.find_by_name(name):
                return {'message': f'Item {name} already exists.'}, 400 # 400: bad request
        except:
            return {'message': 'Failed when searching for item.'}, 500 # 500: internal server error
            
        req_data = Item.parser.parse_args()
        new_item = {'name': name, 'price': req_data['price']}

        try:
            self.insert(new_item)
        except:
            return {'message': 'Failed when saving item.'}, 500 # 500: internal server error

        return new_item, 201 # 201: created

    def put(self, name):
        req_data = Item.parser.parse_args()

        try:
            existing_item = self.find_by_name(name)
        except:
            return {'message': 'Failed when searching for item.'}, 500 # 500: internal server error

        item = {'name': name, 'price': req_data['price']}

        if existing_item:
            try:
                self.update(item)
            except:
                return {'message': 'Failed when updating item.'}, 500 # 500: internal server error
        else:
            try:
                self.insert(item)
            except:
                return {'message': 'Failed when saving item.'}, 500 # 500: internal server error

        return item

    @jwt_required()
    def delete(self, name):
        try:
            self.remove(name)
        except:
            return {'message': 'Failed when deleting item.'}, 500 # 500: internal server error
        return {'message': f'Item {name} was removed.'}

class ItemList(Resource):
    def get(self):
        connection = sqlite3.connect('data.db')
        cursor = connection.cursor()

        qry = "SELECT name, price FROM items"
        result = cursor.execute(qry)
        items = [{'name': row[0], 'price': row[1]} for row in result]
        connection.close()

        return {'items': items}