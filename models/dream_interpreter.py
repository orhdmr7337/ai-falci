import json
import random
from datetime import datetime

class DreamInterpreter:
    def __init__(self):
        self.dream_symbols = {
            'ev': [
                'Yeni bir başlangıç yapacaksınız',
                'Ailenizle ilgili güzel gelişmeler olacak',
                'İç huzurunuz artacak'
            ],
            'araba': [
                'Kariyerinizde ilerleme kaydedeceksiniz',
                'Yeni bir yolculuğa çıkacaksınız',
                'Hayatınızda hızlı değişimler olacak'
            ],
            'uçmak': [
                'Hedeflerinize ulaşacaksınız',
                'Özgürlüğünüze kavuşacaksınız',
                'Büyük bir başarı elde edeceksiniz'
            ],
            'deniz': [
                'Duygusal bir dönemden geçeceksiniz',
                'İç huzurunuz artacak',
                'Yeni bir aşka yelken açacaksınız'
            ],
            'ağaç': [
                'Aileniz büyüyecek',
                'Köklü değişiklikler yaşayacaksınız',
                'Maddi durumunuz iyileşecek'
            ],
            'bebek': [
                'Yeni bir başlangıç yapacaksınız',
                'Güzel bir haber alacaksınız',
                'Hayatınıza yeni biri girecek'
            ],
            'yılan': [
                'Düşmanlarınıza dikkat edin',
                'İş hayatınızda değişiklikler olacak',
                'Sağlığınıza dikkat etmelisiniz'
            ],
            'düğün': [
                'Mutlu bir döneme gireceksiniz',
                'Önemli bir karar vereceksiniz',
                'Hayatınızda yeni bir sayfa açılacak'
            ],
            'para': [
                'Maddi kazanç elde edeceksiniz',
                'İş hayatınızda yükselme olacak',
                'Beklenmedik bir gelir kapınızı çalacak'
            ],
            'uçurum': [
                'Riskli kararlar almaktan kaçının',
                'Tedbirli olmanız gereken bir dönemdesiniz',
                'Önemli bir karar arifesinde olabilirsiniz'
            ]
        }
        
    def interpret_dream(self, dream_text):
        """Rüyayı yorumlar"""
        try:
            # Rüya metnini küçük harfe çevir
            dream_text = dream_text.lower()
            
            # Bulunan sembolleri ve yorumlarını topla
            found_symbols = []
            interpretations = []
            
            # Metinde geçen sembolleri bul
            for symbol in self.dream_symbols:
                if symbol in dream_text:
                    found_symbols.append(symbol)
                    # Her sembol için rastgele bir yorum seç
                    interpretation = random.choice(self.dream_symbols[symbol])
                    interpretations.append(interpretation)
            
            # Eğer hiç sembol bulunamadıysa
            if not interpretations:
                return "Rüyanızda belirgin semboller bulamadım. Lütfen daha detaylı anlatır mısınız?"
            
            # Giriş cümlesi
            intro = f"Rüyanızda {', '.join(found_symbols)} sembolleri görünüyor. "
            
            # Yorumları birleştir
            interpretation_text = " ".join(interpretations)
            
            return intro + interpretation_text
            
        except Exception as e:
            print(f"Rüya yorumlama hatası: {str(e)}")
            return "Üzgünüm, şu anda rüyanızı yorumlayamıyorum. Lütfen daha sonra tekrar deneyin."
    
    def get_daily_tip(self):
        """Günlük rüya tavsiyesi verir"""
        tips = [
            "Rüyanızı hatırlamak için uyandığınızda hemen not alın.",
            "Uyumadan önce rüya görmek istediğinizi zihninizde tekrarlayın.",
            "Düzenli uyku saatleri rüyaları hatırlamayı kolaylaştırır.",
            "Rüya günlüğü tutmak, rüya sembollerini anlamada yardımcı olur.",
            "Uyumadan önce kafein tüketmekten kaçının.",
            "Rahat bir uyku ortamı rüya görme olasılığını artırır.",
            "Rüyalarınızı başkalarıyla paylaşmak yeni bakış açıları kazandırabilir."
        ]
        return random.choice(tips) 