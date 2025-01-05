from flask import request, jsonify
from functools import wraps
import jwt
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from src.models.user import User, db

class Auth:
    def __init__(self, app):
        self.app = app
        self.secret_key = app.config['SECRET_KEY']
    
    def generate_token(self, user_id):
        """JWT token oluştur"""
        try:
            payload = {
                'exp': datetime.utcnow() + timedelta(days=1),
                'iat': datetime.utcnow(),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                self.secret_key,
                algorithm='HS256'
            )
        except Exception as e:
            return str(e)
    
    def decode_token(self, token):
        """Token'ı çöz"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Token süresi doldu. Lütfen tekrar giriş yapın.'
        except jwt.InvalidTokenError:
            return 'Geçersiz token. Lütfen tekrar giriş yapın.'
    
    def register_user(self, email, password, name):
        """Yeni kullanıcı kaydı"""
        try:
            # E-posta kontrolü
            if User.query.filter_by(email=email).first():
                return {
                    'message': 'Bu e-posta adresi zaten kayıtlı',
                    'status': 'error'
                }
            
            # Yeni kullanıcı oluştur
            user = User(
                email=email,
                password=generate_password_hash(password),
                name=name
            )
            
            # Veritabanına kaydet
            db.session.add(user)
            db.session.commit()
            
            # Token oluştur
            token = self.generate_token(user.id)
            
            return {
                'message': 'Kayıt başarılı',
                'token': token,
                'status': 'success'
            }
            
        except Exception as e:
            return {
                'message': str(e),
                'status': 'error'
            }
    
    def login_user(self, email, password):
        """Kullanıcı girişi"""
        try:
            # Kullanıcıyı bul
            user = User.query.filter_by(email=email).first()
            
            if user and check_password_hash(user.password, password):
                token = self.generate_token(user.id)
                return {
                    'message': 'Giriş başarılı',
                    'token': token,
                    'status': 'success'
                }
            
            return {
                'message': 'Geçersiz kimlik bilgileri',
                'status': 'error'
            }
            
        except Exception as e:
            return {
                'message': str(e),
                'status': 'error'
            }
    
    def token_required(self, f):
        """Token kontrolü için dekoratör"""
        @wraps(f)
        def decorated(*args, **kwargs):
            token = None
            
            if 'Authorization' in request.headers:
                token = request.headers['Authorization'].split(" ")[1]
            
            if not token:
                return jsonify({
                    'message': 'Token gerekli',
                    'status': 'error'
                }), 401
            
            try:
                user_id = self.decode_token(token)
                current_user = User.query.get(user_id)
                
                if not current_user:
                    return jsonify({
                        'message': 'Geçersiz token',
                        'status': 'error'
                    }), 401
                    
            except:
                return jsonify({
                    'message': 'Geçersiz token',
                    'status': 'error'
                }), 401
                
            return f(current_user, *args, **kwargs)
        
        return decorated
    
    def admin_required(self, f):
        """Admin kontrolü için dekoratör"""
        @wraps(f)
        def decorated(*args, **kwargs):
            token = None
            
            if 'Authorization' in request.headers:
                token = request.headers['Authorization'].split(" ")[1]
            
            if not token:
                return jsonify({
                    'message': 'Token gerekli',
                    'status': 'error'
                }), 401
            
            try:
                user_id = self.decode_token(token)
                current_user = User.query.get(user_id)
                
                if not current_user or not current_user.is_admin:
                    return jsonify({
                        'message': 'Bu işlem için admin yetkisi gerekli',
                        'status': 'error'
                    }), 403
                    
            except:
                return jsonify({
                    'message': 'Geçersiz token',
                    'status': 'error'
                }), 401
                
            return f(current_user, *args, **kwargs)
        
        return decorated 