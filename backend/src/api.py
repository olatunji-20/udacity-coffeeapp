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

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
with app.app_context():
    db_drop_and_create_all()

# ROUTES
# this route is to test the homeroute

@app.route("/", methods=["GET"])
def home_page():

    return jsonify({
        "message": "WELCOME TO THE COFFEE SHOP PROJECT"
    })

'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''



@app.route("/drinks", methods=["GET"])
def get_short_drinks():
    try:
        # this is to get all the drinks in the collection
        drinks = Drink.query.all()
        print(drinks)

        # to get the drinks with the .short() data representation
        short_drinks = [drink.short() for drink in drinks]
        print(short_drinks)

        return jsonify({
            "success": True,
            "drinks": short_drinks
        }), 200

    except:
        abort(422)

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route("/drinks-detail", methods=["GET"])
def get_long_drinks():
    try:
        # this is to get all the drinks in the collection
        drinks = Drink.query.all()
        print(drinks)

        # to get the drinks with the .long() data representation
        long_drinks = [drink.long() for drink in drinks]
        print(long_drinks)

        return jsonify({
            "success": True,
            "drinks": long_drinks
        }), 200

    except:
        abort(422)




'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

@app.route("/drinks", methods=["POST"])
def upload_drinks():
    try:
        # to get the details of the newly uploaded drinks
        drink_title = data["title"]
        drink_recipes = json.dumps(data["recipe"])

        # make the new drink model
        new_drink = Drink(title=drink_title, recipe=drink_recipes)

        # add new drink to the drinks collection
        new_drink.insert()

        drinks = Drink.query.all()
        long_drinks = [drink.long() for drink in drinks]

        return jsonify({
            "success": True,
            "drinks": long_drinks
        }), 200

    except:
        abort(422)



'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''

@app.route("/drinks/<int:id>", methods=["PATCH"])
def modify_drink(id):
    # to get the id of th drink that is to be modified
    this_drink = Drinks.query.all(id)

    # to check if the drink exists
    if len(this_drink) == 0:
        abort(404)
    
    # to get the body of the information about the drink to be updated
    details = request.get_json()

    # title to be updated
    this_drink.title = details["title"]

    # recipe to be updated
    this_drink.recipe = json.dumps(details["recipe"])

    this_drink.update()

    # get all drinks so as to select the ones with .long() data representation
    drinks = Drink.query.all()
    long_drinks = [drink.long() for drink in drinks]

    return jssonify({
        "success": True,
        "drinks": long_drinks
    }), 200






'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''

@app.route("/drinks/<int:id>", methods=["DELETE"])
def remove_drink(id):

    this_drink = Drink.query.all(id)

    if len(this_drink) == 0:
        abort(404)

    this_drink.delete()

    return jsonify({
        "success": True,
        "delete": this_drink.id
    }), 200



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
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "RESOURCE CANNOT BE FOUND"
    }), 404

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "PERMISSION DENIED"
    }), 401


@app.errorhandler(AuthError)
def process_AuthError(error):
    response = jsonify(error.error)
    response.status_code = error.status_code
    return response