from config import app, api
import logging
import traceback
from flask import jsonify
from resources.auth import Signup, Login, Logout
from resources.client import ClientDetails, ClientApplicants
from resources.job import JobResource
from resources.developer import DeveloperDetails
from resources.comment import CommentResource
from resources.comment_reply import CommentReplyResource
from resources.admin import AdminDevelopers, AdminClients, AdminAssignDeveloper, AdminAddJobToClient, AdminDeveloperPoints

api.add_resource(Signup, "/signup", endpoint="signup")
api.add_resource(Login, "/login", endpoint="login")
api.add_resource(Logout, "/logout", endpoint="logout")
api.add_resource(ClientDetails, "/client_details", "/client_details/<int:client_id>", endpoint="client_details")
api.add_resource(JobResource, "/jobs", "/jobs/<int:id>", endpoint="jobs")
api.add_resource(DeveloperDetails, "/developer_details", "/developer_details/<int:id>", endpoint="developer_details")
api.add_resource(CommentResource, "/comments", "/comments/<int:id>", endpoint="comment_resource")
api.add_resource(CommentReplyResource, "/comment_reply", endpoint="comment_reply_resource")
api.add_resource(AdminDevelopers, "/admin/developers", endpoint="admin_developers")
api.add_resource(AdminClients, "/admin/clients", endpoint="admin_clients")
api.add_resource(AdminAssignDeveloper, "/admin/assign_developer", endpoint="admin_assign_developer")
api.add_resource(AdminAddJobToClient, "/admin/add_job_to_client", endpoint="admin_add_job_to_client")
api.add_resource(AdminDeveloperPoints, "/admin/developer_points", endpoint="admin_developer_points")
api.add_resource(ClientApplicants, "/client/<int:client_id>/applicants", endpoint="client_applicants")


# configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.errorhandler(Exception)
def handle_unexpected_error(e):
    """Return JSON with error message and traceback when in debug mode, and log the exception."""
    tb = traceback.format_exc()
    logger.error("Unhandled Exception: %s", tb)
    if app.debug:
        return jsonify({"error": str(e), "traceback": tb}), 500
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    app.run(port=5555, debug=True)