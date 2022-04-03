import sqlite3

class ItemModel:

    def __init__(self, name, price):
        self.name = name
        self.price = price

    def json(self):
        return {'name': self.name, 'price': self.price}

    @classmethod
    def find_by_name(cls, name):
        connection = sqlite3.connect('data01.db')
        cursor = connection.cursor()

        qry = "SELECT name, price FROM items WHERE name=?"
        result = cursor.execute(qry, (name,))
        row = result.fetchone()
        connection.close()

        if row:
            return cls(*row)

    def insert(self):
        connection = sqlite3.connect('data01.db')
        cursor = connection.cursor()

        qry = "INSERT INTO items VALUES (?, ?)"
        cursor.execute(qry, (self.name, self.price))
        
        connection.commit()
        connection.close()

    def update(self, price):
        self.price = price

        connection = sqlite3.connect('data01.db')
        cursor = connection.cursor()

        qry = "UPDATE items SET price=? WHERE name=?"
        cursor.execute(qry, (self.price, self.name))
        
        connection.commit()
        connection.close()

    def remove(self):
        connection = sqlite3.connect('data01.db')
        cursor = connection.cursor()

        qry = "DELETE FROM items WHERE name=?"
        cursor.execute(qry, (self.name,))
        
        connection.commit()
        connection.close()