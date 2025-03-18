#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route("/restaurants", methods=['GET'])
def list_restaurants():
    restaurants = Restaurant.query.all()
    return make_response([{
        "id": restaurant.id,
        "name": restaurant.name,
        "address": restaurant.address
    } for restaurant in restaurants])

@app.route("/restaurants/<int:id>", methods=["GET"])
def get_restaurant_by_id(id):
    restaurant = db.session.get(Restaurant, id)
    if restaurant is None:
        return make_response({'error': 'Restaurant not found'}, 404)     

    restaurant_data = {
        "id": restaurant.id,
        "name": restaurant.name,
        "address": restaurant.address,
        "restaurant_pizzas": [
            {
                "id": restaurant_pizza.id,
                "pizza": {
                    "id": restaurant_pizza.pizza.id,
                    "name": restaurant_pizza.pizza.name,
                    "ingredients": restaurant_pizza.pizza.ingredients
                },
                "pizza_id": restaurant_pizza.pizza_id,
                "price": restaurant_pizza.price,
                "restaurant_id": restaurant_pizza.restaurant_id
            }
            for restaurant_pizza in restaurant.restaurant_pizzas
        ]
    }
    return make_response(restaurant_data)

@app.route("/restaurants/<int:id>", methods=["DELETE"])
def delete_restaurant(id):
    restaurant = db.session.get(Restaurant, id)
    if restaurant is None:
        return make_response({"error": "Restaurant not found"}, 404)
        
    db.session.delete(restaurant)
    db.session.commit()
    return make_response({"message": "Restaurant deleted successfully"}, 204)

@app.route("/pizzas", methods=["GET"])
def list_pizzas():
    pizzas = Pizza.query.all()
    return make_response([{
        "id": pizza.id,
        "name": pizza.name,
        "ingredients": pizza.ingredients
    } for pizza in pizzas])

@app.route("/restaurant_pizzas", methods=["POST"])
def add_restaurant_pizza():
    data = request.get_json()
    restaurant = db.session.get(Restaurant, data.get('restaurant_id'))
    pizza = db.session.get(Pizza, data.get('pizza_id'))

    if not restaurant or not pizza:
        return make_response({"errors": ["validation errors"]}, 400)

    try:
        new_restaurant_pizza = RestaurantPizza(
            price=data['price'],
            pizza_id=data['pizza_id'],
            restaurant_id=data['restaurant_id']
        )
        db.session.add(new_restaurant_pizza)
        db.session.commit()

        response_data = {
            "id": new_restaurant_pizza.id,
            "pizza": {
                "id": pizza.id,
                "name": pizza.name,
                "ingredients": pizza.ingredients
            },
            "pizza_id": pizza.id,
            "price": new_restaurant_pizza.price,
            "restaurant": {
                "id": restaurant.id,
                "name": restaurant.name,
                "address": restaurant.address
            },
            "restaurant_id": restaurant.id
        }
        return make_response(response_data, 201)

    except ValueError:
        return make_response({"errors": ["validation errors"]}, 400)

if __name__ == "__main__":
    app.run(port=5555, debug=True)