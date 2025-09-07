from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.Text, nullable=False)
    title = db.Column(db.String(200))
    company = db.Column(db.String(100))
    description = db.Column(db.Text)
    location = db.Column(db.String(100))
    status = db.Column(db.String(20), default='saved')  # saved, applied, interview, offered
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    date_applied = db.Column(db.DateTime)
    salary_range = db.Column(db.String(50))
    job_type = db.Column(db.String(50))  # full-time, part-time, contract, etc.
    
    # Relationships
    applications = db.relationship('Application', backref='job', lazy=True)
    
    def __repr__(self):
        return f'<Job {self.title} at {self.company}>'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    original_cv_path = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    applications = db.relationship('Application', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.name}>'

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    custom_cv_path = db.Column(db.String(200))
    cover_letter_path = db.Column(db.String(200))
    application_date = db.Column(db.DateTime, default=datetime.utcnow)
    status_notes = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Application for Job {self.job_id}>'

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    website = db.Column(db.String(200))
    description = db.Column(db.Text)
    hiring_manager = db.Column(db.String(100))
    research_notes = db.Column(db.Text)
    last_researched = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Company {self.name}>'