from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_from_directory
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from models.fortune_model import FortuneTeller
from models.coffee_model import CoffeeFortuneModel
from models.palm_reader import PalmReader
from models.dream_interpreter import DreamInterpreter
from models.user import User
from auth import login_required, profile_required, validate_registration_data, validate_profile_data
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
import jwt
from functools import wraps
from werkzeug.security import generate_password_hash
import numpy as np
import cv2
import tensorflow as tf
from tensorflow.keras.models import load_model

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Güvenli bir anahtar kullanın
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Login manager kurulumu
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_page'

# Modeli yükle
try:
    coffee_cup_model = load_model('models/coffee_cup_detector.h5')
    print("Kahve fincanı tespit modeli başarıyla yüklendi")
except Exception as e:
    print(f"Model yükleme hatası: {str(e)}")
    coffee_cup_model = None

@login_manager.user_loader
def load_user(user_id):
    # E-posta adresini kullanarak kullanıcıyı bul
    for user in users.values():
        if str(user.id) == str(user_id):
            return user
    return None

# Demo kullanıcılar
demo_user = User()
demo_user.id = 1
demo_user.username = "demo"
demo_user.email = "demo@example.com"
demo_user.set_password("demo123")
demo_user.email_verified = True

demo_admin = User()
demo_admin.id = 2
demo_admin.username = "admin"
demo_admin.email = "admin@example.com"
demo_admin.set_password("admin123")
demo_admin.email_verified = True
demo_admin.is_admin = True

# Geçici kullanıcı veritabanı
users = {
    'demo@example.com': demo_user,
    'admin@example.com': demo_admin
}

# Admin required decorator
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
                
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            user = users.get(data['email'])
            
            if not user or not user.is_admin:
                raise ValueError('Bu sayfaya erişim yetkiniz yok')
                
            return f(*args, **kwargs)
            
        except Exception as e:
            if request.is_json:
                return jsonify({'error': str(e)}), 401
            return redirect(url_for('login_page'))
            
    return decorated_function

# Model nesnelerini oluştur
fortune_teller = FortuneTeller()
coffee_model = CoffeeFortuneModel()
palm_reader = PalmReader()
dream_interpreter = DreamInterpreter()

# Sayfa yönlendirmeleri
@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/verify-email')
def verify_email_page():
    return render_template('verify-email.html')

@app.route('/forgot-password')
def forgot_password_page():
    return render_template('forgot-password.html')

# API endpoint'leri
@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Veri doğrulama
        errors = validate_registration_data(data)
        if errors:
            return jsonify({'errors': errors}), 400
        
        # E-posta kontrolü
        if data['email'] in users:
            return jsonify({'error': 'Bu e-posta adresi zaten kullanılıyor'}), 400
        
        # Kullanıcı oluştur
        user = User()
        user.id = len(users) + 1
        user.username = data['username']
        user.email = data['email']
        user.set_password(data['password'])
        user.email_verified = True  # Geliştirme aşamasında doğrulamayı atlıyoruz
        
        # Kullanıcıyı geçici veritabanına kaydet
        users[user.email] = user
        
        # Kullanıcıyı giriş yap
        login_user(user)
        
        # Token oluştur
        auth_token = user.generate_auth_token(app.config['SECRET_KEY'])
        
        return jsonify({
            'token': auth_token,
            'user': user.to_dict(),
            'message': 'Kayıt başarılı!'
        })
        
    except Exception as e:
        print(f"Kayıt hatası: {str(e)}")
        return jsonify({'error': 'Kayıt sırasında bir hata oluştu'}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'E-posta ve şifre gerekli'}), 400
        
        user = users.get(data['email'])
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Geçersiz e-posta veya şifre'}), 401
        
        # Son giriş zamanını güncelle
        user.last_login = datetime.utcnow()
        
        # Kullanıcıyı giriş yap
        login_user(user)
        
        # Token oluştur
        token = user.generate_auth_token(app.config['SECRET_KEY'])
        
        return jsonify({
            'token': token,
            'user': user.to_dict(),
            'message': 'Giriş başarılı!'
        })
        
    except Exception as e:
        print(f"Giriş hatası: {str(e)}")
        return jsonify({'error': 'Giriş sırasında bir hata oluştu'}), 500

