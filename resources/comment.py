from flask import make_response, request
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from sqlalchemy import and_

from models import  Job, Comment
from config import db

class CommentResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("job_id", required=True, help="Job id is required")
    parser.add_argument("content", required=True, help="Content is required")
    
    @jwt_required()
    def post(self):
        data = self.parser.parse_args()
        try:
            user_id = get_jwt_identity()
            job = Job.query.filter_by(id=data["job_id"]).first()
            if not job:
                return {"message": "Job not found"}, 404
            comment = Comment(
                job_id=data["job_id"],
                content=data["content"],
                user_id=user_id,  
            )
            db.session.add(comment)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {"message": str(e)}, 422
        
        response = comment.to_dict()
        return make_response(response, 201)
    
    @jwt_required()
    def get(self, id):
        jwt = get_jwt()
        user_id = get_jwt_identity()

        if not id:
            return {"message": "job_id is required"}, 400

        if jwt["role"] in ["client", "developer"]:
            comments = Comment.query.filter(
                and_(Comment.job_id == id, Comment.user_id == user_id)
            ).all()
        else:
            comments = Comment.query.filter_by(job_id=id).all()
        
        if not comments:
            return {"message": "No comments found"}, 404
        
        response = []

        for comment in comments:
            comment_data = comment.to_dict()
            response.append(comment_data)
        
        return make_response(response, 200)
    

    @jwt_required()
    def patch(self, id):
        if not id:
            return {"message": "job_id is required"}, 400

        data = request.get_json()

        if not data:
            return {"message": "No data provided"}, 400
        
        try: 
            user_id = get_jwt_identity()
            comment = Comment.query.filter(
                    and_(Comment.job_id == id, Comment.user_id == user_id)
                ).first()
            if not comment:
                return {"message": "Comment not found"}, 404
            for attr in data:
                setattr(comment, attr, data[attr])
            db.session.add(comment)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {"message": str(e)}, 500
        
        response = {
                "message": "Updated Successfully",
                "developer": comment.to_dict(),
                "status": "success"
            }
        return make_response(response, 200)
    
    @jwt_required()
    def delete(self, id):
        if not id:
            return {"message": "job_id is required"}, 400 
        
        user_id = get_jwt_identity()

        try:
            comment = Comment.query.filter(
                    and_(Comment.job_id == id, Comment.user_id == user_id)
                ).first()
            if not comment:
                return make_response({"message": "Comment not found", "status": "fail"}, 404)
            db.session.delete(comment)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {"message": str(e)}, 422

        response = {"message": "comment successfully deleted", "status": "success"}
        return make_response(response, 200)

        

        


    

        
    

