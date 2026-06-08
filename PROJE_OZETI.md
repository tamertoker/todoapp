# Proje Revizyon Özeti: "Level-Up Todo" (8 Haziran 2026)

Bu belge, projedeki son büyük güncellemeleri ve eklenen yeni özellikleri teknik detaylarıyla özetlemektedir. Sunum hazırlığı için temel teşkil eder.

## 1. Düşman (Şeytan) Sistemi
Tembelliği görselleştiren ve oyunlaştıran yeni bir mekanik eklenmiştir.

- **Teknik Mimari:** `DusmanServisi` (Application) ve `Dusman` (Domain) modülleri üzerinden yönetilir.
- **Biriken Hasar (Accumulated Damage):** Görevler tamamlandığında düşmana anında hasar verilmez. Kazanılan XP, `hasar_katsayısı` ile çarpılarak "biriken hasar" havuzuna eklenir. Kullanıcı UI üzerinden "Vur" komutu verdiğinde tüm hasar tek seferde indirilir.
- **Tier ve Evrim:** Düşmanlar tier sistemine sahiptir. Her tier'da maksimum HP doğrusal artar. Her 3 tier'da bir düşman karakteri değişir veya boyutu (`BOYUT_CARPANLARI`) büyür.
- **İyileşme Mekaniği:** Hasar alınmayan her gün için düşman maksimum canının %3'ü kadar iyileşir.
- **Hazine Ödülleri:** Düşman devrildiğinde bir `HazineOdulu` düşer. Bu ödüller Puan, XP veya Combo çarpanı (x1.5) olabilir.

## 2. Mağaza ve Ödül Sistemi
Kullanıcının kazandığı puanları gerçek hayat ödüllerine dönüştürebileceği bir market modülü eklenmiştir.

- **Maliyet Hesaplama:** Ödüller "dakika başına puan" (`cost_per_min`) esasına göre fiyatlandırılır.
- **Persistence:** `SqlMagazaRepository` üzerinden ödüller ve satın alma geçmişi (`StorePurchase`) takip edilir.
- **Esneklik:** Kullanıcı kendi ödüllerini ekleyebilir, silebilir veya maliyetlerini güncelleyebilir.

## 3. Cüzdan ve Tasarruf Yönetimi
Uygulama içi puandan bağımsız olarak, kullanıcının gerçek parasını yönettiği bir finans modülü.

- **Kuruş Bazlı Takip:** Tüm finansal işlemler veri tutarlılığı için kuruş cinsinden saklanır.
- **Aylık Hedefler:** Kullanıcı "Tasarruf Hedefi" ve "Harcama Bütçesi" belirleyebilir. `aylik_ozet` fonksiyonu gelir/gider dengesini raporlar.
- **Wishlist (İstek Listesi):** Satın alınmak istenen ürünler listelenir. Bu ürünlerin "fonlanma oranı", cüzdan bakiyesinin ürün fiyatına oranına göre anlık hesaplanır.

## 4. Gelişmiş Takvim ve Zaman Çizelgesi
Kullanıcının çalışma bloklarını görselleştiren yeni bir `TakvimView` bileşeni eklenmiştir.

- **Görselleştirme:** 24 saatlik ızgara üzerinde çalışma blokları renkli dikdörtgenler olarak çizilir.
- **Çakışma Yönetimi (Conflict Handling):** Aynı saat dilimine denk gelen birden fazla görev, sütun genişliği bölünerek yan yana gösterilir (`_seri_yerlesim` algoritması).
- **Zoom ve Navigasyon:** Kullanıcı dikey ölçeği (saat başına düşen piksel) değiştirebilir ve Gün/Hafta görünümleri arasında geçiş yapabilir.

## 5. UI/UX ve Estetik Güncellemeler
Uygulamanın "canlı" hissettirmesi için dinamik öğeler eklenmiştir.

- **Zamana Bağlı Temalar:** Arka planlar ve avatar görselleri günün saatine göre (Sabah, Öğlen, İkindi, Akşam, Gece) otomatik değişir.
- **Yeni Fontlar ve İkonlar:** Pixel art estetiğine uygun `PixelifySans`, `Silkscreen` gibi fontlar ve genişletilmiş ikon seti (XP, Puan, Seri, Rozet ikonları) entegre edilmiştir.
- **Otomatik Tazeleme:** Saat dilimi sınırlarında UI öğeleri `tick` mekanizmasıyla otomatik güncellenir.

## 6. Veritabanı ve Altyapı
- **Migrasyonlar:** SQLite şeması; Cüzdan (0012), Mağaza (0013), Etiketler (0014), Özel Statlar (0015) ve Seanslar (0016-17) için güncellenmiştir.
- **Bildirim Sistemi:** `BildirimServisi` üzerinden hatırlatıcılar ve ödül duyuruları yönetilir.
