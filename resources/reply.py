# from flask import make_response
# from flask_restful import Resource, reqparse
# from flask_jwt_extended import jwt_required, get_jwt_identity

# from models import  User, Reply
# from config import db

# class ReplyResource(Resource):
#     parser = reqparse.RequestParser()
#     parser.add_argument("comment_id", required=True, help="Comment id is required")
#     parser.add_argument("content", required=True, help="Content is required")

#     @jwt_required()
#     def post(self):
#         data = self.parser.parse_args()
#         user_id = get_jwt_identity()

#         try:
#             reply = Reply(
#                 comment_id = data["comment_id"],
#                 content = data["content"],
#                 user_id = user_id
#             )
#             db.session.add(reply)
#             db.session.commit()
#         except Exception as e:
#             db.session.rollback()
#             return {"message": str(e)}, 422
        
#         response = reply.to_dict()
#         return make_response(response, 201)