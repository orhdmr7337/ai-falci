from abc import ABC, abstractmethod
import numpy as np
from datetime import datetime
import random

class BaseFortune(ABC):
    """Temel fal sınıfı"""
    
    @abstractmethod
    def interpret(self, *args, **kwargs):
        """Falı yorumla"""
        pass
    
    @abstractmethod
    def validate_input(self, *args, **kwargs):
        """Girdiyi doğrula"""
        pass

class ZodiacFortune(BaseFortune):
    """Burç yorumu sınıfı"""
    
    ZODIAC_SIGNS = {
        'aries': {'date_range': ((3, 21), (4, 19)), 'element': 'fire'},
        'taurus': {'date_range': ((4, 20), (5, 20)), 'element': 'earth'},
        'gemini': {'date_range': ((5, 21), (6, 20)), 'element': 'air'},
        'cancer': {'date_range': ((6, 21), (7, 22)), 'element': 'water'},
        'leo': {'date_range': ((7, 23), (8, 22)), 'element': 'fire'},
        'virgo': {'date_range': ((8, 23), (9, 22)), 'element': 'earth'},
        'libra': {'date_range': ((9, 23), (10, 22)), 'element': 'air'},
        'scorpio': {'date_range': ((10, 23), (11, 21)), 'element': 'water'},
        'sagittarius': {'date_range': ((11, 22), (12, 21)), 'element': 'fire'},
        'capricorn': {'date_range': ((12, 22), (1, 19)), 'element': 'earth'},
        'aquarius': {'date_range': ((1, 20), (2, 18)), 'element': 'air'},
        'pisces': {'date_range': ((2, 19), (3, 20)), 'element': 'water'}
    }
    
    def get_zodiac_sign(self, birth_date):
        """Doğum tarihine göre burç hesapla"""
        month = birth_date.month
        day = birth_date.day
        
        for sign, data in self.ZODIAC_SIGNS.items():
            start_date = data['date_range'][0]
            end_date = data['date_range'][1]
            
            if (month == start_date[0] and day >= start_date[1]) or \
               (month == end_date[0] and day <= end_date[1]):
                return sign
        
        return None
    
    def validate_input(self, birth_date):
        """Doğum tarihi formatını kontrol et"""
        try:
            if isinstance(birth_date, str):
                birth_date = datetime.strptime(birth_date, '%Y-%m-%d')
            return True, birth_date
        except:
            return False, "Geçersiz tarih formatı"
    
    def interpret(self, birth_date):
        """Burç yorumu yap"""
        is_valid, result = self.validate_input(birth_date)
        if not is_valid:
            return result
        
        sign = self.get_zodiac_sign(result)
        if not sign:
            return "Burç hesaplanamadı"
        
        # Burç yorumu oluştur
        return self._generate_zodiac_reading(sign)
    
    def _generate_zodiac_reading(self, sign):
        """Burç yorumu oluştur"""
        # Burada daha karmaşık bir yorum sistemi kullanılabilir
        base_readings = {
            'fire': [
                "Enerjiniz yüksek ve yeni projelere başlamak için uygun bir dönemdesiniz.",
                "Yaratıcılığınız dorukta, bu enerjiyi doğru yönlendirin."
            ],
            'earth': [
                "Pratik çözümler bulma konusunda başarılı olacaksınız.",
                "Maddi konularda olumlu gelişmeler yaşanabilir."
            ],
            'air': [
                "İletişim becerileriniz güçlü, yeni bağlantılar kurabilirsiniz.",
                "Entelektüel faaliyetler için uygun bir dönem."
            ],
            'water': [
                "Duygusal zekanız yüksek, ilişkilerinizde olumlu gelişmeler olabilir.",
                "Sezgilerinize güvenin, size doğru yolu gösterecek."
            ]
        }
        
        element = self.ZODIAC_SIGNS[sign]['element']
        reading = random.choice(base_readings[element])
        
        return reading

class RuneFortune(BaseFortune):
    """Rün falı sınıfı"""
    
    RUNES = {
        'fehu': {
            'meaning': 'Servet, başarı',
            'reversed_meaning': 'Kayıp, başarısızlık'
        },
        'uruz': {
            'meaning': 'Güç, sağlık',
            'reversed_meaning': 'Zayıflık, hastalık'
        },
        'thurisaz': {
            'meaning': 'Koruma, güç',
            'reversed_meaning': 'Tehlike, savunmasızlık'
        }
    }
    
    def validate_input(self, rune_count):
        """Rün sayısını kontrol et"""
        if not isinstance(rune_count, int) or rune_count < 1 or rune_count > 9:
            return False, "Rün sayısı 1-9 arasında olmalıdır"
        return True, rune_count
    
    def interpret(self, rune_count=3):
        """Rün falı bak"""
        is_valid, result = self.validate_input(rune_count)
        if not is_valid:
            return result
        
        # Rünleri seç
        selected_runes = random.sample(list(self.RUNES.keys()), result)
        readings = []
        
        # Her rün için yorum oluştur
        for rune in selected_runes:
            is_reversed = random.choice([True, False])
            reading = self.RUNES[rune]['reversed_meaning' if is_reversed else 'meaning']
            readings.append({
                'rune': rune,
                'is_reversed': is_reversed,
                'meaning': reading
            })
        
        return readings

class NumerologyFortune(BaseFortune):
    """Numeroloji falı sınıfı"""
    
    NUMBER_MEANINGS = {
        1: "Liderlik, bağımsızlık",
        2: "İşbirliği, denge",
        3: "Yaratıcılık, ifade",
        4: "Stabilite, düzen",
        5: "Değişim, özgürlük",
        6: "Uyum, sorumluluk",
        7: "Analiz, içgörü",
        8: "Güç, başarı",
        9: "Evrensel sevgi, hizmet"
    }
    
    def calculate_life_path_number(self, birth_date):
        """Yaşam yolu sayısını hesapla"""
        # Tarihi string'e çevir ve sadece sayıları al
        date_str = birth_date.strftime('%Y%m%d')
        
        # Tüm rakamları topla
        total = sum(int(digit) for digit in date_str)
        
        # Tek basamaklı sayıya indir
        while total > 9:
            total = sum(int(digit) for digit in str(total))
        
        return total
    
    def validate_input(self, birth_date):
        """Doğum tarihi formatını kontrol et"""
        try:
            if isinstance(birth_date, str):
                birth_date = datetime.strptime(birth_date, '%Y-%m-%d')
            return True, birth_date
        except:
            return False, "Geçersiz tarih formatı"
    
    def interpret(self, birth_date):
        """Numeroloji yorumu yap"""
        is_valid, result = self.validate_input(birth_date)
        if not is_valid:
            return result
        
        life_path_number = self.calculate_life_path_number(result)
        meaning = self.NUMBER_MEANINGS.get(life_path_number, "Bilinmeyen sayı")
        
        return {
            'life_path_number': life_path_number,
            'meaning': meaning
        } 