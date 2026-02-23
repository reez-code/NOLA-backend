from flask import make_response, request
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from flask_jwt_extended.exceptions import JWTExtendedException


from models import ClientProfile, User, DeveloperProfile
from config import db


class ClientDetails(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("business_name", help="Business name")
    parser.add_argument("business_category", help="Business Category")
    parser.add_argument("business_description", help="Business Description")
    parser.add_argument("business_logo", help="Business logo")

    @jwt_required()
    def post(self):
        """Update client profile details"""
        data = self.parser.parse_args()
        jwt = get_jwt()

        if jwt["role"] not in ["client"]:
            return {"error": "Unauthorized", "status": "fail"}, 401
        
        try:
            user_id = get_jwt_identity()
            client_details = ClientProfile.query.filter_by(user_id=user_id).first()
            
            if not client_details:
                return {"error": "Client profile not found", "status": "fail"}, 404
            
            # Update fields that are provided
            if data.get("business_name"):
                client_details.business_name = data["business_name"]
            if data.get("business_category"):
                client_details.business_category = data["business_category"]
            if data.get("business_description"):
                client_details.business_description = data["business_description"]
            if data.get("business_logo"):
                client_details.business_logo = data["business_logo"]
            
            db.session.add(client_details)
            db.session.commit()
        except JWTExtendedException as jwt_err:
            return {"msg": str(jwt_err), "status": "fail"}, 400
        except Exception as e:
            db.session.rollback()
            response = {"errors": [str(e)], "status": "fail"}
            return make_response(response, 422)
        
        client_details_dict = client_details.to_dict()
        return make_response({**client_details_dict, "message": "Updated successfully", "status": "success"}, 200)
    
    @jwt_required()
    def get(self, client_id=None):
        jwt = get_jwt()

        if jwt["role"] not in ["client", "admin", "developer"]:
            return {"error": "Unauthorized", "status": "fail"}, 401

        if jwt["role"] in ["client"]: 
           user_id = get_jwt_identity()
        else:
            user_id = client_id

        if user_id:
            user = User.query.filter_by(id=user_id).first()
            if not user:
                return {"error": "Client not found", "status": "fail"}, 404
            response = user.to_dict()
            return make_response(response, 200)
        else:
            if jwt["role"] not in ["admin"]:
                return {"error": "Unauthorized", "status": "fail"}, 401
                 
            clients = ClientProfile.query.all()
            if not clients:
                 return {"error": "No clients found", "status": "fail"}, 404
            response = [client.to_dict() for client in clients]
            return make_response(response, 200)
        
        
        
    
    @jwt_required()
    def patch(self):
        jwt = get_jwt()
        if jwt["role"] not in ["client"]:
            return {"error": "Unauthorized", "status": "fail"}, 401
        
        data = request.get_json()

        if not data:
            return make_response({"message": "No input data provided", "status": "fail"}, 400)

        try:
            user_id = get_jwt_identity()
            client = ClientProfile.query.filter_by(user_id=user_id).first()

            if not client:
                return make_response({"message": "Client profile not found", "status": "fail"}, 404)
            
            for attr in data:
                if hasattr(client, attr):
                    setattr(client, attr, data[attr])
            db.session.add(client)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            response = {"errors": [str(e)]}
            return make_response(response, 422)
        
        response = {"message": "Client details updated successfully", "status": "success"}
        return make_response(response, 200)
        
    @jwt_required()
    def delete(self, client_id=None):
        jwt = get_jwt()

        if jwt["role"] not in ["client", "admin"]:
            return {"error": "Unauthorized", "status": "fail"}, 401
        
        if jwt["role"] in ["client"]:
            user_id = get_jwt_identity()
        else:
            user_id = client_id

        if not user_id:
            return {"error": "Client ID is required", "status": "fail"}, 400
        
        try:
            client = User.query.filter_by(id=user_id).first()
            if not client:
                    return make_response({"message": "Client not found", "status": "fail"}, 404)
            db.session.delete(client)
            db.session.commit()
        except Exception as e:
                    db.session.rollback()
                    response = {"errors": [str(e)], "status": "fail"}
                    return make_response(response, 422)
        
        response = {"message": "Client successfully deleted", "status": "success"}
        return make_response(response, 200)


class ClientApplicants(Resource):
    """Return developers visible to a specific client (applicants)"""

    @jwt_required()
    def get(self, client_id):
        jwt = get_jwt()

        # allow client to view their own applicants, admin to view any, developer for public view
        if jwt["role"] not in ["client", "admin", "developer"]:
            return {"error": "Unauthorized", "status": "fail"}, 401

        # if requester is client, ensure they can only fetch their own list unless admin
        if jwt["role"] == "client":
            requester_id = get_jwt_identity()
            if int(requester_id) != int(client_id):
                return {"error": "Unauthorized", "status": "fail"}, 401

        # find client profile
        client_profile = ClientProfile.query.filter_by(user_id=client_id).first()
        if not client_profile:
            return {"error": "Client profile not found", "status": "fail"}, 404

        developers = client_profile.developers or []
        result = [dev.user.to_dict() for dev in developers]
        return {"developers": result, "status": "success"}, 200







            




            

        

                



