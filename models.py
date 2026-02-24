from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from datetime import datetime
from email_validator import validate_email, EmailNotValidError
from config import db, bcrypt



# association table between clients and developers (visibility / applicants)
client_developer_association = db.Table(
    'client_developers',
    db.Column('client_profile_id', db.Integer, db.ForeignKey('client_profiles.id'), primary_key=True),
    db.Column('developer_profile_id', db.Integer, db.ForeignKey('developer_profiles.id'), primary_key=True)
)


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
        return f"<User:{self.email}/>"

 



class DeveloperProfile(db.Model, SerializerMixin):
    __tablename__ = 'developer_profiles'

    # exclude back-references and the clients relationship to avoid circular serialization
    serialize_rules = ("-user.developer_profile", "-comments.developer", "-job_applications.assigned_developer", "-clients",)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    profession = db.Column(db.String(150), nullable=False)  # Required field
    profile_picture = db.Column(db.String(200), nullable=False)
    github_account = db.Column(db.String(100), nullable=True)
    linkedin_account = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    skills = db.Column(db.String(200), nullable=True)
    available_time = db.Column(db.String(50), nullable=True)
    education_level = db.Column(db.String(100), nullable=True)
    years_of_experience = db.Column(db.Integer, nullable=True, default=0)
    proficiency_points = db.Column(db.Integer, default=0)
    courtesy_points = db.Column(db.Integer, default=0)
    last_proficiency_award_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    user = db.relationship("User", back_populates="developer_profile")
    job_applications = db.relationship("Job", back_populates="assigned_developer")
    clients = db.relationship("ClientProfile", secondary=client_developer_association, back_populates="developers")


class ClientProfile(db.Model, SerializerMixin):
    __tablename__ = 'client_profiles'

    # exclude back-references and the developers relationship to avoid circular serialization
    serialize_rules = ("-user.client_profile", "-jobs.client", "-developers", )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    business_name = db.Column(db.String(150), nullable=False)
    business_category = db.Column(db.String(150), nullable=False)  # Required field
    business_description = db.Column(db.Text, nullable=False)
    business_logo = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    user = db.relationship("User", back_populates="client_profile")
    jobs = db.relationship("Job", back_populates="client", cascade="all, delete-orphan")
    developers = db.relationship("DeveloperProfile", secondary=client_developer_association, back_populates="clients")
    


class Job(db.Model, SerializerMixin):
    __tablename__ = 'jobs'

    serialize_rules = ("-client.jobs", "-assigned_developer.job_applications", "-comments.job",)

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client_profiles.id'), nullable=False)
    developer_id = db.Column(db.Integer, db.ForeignKey('developer_profiles.id'), nullable=True)  # Assigned developer
    
    # Basic job info
    title = db.Column(db.String(150), nullable=False)
    position = db.Column(db.String(150), nullable=True)  # Job position title
    description = db.Column(db.Text, nullable=True)
    
    # Contract info
    contract_type = db.Column(db.String(50), nullable=True)  # 'full-time', 'part-time', 'contract', 'freelance'
    hours_per_week = db.Column(db.Integer, nullable=True)  # Commitment in hours
    
    # Location info
    location_type = db.Column(db.String(20), nullable=True)  # 'remote' or 'physical'
    location_details = db.Column(db.Text, nullable=True)  # For remote: tech requirements; for physical: exact address
    
    # Job details as JSON arrays
    roles_and_responsibilities = db.Column(db.JSON, nullable=True, default=[])  # List of responsibilities
    requirements = db.Column(db.JSON, nullable=True, default=[])  # List of requirements
    desired_skills = db.Column(db.JSON, nullable=True, default=[])  # List of desired skills
    experience_required = db.Column(db.Text, nullable=True)  # Description of experience needed
    
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
            "user": {"id": self.user.id, "firstname": self.user.first_name, "lastname":self.user.last_name, "role":self.user.role} if self.user else None,
            "job_id": self.job_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "replies": [reply.to_dict() for reply in self.replies]
        }


class Profession(db.Model, SerializerMixin):
    __tablename__ = 'professions'

    serialize_rules = ("-exam_links.profession", "-hackathons.profession", "-code_quizzes.profession",)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    exam_links = db.relationship("ExamLink", back_populates="profession", cascade="all, delete-orphan")
    hackathons = db.relationship("Hackathon", back_populates="profession", cascade="all, delete-orphan")
    code_quizzes = db.relationship("CodeQuiz", back_populates="profession", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Profession:{self.name}>"


class ExamLink(db.Model, SerializerMixin):
    __tablename__ = 'exam_links'

    serialize_rules = ("-profession",)

    id = db.Column(db.Integer, primary_key=True)
    profession_id = db.Column(db.Integer, db.ForeignKey('professions.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    url = db.Column(db.String(500), nullable=False)
    difficulty_level = db.Column(db.String(50), nullable=True)  # 'beginner', 'intermediate', 'advanced'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    profession = db.relationship("Profession", back_populates="exam_links")

    def __repr__(self):
        return f"<ExamLink:{self.title}>"


class Hackathon(db.Model, SerializerMixin):
    __tablename__ = 'hackathons'

    serialize_rules = ("-profession",)

    id = db.Column(db.Integer, primary_key=True)
    profession_id = db.Column(db.Integer, db.ForeignKey('professions.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=True)
    registration_link = db.Column(db.String(500), nullable=True)
    location = db.Column(db.String(200), nullable=True)  # 'online' or physical location
    prize_pool = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    profession = db.relationship("Profession", back_populates="hackathons")

    def __repr__(self):
        return f"<Hackathon:{self.title}>"


class CodeQuiz(db.Model, SerializerMixin):
    __tablename__ = 'code_quizzes'

    serialize_rules = ("-profession",)

    id = db.Column(db.Integer, primary_key=True)
    profession_id = db.Column(db.Integer, db.ForeignKey('professions.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    difficulty_level = db.Column(db.String(50), nullable=True)  # 'beginner', 'intermediate', 'advanced'
    quiz_url = db.Column(db.String(500), nullable=False)
    estimated_time = db.Column(db.Integer, nullable=True)  # in minutes
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    profession = db.relationship("Profession", back_populates="code_quizzes")

    def __repr__(self):
        return f"<CodeQuiz:{self.title}>"
