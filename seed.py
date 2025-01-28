from config import app, db
from models import User, ClientProfile, Comment

with app.app_context():
    print("Deleting Records")
    
    comments = Comment.query.all()
    for comment in comments:
        db.session.delete(comment)
    db.session.commit()
