#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
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

@app.route("/restaurants")
def get_restaurants():
    restaurants = [restaurant.to_dict() for restaurant in Restaurant.query.all()]
    return make_response(jsonify(restaurants), 200)

@app.route("/restaurants/<int:id>", methods=['GET', 'DELETE'])
def handle_restaurants(id):
    restaurant = Restaurant.query.filter_by(id=id).first()

    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404

    # Get request
    if request.method == 'GET':
        try:
            return make_response(jsonify(restaurant.to_dict(rules=("restaurant_pizzas", "-restaurant_pizzas.restaurants"))), 200)
        except Exception as e:
            return make_response(jsonify({"errors": [str(e)]}), 404)
        
    # Delete request
    if request.method == 'DELETE':
        try:
            db.session.delete(restaurant)
            db.session.commit()
            return make_response(jsonify({}), 204)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({"errors": [str(e)]}), 500)
        
@app.route('/pizzas')
def get_pizzas():
    pizzas = [pizza.to_dict() for pizza in Pizza.query.all()]
    return make_response(jsonify(pizzas), 200)

@app.route('/restaurant_pizzas', methods=['POST'])
def handle_restaurant_pizzas():
    data = request.get_json()
    price = data.get('price')
    pizza_id = data.get('pizza_id')
    restaurant_id = data.get('restaurant_id')

    if request.method == 'POST':
        try:
            new_restaurant_pizza = RestaurantPizza(
                price=price,
                pizza_id=pizza_id,
                restaurant_id=restaurant_id
            )
            db.session.add(new_restaurant_pizza)
            db.session.commit()
            return make_response(jsonify(new_restaurant_pizza.to_dict()), 201)
        except Exception as e:
            return make_response(jsonify({"errors": [str(e)]}), 400)
    
if __name__ == "__main__":
    app.run(port=5555, debug=True)
