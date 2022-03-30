from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from flask_jwt import JWT, jwt_required

from security import authenticate, identity

app = Flask(__name__)
app.secret_key = 'replace_for_secret_out_of_source_code'
api = Api(app)
jwt = JWT(app, authenticate, identity)

items = []

class Item(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument(
        'price',
        type=float,
        required=True,
        help='This field cannot be left blank.'
    )

    def get(self, name):
        item = next(filter(lambda x: x['name'] == name, items), None)
        return {'name': item}, 200 if item else 404 # 200: ok; 404: not found

    def post(self, name):
        if next(filter(lambda x: x['name'] == name, items), None):
            return {'message': f'Item {name} already exists.'}, 400 # 400: bad request
            
        req_data = Item.parser.parse_args()
        new_item = {'name': name, 'price': req_data['price']}
        items.append(new_item)
        return new_item, 201 # 201: created

    def put(self, name):
        req_data = Item.parser.parse_args()

        item = next(filter(lambda x: x['name'] == name, items), None)
        if item:
            item.update(req_data)
        else:
            item = {'name': name, 'price': req_data['price']}
            items.append(item)
        return item

    @jwt_required()
    def delete(self, name):
        global items
        items = list(filter(lambda x: x['name'] != name, items))
        return {'message': f'Item {name} was removed.'}

class Items(Resource):
    def get(self):
        return {'items': items}

api.add_resource(Item, '/item/<string:name>')
api.add_resource(Items, '/items')

if __name__ == '__main__':
    app.run(port=5000, debug=True)