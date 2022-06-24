from hashlib import new
import json
from os import stat
from flask import Blueprint, Response, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson.objectid import ObjectId
from src.constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND
from src.database import db

def getAllDataWithObjectIdToString(list):
    newlist = []
    if len(list) > 0:
        for item in list:
             item['_id'] = str(item['_id'])
             item['user_id'] = str(item['user_id'])
             newlist.append(item)
    
    return newlist

            
            
            

temp = Blueprint("temp", __name__, url_prefix="/")

@temp.post("template")
@jwt_required()
def post_template(): 
    template_name = request.json.get('template_name','')
    subject = request.json.get('subject','')
    body = request.json.get('body','')
    
    _id = get_jwt_identity()
    user = db.users.find_one({"_id":ObjectId(_id)})
    
    
    if user is not None:
        try:
           tempResponse = db.template.insert_one({"template_name":template_name, "subject":subject, "body":body, "user_id": ObjectId(_id) })
           
           if tempResponse.inserted_id:
                return jsonify({
                    "message": "Template created",
                    "results":{
                        "_id": str(tempResponse.inserted_id),
                        "template_name":template_name,
                        "subject":subject,
                        "body":body,
                        "user": {
                            "_id": str(user['_id'],),
                            "first_name":user['first_name'],
                            "last_name":user['last_name'],
                            "email":user['email']
                       }
                    },
                    "status": 200
                    
                }), HTTP_201_CREATED
        
           return jsonify({'message': 'Template could not be created', 'status': 400}), HTTP_404_NOT_FOUND
       
        except Exception as ex:
            print(ex)
            
            return jsonify({"error": "Error creating template","status": 400}), HTTP_400_BAD_REQUEST
    
    
    return jsonify({'error': 'User not found','status': 401}), HTTP_401_UNAUTHORIZED



@temp.get("template")
@jwt_required()
def get_all_template():
    
    _id = get_jwt_identity()
    user = db.users.find_one({"_id":ObjectId(_id)})
    
    if user is not None:
        try:
            allTempResponse = list(db.template.find({"user_id":ObjectId(_id)}))
            convertedList  = getAllDataWithObjectIdToString(allTempResponse)
            return jsonify({
                        "message": "fetched all templates",
                        "results":{
                            "templates":convertedList,
                            "user": {
                                "_id": str(user['_id'],),
                                "first_name":user['first_name'],
                                "last_name":user['last_name'],
                                "email":user['email']
                        }
                        },
                        "status": 200}
                        ), HTTP_200_OK
        except Exception as ex:
            print(ex)
            
            return jsonify({"error": "Error fetching all template","status": 400}), HTTP_400_BAD_REQUEST
        
    
    return jsonify({'error': 'User not found','status': 401}), HTTP_401_UNAUTHORIZED



@temp.get("template/<string:template_id>")
@jwt_required()
def get_single_template(template_id):
    
    _id = get_jwt_identity()
    user = db.users.find_one({"_id":ObjectId(_id)})
    
    if user is not None:
        try:
            singleTemp = db.template.find_one(
                {"_id":ObjectId(template_id),"user_id": ObjectId(_id)}
                )
            
            if singleTemp :
                
                return jsonify({
                    "message": "success",
                    "results":{
                        "_id": str(singleTemp['_id']),
                        "template_name": singleTemp['template_name'],
                        "subject":singleTemp['subject'],
                        "body":singleTemp['body'],
                        "user": {
                            "_id": str(user['_id'],),
                            "first_name":user['first_name'],
                            "last_name":user['last_name'],
                            "email":user['email']
                       }
                    },
                    "status": 200
                    
                }), HTTP_200_OK
                
            return jsonify({'message': 'Template not found'}), HTTP_404_NOT_FOUND
                
        except Exception as ex:
            print(ex)
            
            return jsonify({"error": "Error fetching template","status": 400}), HTTP_400_BAD_REQUEST
        
    return jsonify({'error': 'User not found','status': 401}), HTTP_401_UNAUTHORIZED


@temp.put("template/<string:template_id>")
@temp.patch("template/<string:template_id>")
@jwt_required()
def update_template(template_id):
    
    template_name = request.json.get('template_name','')
    subject = request.json.get('subject','')
    body = request.json.get('body','')
    
    _id = get_jwt_identity()
    user = db.users.find_one({"_id":ObjectId(_id)})
    
    if user is not None:
        try:
            updateTemp = db.template.update_one(
                {"_id":ObjectId(template_id),"user_id": ObjectId(_id)},
                {"$set":{ "template_name":template_name, "subject":subject, "body":body }}
            )
            if updateTemp.modified_count:
                return jsonify({
                    "_id":str(template_id),
                    "message": "success",
                    "details": "updated template",
                    "status": 200
                }), HTTP_200_OK
                
            return jsonify({'message': 'Could not update template','status': 404}), HTTP_404_NOT_FOUND
            
        except Exception as ex:
            print(ex)
            return jsonify({"error": "Error Updating template","status": 400}), HTTP_400_BAD_REQUEST
        
        
    return jsonify({'error': 'User not found','status': 401}), HTTP_401_UNAUTHORIZED



@temp.delete("template/<string:template_id>")
@jwt_required()
def delete_template(template_id):
        
    _id = get_jwt_identity()
    user = db.users.find_one({"_id":ObjectId(_id)})
    
    if user is not None:
        try:
            deleteTemp = db.template.delete_one(
                {"_id":ObjectId(template_id),"user_id": ObjectId(_id)},
            )
           
            print(deleteTemp)
            if deleteTemp.deleted_count:
                return jsonify({
                    "message": "success",
                    "_id": template_id,
                    "status": 200
                }), HTTP_200_OK
            
            return jsonify({'message': 'Could not delete template'}), HTTP_404_NOT_FOUND
            
        except Exception as ex:
            print(ex)
            return jsonify({"error": "Error deleting template","status": 400}), HTTP_400_BAD_REQUEST
        
    return jsonify({'error': 'Wrong credentials','status': 401}), HTTP_401_UNAUTHORIZED