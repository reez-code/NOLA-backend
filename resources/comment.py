from flask import make_response, request
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity

from models import  User, Comment
from config import db

class CommentResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("job_id", required=True, help="Job id is required")
    parser.add_argument("content", required=True, help="Content is required")
    parser.add_argument("parent_id", help="Parent Id is required")
    
    @jwt_required()
    def post(self):
        data = self.parser.parse_args()
        try:
            user_id = get_jwt_identity()
            if data["parent_id"]:
                parent_id = data["parent_id"]
            else:
                parent_id = None

            comment = Comment(
                job_id=data["job_id"],
                content=data["content"],
                user_id=user_id,
                parent_id=parent_id
            )
            db.session.add(comment)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {"message": str(e)}, 422
        
        response = comment.to_dict()
        return make_response(response, 201)
        
    

