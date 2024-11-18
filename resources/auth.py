from flask_restful import Resource, reqparse
from flask_bcrypt import generate_password_hash
from flask_jwt_extended import create_access_token, jwt_required

from models import User, DeveloperProfile, ClientProfile

class SignupResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('email', required=True, help='Email is required')
    parser.add_argument('username', required=True, help='First name is required')
    parser.add_argument('password', required=True, help='Password is required')
    parser.add_argument('role', required=True, help='Role is required (must be either developer, client or admin)')

    # additional arguments: Client
    parser.add_argument('business_name', help='business_name is required for clients')
    parser.add_argument('business_description', help='business_description is required for clients')
    parser.add_argument('logo', help='logo is required for clients')
    
    # additional arguments: Developer
    parser.add_argument("full_name", help="fullname is required for developers")
    parser.add_argument("description", help="description is required for developers") 
    parser.add_argument("github_account", help="github is required for developers")
    parser.add_argument("profile_picture", help="profile_picture is required for developers")
    parser.add_argument("skills", help="skills is required for developers")
    parser.add_argument("education_level", help="education_level is required for developers")
    parser.add_argument("available_time", help="available_time is required for developers")
