from config import app, db, api
from resources.auth import Signup

api.add_resource(Signup, "/signup", endpoint="signup")



if __name__ == '__main__':
    app.run(port=5555, debug=True)