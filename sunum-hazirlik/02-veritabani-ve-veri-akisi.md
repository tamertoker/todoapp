# 02 — Veritabanı Tasarımı, ORM ve Veri Akışı

## 1. Genel resim

- **Veritabanı:** SQLite (tek `.db` dosyası, kullanıcının veri klasöründe).
- **ORM:** SQLAlchemy 2.0 — Python sınıfları (`models.py`) ↔ SQL tabloları.
- **Şema göçü (migration):** Alembic — şemanın her değişimi numaralı bir dosya
  (`0001_initial` … `0018_gorev_hedef_sure`, toplam **18 migration**).
- Uygulama her açılışta `upgrade_to_head(url)` ile veritabanını **en güncel şemaya**
  taşır (`bootstrap.py`).

## 2. ORM nedir, neden? (sorulur)

ORM = Object-Relational Mapping. Python sınıfını bir tabloya, nesnesini bir satıra eşler.
SQL string'i elle yazmak yerine Python nesneleriyle çalışırsın.
```python
class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    recurrence: Mapped[str] = mapped_column(String(10))  # none|daily|weekly...
```
**Neden:** Tip güvenliği, SQL enjeksiyonuna karşı koruma, veritabanı bağımsızlığı,
okunabilirlik.

## 3. Ana tablolar ve EN ÖNEMLİ tasarım kararları

### a) Şablon / Oluşum ayrımı (Template / Instance) ⭐
İki ayrı tablo:
- **`tasks`** = görev **şablonu** (tanım): "Her gün spor yap", tekrar kuralı, ödül,
  hangi stat'ı büyüttüğü, seri sayacı.
- **`task_instances`** = şablonun **belli bir güne** düşen somut kaydı: o günün durumu
  (`pending`/`done`), kronometre süresi, kazanılan ödül, tamamlanma zamanı.

**Neden ayırdık?**
- Tekrarlı görev (her gün spor) **tek tanım**, ama **her gün ayrı kayıt** tutmalı ki
  geçmiş bozulmasın ("dün yaptım mı?" sorusunun cevabı kalıcı olsun).
- `task_instances`'ta `UniqueConstraint(task_id, day)` var → aynı görev aynı güne **iki
  kez düşemez**.
- Bu desen RPG'deki "şablon karakter" ↔ "o anki örnek" mantığıyla aynı; veri tasarımında
  klasik bir yaklaşım.

> Oluşumlar **tembel (lazy)** üretilir: bir gün ekrana gelince `_gunluk_kayitlari_uret`
> o güne düşmesi gereken şablonları bulup eksik instance'ları yaratır. Yani gelecekteki
> her gün için önceden milyon satır yazmayız.

### b) Defter / Event Sourcing mantığı (Ledger) ⭐⭐
**`xp_events`** ve **`point_transactions`** tabloları: kazanılan **her** XP ve puan
**ayrı bir satır** olarak yazılır (kaynağı, günü, ne kadar, hangi stat).

> Kodun yorumu: *"Toplamlar bu satırların toplanmasıyla bulunur — tek doğruluk kaynağı
> budur, ayrı bir 'bakiye' alanı tutulmaz."*

**Neden ayrı bakiye tutmuyoruz?**
- **Tek doğruluk kaynağı (single source of truth):** "bakiye" ayrı tutulursa bir yerde
  +5, bakiyeyi güncellemeyi unutursan tutarsızlık olur. Toplamı her zaman satırlardan
  `SUM()` ile hesaplarsak **asla tutarsız olamaz**.
- **Tam geçmiş:** "Ne zaman, neyden kazandın" tarihi durur → istatistik, heatmap, grafik
  hepsi bu defterden beslenir.
- **Geri alma:** Bir seans silinince ters kayıt (`-xp`) yazarız; satırlar asla "değişmez",
  sadece yenisi eklenir (muhasebe defteri mantığı).

Bu yaklaşımın adı **Event Sourcing**'e yakındır: durumu saklamak yerine, durumu oluşturan
**olayları** saklarız; güncel durum onların toplamıdır.

### c) Ayarlar = anahtar/değer tablosu
`settings` tablosu: `(user_id, key, value)`. `value` bir JSON metni.
```python
DEFAULTS = {"day_start_hour": 4, "theme": "dark", "dusman_tier": 0, ...}
```
**Neden:** Yeni bir ayar (ör. `dusman_biriken_hasar`) eklemek için **migration gerekmez**;
sadece yeni anahtar yazılır. `SettingsService` JSON'a çevirip saklar, okurken çözer,
bir bellek-içi cache tutar. Düşmanın canı/tier'ı bile burada — ayrı tablo gerektirmeyecek
kadar küçük durumlar burada yaşar.

### Diğer tablolar (kısaca)
`sessions` (kronometre seansları), `streaks` (giriş serisi), `will_acts` (irade),
`routines` (rutinler), `journal` (günlük), `wake` (uyandırma), `wallet_*` (cüzdan, kuruş),
`store_*` (mağaza), `tags` (etiketler), `custom_stats` (özel statlar).

## 4. Birincil anahtarlar neden ULID?
`shared/ids.py` ULID üretir (String(26)). Auto-increment int yerine:
- **Sıralanabilir:** ULID zaman önekli, oluşturma sırasına göre artar.
- **Çakışmasız birleştirme:** İleride çoklu cihaz/profilde ID çakışması olmaz.

## 5. "Mantıksal gün" — şık bir domain kararı (`Gun`)
Gece 03:00'te uygulamayı açan biri için bu hâlâ "dünkü gün" sayılmalı.
```python
# gün başlangıcı 04:00 ise:
# 2 Haziran 03:30 → mantıksal gün = 1 Haziran
# 2 Haziran 04:30 → mantıksal gün = 2 Haziran
Gun.olustur(an, gun_baslangic_saati)  # an - timedelta(hours=baslangic) sonra .date()
```
**Neden:** Gece geç çalışan birinin görevi "ertesi güne" kaymasın. Gün başlangıç saati
ayarlardan değiştirilebilir (varsayılan 4).

## 6. Veri akışı tek bakışta
```
[Ekran/View]
   ↓ kullanıcı tıklar
[ViewModel]  (changed sinyali)
   ↓ çağırır
[Application Servisi]  (iş akışı)
   ├─→ [Domain saf kural]   (odul_hesapla, seviye_hesapla...)  → sadece hesap
   ├─→ [Repository]         (SqlTaskRepository, SqlLedgerRepository) → SQLite
   └─→ [OlayHatti.publish]  (TaskCompleted...)
                              ↓
                       [QtEventBridge] → Qt sinyali → [Ses/Toast/Ekran tazele]
```
```
