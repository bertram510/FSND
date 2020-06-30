import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

# DONE initialize the datbase
db_drop_and_create_all()


# ----------------------------------------------------------------------------#
# API Endpoints
# ----------------------------------------------------------------------------#
@app.route('/drinks', methods=['GET'])
def get_drinks():
    '''
    DONE implement endpoint
        GET /drinks
            it should be a public endpoint
            it should contain only the drink.short() data representation
        returns status code 200 and json {"success": True, "drinks": drinks}
        where drinks is the list of drinks
            or appropriate status code indicating reason for failure
    '''
    drinks = Drink.query.order_by(Drink.id).all()
    if not drinks:
        abort(404)

    formatted_drinks = [drink.short() for drink in drinks]

    return jsonify({
        'success': True,
        'drinks': formatted_drinks
    })


@app.route('/drinks-detail',  methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    '''
    DONE implement endpoint
        GET /drinks-detail
            it should require the 'get:drinks-detail' permission
            it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drinks}
        where drinks is the list of drinks
            or appropriate status code indicating reason for failure
    '''
    drinks = Drink.query.order_by(Drink.id).all()
    if not drinks:
        abort(404)

    formatted_drinks = [drink.long() for drink in drinks]

    return jsonify({
        'success': True,
        'drinks': formatted_drinks
    })


@app.route('/drinks',  methods=['POST'])
@requires_auth('post:drinks')
def create_drinks(payload):
    '''
    DONE implement endpoint
        POST /drinks
            it should create a new row in the drinks table
            it should require the 'post:drinks' permission
            it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drink}
        where drink an array containing only the newly created drink
            or appropriate status code indicating reason for failure
    '''
    body = request.get_json()

    new_title = body.get('title', None)
    new_recipe = body.get('recipe', None)

    if new_title is None:
        abort(400)
    if new_recipe is None:
        abort(400)

    try:
        new_drink = Drink(title=new_title, recipe=json.dumps(new_recipe))

        new_drink.insert()
        return jsonify({
            'success': True,
            'drinks': [Drink.long(new_drink)]
        })
    except Exception:
        abort(422)


@app.route('/drinks/<int:drink_id>',  methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, drink_id):
    '''
    DONE implement endpoint
        PATCH /drinks/<id>
            where <id> is the existing model id
            it should respond with a 404 error if <id> is not found
            it should update the corresponding row for <id>
            it should require the 'patch:drinks' permission
            it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drink}
        where drink an array containing only the updated drink
            or appropriate status code indicating reason for failure
    '''
    body = request.get_json()

    update_drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

    if update_drink is None:
        abort(400)

    update_title = body.get('title', None)
    update_recipe = body.get('recipe', None)
    if update_title is None:
        abort(400)
    if update_recipe is None:
        abort(400)

    try:
        update_drink.title = update_title
        update_drink.recipe = json.dumps(update_recipe)
        update_drink.update()

        return jsonify({
            'success': True,
            'drinks': [Drink.long(update_drink)]
        })
    except Exception:
        abort(422)


@app.route('/drinks/<int:drink_id>',  methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks_by_id(payload, drink_id):
    '''
    DONE implement endpoint
        DELETE /drinks/<id>
            where <id> is the existing model id
            it should respond with a 404 error if <id> is not found
            it should delete the corresponding row for <id>
            it should require the 'delete:drinks' permission
        returns status code 200 and json {"success": True, "delete": id}
        where id is the id of the deleted record
            or appropriate status code indicating reason for failure
    '''
    delete_drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

    if delete_drink is None:
        abort(400)

    try:
        delete_drink.delete()
        return jsonify({
            'success': True,
            'delete': drink_id
        })
    except Exception:
        abort(422)


# Error Handling
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 422,
                    "message": "unprocessable"
                    }), 422


@app.errorhandler(404)
def ressource_not_found(error):
    return jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
                    "success": False,
                    "error": 400,
                    "message": "bad request"
                    }), 400


@app.errorhandler(AuthError)
def authentification_failed(AuthError):
    return jsonify({
                    "success": False,
                    "error": AuthError.status_code,
                    "message": "authentification failed"
                    }), 401
