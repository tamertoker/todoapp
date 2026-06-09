# 01 — Katmanlı Mimari, OOP ve Tasarım Desenleri

> Sunumda en çok soru bu başlıktan gelir. Buradaki her şeyi **gerekçesiyle** bil.

## 1. Neden katmanlı mimari?

Proje **5 katmana** ayrılmış. Her katman yalnızca **kendi altındaki** katmana bağımlı.
Bu yaklaşımın adı **Clean Architecture / Katmanlı (Layered) Mimari**.

```
┌─────────────────────────────────────────────────────────┐
│  presentation/   PyQt6 ekranlar (View), ViewModel'ler     │  ← kullanıcı
├─────────────────────────────────────────────────────────┤
│  application/    Servisler — iş akışını koordine eder      │
├─────────────────────────────────────────────────────────┤
│  domain/         SAF iş kuralları (Python'dan başka şey    │  ← kalp
│                  bilmez: PyQt yok, SQL yok)                │
├─────────────────────────────────────────────────────────┤
│  infrastructure/ Dış dünya: SQLite, dosya, OS bildirimi,   │
│                  ses, event bus implementasyonu            │
├─────────────────────────────────────────────────────────┤
│  shared/         Ortak küçük yardımcılar (id, log, Result) │
└─────────────────────────────────────────────────────────┘
```

### Bağımlılık yönü (en kritik kavram — KESİN sorulur)

**Bağımlılıklar her zaman içeriye, `domain`'e doğru akar.**

- `domain` **hiçbir** üst katmanı import etmez. `import PyQt6` veya `import sqlalchemy`
  domain'de **yoktur**. Bu yüzden domain'i bir saniyede, veritabanı/ekran açmadan test
  edebilirsin.
- `presentation` doğrudan veritabanına dokunmaz; hep `application` servisleri üzerinden gider.
- `infrastructure` domain'in tanımladığı **arayüzleri** (Protocol/interface) uygular.

**Neden böyle?**
1. **Test edilebilirlik:** Saf domain = dış bağımlılık yok = anında test.
2. **Değiştirilebilirlik:** SQLite'ı yarın PostgreSQL yapsam, sadece `infrastructure`
   değişir; domain ve application'a dokunmam.
3. **Anlaşılabilirlik:** İş kuralları tek yerde (`domain`), UI gürültüsünden ayrı.

> **Somut kanıt:** `domain/tasks/kurallar.py` dosyasının başında yazıyor:
> *"Görevlerle ilgili saf kurallar (PyQt ve veritabanından bağımsız)... saniyeler
> içinde test edilebilir."* Ödül hesabı (`odul_hesapla`) sadece sayı alıp sayı döndürür.

## 2. Her katman tam olarak neyi temsil eder?

### domain/ — İş kurallarının kalbi (saf)
Uygulamanın "ne olduğunu" tanımlar; "nasıl saklandığını/gösterildiğini" değil.
- **Entity / Value Object'ler:** `Gun` (mantıksal gün), `Odul` (xp+puan), `Dusman`,
  `SeviyeDurumu`, `UnvanDurumu`, `Stat` (enum).
- **Saf fonksiyonlar (kurallar):** `seviye_hesapla`, `unvan_hesapla`, `odul_hesapla`,
  `gunde_olusur_mu`, `max_hp`, `hasar`.
- **Arayüzler (Protocol):** `Saat`, `ISettingsRepository` — sözleşme; implementasyon
  infrastructure'da.
- **Olaylar:** `events.py` → `TaskCompleted`, `SeviyeAtlandi`, `DusmanDevrildi`.

### application/ — Servisler (orkestra şefi)
Tek tek domain kurallarını **birleştirip bir iş akışına** çevirir. Örn. `GorevServisi.tamamla()`:
ödülü hesaplar (domain), deftere yazar (infrastructure repo), seriyi günceller, olay yayınlar.
Kendisi "saf kural" içermez; **koordinasyon** yapar. (`gorev_servisi`, `dusman_servisi`,
`cuzdan_servisi`, `magaza_servisi`, `stat_servisi`, ... 22 servis.)

