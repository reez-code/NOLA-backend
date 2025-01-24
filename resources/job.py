from flask import make_response, request
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from sqlalchemy import and_



from models import Job
from config import db

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
    
    @jwt_required()
    def get(self, id=None):
        jwt = get_jwt()

        if jwt["role"] in ["client", "developer"]:
            user_id = get_jwt_identity()
        else:
            user_id = None
        
        if user_id:
        
            if jwt["role"] in ["client"]:
                jobs = Job.query.filter_by(client_id=user_id).all()
            elif jwt["role"] in ["developer"]:
                jobs = Job.query.filter_by(developer_id=user_id).all()
            
            if jobs:
                    job = [job.to_dict() for job in jobs]
                    return make_response(job, 200)
            else:
                    return {"message": "No jobs found"}, 404
        
        elif id:
            if jwt["role"] not in ["admin"]:
                   return {"message": "Something went wrong"}, 401
            job = Job.query.filter_by(id=id).first()
            
            if not job:
                return {"message": "Job not found"}, 404
            return make_response(job.to_dict(), 200)
                   
        else:
            if jwt['role'] not in ["admin"]:
                return {"message": "Something went wrong"}, 401
            
            jobs = Job.query.all()
            if not jobs:
                return {"message": "No jobs found"}, 404
            
            response = [job.to_dict() for job in jobs]
            return make_response(response, 200)
            
    @jwt_required()
    def patch(self, id=None):
        jwt = get_jwt()
        if jwt["role"] not in ["client", "admin"]:
            return {"message": "Something went wrong"}, 401
        
        data = request.get_json()

        if not data:
            return make_response({"message": "No input data provided", "status": "fail"}, 400)
        
        if jwt["role"] in ["client"]:
            user_id = get_jwt_identity()
        else:
            user_id = id
        
        if not user_id:
            return {"message": "Job id is required"}, 400
        
        if jwt["role"] in ["client"]:
            job = Job.query.filter(
                and_(Job.client_id == user_id, 
                     Job.id == id)
            ).first()
        else:
            job = Job.query.filter_by(id=user_id).first()

        if not job:
            return {"message": "Job not found"}, 404
        
        try:
            for attr in data:
                setattr(job, attr, data[attr])
            db.session.add(job)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            response = {"errors": [str(e)]}
            return make_response(response, 422)
        
        response = {"message": "Job updated successfully", "Job":job.to_dict()}
        return make_response(response, 200)
        

        

        

        
        


             
             
            
                
      