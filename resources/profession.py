from flask import request
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt

from models import Profession, ExamLink, Hackathon, CodeQuiz
from config import db
from datetime import datetime


class ProfessionList(Resource):
    """Get all professions or create a new profession"""
    
    def get(self):
        """Get all professions with their content"""
        try:
            professions = Profession.query.all()
            if not professions:
                return {"message": "No professions found", "professions": [], "status": "success"}, 200
            
            response = [prof.to_dict() for prof in professions]
            return {"professions": response, "status": "success"}, 200
        except Exception as e:
            return {"error": str(e), "status": "fail"}, 500
    
    @jwt_required()
    def post(self):
        """Create a new profession (admin only)"""
        jwt = get_jwt()
        
        if jwt["role"] != "admin":
            return {"error": "Unauthorized", "status": "fail"}, 401
        
        try:
            data = request.get_json()
            
            if not data or not data.get('name'):
                return {"error": "Profession name is required", "status": "fail"}, 400
            
            # Check if profession already exists
            existing = Profession.query.filter_by(name=data['name']).first()
            if existing:
                return {"error": "Profession already exists", "status": "fail"}, 400
            
            profession = Profession(
                name=data['name'],
                description=data.get('description', '')
            )
            
            db.session.add(profession)
            db.session.commit()
            
            return {
                "message": "Profession created successfully",
                "profession": profession.to_dict(),
                "status": "success"
            }, 201
        except Exception as e:
            db.session.rollback()
            return {"error": str(e), "status": "fail"}, 500


class ProfessionDetail(Resource):
    """Get, update, or delete a specific profession"""
    
    def get(self, profession_id):
        """Get a specific profession with all its content"""
        try:
            profession = Profession.query.get(profession_id)
            
            if not profession:
                return {"error": "Profession not found", "status": "fail"}, 404
            
            return {
                "profession": profession.to_dict(),
                "exam_links": [exam.to_dict() for exam in profession.exam_links],
                "hackathons": [hack.to_dict() for hack in profession.hackathons],
                "code_quizzes": [quiz.to_dict() for quiz in profession.code_quizzes],
                "status": "success"
            }, 200
        except Exception as e:
            return {"error": str(e), "status": "fail"}, 500
    
    @jwt_required()
    def put(self, profession_id):
        """Update a profession (admin only)"""
        jwt = get_jwt()
        
        if jwt["role"] != "admin":
            return {"error": "Unauthorized", "status": "fail"}, 401
        
        try:
            profession = Profession.query.get(profession_id)
            
            if not profession:
                return {"error": "Profession not found", "status": "fail"}, 404
            
            data = request.get_json()
            
            if 'name' in data:
                profession.name = data['name']
            if 'description' in data:
                profession.description = data['description']
            
            profession.updated_at = datetime.utcnow()
            db.session.commit()
            
            return {
                "message": "Profession updated successfully",
                "profession": profession.to_dict(),
                "status": "success"
            }, 200
        except Exception as e:
            db.session.rollback()
            return {"error": str(e), "status": "fail"}, 500
    
    @jwt_required()
    def delete(self, profession_id):
        """Delete a profession (admin only)"""
        jwt = get_jwt()
        
        if jwt["role"] != "admin":
            return {"error": "Unauthorized", "status": "fail"}, 401
        
        try:
            profession = Profession.query.get(profession_id)
            
            if not profession:
                return {"error": "Profession not found", "status": "fail"}, 404
            
            db.session.delete(profession)
            db.session.commit()
            
            return {
                "message": "Profession deleted successfully",
                "status": "success"
            }, 200
        except Exception as e:
            db.session.rollback()
            return {"error": str(e), "status": "fail"}, 500


