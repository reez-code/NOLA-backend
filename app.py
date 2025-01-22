from config import app, api
from resources.auth import Signup, Login, Logout
from resources.client import ClientDetails, JobResource


api.add_resource(Signup, "/signup", endpoint="signup")
api.add_resource(Login, "/login", endpoint="login")
api.add_resource(Logout, "/logout", endpoint="logout")
api.add_resource(ClientDetails, "/client_details", endpoint="clientdetails")
api.add_resource(JobResource, "/job", endpoint="job")


if __name__ == '__main__':
    app.run(port=5555, debug=True)