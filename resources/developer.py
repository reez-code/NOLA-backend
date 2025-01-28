from flask import make_response, request
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity

from models import DeveloperProfile, User
from config import db

class DeveloperDetails(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("description", required=True, help="Description is required")
    parser.add_argument("skills", required=True, help="Skills is required")
    parser.add_argument("available_time", required=True, help="Available time is required")
    parser.add_argument('github_account', required=True, help="Link to Github Account is required")
    parser.add_argument("education_level", required=True, help="Education Level is required")
    parser.add_argument("profile_picture", required=True, help="Profile Picture is required")

    @jwt_required()
    def post(self):
        jwt = get_jwt()
        if jwt["role"] in ["developer"]:
            data = self.parser.parse_args()
            try:
                user_id = get_jwt_identity()
                developer = DeveloperProfile(
                    description=data["description"],
                    skills=data["skills"],
                    available_time=data["available_time"],
                    github_account=data["github_account"],
                    education_level=data["education_level"],
                    profile_picture=data["profile_picture"],
                    user_id=user_id
                )
                db.session.add(developer)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                response =  {"errors": [str(e)], "status":"fail", "message":"Something went wrong"}
                return make_response(response, 422)
            
            response = {"message": "Details added successfully",
                        "status": "success",
                        "developer_details": developer.to_dict()}
            return make_response(response, 201)
        else:
            response = {"message": "Something went wrong", "status": "fail"}
            return make_response(response, 401)
        
    @jwt_required()
    def get(self, id=None):
        jwt = get_jwt()

        if jwt["role"] not in ["developer", "admin"]:
            response = {"message": "Something went wrong", "status": "fail"}
            return make_response(response, 401)
        
        if jwt["role"] in ["developer"]:
            user_id = get_jwt_identity()
        else:
            user_id = id

        if user_id:
            user = User.query.filter_by(id=user_id).first()
            if not user:
                response = {"message": "Something went wrong", "status": "fail"}
                return make_response(response, 404)
            response = user.to_dict()
            return make_response(response, 200)
        else:
            if jwt["role"] not in ["admin"]:
                response = {"message": "Something went wrong", "status": "fail"}
                return make_response(response, 401)
            developers = DeveloperProfile.query.all()
            if not developers:
                response = {"message": "Developers not found", "status": "fail"}
                return make_response(response, 404)
            response =  [developer.to_dict() for developer in developers]
            return {response, 200}

    
    @jwt_required()
    def patch(self):
        jwt = get_jwt()

        if jwt["role"] in ["developer"]:
            data = request.get_json()
            
            if not data:
                return make_response({"message": "No input data provided", "status": "fail"}, 400)
            
            try:
                user_id = get_jwt_identity()
                developer = DeveloperProfile.query.filter_by(user_id=user_id).first()
                
                if not developer:
                    return make_response({"message": "Developer not found", "status": "fail"}, 404)
                
                for attr in data:
                    setattr(developer, attr, data[attr])
                db.session.add(developer)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                response =  {"errors": [str(e)]}
                return make_response(response, 422)
            
            response = {
                "message": "Updated Successfully",
                "developer": developer.to_dict(),
                "status": "success"
            }
            return make_response(response, 200)
        else:
            response = {
                "message": "Something went wrong",
                "status": "fail"
            }
            return make_response(response, 401)
        
    @jwt_required()
    def delete(self, id=None):
        jwt = get_jwt()

        if jwt["role"] not in ["admin", "developer"]:
            return {"message": "Something went wrong"}, 401
        
        if jwt["role"] in ["developer"]:
            user_id = get_jwt_identity()
        else:
            user_id = id

        if not user_id:
            return make_response({"message": "Developer id is required", "status": "fail"}, 400)
        
        try:
            developer = User.query.filter_by(id=user_id).first()
            if not developer:
                return make_response({"message": "Developer not found", "status": "fail"}, 404)
            db.session.delete(developer)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            response =  {"errors": [str(e)]}
            return make_response(response, 422)
        
        response = {"message": "developer successfully deleted", "status": "success"}
        return make_response(response, 200)


