from flask import Blueprint, request, jsonify
from models import db, User, ClientProfile, Job, Comment
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

client_bp = Blueprint('client', __name__)

# Helper function to get the current client profile
def get_current_client_profile():
    current_user_id = get_jwt_identity()
    client = ClientProfile.query.filter_by(user_id=current_user_id).first()
    return client

# Register a new client user
@client_bp.route('/register', methods=['POST'])
def register_client():
    data = request.get_json()
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')
    business_name = data.get('business_name')
    business_description = data.get('business_description')
    logo = data.get('logo')

    # Check if email or username already exists
    if User.query.filter((User.email == email) | (User.username == username)).first():
        return jsonify({'error': 'User with this email or username already exists'}), 400

    # Create new user with role 'client'
    user = User(email=email, username=username, role='client')
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    # Create the client profile associated with the user
    client_profile = ClientProfile(
        user_id=user.id,
        business_name=business_name,
        business_description=business_description,
        logo=logo
    )
    db.session.add(client_profile)
    db.session.commit()

    return jsonify({'message': 'Client registered successfully'}), 201

# Get client's profile information
@client_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    client = get_current_client_profile()
    if not client:
        return jsonify({'error': 'Client profile not found'}), 404

    return jsonify({
        'business_name': client.business_name,
        'business_description': client.business_description,
        'logo': client.logo
    })

# Update client's profile information
@client_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    client = get_current_client_profile()
    if not client:
        return jsonify({'error': 'Client profile not found'}), 404

    data = request.get_json()
    client.business_name = data.get('business_name', client.business_name)
    client.business_description = data.get('business_description', client.business_description)
    client.logo = data.get('logo', client.logo)

    db.session.commit()
    return jsonify({'message': 'Client profile updated successfully'})

# Create a new job
@client_bp.route('/jobs', methods=['POST'])
@jwt_required()
def create_job():
    client = get_current_client_profile()
    if not client:
        return jsonify({'error': 'Client profile not found'}), 404

    data = request.get_json()
    job = Job(
        client_id=client.id,
        title=data.get('title'),
        description=data.get('description'),
        posted_at=datetime.utcnow(),
        status='open'
    )

    db.session.add(job)
    db.session.commit()
    return jsonify({'message': 'Job created successfully', 'job_id': job.id}), 201

# Get all jobs for the current client
@client_bp.route('/jobs', methods=['GET'])
@jwt_required()
def get_jobs():
    client = get_current_client_profile()
    if not client:
        return jsonify({'error': 'Client profile not found'}), 404

    jobs = Job.query.filter_by(client_id=client.id).all()
    job_list = [{'id': job.id, 'title': job.title, 'description': job.description, 'status': job.status} for job in jobs]

    return jsonify(job_list)

# Update a specific job
@client_bp.route('/jobs/<int:job_id>', methods=['PUT'])
@jwt_required()
def update_job(job_id):
    client = get_current_client_profile()
    job = Job.query.filter_by(id=job_id, client_id=client.id).first()

    if not job:
        return jsonify({'error': 'Job not found or access denied'}), 404

    data = request.get_json()
    job.title = data.get('title', job.title)
    job.description = data.get('description', job.description)
    job.status = data.get('status', job.status)

    db.session.commit()
    return jsonify({'message': 'Job updated successfully'})

# Delete a specific job
@client_bp.route('/jobs/<int:job_id>', methods=['DELETE'])
@jwt_required()
def delete_job(job_id):
    client = get_current_client_profile()
    job = Job.query.filter_by(id=job_id, client_id=client.id).first()

    if not job:
        return jsonify({'error': 'Job not found or access denied'}), 404

    db.session.delete(job)
    db.session.commit()
    return jsonify({'message': 'Job deleted successfully'})

# Add a comment for admin review
@client_bp.route('/comments', methods=['POST'])
@jwt_required()
def add_comment():
    client = get_current_client_profile()
    if not client:
        return jsonify({'error': 'Client profile not found'}), 404

    data = request.get_json()
    comment = Comment(
        content=data.get('content'),
        client_id=client.id,
        admin_viewed=False
    )

    db.session.add(comment)
    db.session.commit()
    return jsonify({'message': 'Comment added successfully'})

# Get all comments made by the client
@client_bp.route('/comments', methods=['GET'])
@jwt_required()
def get_comments():
    client = get_current_client_profile()
    if not client:
        return jsonify({'error': 'Client profile not found'}), 404

    comments = Comment.query.filter_by(client_id=client.id).all()
    comment_list = [{'id': comment.id, 'content': comment.content, 'created_at': comment.created_at} for comment in comments]

    return jsonify(comment_list)
