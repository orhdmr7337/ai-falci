# AI Falcı - Yapay Zeka Destekli Fal Uygulaması

AI Falcı, modern yapay zeka teknolojilerini kullanarak geleneksel fal bakma yöntemlerini dijitalleştiren bir uygulamadır. Kahve falı, tarot, el falı ve günlük fal gibi çeşitli fal türlerini destekler.

## Özellikler

- 🔮 **Kahve Falı**: Fincan fotoğraflarını yapay zeka ile analiz ederek yorumlar
- 🎴 **Tarot Falı**: Kullanıcının sorularına göre tarot kartları seçer ve yorumlar
- ✋ **El Falı**: El fotoğraflarını analiz ederek el çizgilerini yorumlar
- 📅 **Günlük Fal**: Kişiselleştirilmiş günlük yorumlar sunar

## Kurulum

1. Gerekli Python paketlerini yükleyin:
```bash
pip install -r requirements.txt
```

2. Uygulamayı başlatın:
```bash
python app.py
```

## API Kullanımı

### Kahve Falı
```bash
POST /api/fortune/coffee
Content-Type: multipart/form-data
Body: image=<fincan_fotografi>
```

### Tarot Falı
```bash
POST /api/fortune/tarot
Content-Type: application/json
Body: {
    "question": "Sorunuz"
}
```

### El Falı
```bash
POST /api/fortune/palm
Content-Type: multipart/form-data
Body: image=<el_fotografi>
```

### Günlük Fal
```bash
GET /api/fortune/daily?birth_date=YYYY-MM-DD&name=İsim
```

## Teknik Detaylar

- Flask web framework'ü
- TensorFlow ve OpenCV görüntü işleme
- Transformers doğal dil işleme
- RESTful API tasarımı

## Geliştirme

1. Repo'yu klonlayın
2. Sanal ortam oluşturun
3. Gerekli paketleri yükleyin
4. Geliştirmeye başlayın!

## Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun
3. Değişikliklerinizi commit edin
4. Branch'inizi push edin
5. Pull request açın

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın. 