from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    """Kullanıcı modeli"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    fortune_credits = db.Column(db.Integer, default=3)  # Günlük ücretsiz fal hakkı
    
    # İlişkiler
    fortunes = db.relationship('Fortune', backref='user', lazy=True)
    
    def __init__(self, email, password, name):
        self.email = email
        self.password = password
        self.name = name
    
    def update_last_login(self):
        """Son giriş zamanını güncelle"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def check_fortune_credits(self):
        """Fal kredisi kontrolü"""
        return self.fortune_credits > 0
    
    def use_fortune_credit(self):
        """Fal kredisi kullan"""
        if self.check_fortune_credits():
            self.fortune_credits -= 1
            db.session.commit()
            return True
        return False
    
    def reset_daily_credits(self):
        """Günlük kredileri sıfırla"""
        self.fortune_credits = 3
        db.session.commit()

class Fortune(db.Model):
    """Fal geçmişi modeli"""
    __tablename__ = 'fortunes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    fortune_type = db.Column(db.String(50), nullable=False)  # coffee, tarot, palm
    question = db.Column(db.Text)  # Tarot için soru
    result = db.Column(db.Text, nullable=False)  # Fal sonucu
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, user_id, fortune_type, result, question=None):
        self.user_id = user_id
        self.fortune_type = fortune_type
        self.result = result
        self.question = question
    
    @staticmethod
    def get_user_history(user_id, limit=10):
        """Kullanıcının fal geçmişini getir"""
        return Fortune.query.filter_by(user_id=user_id)\
            .order_by(Fortune.created_at.desc())\
            .limit(limit)\
            .all()

class Subscription(db.Model):
    """Abonelik modeli"""
    __tablename__ = 'subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    plan_type = db.Column(db.String(50), nullable=False)  # basic, premium, unlimited
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    def __init__(self, user_id, plan_type, end_date):
        self.user_id = user_id
        self.plan_type = plan_type
        self.end_date = end_date
    
    def is_valid(self):
        """Abonelik geçerlilik kontrolü"""
        return self.is_active and self.end_date > datetime.utcnow()
    
    def deactivate(self):
        """Aboneliği devre dışı bırak"""
        self.is_active = False
        db.session.commit() 