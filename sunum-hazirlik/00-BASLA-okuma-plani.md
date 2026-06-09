# 🎓 Bitirme Sunumu Hazırlık Kılavuzu — BURADAN BAŞLA

Bu klasör, **LevelTodo** (RPG öğeli görev takip uygulaması) projesine sunum öncesi
"aşırı hâkim" olman için hazırlandı. Telefonundan da okuyabilmen için markdown.

## Dosyalar (okuma sırası)

1. **00-BASLA-okuma-plani.md** ← buradasın (plan + teknoloji + sözlük)
2. **01-mimari-ve-desenler.md** — Katmanlı mimari, OOP, tasarım desenleri *(en çok soru buradan gelir)*
3. **02-veritabani-ve-veri-akisi.md** — Veritabanı tasarımı, ORM, migration, defter (ledger)
4. **03-iz-surme-trace.md** — "Görev oluştur / tamamla / seviye atla / düşmanı vur" arka plan akışı *(senin istediğin iz sürme)*
5. **04-soru-bankasi.md** — Hocanın sorabileceği zor sorular + örnek cevaplar
6. **05-sunum-15dk-akis.md** — 15 dakikalık sunum iskeleti (ne, ne zaman söylenecek)

## 3 günde değil, 1 gecede çalışma planı

Zamanın kısıtlı (yarın sunum). Şu sırayla çalış:

| Sıra | Ne yap | Süre | Neden |
|------|--------|------|-------|
| 1 | **03-iz-surme** dosyasını oku, kodla yan yana | 45 dk | Hocanın en sevdiği soru tipi; bir akışı baştan sona anlatabilmek = hâkimiyet kanıtı |
| 2 | **01-mimari** dosyasını oku | 40 dk | "Neden 5 katman? Bağımlılık yönü?" kesin sorulur |
| 3 | **02-veritabani** dosyasını oku | 30 dk | Entity/tablo/ilişki soruları |
| 4 | **04-soru-bankasi**'ndaki soruları kapatıp kendine sor | 40 dk | Sınav provası |
| 5 | **05-sunum-akisi**'na göre 1 kez yüksek sesle prova | 20 dk | Akıcılık |
| 6 | Uygulamayı çalıştır, 2-3 senaryoyu canlı dene | 15 dk | Demo güveni |

> **Altın kural:** Ezber değil, **"neden böyle yaptım"** anlat. Her tasarım kararının
> bir gerekçesi var (bu dosyalarda hep "Neden:" diye işaretledim). Hoca gerekçeyi sever.

## Uygulamayı çalıştırma

```powershell
# proje kökünde
.venv\Scripts\activate
python -m leveltodo
```

## Teknoloji yığını (ezberle — "hangi teknolojiler?" ilk sorulardan)

| Katman | Teknoloji | Ne işe yarar |
|--------|-----------|--------------|
| Dil | **Python 3.12** | Tüm proje |
| Arayüz (GUI) | **PyQt6** | Masaüstü pencere, butonlar, çizim (QPainter) |
| Grafik | **pyqtgraph + numpy** | İstatistik çizgi grafikleri |
| Veritabanı | **SQLite** | Tek dosyalık yerel veritabanı |
| ORM | **SQLAlchemy 2.0** | Python sınıfları ↔ SQL tabloları eşlemesi |
| Şema göçü | **Alembic** | Veritabanı şemasının sürümlenmesi (18 migration) |
| Olay hattı | **Blinker** | Yayıncı-abone (pub-sub) sinyalleri |
| Kimlik üretimi | **python-ulid** | Sıralanabilir benzersiz ID'ler |
| OS bildirimi | **plyer** | Masaüstü bildirimleri |
| Dizin yolları | **platformdirs** | İşletim sistemine göre veri klasörü |
| Kalite | **Ruff** | Linter / formatlayıcı |
| Test | **Pytest** | (Test paketi son commit'te silindi — geri getirilebilir) |

## Proje tek cümleyle

> "Yapılacaklar listesini bir RPG'ye çeviren masaüstü uygulaması: her görev sana XP ve
> puan kazandırır, statlarını ve seviyeni büyütür, tembelliği temsil eden 'düşman'a hasar
> verir; puanları gerçek hayat ödüllerine çevirebilir, gerçek paranı ve zamanını yönetebilirsin."

## Mini sözlük (kod Türkçe — terimleri bil)

| Kodda | İngilizce / anlam |
|-------|-------------------|
| `Gorev` / şablon (template) | Görev tanımı (ör. "Her gün spor") |
| `instance` (oluşum/kayıt) | Görevin belli bir güne düşen somut kopyası |
| `defter` (ledger) | XP/puan kayıt defteri (her kazanım ayrı satır) |
| `Stat` | Gelişim alanı (Entelektüellik, Beden, Farkındalık, Disiplin) |
| `unvan` | Profil seviyesine göre rütbe (Çırak → Efsane) |
| `dondurma` (freeze) | Seri koruma jetonu |
| `combo` | Kısa sürede çok görevde ödül çarpanı |
| `tier` (kademe) | Düşmanın gücü/sırası |
| `Saat` | Zamanı veren protokol (testte sahtesi verilir) |
| `OlayHatti` | Event bus (olay yayını) |
| `Container` | Tüm servislerin toplandığı bağımlılık kabı |
```
