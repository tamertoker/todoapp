# 05 — 15 Dakikalık Sunum Akışı (iskelet + zamanlama)

> Amaç: ilk 5 dakikada "ne yaptım", sonraki 10 dakikada "nasıl yaptım (teknik)".
> Demo ile teknik anlatımı harmanla. Slayt yapacaksan her madde ≈ 1 slayt.

## 0:00–1:30 — Giriş & problem
- Kendini tanıt, projenin adı: **LevelTodo**.
- Problem: "Yapılacaklar listeleri motive etmiyor; insan erteliyor."
- Çözüm tek cümle: "Görev takibini bir RPG'ye çevirdim — her görev XP/puan/seviye
  kazandırır, tembelliği temsil eden düşmana hasar verir."

## 1:30–4:00 — Canlı demo (kısa, akıcı)
Şu 3 senaryoyu göster (önceden prova et):
1. Görev ekle → tamamla → XP barının dolması, ses, unvan.
2. Düşman sekmesi → "Vur" → biriken hasarın inmesi, can barı, baloncuk → hazine.
3. İstatistik/Pano (takvim veya halka grafiği) → "verilerim görselleşiyor".
- Demo sırasında **bir cümle teknik köprü** at: "Bunu birazdan mimaride göstereceğim."

## 4:00–6:00 — Teknoloji yığını & genel mimari
- Teknolojiler: Python 3.12, PyQt6, SQLite + SQLAlchemy + Alembic, Blinker, pytest.
- **5 katmanlı mimari** şeması (00/01 dosyasındaki kutu çizimi).
- Tek mesaj: "Bağımlılıklar içeriye, saf domain'e akar."

## 6:00–9:00 — Mimarinin kalbi: katmanlar + neden
- domain (saf kurallar), application (servisler), infrastructure (DB/IO), presentation (PyQt), shared.
- Bağımlılık yönü + faydaları: test edilebilirlik, değiştirilebilirlik.
- **1 tasarım deseni derinlemesine:** `HasarliDefter` (Decorator) — "XP veren her eylem
  düşmana hasar versin'i mevcut kodu değiştirmeden tek noktadan ekledim."

## 9:00–12:00 — İz sürme: "Görev tamamla → seviye atla" (yıldız bölüm)
03-iz-surme TRACE 2'yi sözel anlat:
- View → ViewModel → `GorevServisi.tamamla`
- Ödül **saf domain'de** hesaplanır → defter (event/ledger) → olay yayını
- Seviye **defterden** hesaplanıp önceki ile kıyaslanır → `SeviyeAtlandi` → ses/ekran.
- Burada "tek doğruluk kaynağı" ve "event bus" fikrini vurgula.

## 12:00–14:00 — Veritabanı tasarımı (öne çıkan 2 karar)
- **Şablon/Oluşum** ayrımı (tekrarlı görev + bozulmayan geçmiş).
- **Ledger / Event Sourcing** (bakiye tutmuyorum, topluyorum → tutarlılık).
- Alembic ile 18 migration, açılışta otomatik şema güncelleme.

## 14:00–15:00 — Kapanış
- Öğrendiklerin: temiz mimari, tasarım desenleri, test edilebilir tasarım.
- Olası gelecek: çoklu profil (zaten user_id hazır), mobil, bulut senkron.
- Teşekkür → "Sorularınızı alabilirim."

---

## Sahne notları
- **Yavaş konuş, terimleri açıkla.** Jüri her terimi bilmeyebilir.
- Her teknik karardan sonra **"çünkü..."** de. Gerekçe = puan.
- Demo çökerse panikleme: ekran görüntüsü/yedek video hazır bulundur.
- Bilmediğin bir şey sorulursa: "Bunu şöyle çözdüm / şu an emin değilim ama mantığı şudur"
  — uydurmaktan iyidir.
- En güçlü 3 kozun: **(1) HasarliDefter/Decorator, (2) Ledger/tek doğruluk kaynağı,
  (3) Saat protokolü ile test edilebilirlik.** Bunları mutlaka geçir.
```
