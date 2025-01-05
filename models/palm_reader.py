import cv2
import numpy as np
from PIL import Image
import json
import random

class PalmReader:
    def __init__(self):
        self.lines = {
            'kalp': [
                'Duygusal ve tutkulu bir kişiliğiniz var',
                'Aşk hayatınızda önemli değişiklikler olacak',
                'Romantik ilişkilerinizde daha seçici olmalısınız'
            ],
            'kafa': [
                'Analitik düşünme yeteneğiniz çok güçlü',
                'Eğitim hayatınızda başarılar sizi bekliyor',
                'Yeni bir öğrenme sürecine gireceksiniz'
            ],
            'yaşam': [
                'Uzun ve sağlıklı bir ömrünüz olacak',
                'Hayatınızda önemli dönüm noktaları var',
                'Yakında büyük bir değişim yaşayacaksınız'
            ],
            'kader': [
                'Kariyerinizde yükselme fırsatları görünüyor',
                'Önemli bir karar arifesinde olabilirsiniz',
                'İş hayatınızda beklenmedik gelişmeler olacak'
            ],
            'güneş': [
                'Yaratıcılığınız ön plana çıkacak',
                'Sanatsal yeteneklerinizi geliştirin',
                'Başarı ve şöhret sizi bekliyor'
            ],
            'ay': [
                'Sezgileriniz güçlenecek',
                'Ruhsal gelişiminiz hızlanacak',
                'İç sesinizi dinlemelisiniz'
            ]
        }
        
    def preprocess_image(self, image_path):
        """El fotoğrafını ön işlemden geçirir"""
        try:
            # Görüntüyü oku
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError("Görüntü okunamadı")
            
            # Gri tonlamaya çevir
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Gürültüyü azalt
            denoised = cv2.GaussianBlur(gray, (5,5), 0)
            
            # Kenar tespiti
            edges = cv2.Canny(denoised, 100, 200)
            
            return edges
        except Exception as e:
            print(f"Görüntü işleme hatası: {str(e)}")
            return None
    
    def detect_lines(self, edges):
        """El çizgilerini tespit eder"""
        try:
            # Hough dönüşümü ile çizgileri bul
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50, minLineLength=100, maxLineGap=10)
            
            if lines is None:
                return []
            
            detected_lines = []
            for line in lines:
                x1, y1, x2, y2 = line[0]
                # Çizgi uzunluğu
                length = np.sqrt((x2-x1)**2 + (y2-y1)**2)
                # Çizgi açısı
                angle = np.arctan2(y2-y1, x2-x1) * 180 / np.pi
                
                # Çizgi tipini belirle (basit)
                if length > 200:
                    if -30 < angle < 30:
                        detected_lines.append('yaşam')
                    elif 30 < angle < 60:
                        detected_lines.append('kafa')
                    elif -60 < angle < -30:
                        detected_lines.append('kalp')
                    else:
                        detected_lines.append('kader')
            
            return detected_lines
            
        except Exception as e:
            print(f"Çizgi tespit hatası: {str(e)}")
            return []
    
    def interpret_lines(self, lines):
        """Tespit edilen çizgileri yorumlar"""
        interpretations = []
        
        # Her çizgi için rastgele bir yorum seç
        for line in lines:
            if line in self.lines:
                interpretation = random.choice(self.lines[line])
                interpretations.append(interpretation)
        
        # Eğer hiç çizgi tespit edilmediyse
        if not interpretations:
            interpretations = ["El çizgileriniz net görünmüyor. Lütfen daha net bir fotoğraf çekin."]
        
        return interpretations
    
    def read_palm(self, image_path):
        """Ana fonksiyon: El fotoğrafını alır ve yorum döndürür"""
        try:
            # Görüntüyü işle
            edges = self.preprocess_image(image_path)
            if edges is None:
                return "Görüntü işlenemedi, lütfen tekrar deneyin."
            
            # Çizgileri tespit et
            lines = self.detect_lines(edges)
            
            # Çizgileri yorumla
            interpretations = self.interpret_lines(lines)
            
            # Giriş cümlesi
            if lines:
                intro = f"Elinizde {', '.join(set(lines))} çizgileri belirgin görünüyor. "
            else:
                intro = ""
            
            # Yorumları birleştir
            reading = intro + " ".join(interpretations)
            
            return reading
            
        except Exception as e:
            print(f"El falı okuma hatası: {str(e)}")
            return "Üzgünüm, şu anda el falınızı okuyamıyorum. Lütfen daha sonra tekrar deneyin."
    
    def get_daily_tip(self):
        """Günlük el falı tavsiyesi verir"""
        tips = [
            "El çizgilerinizi daha net görmek için ellerinizi ılık suyla yıkayın.",
            "Fotoğraf çekerken doğal ışık kullanın.",
            "Avuç içinizi tam açarak fotoğraf çekin.",
            "Sol el geçmişi, sağ el geleceği gösterir.",
            "El çizgilerinizi düzenli olarak inceleyin, zamanla değişebilirler.",
            "El bakımı yaparak çizgilerin daha belirgin olmasını sağlayın.",
            "Stres el çizgilerinizi etkileyebilir, sakin bir yaşam sürün."
        ]
        return random.choice(tips) 