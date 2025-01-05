from functools import wraps
from flask import request, jsonify, session, redirect, url_for
import jwt
from datetime import datetime

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get('token') or request.headers.get('Authorization')
        
        if not token:
            if request.is_json:
                return jsonify({'error': 'Lütfen giriş yapın'}), 401
            return redirect(url_for('login_page'))
            
        try:
            if token.startswith('Bearer '):
                token = token.split(' ')[1]
                
            from app import app, users
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            user = users.get(data['email'])
            
            if not user:
                raise ValueError('Kullanıcı bulunamadı')
                
            return f(*args, **kwargs)
            
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            if request.is_json:
                return jsonify({'error': 'Oturum süresi doldu, lütfen tekrar giriş yapın'}), 401
            return redirect(url_for('login_page'))
            
        except Exception as e:
            if request.is_json:
                return jsonify({'error': str(e)}), 401
            return redirect(url_for('login_page'))
            
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get('token') or request.headers.get('Authorization')
        
        if not token:
            if request.is_json:
                return jsonify({'error': 'Lütfen giriş yapın'}), 401
            return redirect(url_for('login_page'))
            
        try:
            if token.startswith('Bearer '):
                token = token.split(' ')[1]
                
            from app import app, users
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            user = users.get(data['email'])
            
            if not user or not user.is_admin:
                if request.is_json:
                    return jsonify({'error': 'Bu sayfaya erişim yetkiniz yok'}), 403
                return redirect(url_for('login_page'))
                
            return f(*args, **kwargs)
            
        except Exception as e:
            if request.is_json:
                return jsonify({'error': str(e)}), 401
            return redirect(url_for('login_page'))
            
    return decorated_function

def validate_registration_data(data):
    errors = []
    
    if not data.get('username'):
        errors.append('Kullanıcı adı gerekli')
    elif len(data['username']) < 3:
        errors.append('Kullanıcı adı en az 3 karakter olmalı')
        
    if not data.get('email'):
        errors.append('E-posta adresi gerekli')
    elif '@' not in data['email']:
        errors.append('Geçerli bir e-posta adresi girin')
        
    if not data.get('password'):
        errors.append('Şifre gerekli')
    elif len(data['password']) < 6:
        errors.append('Şifre en az 6 karakter olmalı')
        
    return errors

def validate_profile_data(data):
    errors = []
    
    if 'birth_date' in data and not data['birth_date']:
        errors.append('Doğum tarihi gerekli')
        
    if 'zodiac_sign' in data and not data['zodiac_sign']:
        errors.append('Burç seçimi gerekli')
        
    return errors 

def profile_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get('token') or request.headers.get('Authorization')
        
        if not token:
            if request.is_json:
                return jsonify({'error': 'Lütfen giriş yapın'}), 401
            return redirect(url_for('login_page'))
            
        try:
            if token.startswith('Bearer '):
                token = token.split(' ')[1]
                
            from app import app, users
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            user = users.get(data['email'])
            
            if not user:
                raise ValueError('Kullanıcı bulunamadı')
                
            # Profil bilgilerinin tamamlanıp tamamlanmadığını kontrol et
            required_fields = ['birth_date', 'zodiac_sign']
            if not all(field in user.__dict__ and user.__dict__[field] for field in required_fields):
                if request.is_json:
                    return jsonify({'error': 'Lütfen önce profilinizi tamamlayın'}), 403
                return redirect(url_for('profile_page'))
                
            return f(user, *args, **kwargs)
            
        except Exception as e:
            if request.is_json:
                return jsonify({'error': str(e)}), 401
            return redirect(url_for('login_page'))
            
    return decorated_function 