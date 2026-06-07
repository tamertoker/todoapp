# LevelTodo — Durum ve Yol Haritası

> Bu dosya "neredeyiz, sırada ne var" sorusunun tek bakışta cevabı.
> Yeni bir sohbet bu dosyayı + `CLAUDE.md`'yi + git geçmişini okuyarak kaldığı yerden devam edebilir.

## Kısa özet
- Dal: `claude/faz5-rutin-gunluk` (main'den açıldı) — Faz 0-8 burada, **push edilmedi**.
- Çalıştır: `.\.venv\Scripts\python.exe -m leveltodo`
- Test: `.\.venv\Scripts\python.exe -m pytest -q` → **168 test yeşil**, ruff temiz (`ruff check src/ tests/`).
- Stack: Python 3.12.8 · PyQt6 (+QtMultimedia) · SQLAlchemy 2.0 + Alembic · blinker · python-dateutil · platformdirs · python-ulid · plyer · pyqtgraph + numpy.

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

- **Faz 6.6 — Fontlar (Faz 6 BİTTİ)**: `fonts.py` tüm assets/fonts/*.ttf yükler
  (`load_all_fonts`/`mevcut_fontlar`/`varsayilan_font`/`gecerli_font`); 5 aile (Pixelify
  Sans default, Geo, Press Start 2P, Silkscreen, VT323). Ayarlar'da "Yazı tipi" seçici;
  `SettingsViewModel.fontChanged` → `app._apply_font` canlı uygular. ayar "font".
- **Uyanma güncellemesi**: `UyandirmaServisi.kalktim(gercek=None)` artık elle "HH:MM"
  alır (kullanıcı saatler sonra açabilir); İrade kartında Kalkış QTimeEdit + "Kalktım".
- **Bildirim debug**: plyer_kanali + bildirim_servisi log ekledi; `BildirimServisi.
  kanallara_gonder` (kuralları atlayan teşhis yolu); Debug ekranında "Test bildirimi"
  (zorla+kurallı) ve "Mentor kontrolünü çalıştır"; gün-atlamada mentor.periyodik_kontrol
  tetikleniyor. **ÖNEMLİ teşhis: gece sessizliği (23-07) varsayılan açık → o saatlerde
  TÜM bildirimler (toast dahil) bastırılır** — kullanıcının "gelmedi" sorununun olası sebebi.

## Faz 7 — İstatistik ✅ (bitti)
- **7.1 Veri katmanı**: `IstatistikServisi` (metrik_secenekleri: xp/calisma/tamamlama +
  her sayı/evet-hayır rutin alanı; gunluk_seri; stat_dagilimi; gun_araligi hafta/ay/yil;
  rekorlar). Repo toplamaları (ledger/task/rutin). `tests/integration/test_istatistik.py`.
- **7.2 Ekran**: "İstatistik" sekmesi (nav). Metrik+aralık+görünüm seçici;
  `presentation/common/heatmap.py` (IsiHaritasi QPainter, GitHub-tarzı, hover tooltip)
  ↔ pyqtgraph çizgi grafiği; stat XP dağılımı (QProgressBar'lar) + kişisel rekorlar paneli.
  pyqtgraph+numpy bağımlılık eklendi.

## Faz 8 — Cüzdan ✅ (bitti)
- **8.1 Veri+servis**: `CuzdanServisi` (gelir/gider KURUŞ, bakiye, aylık özet=tasarruf
  + harcama bütçesi iki hedef, wishlist ilerleme=bakiye/fiyat). models WalletTransaction
  + WishlistItem (migration 0012). `domain/cuzdan` (ilerleme_orani, kurus_tl).
  `tests/integration/test_cuzdan.py`.
- **8.2 Ekran**: "Cüzdan" sekmesi — bakiye, gelir/gider ekle+liste+sil, iki aylık hedef
  barı, wishlist (resim seç → `presentation/common/resim_acilma.py` ResimAcilma:
  ilerledikçe görsel soldan sağa açılır; resim yoksa yeşil dolum çubuğu).

## Mağaza ✅ (plan dışı — kullanıcı kararı değişti)
KARAR DEĞİŞTİ: oyun-içi **Puan artık Mağaza'da gerçek-hayat ödüllerini DAKİKA cinsinden
satın almak için harcanıyor** (eski "mağaza yok" kararı geçersiz). Cüzdan=gerçek para ile
karışmaz; Mağaza=Puan→dakika.
- `domain/magaza` (MIN_DK_MALIYET=1, VARSAYILAN_ODULLER, fiyat_hesapla, maliyet_sinirla);
  models StoreReward/StorePurchase (mig 0013); ledger puan_bakiye/puan_islem;
  `MagazaServisi` (tohumlama, ekle/sil/maliyet_ayarla, satin_al puan harcar+geçmiş).
- "Mağaza" sekmesi: bakiye + ödül ekle + kart başına dk-maliyet düzeni + süre kutusu+çubuk
  + anlık fiyat + Satın al + geçmiş. `tests/integration/test_magaza.py`.

## Autofill + wishlist resmi ✅ (kullanıcı isteği)
- **Autofill** (`presentation/common/autofill.py` `AutoFill` — QCompleter, yazdıkça öneri;
  seçince ilgili alanları doldur). Uygulandığı yerler: **Görev ekle** (başlık→tekrar/param/
  stat/özel ödül; add_task_dialog oneri_getir+sablon_getir), **Cüzdan** (açıklama→tutar+tür;
  wishlist adı→fiyat), **İrade** (başlık→xp), **Mağaza** (ödül adı→dk-maliyet). Repo+servis:
  `baslik_onerileri`/`sablon_oneri`, `aciklama_onerileri`/`islem_oneri`, wishlist öneri,
  irade `baslik_onerileri`/`eylem_oneri`, magaza `ad_onerileri`/`maliyet_oneri`.
  `tests/integration/test_autofill.py`.
- **Wishlist → ayrı "İstek Listesi" sekmesi** (`presentation/views/wishlist/wishlist_view.py`;
  CuzdanView'dan çıkarıldı). Resim artık kendi en-boy oranında **büyük** (resim_acilma.py
  widget'ı resmin boyutuna sabitler, maks 720×460, ortalı; siyah bar yok). Kullanıcı geri
  bildirimi: dar şeride sığdırma kötüydü.

## Yeni özellikler (kullanıcı isteği, plan dışı) — sırayla
Kullanıcı 4 özellik istedi: **#2 etiket → #1 özel stat → #3 seans → #4 etiket-süre grafiği**.
Kararlar: seans modelinde **her seans bitince ödül** (görev kapanmaz, "Bitir" yok); özel
statlar tam stat (profile katılır); etiket grafiği = etiket başına SÜRE; ayrı commit'ler.
- **#2 Etiketler ✅**: `domain/etiket` (renk paleti), `Tag` modeli + `tasks.tag_id`
  (migration 0014), `SqlEtiketRepository`, `EtiketServisi` (ekle/sil, paletten renk).
  `gorev_olustur(tag_id)`, `GorevSatiri.etiket_ad/renk` (today_rows/telafi Tag join),
  görev satırında renkli ● + ad, add_task_dialog'da etiket seçici + "Yeni etiket…".
  `tests/integration/test_etiket.py`.
- **#1 Özel statlar ✅**: `custom_stats` tablosu (migration 0015), `SqlStatRepository`,
  `StatServisi` (StatBilgi; tum_statlar=yerleşik4+özel, gorev_statlari, anahtarlar, etiket,
  stat_ekle/sil; özel anahtar=id). `GorevServisi.profil_durumu` artık TÜM stat anahtarlarını
  toplar (özel dahil); gorev_olustur stat str|Stat. `istatistik.stat_dagilimi` özel statları
  da gösterir. add_task_dialog stat seçici=gorev_statlari + "+ Yeni alan…"; Ayarlar'da
  "Gelişim alanları" yöneticisi (ekle/sil). Etikete **renk seçtirici** (QColorDialog) eklendi.
  KARAR: dashboard 4-stat avatar paneli + rutin stat seçici yerleşik kalır (risk); özel
  statlar görevlerde + profilde + İstatistik'te. saat.py yorumları ruff'a uygun hale getirildi.
  `tests/integration/test_stat.py`.
- **#4 Etiket-süre panosu ✅**: `task_repo.etiket_sure_dagilimi` (Tag join, committed_seconds
  toplamı, group by tag), `istatistik.etiket_sure_dagilimi` (etiketsiz='(Etiketsiz)', büyükten
  küçüğe). `presentation/common/halka.py` (Halka donut QPainter), "Pano" sekmesi: aralık
  seçici (Bugün/Bu hafta/Bu ay/Özel=QDateEdit takvim) + halka + kırılım çubukları (etiket
  rengi + süre + %). `tests/integration/test_pano.py`.
- **#3 Seanslar ✅**: `sessions` tablosu (migration 0016), `SqlSeansRepository`
  (ac/kapat/gun_seanslari/gun_seans_sayisi/seans_sil/acik_seanslari_sil). `GorevServisi`:
  `seans_baslat` (açık seans + başka çalışanı kapat), `seans_durdur` (kapat + SÜRE-temelli
  ödül; <60sn ödülsüz; o günün ilk seansında seri; düşman/combo/kritik/rozet olaydan),
  `seanslar`/`seans_sil` + `SeansSatiri` DTO. Dashboard: `seans_widget.py`
  (başlık+toplam süre kalın + Başlat/Durdur + açılır seans listesi); Bitir kaldırıldı.
  bootstrap açılışta açık seansları temizler. KARARLAR: ödül süre-temelli (özel ödül
  artık yalnız Telafi'de), telafi eski akışta (tamamla 2×). `tests/integration/test_seans.py`.

### KULLANICININ 4 İSTEĞİ TAMAM (#1 stat, #2 etiket, #3 seans, #4 etiket-grafik).

## İşlevsel iyileştirmeler (kullanıcı sırası: önce işlevsel, sonra facelift, en son asset)
- **Açık uçlar**: (a) görev "Sil"→**"Arşivle"** (zaten soft, geçmiş korunur); (b) **"özel ödül"
  alanı dialogdan kaldırıldı** (seans ödülü süre-temelli; tamamla yine reward_override'ı
  kullanır=eski/telafi); (c) **seans silince XP/Puan da geri alınır** (Session.reward_xp/points
  mig 0017, seans_durdur yazar, seans_sil ters kayıt "session_revert").
- **Görev hatırlatıcıları**: tasks.reminder("HH:MM")+reminder_last (mig 0017); add_task_dialog
  "Hatırlatma kur" + QTimeEdit; `HatirlatmaServisi.kontrol` (saat gelince + bugün geçerliyse →
  HATIRLATMA bildirimi, gün başına tek, gece sessizliğine saygılı); app.py 60sn timer + açılışta.
  `tests/integration/test_hatirlatma.py`, test_seans XP-geri-alma.

## SIRADA (kullanıcı planı)
- **2) Kodla RPG facelift** (asset'siz: Press Start 2P başlıklar, bevel QSS panel/buton,
  segment'li barlar, hover glow, tık sesi, animasyon). 3) en son **ikon/asset entegrasyonu**
  (kullanıcı `assets/icons/` üretip ekleyecek — ikon yükleyici + emoji fallback yazılacak).
- Faz 9 (lore/onboarding/günün sözü) hâlâ açık.
- **Seans UI düzeltmeleri** (kullanıcı geri bildirimi): expander açıkken dolu görünür
  (#Expander:checked QSS + ▼/▶) ve **açık kalır** (dashboard `_acik_seanslar` set, render'da
  korunur); **seans silince görev toplamı eksilir** (`committed_ekle(-sure)`); seans saatleri
  **düzenlenebilir** (QTimeEdit + Kaydet → `seans_guncelle`); **manuel seans ekleme**
  (`seans_manuel_ekle`, "Elle: HH:MM–HH:MM Seans ekle"). repo: seans getir/guncelle/ekle_kapali,
  task committed_ekle.

## Sırada ⏸️ — Faz 9 (son faz, yeni özelliklerden sonra)
- **Faz 9**: lore (düşman lore fragmanları) + onboarding "Mentor" NPC (ilk açılış
  tutorial) + açılış mesajı/günün sözü + gelişmiş animasyonlar. **Push edilmedi** ("hadi" bekle).

## Çalışma kuralları (özet — tam hâli CLAUDE.md'de)
- Kullanıcı teknik değil → her değişiklikten sonra sade Türkçe anlat; soruları sonuç-odaklı sor; arayüz tamamen Türkçe.
- Her adım sonu: **tik-kutucuk doğrulama listesi** + kısa sunum-anlatımı.
- Mesaj tonu: gündelik Türkçe + epik alt ton; klişe değil.
- Kod isimleri ASCII-Türkçe; kalıplaşmış terimler ve ORM/Qt/Alembic API İngilizce.
- Asset eksikse durma → kullanıcıdan iste (ne gerek + boyut/format/stil + AI prompt). Mana Seed dosyalarını yeniden adlandırma.
- Push yalnızca kullanıcı açıkça isteyince. Commit sonu: `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`.
