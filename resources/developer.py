from flask import make_response, request
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity

from models import DeveloperProfile, User
from config import db

class DeveloperDetails(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("profession", help="Profession")
    parser.add_argument("description", help="Description")
    parser.add_argument("skills", help="Skills")
    parser.add_argument("available_time", help="Available time")
    parser.add_argument('github_account', help="Link to Github Account")
    parser.add_argument("education_level", help="Education Level")
    parser.add_argument("profile_picture", help="Profile Picture")
    parser.add_argument('linkedin_account', help="LinkedIn account link")
    parser.add_argument("years_of_experience", type=int, help="Years of experience")

    @jwt_required()
    def post(self):
        """Update developer profile details"""
        jwt = get_jwt()
        if jwt["role"] not in ["developer"]:
            response = {"message": "Unauthorized", "status": "fail"}
            return make_response(response, 401)
        
        data = self.parser.parse_args()
        try:
            user_id = get_jwt_identity()
            developer = DeveloperProfile.query.filter_by(user_id=user_id).first()
            
            if not developer:
                response = {"message": "Developer profile not found", "status": "fail"}
                return make_response(response, 404)
            
            # Update fields that are provided
            if data.get("profession"):
                developer.profession = data["profession"]
            if data.get("description"):
                developer.description = data["description"]
            if data.get("skills"):
                developer.skills = data["skills"]
            if data.get("available_time"):
                developer.available_time = data["available_time"]
            if data.get("github_account"):
                developer.github_account = data["github_account"]
            if data.get("linkedin_account"):
                developer.linkedin_account = data["linkedin_account"]
            if data.get("education_level"):
                developer.education_level = data["education_level"]
            if data.get("profile_picture"):
                developer.profile_picture = data["profile_picture"]
            if data.get("years_of_experience"):
                developer.years_of_experience = data["years_of_experience"]
            
            db.session.add(developer)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            response =  {"errors": [str(e)], "status":"fail", "message":"Something went wrong"}
            return make_response(response, 422)
        
        response = {"message": "Details updated successfully",
                    "status": "success",
                    "developer_details": developer.to_dict()}
        return make_response(response, 200)
        
    @jwt_required()
    def get(self, id=None):
        jwt = get_jwt()

        if jwt["role"] not in ["developer", "admin", "client"]:
            response = {"message": "Unauthorized", "status": "fail"}
            return make_response(response, 401)
        
        if jwt["role"] in ["developer"]:
            user_id = get_jwt_identity()
        else:
            user_id = id

        if user_id:
            user = User.query.filter_by(id=user_id).first()
            if not user:
                response = {"message": "User not found", "status": "fail"}
                return make_response(response, 404)
            response = user.to_dict()
            return make_response(response, 200)
        else:
            if jwt["role"] not in ["admin"]:
                response = {"message": "Unauthorized", "status": "fail"}
                return make_response(response, 401)
            developers = DeveloperProfile.query.all()
            if not developers:
                response = {"message": "Developers not found", "status": "fail"}
                return make_response(response, 404)
            response =  [developer.to_dict() for developer in developers]
            return make_response(response, 200)

    
    @jwt_required()
    def patch(self):
        jwt = get_jwt()

        if jwt["role"] not in ["developer"]:
            response = {
                "message": "Unauthorized",
                "status": "fail"
            }
            return make_response(response, 401)
        
        data = request.get_json()
        
        if not data:
            return make_response({"message": "No input data provided", "status": "fail"}, 400)
        
        try:
            user_id = get_jwt_identity()
            developer = DeveloperProfile.query.filter_by(user_id=user_id).first()
            
            if not developer:
                return make_response({"message": "Developer profile not found", "status": "fail"}, 404)
            
            for attr in data:
                if hasattr(developer, attr):
                    setattr(developer, attr, data[attr])
            db.session.add(developer)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            response =  {"errors": [str(e)]}
            return make_response(response, 422)
        
        response = {
            "message": "Profile updated successfully",
            "developer": developer.to_dict(),
            "status": "success"
        }
        return make_response(response, 200)
        
    @jwt_required()
    def delete(self, id=None):
        jwt = get_jwt()

        if jwt["role"] not in ["admin", "developer"]:
            return {"message": "Unauthorized", "status": "fail"}, 401
        
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
        
        response = {"message": "Developer successfully deleted", "status": "success"}
        return make_response(response, 200)
