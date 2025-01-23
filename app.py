from config import app, api
from resources.auth import Signup, Login, Logout
from resources.client import ClientDetails
from resources.job import JobResource
from resources.developer import DeveloperDetails

api.add_resource(Signup, "/signup", endpoint="signup")
api.add_resource(Login, "/login", endpoint="login")
api.add_resource(Logout, "/logout", endpoint="logout")
api.add_resource(ClientDetails, "/client_details", "/client_details/<int:client_id>", endpoint="clientdetails")
api.add_resource(JobResource, "/job", endpoint="job")
api.add_resource(DeveloperDetails, "/developer_details", endpoint="developerdetails")

if __name__ == '__main__':
    app.run(port=5555, debug=True)