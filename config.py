import os
from datetime import timedelta
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from flask_jwt_extended import JWTManager
from flask_cors import CORS

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# Use environment secrets in production; fall back to a development secret if missing
# (Do NOT use the fallback in production environments.)
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY") or "dev-jwt-secret-key"
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or "dev-secret-key"
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.json.compact = False

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(metadata=metadata)

migrate = Migrate(app, db)
db.init_app(app)

# initializing extensions
CORS(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
api = Api(app)
