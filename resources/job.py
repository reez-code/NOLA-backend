from flask import make_response, request
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from sqlalchemy import and_, or_



from models import Job, ClientProfile, DeveloperProfile, client_developer_association
from config import db

class JobResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("title", required=True, help="Title is required")
    parser.add_argument("position", required=False, help="Position of the job")
    parser.add_argument("description", required=False, help="Job description")
    parser.add_argument("contract_type", required=False, help="Type of contract")
    parser.add_argument("hours_per_week", type=int, required=False, help="Hours per week")
    parser.add_argument("location_type", required=False, help="Location type (remote/physical)")
    parser.add_argument("location_details", required=False, help="Location details")
    parser.add_argument("roles_and_responsibilities", type=list, required=False, location='json', help="Roles and responsibilities")
    parser.add_argument("requirements", type=list, required=False, location='json', help="Requirements")
    parser.add_argument("desired_skills", type=list, required=False, location='json', help="Desired skills")
    parser.add_argument("experience_required", required=False, help="Experience required")
    parser.add_argument("status", required=False, help="Job status")

    @jwt_required()
    def post(self):
        data = self.parser.parse_args()
        jwt = get_jwt()
        status = (data.get("status") or "open").lower()

        if jwt["role"] in ["client"]:
            try:
                user_id = get_jwt_identity()
                client_profile = ClientProfile.query.filter_by(user_id=user_id).first()
                if not client_profile:
                    return {"message": "Client profile not found"}, 404
                
                client_id = client_profile.id

                job = Job(
                    title=data["title"],
                    position=data.get("position"),
                    description=data.get("description"),
                    contract_type=data.get("contract_type"),
                    hours_per_week=data.get("hours_per_week"),
                    location_type=data.get("location_type"),
                    location_details=data.get("location_details"),
                    roles_and_responsibilities=data.get("roles_and_responsibilities", []),
                    requirements=data.get("requirements", []),
                    desired_skills=data.get("desired_skills", []),
                    experience_required=data.get("experience_required"),
                    status=status,
                    client_id=client_id
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
            # ensure identity is integer for DB queries
            try:
                user_id = int(get_jwt_identity())
            except Exception:
                user_id = get_jwt_identity()
        else:
            user_id = None
        
        if user_id:
        
            if jwt["role"] in ["client"]:
                client_profile = ClientProfile.query.filter_by(user_id=user_id).first()
                if not client_profile:
                    return {"message": "Client profile not found"}, 404
                client_id  = client_profile.id
                jobs = Job.query.filter_by(client_id=client_id).all()
                job_list = [j.to_dict() for j in jobs] if jobs else []
                return make_response(job_list, 200)
                
            elif jwt["role"] in ["developer"]:
                developer_profile = DeveloperProfile.query.filter_by(user_id=user_id).first()
                if not developer_profile:
                    return {"message": "Developer profile not found"}, 404
                developer_id = developer_profile.id

                # Determine client_profile ids that have this developer associated
                client_id_rows = db.session.query(ClientProfile.id).join(
                    client_developer_association,
                    ClientProfile.id == client_developer_association.c.client_profile_id
                ).filter(
                    client_developer_association.c.developer_profile_id == developer_id
                ).all()

                client_ids = [r[0] for r in client_id_rows] if client_id_rows else []

                if client_ids:
                    jobs = Job.query.filter(
                        or_(Job.developer_id == developer_id, Job.client_id.in_(client_ids))
                    ).all()
                else:
                    jobs = Job.query.filter_by(developer_id=developer_id).all()

                # prepare job dicts
                job_list = [j.to_dict() for j in jobs] if jobs else []

                # load associated client profiles so developer can see business listings even if no jobs
                clients = []
                if client_ids:
                    client_objs = ClientProfile.query.filter(ClientProfile.id.in_(client_ids)).all()
                    clients = [c.to_dict() for c in client_objs] if client_objs else []

                return make_response({"jobs": job_list, "clients": clients}, 200)
        
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
        
        if not id:
            return {"message": "Job id is required"}, 400
        
        if data.get("developer_id"):
            developer_id = data["developer_id"]
            developer_profile = DeveloperProfile.query.filter_by(id=developer_id).first()
            if not developer_profile:
                return {"message": "Developer profile not found"}, 404
        
        if jwt["role"] in ["client"]:
            user_id = get_jwt_identity()
            client_profile = ClientProfile.query.filter_by(user_id=user_id).first()
            if not client_profile:
                return {"message": "Client profile not found"}, 404
            client_id = client_profile.id
            job = Job.query.filter(
                and_(Job.client_id == client_id, 
                     Job.id == id)
            ).first()
        else:
            job = Job.query.filter_by(id=id).first()
            
        if not job:
            return {"message": "Job not found"}, 404
        
        try:
            # Update each attribute if it exists on the model
            for attr, value in data.items():
                if hasattr(job, attr):
                    setattr(job, attr, value)
            
            db.session.commit()
            response = {"message": "Job updated successfully", "job": job.to_dict()}
            return make_response(response, 200)
            
        except Exception as e:
            db.session.rollback()
            print(f"Error updating job: {str(e)}")
            response = {"errors": [str(e)], "message": "Failed to update job"}
            return make_response(response, 422)
    
    @jwt_required()
    def delete(self, id=None):
        jwt = get_jwt()

        if jwt["role"] not in ["admin", "client"]:
            return {"error": "Something went wrong"}, 401
        
        if not id:
            return {"message": "Job id is required"}, 400
        
        if jwt["role"] in ["client"]:
            user_id = get_jwt_identity()
            client_profile = ClientProfile.query.filter_by(user_id=user_id).first()
            if not client_profile:
                return {"message": "Client profile not found"}, 404
            client_id = client_profile.id
            job = Job.query.filter(
                and_(Job.client_id == client_id, 
                     Job.id == id)
            ).first()
        else:
            job = Job.query.filter_by(id=id).first()

        if not job:
            return {"message": "Job not found"}, 404
        
        try:
            db.session.delete(job)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            response = {"errors": [str(e)]}
            return make_response(response, 422)
        
        response = {"message": "job successfully deleted", "status": "success"}
        return make_response(response, 200)

        

        
        
        
        




        

        

        

        
        


             
             
            
                
      