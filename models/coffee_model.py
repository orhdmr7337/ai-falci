import cv2
import numpy as np
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.layers import Input, Conv2D, MaxPooling2D, UpSampling2D, concatenate, Dropout
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import os
import json
from datetime import datetime

class CoffeeFortuneModel:
    def __init__(self):
        self.image_size = (224, 224)
        self.model_path = 'models/weights/coffee_fortune_model.h5'
        self.symbols_path = 'data/coffee_symbols.json'
        self.training_data_path = 'data/training_images'
        self.model = self._create_or_load_model()
        self.symbols_db = self._load_symbols_db()
        
    def _create_or_load_model(self):
        """Model oluştur veya var olan modeli yükle"""
        if os.path.exists(self.model_path):
            return load_model(self.model_path)
        else:
            return self._create_model()
            
    def _create_model(self):
        """U-Net benzeri bir model mimarisi oluştur"""
        inputs = Input(self.image_size + (3,))
        
        # Encoder
        conv1 = Conv2D(64, 3, activation='relu', padding='same')(inputs)
        conv1 = Conv2D(64, 3, activation='relu', padding='same')(conv1)
        pool1 = MaxPooling2D(pool_size=(2, 2))(conv1)
        
        conv2 = Conv2D(128, 3, activation='relu', padding='same')(pool1)
        conv2 = Conv2D(128, 3, activation='relu', padding='same')(conv2)
        pool2 = MaxPooling2D(pool_size=(2, 2))(conv2)
        
        conv3 = Conv2D(256, 3, activation='relu', padding='same')(pool2)
        conv3 = Conv2D(256, 3, activation='relu', padding='same')(conv3)
        
        # Decoder
        up1 = concatenate([UpSampling2D(size=(2, 2))(conv3), conv2])
        conv4 = Conv2D(128, 3, activation='relu', padding='same')(up1)
        conv4 = Conv2D(128, 3, activation='relu', padding='same')(conv4)
        
        up2 = concatenate([UpSampling2D(size=(2, 2))(conv4), conv1])
        conv5 = Conv2D(64, 3, activation='relu', padding='same')(up2)
        conv5 = Conv2D(64, 3, activation='relu', padding='same')(conv5)
        
        # Çıktı katmanı
        outputs = Conv2D(32, 1, activation='sigmoid')(conv5)
        
        model = Model(inputs=inputs, outputs=outputs)
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        
        return model
    
    def _load_symbols_db(self):
        """Kahve falı sembollerini ve anlamlarını yükle"""
        if os.path.exists(self.symbols_path):
            with open(self.symbols_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def preprocess_image(self, image):
        """Görüntü ön işleme"""
        # Boyutlandırma
        image = cv2.resize(image, self.image_size)
        
        # Gri tonlamaya çevir
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Gürültü azaltma
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Kontrast iyileştirme
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(denoised)
        
        # Kenar tespiti
        edges = cv2.Canny(enhanced, 50, 150)
        
        # Morfolojik işlemler
        kernel = np.ones((5,5), np.uint8)
        dilated = cv2.dilate(edges, kernel, iterations=1)
        
        # Normalizasyon
        normalized = dilated.astype('float32') / 255.0
        
        return normalized
    
    def detect_symbols(self, image):
        """Fincandaki sembolleri tespit et"""
        processed = self.preprocess_image(image)
        
        # Kontur tespiti
        contours, _ = cv2.findContours(
            (processed * 255).astype(np.uint8),
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        symbols = []
        height, width = processed.shape[:2]
        min_area = (width * height) * 0.001  # Minimum alan eşiği
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < min_area:
                continue
            
            x, y, w, h = cv2.boundingRect(contour)
            
            # Sembol bölgesini çıkar
            symbol_roi = image[y:y+h, x:x+w]
            
            # Sembol türünü belirle
            symbol_type = self._classify_symbol(symbol_roi)
            
            # Sembolün konumuna göre kategori belirle
            category = self._determine_category(y, height)
            
            symbols.append({
                'type': symbol_type,
                'category': category,
                'position': {'x': x, 'y': y},
                'size': {'width': w, 'height': h}
            })
        
        return symbols
    
    def _determine_category(self, y_pos, height):
        """Sembolün konumuna göre kategori belirle"""
        if y_pos < height * 0.33:
            return 'kariyer'
        elif y_pos < height * 0.66:
            return 'ask'
        else:
            return 'saglik'
    
    def _classify_symbol(self, symbol_image):
        """Tespit edilen sembolün türünü belirle"""
        # Basit şekil analizi
        gray = cv2.cvtColor(symbol_image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        
        # Kontur özellikleri
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return "belirsiz"
        
        contour = max(contours, key=cv2.contourArea)
        
        # Şekil özellikleri
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        circularity = 4 * np.pi * area / (perimeter * perimeter) if perimeter > 0 else 0
        
        # Şekil sınıflandırma
        if 0.85 < circularity < 1.15:
            return "yuvarlak"
        elif circularity < 0.6:
            return "uzun"
        else:
            return "karma"
    
    def interpret_fortune(self, symbols, user_profile=None, mood=None):
        """Tespit edilen sembollere göre fal yorumu oluştur"""
        fortune = {
            'genel': [],
            'ask': [],
            'kariyer': [],
            'saglik': []
        }
        
        # Kullanıcı profilini kontrol et
        if user_profile:
            meslek = user_profile.get('meslek')
            medeni_durum = user_profile.get('medeni_durum')
            yas = user_profile.get('yas')
            
            # Mesleğe göre kariyer yorumlarını özelleştir
            if meslek:
                fortune['kariyer'].append(f"{meslek} alanında önemli gelişmeler görünüyor...")
            
            # Medeni duruma göre aşk yorumlarını özelleştir
            if medeni_durum == 'bekar':
                fortune['ask'].append("Yeni bir tanışma olasılığı yüksek...")
            elif medeni_durum == 'evli':
                fortune['ask'].append("Eşinizle ilişkiniz güçlenecek...")
            
            # Yaşa göre sağlık yorumlarını özelleştir
            if yas:
                if int(yas) > 50:
                    fortune['saglik'].append("Düzenli check-up önemli olacak...")
                else:
                    fortune['saglik'].append("Enerji seviyeniz yükselecek...")
        
        # Ruh haline göre yorumları özelleştir
        if mood:
            if mood == 'mutlu':
                fortune['genel'].append("Pozitif enerjiniz devam edecek...")
            elif mood == 'üzgün':
                fortune['genel'].append("Moralinizi yükseltecek haberler yolda...")
            elif mood == 'stresli':
                fortune['genel'].append("Yakında rahatlayacağınız bir dönem başlayacak...")
        
        # Sembollere göre yorumları ekle
        for symbol in symbols:
            symbol_type = symbol['type']
            category = symbol['category']
            
            meaning = self._get_symbol_meaning(symbol_type, category)
            if meaning:
                fortune[category].append(meaning)
        
        return self._format_fortune(fortune)
    
    def _get_symbol_meaning(self, symbol_type, category):
        """Sembol ve kategoriye göre anlam getir"""
        if symbol_type in self.symbols_db and category in self.symbols_db[symbol_type]:
            meanings = self.symbols_db[symbol_type][category]
            return np.random.choice(meanings) if isinstance(meanings, list) else meanings
        return ""
    
    def _format_fortune(self, fortune_dict):
        """Fal yorumunu formatla"""
        formatted = []
        
        if fortune_dict['genel']:
            formatted.append("Genel Görünüm:\n" + " ".join(fortune_dict['genel']))
        
        if fortune_dict['ask']:
            formatted.append("\nAşk Hayatı:\n" + " ".join(fortune_dict['ask']))
            
        if fortune_dict['kariyer']:
            formatted.append("\nKariyer:\n" + " ".join(fortune_dict['kariyer']))
            
        if fortune_dict['saglik']:
            formatted.append("\nSağlık:\n" + " ".join(fortune_dict['saglik']))
        
        return "\n".join(formatted)
    
    def train(self, epochs=10, batch_size=32):
        """Modeli eğit"""
        if not os.path.exists(self.training_data_path):
            raise ValueError("Eğitim verileri bulunamadı")
            
        # Veri artırma
        datagen = ImageDataGenerator(
            rotation_range=20,
            width_shift_range=0.2,
            height_shift_range=0.2,
            shear_range=0.2,
            zoom_range=0.2,
            horizontal_flip=True,
            fill_mode='nearest',
            validation_split=0.2
        )
        
        # Eğitim ve doğrulama verilerini yükle
        train_generator = datagen.flow_from_directory(
            self.training_data_path,
            target_size=self.image_size,
            batch_size=batch_size,
            class_mode='input',
            subset='training'
        )
        
        validation_generator = datagen.flow_from_directory(
            self.training_data_path,
            target_size=self.image_size,
            batch_size=batch_size,
            class_mode='input',
            subset='validation'
        )
        
        # Modeli eğit
        history = self.model.fit(
            train_generator,
            epochs=epochs,
            validation_data=validation_generator
        )
        
        # Modeli kaydet
        self.model.save(self.model_path)
        
        return history
    
    def save_training_data(self, image, symbols, user_profile=None, mood=None):
        """Eğitim verisi olarak kaydet"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Görüntüyü kaydet
        image_path = os.path.join(self.training_data_path, f'coffee_{timestamp}.jpg')
        
        if not os.path.exists(self.training_data_path):
            os.makedirs(self.training_data_path)
            
        cv2.imwrite(image_path, image)
        
        # Analiz verilerini kaydet
        metadata = {
            'symbols': symbols,
            'user_profile': user_profile,
            'mood': mood,
            'timestamp': timestamp
        }
        
        metadata_path = os.path.join(
            self.training_data_path,
            f'coffee_{timestamp}_metadata.json'
        )
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    def analyze_fortune(self, image, user_profile=None, mood=None):
        """Kahve falı analizi yap"""
        # Sembolleri tespit et
        symbols = self.detect_symbols(image)
        
        # Kullanıcı profilini ve ruh halini dikkate alarak yorumları özelleştir
        fortune = self.interpret_fortune(symbols, user_profile, mood)
        
        # Eğitim verisi olarak kaydet
        self.save_training_data(image, symbols, user_profile, mood)
        
        return {
            'fortune': fortune,
            'symbols': symbols,
            'timestamp': datetime.now().isoformat()
        } 