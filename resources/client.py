from flask import make_response
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from flask_jwt_extended.exceptions import JWTExtendedException


from models import ClientProfile, User, Job
from config import db


class ClientDetails(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("business_name", required=True, help="Business name is required")
    parser.add_argument("business_description", required=True, help="Business Description is required")
    parser.add_argument("logo", required=True, help="Logo is required")

    @jwt_required()
    def post(self):
        data = self.parser.parse_args()
        jwt = get_jwt()

        if jwt["role"] in ["client"]:
            try:
                user_id = get_jwt_identity()

                client_details = ClientProfile(
                    business_name=data["business_name"],
                    business_description=data["business_description"],
                    logo=data["logo"],
                    user_id=int(user_id)
                )
                db.session.add(client_details)
                db.session.commit()
            except JWTExtendedException as jwt_err:
                return {"msg": str(jwt_err)}, 400
            except Exception as e:
                db.session.rollback()
                response = {"errors": [str(e)]}
                return make_response(response, 422)
            
            client_details_dict = client_details.to_dict()
            return make_response(client_details_dict, 201)
    
    @jwt_required()
    def get(self):
        jwt = get_jwt()

        if jwt["role"] in ["client", "admin"]:
                user_id = get_jwt_identity()
                user = User.query.filter_by(id=user_id).first()

                if user:
                    response = user.to_dict()
                    return make_response(response, 200)
                else:
                    return {"error": "Client not found"}, 404
        else:
            return {"error": "You are not authorized to access this"}, 422
    
    @jwt_required()
    def patch(self):
        jwt = get_jwt()
        if jwt["role"] in ["client"]:
            data = self.parser.parse_args()
            try:
                user_id = get_jwt_identity()
                client = ClientProfile.query.filter_by(id=user_id).first()
                for attr in data:
                    setattr(client, attr, data[attr])
                db.session.add(client)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                response = {"errors": [str(e)]}
                return make_response(response, 422)
            
            response = {"message": "Client details updated successfully"}
            return make_response(response, 200)
        else:
            return {"error": "You are not authorized to access this"}, 422
            

class JobResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("title", required=True, help="Title is required")
    parser.add_argument("description", required=True, help="Description is required")
    parser.add_argument("status", required=True, help="Status is required")

    @jwt_required()
    def post(self):
        data = self.parser.parse_args()
        jwt = get_jwt()
        status = data["status"].lower()

        if jwt["role"] in ["client"]:
            try:
                user_id = get_jwt_identity()

                job = Job(
                    title=data["title"],
                    description=data["description"],
                    status=status,
                    client_id=int(user_id)
                )
                db.session.add(job)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                response = {"errors": [str(e)]}
                return make_response(response, 422)
        
        job_dict = job.to_dict()
        return make_response(job_dict, 201)

            

        

                



