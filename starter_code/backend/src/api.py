import os
from flask import Flask, request, jsonify, abort, redirect
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth
import requests

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@COMPLETED uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

# ROUTES


# @app.route('/login')
# def login():
#     return redirect("https://setoapps.auth0.com/authorize?&audience=coffee&response_type=code&client_id=5uBXy4McPOt3F6hq9JwQG1JRrEJuBZhk&redirect_uri=http://127.0.0.1:5000/authenticate&scope=openid%20profile%20email&state=xyzABC123")


# @app.route('/authenticate')
# def authenticate():
#     headers = request.headers
#     print('HEADER IS', headers)
#     code = request.args.get('code')
#     url = "https://setoapps.auth0.com/oauth/token"
#     payload = "grant_type=authorization_code&client_id=5uBXy4McPOt3F6hq9JwQG1JRrEJuBZhk&client_secret=eJTnjfbCGxpUKZaaP9qvat1NvU2lc4bP8BuueQNiAwPD_6DgXJzVKBNAnm3GQwFy&code=" + \
#         code+"&redirect_uri=http://127.0.0.1:5000/"
#     headers = {"Content-type": "application/x-www-form-urlencoded"}
#     response = requests.post(url, data=payload, headers=headers)
#     data = response.json()
#     print('DATA', data)
#     token = data.get('access_token')
#     return json.dumps(data)


@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response


'''
@COMPLETED implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def get_drinks():
    try:
        drinks = Drink.query.order_by(Drink.id).all()
        return jsonify({
            'success': True,
            'drinks': [drink.short() for drink in drinks]
        })
    except:
        return jsonify({
            'success': False,
            'message': "The drink is not formatted correctly and can't be shown"
        })
    # drinks = Drink.query.all()
    # drinks_formated = [drink.short() for drink in drinks]

    # return jsonify({
    #     'success': True,
    #     'drinks': drinks_formated
    # })


'''
@COMPLETED implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drink_detail(jwt):
    drinks = [drink.long() for drink in Drink.query.all()]
    print(type(drinks))

    return jsonify({
        'success': True,
        'drinks': drinks
    })


'''
@COMPLETED implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(jwt):
    data = request.get_json()
    if 'title' and 'recipe' not in data:
        abort(422)

    title = data['title']
    recipe = json.dumps(data['recipe'])
    drink = Drink(title=title, recipe=recipe)

    drink.insert()

    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    })


'''
@COMPLETED implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(jwt, drink_id):
    drink = Drink.query.get(drink_id)
    if drink is None:
        abort(404)
    data = request.get_json()
    if 'title' in data:
        drink.title = data['title']
    if 'recipe' in data:
        drink.recipe = json.dumps(data['recipe'])
    drink.update()
    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    })


'''
@COMPLETED implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, drink_id):
    data = request.get_json()

    drink = Drink.query.get(drink_id)

    if drink is None:
        abort(404)

    drink.delete()

    return jsonify({
        'success': True,
        'delete': drink.id
    })


# Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@COMPLETED implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@COMPLETED implement error handler for 404
    error handler should conform to general task above 
'''


'''
@COMPLETED implement error handler for AuthError
    error handler should conform to general task above 
'''
