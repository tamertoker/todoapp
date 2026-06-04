# LevelTodo — Durum ve Yol Haritası

> Bu dosya "neredeyiz, sırada ne var" sorusunun tek bakışta cevabı.
> Yeni bir sohbet bu dosyayı + `CLAUDE.md`'yi + git geçmişini okuyarak kaldığı yerden devam edebilir.

## Kısa özet
- Dal: `claude/faz0-iskelet` — **push edilmedi**.
- Çalıştır: `.\.venv\Scripts\python.exe -m leveltodo`
- Test: `.\.venv\Scripts\python.exe -m pytest -q` → **100 test yeşil**, ruff temiz.
- Stack: Python 3.12.8 · PyQt6 · SQLAlchemy 2.0 + Alembic · blinker · python-dateutil · platformdirs · python-ulid.

## Bitti ✅
- **Faz 0** İskelet: katmanlı mimari, `bootstrap.py` Container + elle DI, `OlayHatti`(blinker)+Qt köprüsü, `Saat`(IClock)/`Gun`(DayId, gün-başlangıç vars. 04:00), enjekte `Sans`, Alembic migrations.
- **Faz 1** Çekirdek döngü: görev CRUD, tamamlama→XP/Puan defteri, kronometre (başlat/duraklat), Bugün/Tümü.
- **Faz 2** İstatistik+avatar: seviye/unvan bantları, Mana Seed sprite kompozit + AI avatar override (`assets/avatar_ai/`), unvan okları (kilitli ileri seviyeler koyu+kilit). Puan = **gerçek-hayat ödülü** (mağaza YOK).
- **Faz 3** Tekrar+seri: tekrarlı görevler, **görev-başına seri** (🔥N), **sınırsız** seri-dondurma (3 levelde +1), **ayrı Telafi menüsü**, ileri görevler görünür.
- **Faz 4** Oyunlaştırma: kritik (×2 XP+Puan, %10), combo zinciri, rozetler, epik-doğal Türkçe mesajlar.
- **Faz 5 / Adım 1** İrade-Disiplin: `will_acts` (migration 0007), `IradeServisi`, irade görünümü.
- **Faz 5 / Adım 2** Düşman/Şeytan: commit `2827e10`. 4 düşman, `max_hp=round(100*1.5^tier)`, görev XP'si → hasar (olay tabanlı), can bitince üst tier+tam can. Dashboard üst paneli: sprite + kırmızı can barı. Kullanıcının AI sprite'ları `assets/enemies/<anahtar>.png`.

## Sırada ⏸️ (kullanıcı onayı bekliyor — "sonraki adıma geçme" dedi)
- **Faz 5 / Adım 3 — Rutin alanları**: kullanıcı tanımlı sayısal/metin/evet-hayır alanlar (ör. "kaç bardak su", "kaç sayfa okudun").
- **Faz 5 / Adım 4 — Gün sonu günlüğü**: günlük yazısı + dönüşümlü yansıtma soruları.

## Çalışma kuralları (özet — tam hâli CLAUDE.md'de)
- Kullanıcı teknik değil → her değişiklikten sonra sade Türkçe anlat; soruları sonuç-odaklı sor; arayüz tamamen Türkçe.
- Her adım sonu: **tik-kutucuk doğrulama listesi** + kısa sunum-anlatımı.
- Mesaj tonu: gündelik Türkçe + epik alt ton; klişe değil.
- Kod isimleri ASCII-Türkçe; kalıplaşmış terimler ve ORM/Qt/Alembic API İngilizce.
- Asset eksikse durma → kullanıcıdan iste (ne gerek + boyut/format/stil + AI prompt). Mana Seed dosyalarını yeniden adlandırma.
- Push yalnızca kullanıcı açıkça isteyince. Commit sonu: `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`.
