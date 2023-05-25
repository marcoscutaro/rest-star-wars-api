"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, Character, Planet, User
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/characters', methods=['GET'])
def handle_characters():

    characters = Character.query.all()
    characters_list = list(map(lambda character: character.serialize_all(), characters))

    response_body = {
        "message": "ok",
        "results": characters_list
    }

    return jsonify(response_body), 200

@app.route('/characeters/<int:id>', methods=['GET'])
def handle_character():

    ind_character = Character.query.get(id)

    response_body = {
        "message": "ok",
        "results": ind_character.serialize_each()
    }

    return jsonify(response_body), 200

@app.route('/createcharacter', methods=["POST"])
def create_character():
    body = json.loads(request.data)
    new_character = Character(name=body["name"], gender=body["gender"])
    db.session.add(new_character)
    db.session.commit()

    return "ok", 200


@app.route('/planets', methods=['GET'])
def handle_planets():

    planets = Planet.query.all()
    planets_list = list(map(lambda planet: planet.serialize_all(), planets))

    response_body = {
        "message": "ok",
        "results": planets_list
    }

    return jsonify(response_body), 200

@app.route('/planets/<int:id>', methods=['GET'])
def handle_planet():

    ind_planet = Planet.query.get(id)

    response_body = {
        "message": "ok",
        "results": ind_planet.serialize_each()
    }

    return jsonify(response_body), 200

@app.route('/createplanet', methods=["POST"])
def create_planet():
    body = json.loads(request.data)
    new_planet = Planet(name=body["name"], population=body["population"], diameter=body["diameter"])
    db.session.add(new_planet)
    db.session.commit()

    return "ok", 200

@app.route('/users', methods=['GET'])
def handle_users():
        users = User.query.all()
        users_info =list(map(lambda user: user.serialize_user(), users))
        response_body = users_info
        return jsonify(response_body), 200

@app.route('/newuser', methods=["POST"])
def create_user():
    body = json.loads(request.data)
    new_user = User(name=body["name"])
    db.session.add(new_user)
    db.session.commit()

    return "ok", 200

@app.route('/user/<int:id>/favorites', methods=['GET'])
def handling_favoritos(user_id):

    select_character = User.query.filter_by(id=user_id).first().characterFavorite
    select_planet = User.query.filter_by(id=user_id).first().planetsFavorite
    Character = list(map(lambda obj: obj.serialize(), select_character))
    Planets = list(map(lambda obj: obj.serialize(), select_planet))

    return jsonify({
        "CharacterFavorite": Character,
        "PlanetsFavorite": Planets
    }), 200

@app.route('/favorite/character/<int:id>', methods=['POST'])
def add_character(characterid, userid):
    user_id = userid
    user = User.query.get(user_id)
    character = Character.query.get(characterid)
    favList = User.query.filter_by(id=user_id).first().characterFavorite
    favList.append(character)
    db.session.commit()

    return jsonify({
        "characterFavorite": list(map(lambda obj: obj.serialize_user(), favList))
    }), 200

@app.route('/favorite/planet/<int:id>', methods=['POST'])
def add_planet(planetid, userid):
    user_id = userid
    user = User.query.get(user_id)
    planet = Planet.query.get(planetid)
    favList = User.query.filter_by(id=user_id).first().planetsFavorite
    favList.append(planet)
    db.session.commit()

    return jsonify({
        "planetsFavorite": list(map(lambda obj: obj.serialize_user(), favList))
    }), 200

@app.route('/favorite/character/<int:id>', methods=['DELETE'])
def removeFavCharacter(characterid, userid):
    user_id = userid
    user = User.query.get(user_id)
    character = Character.query.get(characterid)
    favList = User.query.filter_by(id=user_id).first().characterFavorite
    favList.remove(character)
    db.session.commit()

    return jsonify({
        "characterFavorite": list(map(lambda obj: obj.serialize_user(), favList))
    }), 200

@app.route('/favorite/character/<int:id>', methods=['DELETE'])
def removeFavPlanet(planetid, userid):
    user_id = userid
    user = User.query.get(user_id)
    planet = Planet.query.get(planetid)
    favList = User.query.filter_by(id=user_id).first().planetsFavorite
    favList.remove(planet)
    db.session.commit()

    return jsonify({
        "planetsFavorite": list(map(lambda obj: obj.serialize_user(), favList))
    }), 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
