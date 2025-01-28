from config import app, api
from resources.auth import Signup, Login, Logout
from resources.client import ClientDetails
from resources.job import JobResource
from resources.developer import DeveloperDetails
from resources.comment import CommentResource


api.add_resource(Signup, "/signup", endpoint="signup")
api.add_resource(Login, "/login", endpoint="login")
api.add_resource(Logout, "/logout", endpoint="logout")
api.add_resource(ClientDetails, "/client_details", "/client_details/<int:client_id>", endpoint="client_details")
api.add_resource(JobResource, "/jobs", "/jobs/<int:id>", endpoint="jobs")
api.add_resource(DeveloperDetails, "/developer_details", "/developer_details/<int:id>", endpoint="developer_details")
api.add_resource(CommentResource, "/comments", "/comments/<int:id>", endpoint="comment_resource")


if __name__ == '__main__':
    app.run(port=5555, debug=True)