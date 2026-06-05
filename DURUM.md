# LevelTodo — Durum ve Yol Haritası

> Bu dosya "neredeyiz, sırada ne var" sorusunun tek bakışta cevabı.
> Yeni bir sohbet bu dosyayı + `CLAUDE.md`'yi + git geçmişini okuyarak kaldığı yerden devam edebilir.

## Kısa özet
- Dal: `claude/faz0-iskelet` — **push edilmedi**.
- Çalıştır: `.\.venv\Scripts\python.exe -m leveltodo`
- Test: `.\.venv\Scripts\python.exe -m pytest -q` → **113 test yeşil**, ruff temiz.
- Stack: Python 3.12.8 · PyQt6 · SQLAlchemy 2.0 + Alembic · blinker · python-dateutil · platformdirs · python-ulid.

## Bitti ✅
- **Faz 0** İskelet: katmanlı mimari, `bootstrap.py` Container + elle DI, `OlayHatti`(blinker)+Qt köprüsü, `Saat`(IClock)/`Gun`(DayId, gün-başlangıç vars. 04:00), enjekte `Sans`, Alembic migrations.
- **Faz 1** Çekirdek döngü: görev CRUD, tamamlama→XP/Puan defteri, kronometre (başlat/duraklat), Bugün/Tümü.
- **Faz 2** İstatistik+avatar: seviye/unvan bantları, Mana Seed sprite kompozit + AI avatar override (`assets/avatar_ai/`), unvan okları (kilitli ileri seviyeler koyu+kilit). Puan = **gerçek-hayat ödülü** (mağaza YOK).
- **Faz 3** Tekrar+seri: tekrarlı görevler, **görev-başına seri** (🔥N), **sınırsız** seri-dondurma (3 levelde +1), **ayrı Telafi menüsü**, ileri görevler görünür.
- **Faz 4** Oyunlaştırma: kritik (×2 XP+Puan, %10), combo zinciri, rozetler, epik-doğal Türkçe mesajlar.
- **Faz 5 / Adım 1** İrade-Disiplin: `will_acts` (migration 0007), `IradeServisi`, irade görünümü.
- **Faz 5 / Adım 2** Düşman/Şeytan: commit `2827e10`. 4 düşman, `max_hp=round(100*1.5^tier)`, görev XP'si → hasar (olay tabanlı), can bitince üst tier+tam can. Dashboard üst paneli: sprite + kırmızı can barı. Kullanıcının AI sprite'ları `assets/enemies/<anahtar>.png`.
- **Faz 5 / Adım 3** Rutin alanları: **commit edilmedi (çalışma ağacında)**. Kullanıcı tanımlı günlük ölçütler. `routine_fields`+`routine_entries` (migration 0008), `domain/rutinler` (RutinTuru SAYI/EVET_HAYIR, Yon EN_AZ/EN_FAZLA, `hedef_tuttu_mu`), `RutinServisi` (alan ekle/pasife al, `deger_gir` → ödülü hedef durumuyla eşitler: tutunca seçilen stata `reward_xp` [gün-başına-tek], hedef artık tutmuyorsa ters/negatif kayıtla geri alır), ayrı "Rutin" sekmesi (`RutinView`, nav index 2). Stat alan başına seçilir. `tests/integration/test_rutin.py`.
- **Faz 5 / Adım 4** Gün sonu günlüğü: **commit edilmedi (çalışma ağacında)** — Faz 5 tamamlandı. `journal_entries`+`reflection_questions` (migration 0009), `domain/gunluk` (HAVUZ sabit sorular, `gunun_sorusu` takvim-günü dönüşümü, `gunluk_odulu`=40+1×dolu_gün artan eğri), `GunlukServisi` (günde tek, kaydet→Farkındalık'a artan XP [gün-başına-tek], boşaltınca ters kayıtla geri alır; reward_xp ilk dolduruşta sabitlenir; kendi soruları ekle/sil), ayrı "Günlük" sekmesi (`GunlukView`, nav index 3). `tests/integration/test_gunluk.py`.

## Sırada ⏸️
- Faz 5'in 4 adımı da bitti. Sırada belirlenmiş iş yok — kullanıcının yeni yönlendirmesini bekle. Adım 3 ve 4 **henüz commit edilmedi**; kullanıcı isterse commit + (sonra) push.

## Çalışma kuralları (özet — tam hâli CLAUDE.md'de)
- Kullanıcı teknik değil → her değişiklikten sonra sade Türkçe anlat; soruları sonuç-odaklı sor; arayüz tamamen Türkçe.
- Her adım sonu: **tik-kutucuk doğrulama listesi** + kısa sunum-anlatımı.
- Mesaj tonu: gündelik Türkçe + epik alt ton; klişe değil.
- Kod isimleri ASCII-Türkçe; kalıplaşmış terimler ve ORM/Qt/Alembic API İngilizce.
- Asset eksikse durma → kullanıcıdan iste (ne gerek + boyut/format/stil + AI prompt). Mana Seed dosyalarını yeniden adlandırma.
- Push yalnızca kullanıcı açıkça isteyince. Commit sonu: `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`.