class ExamLinkResource(Resource):
    """Manage exam links for a profession"""
    
    @jwt_required()
    def post(self, profession_id):
        """Add an exam link to a profession (admin only)"""
        jwt = get_jwt()
        
        if jwt["role"] != "admin":
            return {"error": "Unauthorized", "status": "fail"}, 401
        
        try:
            profession = Profession.query.get(profession_id)
            
            if not profession:
                return {"error": "Profession not found", "status": "fail"}, 404
            
            data = request.get_json()
            
            if not data or not data.get('title') or not data.get('url'):
                return {"error": "Title and URL are required", "status": "fail"}, 400
            
            exam_link = ExamLink(
                profession_id=profession_id,
                title=data['title'],
                description=data.get('description', ''),
                url=data['url'],
                difficulty_level=data.get('difficulty_level', 'intermediate')
            )
            
            db.session.add(exam_link)
            db.session.commit()
            
            return {
                "message": "Exam link added successfully",
                "exam_link": exam_link.to_dict(),
                "status": "success"
            }, 201
        except Exception as e:
            db.session.rollback()
            return {"error": str(e), "status": "fail"}, 500
    
    @jwt_required()
    def put(self, profession_id, exam_id):
        """Update an exam link (admin only)"""
        jwt = get_jwt()
        
        if jwt["role"] != "admin":
            return {"error": "Unauthorized", "status": "fail"}, 401
        
        try:
            exam_link = ExamLink.query.filter_by(id=exam_id, profession_id=profession_id).first()
            
            if not exam_link:
                return {"error": "Exam link not found", "status": "fail"}, 404
            
            data = request.get_json()
            
            if 'title' in data:
                exam_link.title = data['title']
            if 'description' in data:
                exam_link.description = data['description']
            if 'url' in data:
                exam_link.url = data['url']
            if 'difficulty_level' in data:
                exam_link.difficulty_level = data['difficulty_level']
            
            exam_link.updated_at = datetime.utcnow()
            db.session.commit()
            
            return {
                "message": "Exam link updated successfully",
                "exam_link": exam_link.to_dict(),
                "status": "success"
            }, 200
        except Exception as e:
            db.session.rollback()
            return {"error": str(e), "status": "fail"}, 500
    
    @jwt_required()
    def delete(self, profession_id, exam_id):
        """Delete an exam link (admin only)"""
        jwt = get_jwt()
        
        if jwt["role"] != "admin":
            return {"error": "Unauthorized", "status": "fail"}, 401
        
        try:
            exam_link = ExamLink.query.filter_by(id=exam_id, profession_id=profession_id).first()
            
            if not exam_link:
                return {"error": "Exam link not found", "status": "fail"}, 404
            
            db.session.delete(exam_link)
            db.session.commit()
            
            return {
                "message": "Exam link deleted successfully",
                "status": "success"
            }, 200
        except Exception as e:
            db.session.rollback()
            return {"error": str(e), "status": "fail"}, 500


class HackathonResource(Resource):
    """Manage hackathons for a profession"""
    
    @jwt_required()
    def post(self, profession_id):
        """Add a hackathon to a profession (admin only)"""
        jwt = get_jwt()
        
        if jwt["role"] != "admin":
            return {"error": "Unauthorized", "status": "fail"}, 401
        
        try:
            profession = Profession.query.get(profession_id)
            
            if not profession:
                return {"error": "Profession not found", "status": "fail"}, 404
            
            data = request.get_json()
            
            if not data or not data.get('title') or not data.get('start_date'):
                return {"error": "Title and start_date are required", "status": "fail"}, 400
            
            hackathon = Hackathon(
                profession_id=profession_id,
                title=data['title'],
                description=data.get('description', ''),
                start_date=datetime.fromisoformat(data['start_date']),
                end_date=datetime.fromisoformat(data['end_date']) if data.get('end_date') else None,
                registration_link=data.get('registration_link', ''),
                location=data.get('location', 'online'),
                prize_pool=data.get('prize_pool', '')
            )
            
            db.session.add(hackathon)
            db.session.commit()
            
            return {
                "message": "Hackathon added successfully",
                "hackathon": hackathon.to_dict(),
                "status": "success"
            }, 201
        except Exception as e:
            db.session.rollback()
            return {"error": str(e), "status": "fail"}, 500
    
    @jwt_required()
    def put(self, profession_id, hackathon_id):
        """Update a hackathon (admin only)"""
        jwt = get_jwt()
        
        if jwt["role"] != "admin":
            return {"error": "Unauthorized", "status": "fail"}, 401
        
        try:
            hackathon = Hackathon.query.filter_by(id=hackathon_id, profession_id=profession_id).first()
            
            if not hackathon:
                return {"error": "Hackathon not found", "status": "fail"}, 404
            
            data = request.get_json()
            
            if 'title' in data:
                hackathon.title = data['title']
            if 'description' in data:
                hackathon.description = data['description']
            if 'start_date' in data:
                hackathon.start_date = datetime.fromisoformat(data['start_date'])
            if 'end_date' in data:
                hackathon.end_date = datetime.fromisoformat(data['end_date']) if data.get('end_date') else None
            if 'registration_link' in data:
                hackathon.registration_link = data['registration_link']
            if 'location' in data:
                hackathon.location = data['location']
            if 'prize_pool' in data:
                hackathon.prize_pool = data['prize_pool']
            
            hackathon.updated_at = datetime.utcnow()
            db.session.commit()
            
            return {
                "message": "Hackathon updated successfully",
                "hackathon": hackathon.to_dict(),
                "status": "success"
            }, 200
        except Exception as e:
            db.session.rollback()
            return {"error": str(e), "status": "fail"}, 500
    
    @jwt_required()
    def delete(self, profession_id, hackathon_id):
        """Delete a hackathon (admin only)"""
        jwt = get_jwt()
        
        if jwt["role"] != "admin":
            return {"error": "Unauthorized", "status": "fail"}, 401
        
        try:
            hackathon = Hackathon.query.filter_by(id=hackathon_id, profession_id=profession_id).first()
            
            if not hackathon:
                return {"error": "Hackathon not found", "status": "fail"}, 404
            
            db.session.delete(hackathon)
            db.session.commit()
            
            return {
                "message": "Hackathon deleted successfully",
                "status": "success"
            }, 200
        except Exception as e:
            db.session.rollback()
            return {"error": str(e), "status": "fail"}, 500


