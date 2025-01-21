from config import app, db
from models import User, ClientProfile

with app.app_context():
    print("Deleting Records")
    user = User.query.all()
    # User.query.delete()
    # ClientProfile.query.delete()
    for user in user:
     db.session.delete(user)
    db.session.commit()