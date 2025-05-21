from . import db
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)  
    phone = db.Column(db.String(20))
    age = db.Column(db.Integer)
    password = db.Column(db.String(150), nullable=False)
    batch_number = db.Column(db.String(50))
    address = db.Column(db.String(250))  
    is_approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    passkey = db.Column(db.String(150), nullable=True)  
    
class StudentCheckInOut(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(150), nullable=False)
    roll_number = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    year = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(10), nullable=False)  
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    watchman_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    roll_number = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    year = db.Column(db.String(20), nullable=False)  


