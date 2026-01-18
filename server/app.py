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


# Ensure tables exist for test runs / simple setup
with app.app_context():
    db.create_all()


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


@app.route('/restaurants')
def get_restaurants():
    restaurants = Restaurant.query.all()
    restaurants_list = []
    for r in restaurants:
        d = r.to_dict()
        d.pop('restaurant_pizzas', None)
        restaurants_list.append(d)
    return make_response(jsonify(restaurants_list), 200)


@app.route('/restaurants/<int:id>')
def get_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return make_response(jsonify({'error': 'Restaurant not found'}), 404)
    # include restaurant_pizzas and nested pizza
    return make_response(jsonify(restaurant.to_dict()), 200)


@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return make_response(jsonify({'error': 'Restaurant not found'}), 404)
    db.session.delete(restaurant)
    db.session.commit()
    return ('', 204)


@app.route('/pizzas')
def get_pizzas():
    pizzas = Pizza.query.all()
    pizzas_list = []
    for p in pizzas:
        d = p.to_dict()
        d.pop('restaurant_pizzas', None)
        pizzas_list.append(d)
    return make_response(jsonify(pizzas_list), 200)


@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.get_json()
    try:
        rp = RestaurantPizza(
            price=data['price'],
            pizza_id=data['pizza_id'],
            restaurant_id=data['restaurant_id']
        )
        db.session.add(rp)
        db.session.commit()
        return make_response(jsonify(rp.to_dict()), 201)
    except Exception:
        db.session.rollback()
        return make_response(jsonify({'errors': ['validation errors']}), 400)


if __name__ == "__main__":
    app.run(port=5555, debug=True)
