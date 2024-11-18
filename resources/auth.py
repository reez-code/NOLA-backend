from flask_restful import Resource, reqparse
from flask_bcrypt import generate_password_hash
from flask_jwt_extended import create_access_token, jwt_required

from models import User, DeveloperProfile, ClientProfile

class SignupResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('email', required=True, help='Email is required')
    parser.add_argument('username', required=True, help='First name is required')
    parser.add_argument('password', required=True, help='Password is required')