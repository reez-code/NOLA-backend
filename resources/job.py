from flask import make_response
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity



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
    def get(self):
        jwt = get_jwt()
        if jwt["role"] in ["client"]:
            user_id = get_jwt_identity()
            jobs = Job.query.filter_by(client_id=user_id).all()
            if jobs:
                job = [job.to_dict() for job in jobs]
                return make_response(job, 200)
            else:
                return {"message": "No jobs found"}, 200
        else:
            return {"error": "You are not authorized to access this"}, 422