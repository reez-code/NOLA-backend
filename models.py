from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from datetime import datetime
from email_validator import validate_email, EmailNotValidError
from config import db, bcrypt



class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    serialize_rules = ("-developer_profile.user", "-client_profile.user", "-_password_hash", "-comments",)

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    _password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'developer', 'client', or 'admin'db
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    developer_profile = db.relationship("DeveloperProfile", uselist=False, back_populates="user", cascade="all, delete-orphan")
    client_profile = db.relationship("ClientProfile", uselist=False, back_populates="user", cascade="all, delete-orphan")

    comments = db.relationship("Comment", back_populates="user", cascade="all, delete-orphan")


    @hybrid_property
    def password_hash(self):
        raise AttributeError("Cannot be accessed!")
    
    @password_hash.setter
    def password_hash(self, password):
        password_hash = bcrypt.generate_password_hash(password.encode("utf-8"))
        self._password_hash = password_hash.decode("utf-8")

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password.encode("utf-8"))
    
    @validates("email")
    def validate_email(self, key, email):
        try:
            valid = validate_email(email)
            email = valid.email
        except EmailNotValidError as e:
            raise ValueError(f"Invalid email: {e}")
        return email
      
    @validates("role")
    def validate_role(self, key, role):
        if role not in ["developer", "client", "admin"]:
            raise ValueError("Role must be either client or developer")
        return role
    
    def __repr__(self):
        return f"<User:{self.username}/>"

 



class DeveloperProfile(db.Model, SerializerMixin):
    __tablename__ = 'developer_profiles'

    serialize_rules = ("-user.developer_profile", "-comments.developer", "-job_applications.assigned_developer",)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    profile_picture = db.Column(db.String(200), nullable=True)
    skills = db.Column(db.String(200), nullable=False)
    available_time = db.Column(db.String(50), nullable=True)
    github_account = db.Column(db.String(100), nullable=True)
    education_level = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    user = db.relationship("User", back_populates="developer_profile")
    job_applications = db.relationship("Job", back_populates="assigned_developer")


class ClientProfile(db.Model, SerializerMixin):
    __tablename__ = 'client_profiles'

    serialize_rules = ("-user.client_profile", "-jobs.client", )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    business_name = db.Column(db.String(150), nullable=True)
    business_description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    user = db.relationship("User", back_populates="client_profile")
    jobs = db.relationship("Job", back_populates="client", cascade="all, delete-orphan")
    


class Job(db.Model, SerializerMixin):
    __tablename__ = 'jobs'

    serialize_rules = ("-client.jobs", "-assigned_developer.job_applications", "-comments.job",)

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client_profiles.id'), nullable=False)
    developer_id = db.Column(db.Integer, db.ForeignKey('developer_profiles.id'), nullable=True)  # Assigned developer
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    posted_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    status = db.Column(db.String(20), default='open')  # 'open', 'in-progress', 'completed'

    client = db.relationship("ClientProfile", back_populates="jobs")
    assigned_developer = db.relationship("DeveloperProfile", back_populates="job_applications")
    comments = db.relationship("Comment", back_populates="job")


class Comment(db.Model, SerializerMixin):
    __tablename__ = 'comments'

    serialize_rules = ("-replies", "-parent", "-user", "-job.comments",)

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey("comments.id"), nullable=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    

    def add_reply(self, content, user_id):
        return Comment(content=content, parent_id=self.id, job_id=self.job_id, user_id=user_id)    

    user = db.relationship("User", back_populates="comments")
    job = db.relationship("Job", back_populates="comments")
    replies = db.relationship("Comment", backref=db.backref("parent", remote_side=[id]), cascade="all, delete-orphan",
                              lazy="dynamic")
    
    def to_dict(self):
        return {
            "id": self.id,
            "content": self.content,
            "user": {"id": self.user.id, "firstname": self.user.first_name, "role":self.user.role} if self.user else None,
            "job_id": self.job_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "replies": [reply.to_dict() for reply in self.replies]
        }

  

 
