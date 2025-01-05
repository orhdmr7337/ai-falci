import sqlite3
import json
from datetime import datetime, timedelta
from functools import wraps

class Cache:
    def __init__(self, db_path='cache.db'):
        """SQLite bağlantısını başlat"""
        self.db_path = db_path
        self._init_db()
        
        # Varsayılan TTL değerleri (saniye)
        self.default_ttl = {
            'fortune': 3600,  # 1 saat
            'user': 86400,    # 24 saat
            'tarot': 43200    # 12 saat
        }
    
    def _init_db(self):
        """Veritabanı tablosunu oluştur"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS cache
            (key TEXT PRIMARY KEY,
             value TEXT,
             expires_at TIMESTAMP)
        ''')
        conn.commit()
        conn.close()
    
    def cache_key(self, prefix, *args):
        """Önbellek anahtarı oluştur"""
        return f"{prefix}:{':'.join(str(arg) for arg in args)}"
    
    def get(self, key):
        """Önbellekten veri al"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('SELECT value, expires_at FROM cache WHERE key = ?', (key,))
            result = c.fetchone()
            conn.close()
            
            if result:
                value, expires_at = result
                if datetime.strptime(expires_at, '%Y-%m-%d %H:%M:%S') > datetime.now():
                    return json.loads(value)
                else:
                    self.delete(key)
            return None
        except:
            return None
    
    def set(self, key, value, ttl=None):
        """Önbelleğe veri kaydet"""
        try:
            if ttl is None:
                prefix = key.split(':')[0]
                ttl = self.default_ttl.get(prefix, 3600)
            
            expires_at = datetime.now() + timedelta(seconds=ttl)
            
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('''
                INSERT OR REPLACE INTO cache (key, value, expires_at)
                VALUES (?, ?, ?)
            ''', (key, json.dumps(value), expires_at.strftime('%Y-%m-%d %H:%M:%S')))
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def delete(self, key):
        """Önbellekten veri sil"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('DELETE FROM cache WHERE key = ?', (key,))
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def clear_pattern(self, pattern):
        """Belirli bir desene uyan tüm anahtarları sil"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('DELETE FROM cache WHERE key LIKE ?', (f'{pattern}%',))
            conn.commit()
            conn.close()
            return True
        except:
            return False

def cached(prefix, ttl=None):
    """Önbellekleme için dekoratör"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cache_key = f"{prefix}:{f.__name__}:{hash(str(args) + str(kwargs))}"
            cache = Cache()
            result = cache.get(cache_key)
            
            if result is not None:
                return result
            
            result = f(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            
            return result
        return decorated_function
    return decorator

class UserCache:
    """Kullanıcı önbelleği işlemleri"""
    def __init__(self):
        self.cache = Cache()
        self.prefix = 'user'
    
    def get_user(self, user_id):
        """Kullanıcı bilgilerini önbellekten al"""
        key = self.cache.cache_key(self.prefix, user_id)
        return self.cache.get(key)
    
    def set_user(self, user_id, user_data):
        """Kullanıcı bilgilerini önbelleğe kaydet"""
        key = self.cache.cache_key(self.prefix, user_id)
        return self.cache.set(key, user_data)
    
    def clear_user(self, user_id):
        """Kullanıcı önbelleğini temizle"""
        key = self.cache.cache_key(self.prefix, user_id)
        return self.cache.delete(key)

class FortuneCache:
    """Fal önbelleği işlemleri"""
    def __init__(self):
        self.cache = Cache()
        self.prefix = 'fortune'
    
    def get_fortune(self, fortune_id):
        """Fal sonucunu önbellekten al"""
        key = self.cache.cache_key(self.prefix, fortune_id)
        return self.cache.get(key)
    
    def set_fortune(self, fortune_id, fortune_data):
        """Fal sonucunu önbelleğe kaydet"""
        key = self.cache.cache_key(self.prefix, fortune_id)
        return self.cache.set(key, fortune_data)
    
    def clear_fortune(self, fortune_id):
        """Fal önbelleğini temizle"""
        key = self.cache.cache_key(self.prefix, fortune_id)
        return self.cache.delete(key)
    
    def get_user_fortunes(self, user_id):
        """Kullanıcının fal geçmişini önbellekten al"""
        key = self.cache.cache_key(self.prefix, f"user:{user_id}")
        return self.cache.get(key)
    
    def set_user_fortunes(self, user_id, fortunes_data):
        """Kullanıcının fal geçmişini önbelleğe kaydet"""
        key = self.cache.cache_key(self.prefix, f"user:{user_id}")
        return self.cache.set(key, fortunes_data)

class TarotCache:
    """Tarot kartları önbelleği işlemleri"""
    def __init__(self):
        self.cache = Cache()
        self.prefix = 'tarot'
    
    def get_card(self, card_name):
        """Tarot kartı bilgilerini önbellekten al"""
        key = self.cache.cache_key(self.prefix, card_name)
        return self.cache.get(key)
    
    def set_card(self, card_name, card_data):
        """Tarot kartı bilgilerini önbelleğe kaydet"""
        key = self.cache.cache_key(self.prefix, card_name)
        return self.cache.set(key, card_data)
    
    def get_all_cards(self):
        """Tüm tarot kartlarını önbellekten al"""
        key = self.cache.cache_key(self.prefix, 'all')
        return self.cache.get(key)
    
    def set_all_cards(self, cards_data):
        """Tüm tarot kartlarını önbelleğe kaydet"""
        key = self.cache.cache_key(self.prefix, 'all')
        return self.cache.set(key, cards_data) 