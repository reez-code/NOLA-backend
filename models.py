from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from datetime import datetime
from email_validator import validate_email, EmailNotValidError
from config import db, bcrypt



class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    serialize_rules = ("-developer_profile.user", "-client_profile.user", "-_password_hash",)

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    _password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'developer', 'client', or 'admin'
    
    developer_profile = db.relationship("DeveloperProfile", uselist=False, back_populates="user", cascade="all, delete-orphan")
    client_profile = db.relationship("ClientProfile", uselist=False, back_populates="user", cascade="all, delete-orphan")


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
    first_name = db.Column(db.String(150), nullable=True)
    last_name = db.Column(db.String(150), nullable=True)
    description = db.Column(db.Text, nullable=True)
    profile_picture = db.Column(db.String(200), nullable=True)
    skills = db.Column(db.String(200), nullable=True)
    available_time = db.Column(db.String(50), nullable=True)
    github_account = db.Column(db.String(100), nullable=True)
    education_level = db.Column(db.String(100), nullable=True)

    user = db.relationship("User", back_populates="developer_profile")
    comments = db.relationship("Comment", back_populates="developer")
    job_applications = db.relationship("Job", back_populates="assigned_developer", foreign_keys='Job.developer_id')


class ClientProfile(db.Model, SerializerMixin):
    __tablename__ = 'client_profiles'

    serialize_rules = ("-user.client_profile", "-jobs.client", "-comments.clent",)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    business_name = db.Column(db.String(150), nullable=True)
    business_description = db.Column(db.Text, nullable=True)
    logo = db.Column(db.String(200), nullable=True)

    user = db.relationship("User", back_populates="client_profile")
    jobs = db.relationship("Job", back_populates="client", cascade="all, delete-orphan")
    comments = db.relationship("Comment", back_populates="client")


class Job(db.Model, SerializerMixin):
    __tablename__ = 'jobs'

    serialize_rules = ("-client.jobs", "-assigned_developer.job_applications",)

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client_profiles.id'), nullable=False)
    developer_id = db.Column(db.Integer, db.ForeignKey('developer_profiles.id'), nullable=True)  # Assigned developer
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    posted_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    status = db.Column(db.String(20), default='open')  # 'open', 'in-progress', 'completed'

    client = db.relationship("ClientProfile", back_populates="jobs")
    assigned_developer = db.relationship("DeveloperProfile", back_populates="job_applications", foreign_keys=[developer_id])


class Comment(db.Model, SerializerMixin):
    __tablename__ = 'comments'

    serialize_rules = ("-developer.comments", "-client.comments",)

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    developer_id = db.Column(db.Integer, db.ForeignKey('developer_profiles.id'), nullable=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client_profiles.id'), nullable=True)
    admin_viewed = db.Column(db.Boolean, default=False)  # Whether the admin has viewed the comment

    developer = db.relationship("DeveloperProfile", back_populates="comments")
    client = db.relationship("ClientProfile", back_populates="comments")