@app.route('/api/auth/verify-email/<token>')
def verify_email(token):
    try:
        # Token'ı doğrula
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = email_verifications.get(token)
        
        if not user_id:
            return jsonify({'error': 'Geçersiz veya kullanılmış doğrulama bağlantısı'}), 400
        
        # Kullanıcıyı bul
        user = next((u for u in users.values() if u.id == user_id), None)
        if not user:
            return jsonify({'error': 'Kullanıcı bulunamadı'}), 404
        
        # E-posta doğrulandı olarak işaretle
        user.email_verified = True
        
        # Token'ı sil
        del email_verifications[token]
        
        return redirect(url_for('login_page'))
        
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Doğrulama bağlantısının süresi dolmuş'}), 400
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Geçersiz doğrulama bağlantısı'}), 400

@app.route('/api/auth/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({'error': 'E-posta adresi gerekli'}), 400
    
    user = users.get(email)
    if not user:
        return jsonify({'error': 'Bu e-posta adresiyle kayıtlı kullanıcı bulunamadı'}), 404
    
    # Şifre sıfırlama token'ı oluştur
    reset_token = jwt.encode(
        {'user_id': user.id, 'exp': datetime.utcnow() + datetime.timedelta(hours=1)},
        app.config['SECRET_KEY'],
        algorithm='HS256'
    )
    
    # E-posta gönder (bu kısım e-posta servisi entegrasyonunda eklenecek)
    # send_password_reset_email(email, reset_token)
    
    return jsonify({
        'message': 'Şifre sıfırlama bağlantısı e-posta adresinize gönderildi'
    })

@app.route('/api/auth/reset-password/<token>', methods=['POST'])
def reset_password(token):
    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = data['user_id']
        
        # Kullanıcıyı bul
        user = next((u for u in users.values() if u.id == user_id), None)
        if not user:
            return jsonify({'error': 'Kullanıcı bulunamadı'}), 404
        
        # Yeni şifreyi ayarla
        new_password = request.json.get('password')
        if not new_password or len(new_password) < 6:
            return jsonify({'error': 'Geçersiz şifre'}), 400
            
        user.set_password(new_password)
        
        return jsonify({
            'message': 'Şifreniz başarıyla güncellendi'
        })
        
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Şifre sıfırlama bağlantısının süresi dolmuş'}), 400
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Geçersiz şifre sıfırlama bağlantısı'}), 400

@app.route('/api/profile', methods=['GET'])
@login_required
def get_profile(user):
    return jsonify(user.to_dict())

@app.route('/api/profile/update', methods=['POST'])
@login_required
def update_profile(user):
    data = request.get_json()
    
    # Veri doğrulama
    errors = validate_profile_data(data)
    if errors:
        return jsonify({'errors': errors}), 400
    
    # Profili güncelle
    user.update_profile(data)
    
    # Veritabanını güncelle (veritabanı entegrasyonunda eklenecek)
    
    return jsonify({
        'message': 'Profil başarıyla güncellendi',
        'user': user.to_dict()
    })

@app.route('/api/profile/readings', methods=['GET'])
@login_required
def get_readings(user):
    return jsonify({
        'readings': user.readings_history
    })

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/kahve-fali')
def coffee_fortune():
    return render_template('coffee_fortune.html')

@app.route('/el-fali')
def palm():
    return render_template('palm.html')

@app.route('/tarot')
def tarot():
    return render_template('tarot.html')

@app.route('/burc-yorumu')
def zodiac():
    return render_template('zodiac.html')

@app.route('/ruya-yorumu')
def dream():
    return render_template('dream.html')

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@app.route('/api/profile/settings', methods=['POST'])
@login_required
def update_profile_settings(user):
    try:
        data = request.get_json()
        
        # E-posta güncelleme
        if 'email' in data and data['email'] != user.email:
            # E-posta değişikliği için doğrulama gerekebilir
            user.email = data['email']
        
        # Şifre güncelleme
        if 'password' in data and data['password']:
            user.set_password(data['password'])
        
        # Bildirim ayarları
        if 'notifications' in data:
            user.notifications = {
                'email': bool(data['notifications'].get('email')),
                'daily': bool(data['notifications'].get('daily'))
            }
        
        return jsonify({'message': 'Ayarlar başarıyla güncellendi'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/upgrade-premium', methods=['POST'])
@login_required
def upgrade_premium(user):
    try:
        # Ödeme sayfasına yönlendirme için gerekli bilgileri hazırla
        payment_data = {
            'user_id': user.id,
            'amount': 49.99,  # Aylık ücret
            'currency': 'TRY',
            'description': 'Premium Üyelik - Aylık'
        }
        
        # Ödeme işlemi başlatıldı olarak işaretle
        user.pending_payment = payment_data
        
        return jsonify({
            'message': 'Ödeme sayfasına yönlendiriliyorsunuz',
            'payment_url': '/payment'  # Gerçek ödeme sayfası URL'si
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/readings/<reading_id>')
@login_required
def view_reading(user, reading_id):
    # Kullanıcının falını bul
    reading = next(
        (r for r in user.readings if str(r.get('id')) == reading_id),
        None
    )
    
    if not reading:
        return jsonify({'error': 'Fal bulunamadı'}), 404
    
    return render_template('reading.html', reading=reading)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    response = redirect(url_for('home'))
    response.delete_cookie('token')
    return response

# Admin login sayfası
@app.route('/admin/login')
def admin_login_page():
    return render_template('admin_login.html')

# Admin login API endpoint'i
@app.route('/api/auth/admin/login', methods=['POST'])
def admin_login():
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'E-posta ve şifre gerekli'}), 400
        
        user = users.get(data['email'])
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Geçersiz e-posta veya şifre'}), 401
            
        if not user.is_admin:
            return jsonify({'error': 'Bu sayfaya erişim yetkiniz yok'}), 403
        
        # Son giriş zamanını güncelle
        user.last_login = datetime.utcnow()
        
        # Kullanıcıyı giriş yap
        login_user(user)
        
        # Token oluştur
        token = user.generate_auth_token(app.config['SECRET_KEY'])
        
        return jsonify({
            'token': token,
            'user': user.to_dict(),
            'message': 'Admin girişi başarılı!'
        })
        
    except Exception as e:
        print(f"Admin giriş hatası: {str(e)}")
        return jsonify({'error': 'Giriş sırasında bir hata oluştu'}), 500

@app.route('/api/validate-coffee-image', methods=['POST'])
def validate_coffee_image():
    if 'image' not in request.files:
        return jsonify({'error': 'Görüntü dosyası bulunamadı'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'Dosya seçilmedi'}), 400

    try:
        # Görüntüyü oku
        image_bytes = file.read()
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return jsonify({
                'isValidCoffeeImage': False,
                'message': 'Görüntü okunamadı. Lütfen geçerli bir fotoğraf yükleyin.'
            }), 400
        
        # Görüntü boyutlarını kontrol et
        height, width = img.shape[:2]
        if width < 200 or height < 200:
            return jsonify({
                'isValidCoffeeImage': False,
                'message': 'Fotoğraf çok küçük. Lütfen daha yüksek çözünürlüklü bir fotoğraf yükleyin.'
            }), 400
        
        # Gri tonlamaya çevir
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Gürültü azaltma
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Kenar tespiti
        edges = cv2.Canny(denoised, 50, 150)
        
        # Daire tespiti
        circles = cv2.HoughCircles(
            edges,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=100,
            param1=50,
            param2=30,
            minRadius=int(min(width, height) * 0.2),
            maxRadius=int(min(width, height) * 0.4)
        )
        
        if circles is None:
            return jsonify({
                'isValidCoffeeImage': False,
                'message': 'Fotoğrafta kahve fincanı tespit edilemedi. Lütfen fincanın tamamının göründüğü bir fotoğraf çekin.'
            })
        
        # Fincan içindeki telve kontrolü
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            x, y, r = i
            # Fincan içi ROI
            mask = np.zeros_like(gray)
            cv2.circle(mask, (x, y), int(r * 0.8), 255, -1)
            roi = cv2.mean(gray, mask=mask)[0]
            
            # Telve kontrolü (koyu renkli bölge)
            if roi > 180:  # Çok açık renkli
                return jsonify({
                    'isValidCoffeeImage': False,
                    'message': 'Fincan içinde telve tespit edilemedi. Lütfen falın daha net göründüğü bir fotoğraf çekin.'
                })
        
        return jsonify({
            'isValidCoffeeImage': True,
            'message': 'Kahve fincanı başarıyla tespit edildi.'
        })

    except Exception as e:
        print(f"Görüntü doğrulama hatası: {str(e)}")
        return jsonify({
            'isValidCoffeeImage': False,
            'message': 'Fotoğraf işlenirken bir hata oluştu. Lütfen tekrar deneyin.'
        }), 500

@app.route('/api/coffee-fortune', methods=['POST'])
@login_required
def api_coffee_fortune():
    if 'image' not in request.files:
        return jsonify({'error': 'Fotoğraf yüklenmedi'}), 400
    
    image = request.files['image']
    if image.filename == '':
        return jsonify({'error': 'Dosya seçilmedi'}), 400
    
    # Kullanıcı profili ve ruh hali bilgilerini al
    data = request.form.to_dict()
    mood = data.get('mood')
    
    try:
        # Görüntüyü oku
        image_bytes = image.read()
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return jsonify({'error': 'Görüntü okunamadı'}), 400
        
        # Kahve falı analizi yap
        result = coffee_model.analyze_fortune(
            img,
            user_profile=current_user.profile,
            mood=mood
        )
        
        # Sonucu kaydet
        timestamp = datetime.now().isoformat()
        image_filename = f'coffee_{timestamp}.jpg'
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
        
        # Görüntüyü kaydet
        cv2.imwrite(image_path, img)
        
        # Kullanıcının fal geçmişine ekle
        current_user.add_reading(
            reading_type='coffee',
            result=result['fortune'],
            image_path=image_filename,
            mood=mood
        )
        
        return jsonify({
            'fortune': result['fortune'],
            'symbols': result['symbols'],
            'timestamp': timestamp,
            'image_path': image_filename
        })
        
    except Exception as e:
        print(f"Kahve falı analiz hatası: {str(e)}")
        return jsonify({
            'error': 'Fal analizi sırasında bir hata oluştu. Lütfen daha net bir fotoğraf ile tekrar deneyin.'
        }), 500

@app.route('/api/palm-reading', methods=['POST'])
def api_palm_reading():
    if 'image' not in request.files:
        return jsonify({'error': 'Fotoğraf yüklenmedi'}), 400
    
    image = request.files['image']
    if image.filename == '':
        return jsonify({'error': 'Dosya seçilmedi'}), 400
        
    # El fotoğrafı işleme ve yapay zeka analizi burada yapılacak
    fortune = "El çizgileriniz uzun ve başarılı bir kariyer yolculuğuna işaret ediyor..."
    
    return jsonify({'fortune': fortune})

@app.route('/api/tarot', methods=['POST'])
def api_tarot():
    data = request.get_json()
    question = data.get('question')
    
    if not question:
        return jsonify({'error': 'Soru belirtilmedi'}), 400
        
    # Tarot kartları ve yorumları burada yapılacak
    cards = [
        {'name': 'The Fool', 'image': '/static/images/tarot/fool.jpg'},
        {'name': 'The Magician', 'image': '/static/images/tarot/magician.jpg'},
        {'name': 'The High Priestess', 'image': '/static/images/tarot/priestess.jpg'}
    ]
    fortune = "Tarot kartları size yakın zamanda önemli bir karar vermeniz gerekeceğini gösteriyor..."
    
    return jsonify({'cards': cards, 'fortune': fortune})

@app.route('/api/zodiac', methods=['POST'])
def api_zodiac():
    data = request.get_json()
    birthdate = data.get('birthdate')
    
    if not birthdate:
        return jsonify({'error': 'Doğum tarihi belirtilmedi'}), 400
        
    # Burç hesaplama ve yorum burada yapılacak
    zodiac = {
        'name': 'Koç',
        'dates': '21 Mart - 20 Nisan'
    }
    fortune = "Bu hafta kariyer hayatınızda önemli gelişmeler olabilir..."
    
    return jsonify({'zodiac': zodiac, 'fortune': fortune})

@app.route('/api/dream', methods=['POST'])
def api_dream():
    data = request.get_json()
    dream = data.get('dream')
    
    if not dream:
        return jsonify({'error': 'Rüya anlatılmadı'}), 400
        
    # Rüya yorumu burada yapılacak
    fortune = "Rüyanızda gördüğünüz semboller yakın zamanda alacağınız güzel haberlere işaret ediyor..."
    
    return jsonify({'fortune': fortune})

if __name__ == '__main__':
    # Upload klasörünü oluştur
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    app.run(debug=True) 