from flask import make_response, session, request
from flask_restful import Resource, reqparse
from flask_bcrypt import generate_password_hash
from flask_jwt_extended import create_access_token, jwt_required

from models import User, DeveloperProfile, ClientProfile
from config import db

class Signup(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('email', required=True, help='Email is required')
    parser.add_argument('username', required=True, help='First name is required')
    parser.add_argument('password', required=True, help='Password is required')
    parser.add_argument('role', required=True, help='Role is required (must be either developer or client)')
    
    def post(self):
        User.query.delete()
        data = self.parser.parse_args()

        # validate the role
        role = data["role"].lower()
        if role not in ["developer", "client", "admin"]:
             return {'message': 'Invalid role. Must be either developer or client', 'status': 'fail'}, 422
        
        # Check if the email already exists
        email = User.query.filter_by(email=data['email']).first()
        if email:
            return {'message': 'Email already exists', 'status': 'fail'}, 422
        
        # Create a new user instance
        try:
            user = User(
                email=data["email"],
                username=data["username"],
                role=role
            )
            user.password_hash = data["password"]
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            response = {"errors": [str(e)]}
            return make_response(response, 422)
        
        user_dict = user.to_dict()
        additional_claims = {"role": user_dict["role"]}
        access_token = create_access_token(identity=user_dict["id"],
                                           additional_claims=additional_claims)
        
        return {
            "message": "Registered Successfully",
            "status": "success",
            "user": {**user_dict, "role":user.role},
            "access_token": access_token
        }

class Login(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument("email", required=True, help="Email is required")
    parser.add_argument("password", required=True, help="Password is required")

    def post(self):
        data = self.parser.parse_args()

        user = User.query.filter_by(email=data["email"]).first()

        if user:
            if user.authenticate(data["password"]):
                user_dict = user.to_dict()
                additional_claims = {"role": user_dict["role"]}
                access_token = create_access_token(identity=user_dict["id"],
                                           additional_claims=additional_claims)
                return {
                    "message": "Registered Successfully",
                    "status": "success",
                    "user": {**user_dict, "role":user.role},
                    "access_token": access_token
                }
            else:
                return make_response({"error": "Invalid username/password", "status":"fail"}, 401)
        else:
            return make_response({"error": "Invalid username/password", "status":"fail"}, 401)
                
