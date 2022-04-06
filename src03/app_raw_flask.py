from flask import Flask, request, jsonify

app = Flask(__name__)

stores = [
    {
        'name': 'Store A',
        'items': [{'name': 'Item a1', 'price': 9.99}]
    }
]

@app.route('/')
def home():
    return 'Hello World!!!'

# post /store - data: {name: }
@app.route('/store', methods=['POST'])
def create_store():
    request_data = request.get_json()
    new_store = {
        'name': request_data['name'],
        'items': []
    }
    stores.append(new_store)
    return jsonify(new_store)

# get /store/<name>
@app.route('/store/<string:name>')
def get_store(name):
    for store in stores:
        if store['name'] == name:
            return jsonify(store)
    return jsonify({'message': 'store not found'})

# get /store
@app.route('/store')
def get_stores():
    return jsonify({'stores': stores})

# post /store/<store name>/item - data: {name: , price: }
@app.route('/store/<string:store_name>/item', methods=['POST'])
def create_item_in_store(store_name):
    request_data = request.get_json()
    for store in stores:
        if store['name'] == store_name:
            new_item = {
                'name': request_data['name'],
                'price': request_data['price']
            }
            store['items'].append(new_item)
            return jsonify(new_item)
    return jsonify({'message': 'store not found'})

# get /store/<store name>/item
@app.route('/store/<string:store_name>/item')
def get_item_from_store(store_name):
    for store in stores:
        if store['name'] == store_name:
            return jsonify({'items': store['items']})
    return jsonify({'message': 'store not found'})

app.run(port=5000)