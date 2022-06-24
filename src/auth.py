from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import generate_password_hash, check_password_hash
from flasgger import swag_from

import validators
from src.constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_409_CONFLICT
from src.database import db


auth = Blueprint("auth", __name__, url_prefix="/")

@auth.post("register")
def register():
    first_name = request.json['first_name']
    last_name = request.json['last_name']
    email = request.json['email']
    password = request.json['password']
    
    #print(first_name, last_name, email, password)
    
    if len(password) < 6:
        return jsonify({"error": "Password too short","status": 400}), HTTP_400_BAD_REQUEST
    
    if not validators.email(email):
        return jsonify({"error": "Email not valid","status": 400}), HTTP_400_BAD_REQUEST
    

    if db.users.find_one({"email":email}) is not None:
        return jsonify({"error": "Email already exist","status": 409}), HTTP_409_CONFLICT
    
    pwd_hash=generate_password_hash(password)
    
    try:
      userResponse=db.users.insert_one({"first_name":first_name, "last_name":last_name, "email":email, "password":pwd_hash})
      if userResponse.inserted_id:
          return jsonify({
              "message": "User created",
              "status": 200,
              "user": {
                  "_id": str(userResponse.inserted_id),
                  "first_name":first_name,
                  "last_name":last_name,
                  "email":email, 
              }
        }), HTTP_201_CREATED
      
    except Exception as ex:
        print(ex)
        
        return jsonify({"error": "Error creating user","status": 400}), HTTP_400_BAD_REQUEST
    

@auth.post("login")
@swag_from('./docs/auth/login.yaml')
def login():
    email = request.json.get('email','')
    password = request.json.get('password','')
    
    user = db.users.find_one({"email":email})
    
    if user is not None:
        is_pass_correct = check_password_hash(user['password'], password)
        
        if is_pass_correct:
            refresh = create_refresh_token(identity=str(user['_id']))
            access = create_access_token(identity=str(user['_id']))

            return jsonify({
                "message": "login successful",
                "status": 200,
                'user': {
                    'refresh': refresh,
                    'access': access,
                    '_id': str(user['_id']),
                    'first_name': user['first_name'],
                    'last_name': user['last_name'],
                    'email': user['email'],
                }

            }), HTTP_200_OK

    return jsonify({'error': 'Wrong credentials','status': 401}), HTTP_401_UNAUTHORIZED
