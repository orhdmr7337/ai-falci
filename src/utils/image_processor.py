import cv2
import numpy as np
from PIL import Image
import tensorflow as tf

class ImageProcessor:
    def __init__(self):
        # Görüntü işleme parametreleri
        self.target_size = (224, 224)
        self.preprocessing_functions = {
            'coffee': self._preprocess_coffee_image,
            'palm': self._preprocess_palm_image
        }
    
    def process_coffee_cup(self, image_file):
        """Kahve fincanı fotoğrafını işler"""
        # Görüntüyü oku
        image = self._read_image(image_file)
        
        # Görüntüyü ön işle
        processed_image = self._preprocess_coffee_image(image)
        
        return processed_image
    
    def process_palm_image(self, image_file):
        """El falı için el fotoğrafını işler"""
        # Görüntüyü oku
        image = self._read_image(image_file)
        
        # Görüntüyü ön işle
        processed_image = self._preprocess_palm_image(image)
        
        return processed_image
    
    def _read_image(self, image_file):
        """Görüntü dosyasını okur ve numpy dizisine dönüştürür"""
        # PIL Image olarak oku
        image = Image.open(image_file)
        
        # RGB'ye dönüştür
        image = image.convert('RGB')
        
        # Numpy dizisine dönüştür
        image_array = np.array(image)
        
        return image_array
    
    def _preprocess_coffee_image(self, image):
        """Kahve fincanı görüntüsünü ön işler"""
        # Boyutu yeniden ayarla
        resized = cv2.resize(image, self.target_size)
        
        # Görüntüyü normalize et
        normalized = resized / 255.0
        
        # Kontrast artır
        enhanced = self._enhance_contrast(normalized)
        
        # Kenarları belirginleştir
        edges = self._detect_edges(enhanced)
        
        return edges
    
    def _preprocess_palm_image(self, image):
        """El fotoğrafını ön işler"""
        # Boyutu yeniden ayarla
        resized = cv2.resize(image, self.target_size)
        
        # Görüntüyü normalize et
        normalized = resized / 255.0
        
        # Çizgileri belirginleştir
        enhanced_lines = self._enhance_palm_lines(normalized)
        
        return enhanced_lines
    
    def _enhance_contrast(self, image):
        """Görüntü kontrastını artırır"""
        # Lab renk uzayına dönüştür
        lab = cv2.cvtColor((image * 255).astype(np.uint8), cv2.COLOR_RGB2LAB)
        
        # L kanalını eşitle
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        cl = clahe.apply(l)
        
        # Kanalları birleştir
        enhanced_lab = cv2.merge((cl, a, b))
        
        # RGB'ye geri dönüştür
        enhanced_rgb = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2RGB)
        
        return enhanced_rgb / 255.0
    
    def _detect_edges(self, image):
        """Görüntüdeki kenarları tespit eder"""
        # Gri tonlamaya dönüştür
        gray = cv2.cvtColor((image * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
        
        # Gürültüyü azalt
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Kenarları tespit et
        edges = cv2.Canny(blurred, 50, 150)
        
        return edges
    
    def _enhance_palm_lines(self, image):
        """El çizgilerini belirginleştirir"""
        # Gri tonlamaya dönüştür
        gray = cv2.cvtColor((image * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
        
        # Adaptif eşikleme uygula
        binary = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            11,
            2
        )
        
        # Morfolojik işlemler
        kernel = np.ones((3,3), np.uint8)
        enhanced = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        return enhanced 