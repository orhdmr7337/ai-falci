from flask import Blueprint, request, jsonify, current_app
from src.models.fortune_model import FortuneTeller
from src.utils.image_processor import ImageProcessor
from src.auth.auth import Auth
from src.models.user import User, db

api_bp = Blueprint('api', __name__)
fortune_teller = FortuneTeller()
image_processor = ImageProcessor()

@api_bp.route('/health', methods=['GET'])
def health_check():
    """API sağlık kontrolü"""
    return jsonify({
        "status": "healthy",
        "message": "AI Falcı API çalışıyor"
    })

@api_bp.route('/fortune/coffee', methods=['POST'])
def get_coffee_fortune():
    """Kahve falı endpoint'i"""
    try:
        if 'image' not in request.files:
            return jsonify({
                "error": "Fincan fotoğrafı gerekli"
            }), 400
        
        image = request.files['image']
        
        # Görüntüyü işle
        processed_image = image_processor.process_coffee_cup(image)
        
        # Falı yorumla
        fortune = fortune_teller.interpret_coffee(processed_image)
        
        return jsonify({
            "success": True,
            "fortune": fortune
        })
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "Fal bakma işlemi başarısız oldu"
        }), 500

@api_bp.route('/fortune/tarot', methods=['POST'])
def get_tarot_reading():
    """Tarot falı endpoint'i"""
    try:
        data = request.get_json()
        
        if not data or 'question' not in data:
            return jsonify({
                "error": "Soru gerekli"
            }), 400
        
        # Tarot falı bak
        reading = fortune_teller.read_tarot(data['question'])
        
        return jsonify({
            "success": True,
            "reading": reading
        })
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "Tarot falı bakma işlemi başarısız oldu"
        }), 500

@api_bp.route('/fortune/zodiac', methods=['POST'])
def get_zodiac_reading():
    """Burç yorumu endpoint'i"""
    try:
        data = request.get_json()
        
        if not data or 'birth_date' not in data:
            return jsonify({
                "error": "Doğum tarihi gerekli"
            }), 400
        
        # Burç yorumu al
        reading = fortune_teller.interpret_zodiac(data['birth_date'])
        
        return jsonify({
            "success": True,
            "reading": reading
        })
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "Burç yorumu alma işlemi başarısız oldu"
        }), 500 