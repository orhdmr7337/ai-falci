import tensorflow as tf
from tensorflow.keras import layers, models
import numpy as np
import os
from PIL import Image
import cv2
from sklearn.model_selection import train_test_split

class CoffeeFortuneModelTrainer:
    def __init__(self, data_dir='data/coffee_images'):
        self.data_dir = data_dir
        self.image_size = (224, 224)
        self.batch_size = 32
        self.epochs = 50
        
    def prepare_data(self):
        """Veri setini hazırla"""
        images = []
        labels = []
        
        # Veri klasörlerini oku
        for symbol_class in os.listdir(self.data_dir):
            class_dir = os.path.join(self.data_dir, symbol_class)
            if not os.path.isdir(class_dir):
                continue
                
            # Her sınıf için görüntüleri oku
            for image_file in os.listdir(class_dir):
                image_path = os.path.join(class_dir, image_file)
                try:
                    # Görüntüyü oku ve ön işle
                    image = self._preprocess_image(image_path)
                    images.append(image)
                    labels.append(symbol_class)
                except Exception as e:
                    print(f"Görüntü yükleme hatası {image_path}: {str(e)}")
        
        # Numpy dizilerine dönüştür
        X = np.array(images)
        y = np.array(labels)
        
        # Eğitim ve test setlerine ayır
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        return X_train, X_test, y_train, y_test
    
    def build_model(self, num_classes):
        """Model mimarisini oluştur"""
        base_model = tf.keras.applications.EfficientNetB0(
            include_top=False,
            weights='imagenet',
            input_shape=(*self.image_size, 3)
        )
        
        # Transfer öğrenme için temel modeli dondur
        base_model.trainable = False
        
        model = models.Sequential([
            base_model,
            layers.GlobalAveragePooling2D(),
            layers.Dropout(0.5),
            layers.Dense(256, activation='relu'),
            layers.Dropout(0.3),
            layers.Dense(num_classes, activation='softmax')
        ])
        
        return model
    
    def train_model(self):
        """Modeli eğit"""
        # Veriyi hazırla
        X_train, X_test, y_train, y_test = self.prepare_data()
        
        # Sınıf sayısını belirle
        num_classes = len(np.unique(y_train))
        
        # Modeli oluştur
        model = self.build_model(num_classes)
        
        # Modeli derle
        model.compile(
            optimizer='adam',
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        # Veri artırma
        data_augmentation = tf.keras.Sequential([
            layers.RandomFlip("horizontal"),
            layers.RandomRotation(0.2),
            layers.RandomZoom(0.2),
        ])
        
        # Eğitim
        history = model.fit(
            data_augmentation(X_train),
            y_train,
            batch_size=self.batch_size,
            epochs=self.epochs,
            validation_data=(X_test, y_test),
            callbacks=[
                tf.keras.callbacks.EarlyStopping(
                    patience=5,
                    restore_best_weights=True
                ),
                tf.keras.callbacks.ReduceLROnPlateau(
                    factor=0.2,
                    patience=3
                )
            ]
        )
        
        # Modeli kaydet
        model.save('models/coffee_fortune_model.h5')
        
        return history, model
    
    def _preprocess_image(self, image_path):
        """Görüntü ön işleme"""
        # Görüntüyü oku
        image = Image.open(image_path)
        image = image.convert('RGB')
        image = image.resize(self.image_size)
        
        # Numpy dizisine dönüştür
        image_array = np.array(image)
        
        # Normalize et
        image_array = image_array / 255.0
        
        return image_array

if __name__ == '__main__':
    # Model eğitimini başlat
    trainer = CoffeeFortuneModelTrainer()
    history, model = trainer.train_model()
    
    # Eğitim sonuçlarını görselleştir
    import matplotlib.pyplot as plt
    
    plt.figure(figsize=(12, 4))
    
    plt.subplot(1, 2, 1)
    plt.plot(history.history['accuracy'], label='Eğitim Doğruluğu')
    plt.plot(history.history['val_accuracy'], label='Doğrulama Doğruluğu')
    plt.title('Model Doğruluğu')
    plt.xlabel('Epoch')
    plt.ylabel('Doğruluk')
    plt.legend()
    
    plt.subplot(1, 2, 2)
    plt.plot(history.history['loss'], label='Eğitim Kaybı')
    plt.plot(history.history['val_loss'], label='Doğrulama Kaybı')
    plt.title('Model Kaybı')
    plt.xlabel('Epoch')
    plt.ylabel('Kayıp')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('training_results.png')
    plt.close() 