### infrastructure/ — Dış dünya
- **persistence/sqlite/**: SQLAlchemy ORM modelleri (`models.py`) + Repository sınıfları
  (`task_repository`, `ledger_repository`, ...) + Alembic migration'ları.
- **eventbus/**: `OlayHatti` (Blinker sarmalayıcı) + `qt_bridge` (olayı Qt sinyaline çevirir).
- **notifications/**, **sound/**, **backup/**, **config/**, **assets/**.

### presentation/ — Arayüz (PyQt6)
- **views/**: Her sekme bir View (`DashboardView`, `DusmanView`, ...).
- **ViewModel'ler:** View ile servis arasında aracı (`DashboardViewModel`). MVVM deseni.
- **common/**, **theme/**: ortak widget'lar, tema/font/QSS.

### shared/ — Çapraz yardımcılar
`ids.py` (ULID üretimi), `logging.py`, `result.py`. Her katman kullanabilir.

## 3. OOP ilkeleri — bu projede nerede?

Hoca "OOP ilkelerini nasıl uyguladın?" diye sorabilir. Hazır cevaplar:

### Kapsülleme (Encapsulation)
Servisler bağımlılıklarını `self._gorev`, `self._defter` gibi **alt çizgili (private)**
alanlarda tutar; dışarıdan veriye değil, **metoda** erişilir (`tamamla()`, `gorev_olustur()`).
`SettingsService` içte bir cache tutar ama dışarıya sadece `get/set` verir.

### Soyutlama (Abstraction)
`Saat` ve `ISettingsRepository` birer **Protocol** (soyut sözleşme). Kod somut sınıfa
değil, soyutlamaya bağımlı. "Zamanı nereden alıyoruz" detayı gizli.

### Kalıtım (Inheritance)
- `domain/events.py`: `TaskCompleted`, `SeviyeAtlandi` hepsi `DomainEvent`'ten türer
  (ortak `occurred_at` alanı).
- PyQt tarafında `MainWindow(QWidget)`, `DashboardViewModel(QObject)`.
- ORM: tüm tablolar `Base`'ten türer (SQLAlchemy declarative).

### Çok biçimlilik (Polymorphism)
- `OlayHatti.publish(event)` herhangi bir `DomainEvent` alır; `main_window._ses_isle`
  `isinstance` ile türe göre farklı davranır (TaskCompleted→tamamlama sesi,
  SeviyeAtlandi→seviye sesi).
- **`HasarliDefter`** ham defterle aynı arayüzü taşır; kodun geri kalanı hangisini
  kullandığını bilmez (aşağıda Decorator).

## 4. Tasarım desenleri (Design Patterns) — projede gerçekten var olanlar

Bunlar sunumda "fark yaratan" cevaplardır. Her birini bir cümleyle anlatabil:

### a) Repository Pattern
Veritabanı erişimi `...Repository` sınıflarında toplanır (`SqlTaskRepository`,
`SqlLedgerRepository`). Servisler SQL bilmez; repository'ye "şunu kaydet / şunu getir" der.
**Neden:** İş mantığını SQL'den ayırır; veritabanını değiştirmeyi kolaylaştırır; test'te
sahte repository verilebilir.

### b) Dependency Injection + Composition Root
`bootstrap.py` içindeki `build_container()` **tek yer**, tüm nesneleri kurup birbirine
"enjekte eder" (constructor'dan geçirir). Sınıflar kendi bağımlılığını **kendi yaratmaz**,
dışarıdan **alır**.
```python
gorevler = GorevServisi(
    gorev_repo=gorev_repo, defter_repo=hasarli_defter, saat=aktif_saat,
    olay_hatti=olay_hatti, dondurma=dondurma, combo=combo, rozet=rozet, ...
)
```
**Neden:** Gevşek bağlılık (loose coupling) + test'te gerçek nesne yerine sahtesini vermek
(ör. `SahteSaat`, geçici veritabanı) çok kolay. `Container` bir dataclass; tüm servisleri taşır.

### c) Decorator Pattern — `HasarliDefter` (sunumun yıldızı ⭐)
`bootstrap.py`'de tanımlı. Gerçek defteri (`SqlLedgerRepository`) **sarmalar**:
```python
class HasarliDefter:
    def __init__(self, gercek, dusman): ...
    def record(self, *, xp, ...):
        self._gercek.record(...)        # önce normal kaydı yap
        if xp > 0:
            self._dusman.hasar_biriktir(xp)   # SONRA düşmana hasar biriktir
    def __getattr__(self, ad):          # record dışındaki her çağrı gerçeğe gider
        return getattr(self._gercek, ad)
```
**Ne çözüyor:** "XP veren HER eylem (görev, seans, günlük, irade, rutin, uyandırma)
otomatik olarak düşmana hasar versin" istiyoruz. Her servise tek tek düşman kodu
yazmak yerine, hepsine **aynı sarılmış defteri** veriyoruz. Servisler hâlâ "deftere
yazıyorum" sanıyor; arkada düşman da besleniyor. Tek noktadan davranış eklendi,
mevcut kod hiç değişmedi → **Açık/Kapalı İlkesi (Open/Closed)**.

### d) Observer / Pub-Sub (Event Bus)
`OlayHatti` (Blinker üzerine). Servisler olay **yayınlar** (`publish`), ekran/ses
sistemi **abone olur** (`subscribe`). Yayıncı, kimin dinlediğini bilmez.
**Neden:** UI ile iş mantığını birbirinden ayırır. `GorevServisi` "TaskCompleted yayınladım"
der, gerisi onu ilgilendirmez.

### e) Bridge (Qt köprüsü)
`QtEventBridge`: domain olayını PyQt sinyaline çevirir ve **doğru thread'e** taşır.
Domain saf kalır (PyQt bilmez); UI yine de güncellenir.

### f) MVVM (Model-View-ViewModel)
`DashboardView` (ekran) ↔ `DashboardViewModel` (aracı) ↔ `GorevServisi` (iş).
ViewModel `changed` sinyali yayar, View duyup yeniden çizer. **Neden:** Ekran kodu
ile iş kodu birbirine karışmaz.

### g) Strategy (küçük) — `Saat` ve `Sans`
`Saat` protokolünün gerçek (`AyarlanabilirSaat`) ve sahte (`SahteSaat`) stratejisi var.
`Sans` (şans) aynı şekilde gerçek/sahte. Çalışma anında hangi stratejinin geleceği
`bootstrap`'ta belirlenir.

## 5. Sıkça sorulacak "neden" cevapları (cep notu)

- **Neden kod Türkçe?** Alan dili (domain language) Türkçe; takım/okuyucu Türkçe.
  Yerleşik teknik terimler (repository, instance) İngilizce kaldı.
- **Neden tek kullanıcı ama her tabloda `user_id`?** İleride çoklu profil eklemek
  şemayı bozmadan mümkün olsun diye (`DEFAULT_USER_ID = "default"`).
- **Neden ayarlar anahtar-değer (key-value) tablo?** Yeni ayar eklemek için tablo
  değiştirmek (migration) gerekmesin; sadece yeni bir anahtar yazılır.
- **Neden `domain` PyQt bilmiyor da olaylar UI'yi nasıl güncelliyor?** Köprü
  (`QtEventBridge`) sayesinde — domain olay yayınlar, köprü Qt sinyaline çevirir.
```