class CodeQuizResource(Resource):
    """Manage code quizzes for a profession"""
    
    @jwt_required()
    def post(self, profession_id):
        """Add a code quiz to a profession (admin only)"""
        jwt = get_jwt()
        
        if jwt["role"] != "admin":
            return {"error": "Unauthorized", "status": "fail"}, 401
        
        try:
            profession = Profession.query.get(profession_id)
            
            if not profession:
                return {"error": "Profession not found", "status": "fail"}, 404
            
            data = request.get_json()
            
            if not data or not data.get('title') or not data.get('quiz_url'):
                return {"error": "Title and quiz_url are required", "status": "fail"}, 400
            
            code_quiz = CodeQuiz(
                profession_id=profession_id,
                title=data['title'],
                description=data.get('description', ''),
                difficulty_level=data.get('difficulty_level', 'intermediate'),
                quiz_url=data['quiz_url'],
                estimated_time=data.get('estimated_time', 30)
            )
            
            db.session.add(code_quiz)
            db.session.commit()
            
            return {
                "message": "Code quiz added successfully",
                "code_quiz": code_quiz.to_dict(),
                "status": "success"
            }, 201
        except Exception as e:
            db.session.rollback()
            return {"error": str(e), "status": "fail"}, 500
    
    @jwt_required()
    def put(self, profession_id, quiz_id):
        """Update a code quiz (admin only)"""
        jwt = get_jwt()
        
        if jwt["role"] != "admin":
            return {"error": "Unauthorized", "status": "fail"}, 401
        
        try:
            code_quiz = CodeQuiz.query.filter_by(id=quiz_id, profession_id=profession_id).first()
            
            if not code_quiz:
                return {"error": "Code quiz not found", "status": "fail"}, 404
            
            data = request.get_json()
            
            if 'title' in data:
                code_quiz.title = data['title']
            if 'description' in data:
                code_quiz.description = data['description']
            if 'difficulty_level' in data:
                code_quiz.difficulty_level = data['difficulty_level']
            if 'quiz_url' in data:
                code_quiz.quiz_url = data['quiz_url']
            if 'estimated_time' in data:
                code_quiz.estimated_time = data['estimated_time']
            
            code_quiz.updated_at = datetime.utcnow()
            db.session.commit()
            
            return {
                "message": "Code quiz updated successfully",
                "code_quiz": code_quiz.to_dict(),
                "status": "success"
            }, 200
        except Exception as e:
            db.session.rollback()
            return {"error": str(e), "status": "fail"}, 500
    
    @jwt_required()
    def delete(self, profession_id, quiz_id):
        """Delete a code quiz (admin only)"""
        jwt = get_jwt()
        
        if jwt["role"] != "admin":
            return {"error": "Unauthorized", "status": "fail"}, 401
        
        try:
            code_quiz = CodeQuiz.query.filter_by(id=quiz_id, profession_id=profession_id).first()
            
            if not code_quiz:
                return {"error": "Code quiz not found", "status": "fail"}, 404
            
            db.session.delete(code_quiz)
            db.session.commit()
            
            return {
                "message": "Code quiz deleted successfully",
                "status": "success"
            }, 200
        except Exception as e:
            db.session.rollback()
            return {"error": str(e), "status": "fail"}, 500
