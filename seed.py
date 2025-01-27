from config import app, db
from models import User, ClientProfile, Comment

with app.app_context():
    print("Deleting Records")
    comments = Comment.query.filter_by(id=1).first()
    print(comments.to_dict())