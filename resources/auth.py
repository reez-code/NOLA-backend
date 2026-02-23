from flask import make_response
from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token, jwt_required

from models import User, DeveloperProfile, ClientProfile
from config import db

class Signup(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('role', required=True, help='Role is required (must be developer, client, or admin)')
    
    # Common fields
    parser.add_argument('email', required=True, help='Email is required')
    parser.add_argument('password', required=True, help='Password is required')
    
    # Business/Client fields
    parser.add_argument('business_name', help='Business name is required for clients')
    parser.add_argument('business_category', help='Business category is required for clients')
    parser.add_argument('fullname', help='Full name is required for clients')
    parser.add_argument('business_description', help='Business description is required for clients')
    parser.add_argument('business_logo', help='Business logo is required for clients')
    
    # Developer fields
    parser.add_argument('username', help='Username is required for developers')
    parser.add_argument('profession', help='Profession is required for developers')
    parser.add_argument('profile_picture', help='Profile picture is required for developers')
    parser.add_argument('github_account', help='GitHub account link (optional)')
    parser.add_argument('linkedin_account', help='LinkedIn account link (optional)')
    
    # Admin fields
    parser.add_argument('firstname', help='First name is required for admins')
    
    def post(self):
        data = self.parser.parse_args()

        # validate the role
        role = data["role"].lower()
        if role not in ["developer", "client", "admin"]:
             return {'message': 'Invalid role. Must be developer, client, or admin', 'status': 'fail'}, 422
        
        # Check if the email already exists
        email = User.query.filter_by(email=data['email']).first()
        if email:
            return {'message': 'Email already exists', 'status': 'fail'}, 422
        
        try:
            if role == "client":
                # Validate required fields for client
                if not data.get('business_name') or not data.get('fullname') or \
                   not data.get('business_category') or not data.get('business_description') or not data.get('business_logo'):
                    return {'message': 'Missing required fields for client registration', 'status': 'fail'}, 422
                
                # Split fullname into first and last name
                fullname_parts = data['fullname'].strip().split(' ', 1)
                first_name = fullname_parts[0]
                last_name = fullname_parts[1] if len(fullname_parts) > 1 else ''
                
                user = User(
                    email=data["email"],
                    first_name=first_name,
                    last_name=last_name,
                    role="client"
                )
                user.password_hash = data["password"]
                db.session.add(user)
                db.session.flush()
                
                # Create client profile
                client_profile = ClientProfile(
                    user_id=user.id,
                    business_name=data['business_name'],
                    business_category=data['business_category'],
                    business_description=data['business_description'],
                    business_logo=data['business_logo']
                )
                db.session.add(client_profile)
                
            elif role == "developer":
                # Validate required fields for developer
                if not data.get('username') or not data.get('profession') or not data.get('profile_picture'):
                    return {'message': 'Missing required fields for developer registration', 'status': 'fail'}, 422
                
                # For developer, use username as first_name and last_name can be empty
                user = User(
                    email=data["email"],
                    first_name=data['username'],
                    last_name='',
                    role="developer"
                )
                user.password_hash = data["password"]
                db.session.add(user)
                db.session.flush()
                
                # Create developer profile
                developer_profile = DeveloperProfile(
                    user_id=user.id,
                    profession=data['profession'],
                    profile_picture=data['profile_picture'],
                    github_account=data.get('github_account'),
                    linkedin_account=data.get('linkedin_account')
                )
                db.session.add(developer_profile)
                
            elif role == "admin":
                # Validate required fields for admin
                if not data.get('firstname'):
                    return {'message': 'First name is required for admin registration', 'status': 'fail'}, 422
                
                user = User(
                    email=data["email"],
                    first_name=data['firstname'],
                    last_name='',
                    role="admin"
                )
                user.password_hash = data["password"]
                db.session.add(user)
            
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            response = {"errors": [str(e)], "status": "fail", "message": "Registration failed"}
            return make_response(response, 422)
        
        user_dict = user.to_dict()
        additional_claims = {"role": user_dict["role"].lower()}
        access_token = create_access_token(identity=str(user.id),
                                           additional_claims=additional_claims)
        
        return {
            "message": "Registered Successfully",
            "status": "success",
            "user": {**user_dict, "role":user.role},
            "access_token": access_token
        }, 201

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
                additional_claims = {"role": user_dict["role"].lower()}
                access_token = create_access_token(identity=str(user.id),
                                           additional_claims=additional_claims)
                return {
                    "message": "Logged in Successfully",
                    "status": "success",
                    "user": {**user_dict, "role":user.role},
                    "access_token": access_token
                },201
            else:
                return make_response({"error": "Invalid username/password", "status":"fail"}, 401)
        else:
            return make_response({"error": "Invalid username/password", "status":"fail"}, 401)
    
class Logout(Resource):
    @jwt_required()
    def post(self):
        #jwt handles log out by removing the token from client side
        return {"message": "Logged out successfully"}, 200
