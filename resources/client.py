from flask import make_response, request
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from flask_jwt_extended.exceptions import JWTExtendedException


from models import ClientProfile, User
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
        else:
            return {"error": "Something went wrong"}, 401
    
    @jwt_required()
    def get(self, client_id=None):
        jwt = get_jwt()

        if jwt["role"] not in ["client", "admin"]:
            return {"error": "Something went wrong"}, 401

        if jwt["role"] in ["client"]: 
           user_id = get_jwt_identity()

        user_id = client_id

        if user_id:
            user = User.query.filter_by(id=user_id).first()
            if not user:
                return {"error": "Client not found"}, 404
            response = user.to_dict()
            return make_response(response, 200)
        else:
            if jwt["role"] not in ["admin"]:
                return {"error": "Something went wrong"}, 401
                 
            clients = ClientProfile.query.all()
            if not clients:
                 return {"error": "No clients found"}, 404
            response = [client.to_dict() for client in clients]
            return make_response(response, 200)
        
        
        
    
    @jwt_required()
    def patch(self):
        jwt = get_jwt()
        if jwt["role"] in ["client"]:
            data = request.get_json()

            if not data:
                return make_response({"message": "No input data provided", "status": "fail"}, 400)

            try:
                user_id = get_jwt_identity()
                client = ClientProfile.query.filter_by(user_id=user_id).first()

                if not client:
                    return make_response({"message": "Client not found", "status": "fail"}, 404)
                
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
            return {"error": "Something went wrong"}, 401
        
    @jwt_required()
    def delete(self, client_id=None):
        jwt = get_jwt()

        if jwt["role"] not in ["client", "admin"]:
            return {"error": "Something went wrong"}, 401
        
        if jwt["role"] in ["client"]:
            user_id = get_jwt_identity()
        user_id = client_id

        if not user_id:
            return {"error": "Client ID is required"}, 400
        
        try:
            client = User.query.filter_by(id=user_id).first()
            if not client:
                    return make_response({"message": "Client not found", "status": "fail"}, 404)
            db.session.delete(client)
            db.session.commit()
        except Exception as e:
                    db.session.rollback()
                    response = {"errors": [str(e)]}
                    return make_response(response, 422)
        
        response = {"message": "client successfully deleted", "status": "success"}
        return make_response(response, 200)
        







            




            

        

                



