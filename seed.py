from config import app, db
from models import User, ClientProfile

with app.app_context():
    print("Deleting Records")
    User.query.delete()
    ClientProfile.query.delete()
    db.session.commit()