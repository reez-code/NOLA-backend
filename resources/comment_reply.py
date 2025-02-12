from flask import make_response, request
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from sqlalchemy import and_



from models import Job, Comment
from config import db

class CommentReplyResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("job_id", required=True, help="Job id is required")
    parser.add_argument("content", required=True, help="Content is required")
    parser.add_argument("parent_id", required=True, help="Parent id is required")

    @jwt_required()
    def post(self):
        data = self.parser.parse_args()

        try:
            user_id = get_jwt_identity()
            
            job = Job.query.filter_by(id=data["job_id"]).first()
            if not job:
                return {"message": "Job not found"}, 404
            
            comment = Comment.query.filter(
                and_(Comment.job_id == data["job_id"], Comment.id == data["parent_id"])
            ).first()

            if not comment:
                return {"message": "Comment not found"}, 404
            
            content = data["content"]
            reply = comment.add_reply(content, user_id)
            db.session.add(reply)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {"message": str(e)}, 422
        
        response = reply.to_dict()
        return make_response(response, 201)