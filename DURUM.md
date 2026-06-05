# LevelTodo — Durum ve Yol Haritası

> Bu dosya "neredeyiz, sırada ne var" sorusunun tek bakışta cevabı.
> Yeni bir sohbet bu dosyayı + `CLAUDE.md`'yi + git geçmişini okuyarak kaldığı yerden devam edebilir.

## Kısa özet
- Dal: `claude/faz5-rutin-gunluk` (main'den açıldı) — commit `73a1f4f`, **push edilmedi**.
- Çalıştır: `.\.venv\Scripts\python.exe -m leveltodo`
- Test: `.\.venv\Scripts\python.exe -m pytest -q` → **134 test yeşil**, ruff temiz.
- Stack: Python 3.12.8 · PyQt6 · SQLAlchemy 2.0 + Alembic · blinker · python-dateutil · platformdirs · python-ulid.

## Bitti ✅
- **Faz 0** İskelet: katmanlı mimari, `bootstrap.py` Container + elle DI, `OlayHatti`(blinker)+Qt köprüsü, `Saat`(IClock)/`Gun`(DayId, gün-başlangıç vars. 04:00), enjekte `Sans`, Alembic migrations.
- **Faz 1** Çekirdek döngü: görev CRUD, tamamlama→XP/Puan defteri, kronometre (başlat/duraklat), Bugün/Tümü.
- **Faz 2** İstatistik+avatar: seviye/unvan bantları, Mana Seed sprite kompozit + AI avatar override (`assets/avatar_ai/`), unvan okları (kilitli ileri seviyeler koyu+kilit). Puan = **gerçek-hayat ödülü** (mağaza YOK).
- **Faz 3** Tekrar+seri: tekrarlı görevler, **görev-başına seri** (🔥N), **sınırsız** seri-dondurma (3 levelde +1), **ayrı Telafi menüsü**, ileri görevler görünür.
- **Faz 4** Oyunlaştırma: kritik (×2 XP+Puan, %10), combo zinciri, rozetler, epik-doğal Türkçe mesajlar.
- **Faz 5 / Adım 1** İrade-Disiplin: `will_acts` (migration 0007), `IradeServisi`, irade görünümü.
- **Faz 5 / Adım 2** Düşman/Şeytan: commit `2827e10`. 4 düşman, `max_hp=round(100*1.5^tier)`, görev XP'si → hasar (olay tabanlı), can bitince üst tier+tam can. Dashboard üst paneli: sprite + kırmızı can barı. Kullanıcının AI sprite'ları `assets/enemies/<anahtar>.png`.
- **Faz 5 / Adım 3** Rutin alanları (commit `73a1f4f`). Kullanıcı tanımlı günlük ölçütler. `routine_fields`+`routine_entries` (migration 0008), `domain/rutinler` (RutinTuru SAYI/EVET_HAYIR, Yon EN_AZ/EN_FAZLA, `hedef_tuttu_mu`), `RutinServisi` (alan ekle/pasife al, `deger_gir` → ödülü hedef durumuyla eşitler: tutunca seçilen stata `reward_xp` [gün-başına-tek], hedef artık tutmuyorsa ters/negatif kayıtla geri alır), ayrı "Rutin" sekmesi (`RutinView`, nav index 2). Stat alan başına seçilir. `tests/integration/test_rutin.py`.
- **Faz 5 / Adım 4** Gün sonu günlüğü (commit `73a1f4f`) — Faz 5 tamamlandı. `journal_entries`+`reflection_questions` (migration 0009), `domain/gunluk` (HAVUZ sabit sorular, `gunun_sorusu` takvim-günü dönüşümü, `gunluk_odulu`=40+1×dolu_gün artan eğri), `GunlukServisi` (günde tek, kaydet→Farkındalık'a artan XP [gün-başına-tek], boşaltınca ters kayıtla geri alır; reward_xp ilk dolduruşta sabitlenir; kendi soruları ekle/sil), ayrı "Günlük" sekmesi (`GunlukView`, nav index 3). `tests/integration/test_gunluk.py`.

- **Adım A — Plan düzeltmeleri** (Faz 6 öncesi, bildirimsiz restore'lar): Düşman hasar
  katsayısı (`HASAR_KATSAYISI`) + XP'siz günde iyileşme (`GUNLUK_IYILESME_ORANI`=%3,
  `DusmanServisi._iyilesme_uygula`, `dusman_son_etkinlik` ayarı); Rutin'e **metin türü**
  (`RutinTuru.METIN`, migration 0010 `value_text`, `metin_gir`, view metin satırı);
  **telafi 2× ödül** (`TELAFI_CARPAN`, `gorev_servisi.tamamla` geçmiş-gün dalı).

- **Faz 6.1 — Veri yedekleme/geri yükleme**: `infrastructure/backup/yedekleme.py`
  (`Yedekleyici`: sqlite_yedek_al, json_disa_aktar, geri_yukle_isaretle +
  bekleyen_geri_yukleme_uygula). Geri yükleme `<db>.restore` işaretiyle açılışta
  (motor öncesi, bootstrap) uygulanır — kilit sorunu yok. Ayarlar'da "Veri" paneli
  (yedek al / JSON / geri yükle). `tests/integration/test_backup.py`.

- **Faz 6.2 — Bildirim altyapısı**: `domain/bildirim` (BildirimKategori 4'lü,
  `sessiz_saatte_mi` gece-yarısı saran, `gosterilsin_mi`), `application/bildirim_servisi.py`
  (`BildirimServisi`: kategori aç/kapa + gece sessizliği 23-07 + `kanal_ekle`/`bildir`),
  `infrastructure/notifications/plyer_kanali.py` (OS bildirimi, hata yutar),
  `presentation/common/toast.py` (`ToastYoneticisi` garantili uygulama-içi toast, QSS
  #Toast). Ayarlar'da "Bildirimler" paneli. bootstrap: plyer kanalı + main_window toast
  kanalı. `tests/integration/test_bildirim.py`. plyer bağımlılık eklendi.

- **Faz 6.3 — Mesajlar**: `domain/mentor/mesajlar.py` (Mentor dürtme havuzu),
  `domain/dusman` KISKIRTMALAR + `kiskirtma_sec`, `application/mentor_servisi.py`
  (`MentorServisi.periyodik_kontrol`: ihmal eşiği 3 gün dürtme + %15 düşman kışkırtma +
  amnesti eşiği 10 uyarı; her biri gün başına tek). ledger `son_stat_gunleri`,
  gorev_servisi `telafi_sayisi`/`telafi_amnesti_uygula` + repo `gecmis_bekleyenleri_amnesti`.
  app.py'de 30dk periyodik QTimer + açılışta bir kez. Telafi ekranında "Yükü affet"
  afişi (≥10). `tests/integration/test_mentor.py`.

- **Faz 6.4 — Uyandırma disiplini**: `domain/uyandirma` (`dakikaya`, `uyanma_basarili_mi`,
  ODUL 50, TOLERANS 15dk), `WakeLog` (migration 0011, user+day unique),
  `SqlUyandirmaRepository`, `UyandirmaServisi` (hedef get/set, `kalktim` → zamanındaysa
  Disiplin'e XP, gün başına tek, **ceza yok**). İrade ekranında uyandırma kartı
  (QTimeEdit hedef + "Kalktım" + sonuç). `tests/integration/test_uyandirma.py`.

- **Faz 6.5 — Ses**: `infrastructure/sound/ses_motoru.py` (`SesMotoru` QSoundEffect,
  assets/sounds/<anahtar>.wav yükler, dosya yoksa sessiz), `secim.py` (`tamamlama_sesi`).
  Olaylar: `SeviyeAtlandi`/`DusmanDevrildi` (events.py) — dondurma seviye atlayınca,
  dusman devrilince yayınlar. main_window `_ses_isle` köprüden: tamamla/kritik/combo/
  seviye/dusman_devrildi. rozet→RozetView, hata→geç kalkış (İrade) + geçersiz yedek
  (Settings). Ayarlar'da "Ses" paneli (aç/kapa + düzey). 7 ses WAV (3 mp3 ffmpeg ile
  çevrildi) `assets/sounds/`. `tests/integration/test_ses.py`.

## Sırada ⏸️ — Faz 6 son adım (ASSET gerektirir)
- **6.6** Pixel-art font: `fonts.py` zaten assets/fonts/*.ttf yüklüyor (yoksa fallback
  monospace). **Kullanıcıdan CC0/OFL bir pixel .ttf istenecek**, assets/fonts/'a konunca
  otomatik devreye girer.
- Sonra Faz 7 → 8 → 9. **Push edilmedi** (kullanıcı "hadi" deyince).

## Çalışma kuralları (özet — tam hâli CLAUDE.md'de)
- Kullanıcı teknik değil → her değişiklikten sonra sade Türkçe anlat; soruları sonuç-odaklı sor; arayüz tamamen Türkçe.
- Her adım sonu: **tik-kutucuk doğrulama listesi** + kısa sunum-anlatımı.
- Mesaj tonu: gündelik Türkçe + epik alt ton; klişe değil.
- Kod isimleri ASCII-Türkçe; kalıplaşmış terimler ve ORM/Qt/Alembic API İngilizce.
- Asset eksikse durma → kullanıcıdan iste (ne gerek + boyut/format/stil + AI prompt). Mana Seed dosyalarını yeniden adlandırma.
- Push yalnızca kullanıcı açıkça isteyince. Commit sonu: `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`.
