from flask import make_response, request
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity

from models import User, DeveloperProfile, ClientProfile, Job
from config import db


class AdminDevelopers(Resource):
    """Admin resource for managing developers"""
    
    @jwt_required()
    def get(self):
        """Get all developers"""
        jwt = get_jwt()
        
        if jwt["role"] != "admin":
            return {"error": "Unauthorized", "status": "fail"}, 401
        
        try:
            developers = User.query.filter_by(role="developer").all()
            if not developers:
                return {"message": "No developers found", "developers": [], "status": "success"}, 200
            
            response = [dev.to_dict() for dev in developers]
            return {"developers": response, "status": "success"}, 200
        except Exception as e:
            return {"error": str(e), "status": "fail"}, 500


class AdminClients(Resource):
    """Admin resource for managing clients/businesses"""
    
    @jwt_required()
    def get(self):
        """Get all clients"""
        jwt = get_jwt()
        
        if jwt["role"] != "admin":
            return {"error": "Unauthorized", "status": "fail"}, 401
        
        try:
            clients = User.query.filter_by(role="client").all()
            if not clients:
                return {"message": "No clients found", "clients": [], "status": "success"}, 200
            
            response = [client.to_dict() for client in clients]
            return {"clients": response, "status": "success"}, 200
        except Exception as e:
            return {"error": str(e), "status": "fail"}, 500


class AdminAssignDeveloper(Resource):
    """Admin resource to add developers to available jobs"""
    
    parser = reqparse.RequestParser()
    parser.add_argument('job_id', required=True, type=int, help='Job ID is required')
    parser.add_argument('developer_id', required=True, type=int, help='Developer ID is required')
    
    @jwt_required()
    def post(self):
        """Assign a developer to a job"""
        jwt = get_jwt()
        
        if jwt["role"] != "admin":
            return {"error": "Unauthorized", "status": "fail"}, 401
        
        data = self.parser.parse_args()
        
        try:
            job = Job.query.filter_by(id=data['job_id']).first()
            if not job:
                return {"error": "Job not found", "status": "fail"}, 404
            
            developer = User.query.filter_by(id=data['developer_id'], role="developer").first()
            if not developer:
                return {"error": "Developer not found", "status": "fail"}, 404
            
            developer_profile = DeveloperProfile.query.filter_by(user_id=developer.id).first()
            if not developer_profile:
                return {"error": "Developer profile not found", "status": "fail"}, 404
            
            job.developer_id = developer_profile.id
            db.session.add(job)
            db.session.commit()
            
            return {
                "message": "Developer assigned to job successfully",
                "job": job.to_dict(),
                "status": "success"
            }, 200
        except Exception as e:
            db.session.rollback()
            return {"error": str(e), "status": "fail"}, 500





class AdminDeveloperPoints(Resource):
    """Admin resource to manage developer courtesy and proficiency points"""
    
    parser = reqparse.RequestParser()
    parser.add_argument('developer_id', required=True, type=int, help='Developer ID is required')
    parser.add_argument('proficiency_points', type=int, help='Proficiency points to add')
    parser.add_argument('courtesy_points', type=int, help='Courtesy points to add')
    
    @jwt_required()
    def post(self):
        """Add courtesy or proficiency points to a developer"""
        jwt = get_jwt()
        
        if jwt["role"] != "admin":
            return {"error": "Unauthorized", "status": "fail"}, 401
        
        data = self.parser.parse_args()
        developer_id = data['developer_id']
        proficiency_to_add = data.get('proficiency_points', 0)
        courtesy_to_add = data.get('courtesy_points', 0)
        
        try:
            developer_profile = DeveloperProfile.query.filter_by(user_id=developer_id).first()
            if not developer_profile:
                return {"error": "Developer not found", "status": "fail"}, 404
            
            # Add points
            if proficiency_to_add:
                developer_profile.proficiency_points = (developer_profile.proficiency_points or 0) + proficiency_to_add
            
            if courtesy_to_add:
                developer_profile.courtesy_points = (developer_profile.courtesy_points or 0) + courtesy_to_add
            
            db.session.add(developer_profile)
            db.session.commit()
            
            return {
                "message": "Points added successfully",
                "developer": developer_profile.to_dict(),
                "status": "success"
            }, 200
        except Exception as e:
            db.session.rollback()
            return {"error": str(e), "status": "fail"}, 500
