from config import app, db, api
from resources.auth import Signup, Login

api.add_resource(Signup, "/signup", endpoint="signup")
api.add_resource(Login, "/login", endpoint="login")



if __name__ == '__main__':
    app.run(port=5555, debug=True)