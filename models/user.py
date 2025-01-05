from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta

class User(UserMixin):
    def __init__(self):
        self.id = None
        self.username = None
        self.email = None
        self.password_hash = None
        self.email_verified = False
        self.is_admin = False
        self.created_at = datetime.utcnow()
        self.last_login = None
        self.profile = {
            'meslek': None,
            'yas': None,
            'cinsiyet': None,
            'medeni_durum': None,
            'ruh_hali': None,
            'ilgi_alanlari': []
        }
        self.readings_history = []
        self.mood_history = []
        self.premium = False
        self.notifications = {
            'email': True,
            'daily': True
        }
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_auth_token(self, secret_key, expires_in=3600):
        return jwt.encode(
            {
                'id': self.id,
                'email': self.email,
                'is_admin': self.is_admin,
                'exp': datetime.utcnow() + timedelta(seconds=expires_in)
            },
            secret_key,
            algorithm='HS256'
        )
    
    def update_profile(self, data):
        for key in self.profile.keys():
            if key in data:
                self.profile[key] = data[key]
    
    def add_reading(self, reading_type, result, image_path=None, mood=None):
        reading = {
            'id': len(self.readings_history) + 1,
            'type': reading_type,
            'result': result,
            'image_path': image_path,
            'mood': mood,
            'timestamp': datetime.utcnow().isoformat(),
            'user_profile': self.profile.copy()
        }
        self.readings_history.append(reading)
        
        if mood:
            self.mood_history.append({
                'mood': mood,
                'timestamp': datetime.utcnow().isoformat()
            })
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'email_verified': self.email_verified,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'profile': self.profile,
            'premium': self.premium,
            'notifications': self.notifications
        } 