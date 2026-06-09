# 04 — Soru Bankası (Hocanın sorabileceği zor sorular + örnek cevaplar)

> Önce kendi cevabını ver, sonra örneğe bak. Cevaplarda hep **"neden"** vurgula.

## A) Mimari & Tasarım

**S1. Neden katmanlı mimari kullandın? Tek dosyada yazsan olmaz mıydı?**
> İş kurallarını arayüz ve veritabanından ayırmak için. Domain saf olduğundan
> veritabanı/ekran açmadan test edilebilir; veritabanını veya arayüzü değiştirsem
> iş mantığına dokunmam. Tek dosyada her şey birbirine girer, büyüdükçe bakımı imkânsızlaşır.

**S2. Bağımlılıklar hangi yöne akıyor?**
> Her zaman içeriye, domain'e doğru. Domain hiçbir üst katmanı import etmez; üst katmanlar
> alt katmana bağımlıdır. `infrastructure`, domain'in tanımladığı arayüzleri (Protocol) uygular —
> bu **bağımlılığın tersine çevrilmesi (Dependency Inversion)** ilkesidir.

**S3. Dependency Injection nedir, nerede kullandın?**
> Bir sınıfın ihtiyaç duyduğu nesneleri kendisi yaratmaz, dışarıdan (constructor'dan) alır.
> Tüm kurulum `bootstrap.py`'deki `build_container()`'da (Composition Root). Faydası:
> gevşek bağlılık + testte gerçek nesne yerine sahtesini (sahte saat, geçici DB) vermek.

**S4. Projede hangi tasarım desenleri var?**
> Repository (veri erişimi), Decorator (`HasarliDefter`), Observer/Pub-Sub (`OlayHatti`),
> MVVM (View/ViewModel/Servis), Bridge (`QtEventBridge`), DI + Composition Root.
> (Bir tanesini derinlemesine anlatmaya hazır ol — `HasarliDefter`'i seç.)

**S5. `HasarliDefter` ne yapıyor, neden Decorator?** *(en olası "wow" sorusu)*
> Gerçek XP defterini sarmalıyor. `record()` çağrısında önce normal kaydı yapıyor, sonra
> düşmana hasar biriktiriyor; diğer tüm çağrıları `__getattr__` ile gerçeğe geçiriyor.
> Böylece "XP veren her eylem düşmana hasar versin" davranışını **tek noktadan**, mevcut
> servisleri hiç değiştirmeden ekledim — Açık/Kapalı İlkesi.

## B) Veritabanı

**S6. `tasks` ve `task_instances`'ı neden ayırdın?**
> `tasks` şablon (tekrarlı tanım), `task_instances` o şablonun belli bir güne düşen somut
> kaydı. Tekrarlı bir görev tek tanım ama her gün ayrı durum/ödül tutmalı; geçmiş bozulmasın
> diye ayırdım. `UniqueConstraint(task_id, day)` aynı görevin bir güne iki kez düşmesini engeller.

**S7. XP/puanı neden olay olarak saklıyorsun da bakiye tutmuyorsun?**
> Tek doğruluk kaynağı için. Her kazanım `xp_events`/`point_transactions`'a ayrı satır;
> toplam her zaman `SUM()` ile bulunur. Ayrı bakiye tutsam senkron tutmayı unutunca
> tutarsızlık olur. Ayrıca tam geçmiş kalır (grafik/istatistik) ve geri alma ters kayıtla
> yapılır. Bu Event Sourcing'e yakın bir yaklaşım.

**S8. ORM nedir? Neden SQLAlchemy + Alembic?**
> ORM Python sınıflarını tablolara eşler; ham SQL yazmadan, tip güvenli ve enjeksiyona
> dayanıklı çalışırım. Alembic şema değişikliklerini sürümler (18 migration); uygulama
> açılışta `upgrade_to_head` ile DB'yi güncel tutar.

**S9. Ayarları neden anahtar-değer tabloda tutuyorsun?**
> Yeni ayar eklemek için migration gerekmesin diye. Değer JSON metni; `SettingsService`
> çevirip cache'liyor. Düşmanın tier/can gibi küçük durumları da burada.

**S10. Birincil anahtar olarak neden ULID, int değil?**
> Zaman önekli olduğu için sıralanabilir ve çoklu profil/cihazda çakışmaz.

## C) İş akışı / iz sürme

**S11. Bir görevi tamamlayınca arka planda ne oluyor?** → 03-iz-surme TRACE 2'yi anlat.

**S12. Seviye atladığını sistem nereden biliyor?**
> Profil seviyesi = tüm statların seviyelerinin toplamı, defterdeki XP'lerden hesaplanır.
> Her XP kazanımından sonra `_seviye_dondurma_kontrol` bunu yeniden hesaplayıp ayarlardaki
> "son seviye" ile kıyaslar; büyükse `SeviyeAtlandi` olayını yayınlar.

**S13. Seviye eğrisi nasıl? Neden artan?**
> Bir seviyeye çıkmak için `(8 + 0.4×seviye)` saat ≈ ×60 XP gerekir. Üst seviyeler giderek
> daha pahalı, böylece ilerleme anlamlı kalır. 1 XP ≈ 1 dakika kabulü var.

**S14. Olay (event) mekanizması niye var? Servis direkt ekranı güncelleyemez mi?**
> Güncelleyebilir ama o zaman iş mantığı PyQt'ye bağımlı olur (domain kirlenir). Onun yerine
> servis olay yayınlar, ekran/ses abone olur. Yayıncı kimin dinlediğini bilmez → gevşek bağlılık.
> `QtEventBridge` olayı doğru thread'e taşır.

**S15. Kronometre çalışırken uygulama kapanırsa süre kaybolur mu?**
> Hayır. Süre `committed_seconds` olarak DB'de tutulur; çalışan segment `segment_started_at`
> ile işaretli. `canli_sure` kaydedilmiş süreye o anki segmenti ekler. Periyodik checkpoint
> ve açılışta kurtarma var (`KronometreServisi`).

## D) Test & Kalite

**S16. Bu mimarinin test açısından avantajı ne?** *(tests/ silinmiş olsa da cevap güçlü)*
> Domain saf olduğu için anında test edilir. Zamanı `Saat` protokolünden aldığım için testte
> `SahteSaat` verip günü ileri sarabilirim (gerçek saati beklemeden seri/tekrar testleri).
> Geçici bir SQLite DB enjekte edip gerçek veriye dokunmadan test ederim. Projede ~180 testlik
> bir pytest paketi vardı (entegrasyon + birim).

**S17. `datetime.now()` yerine neden `Saat` protokolü?**
> Zaman bir dış bağımlılık. Doğrudan `now()` çağırsam zamana bağlı kuralları test edemem.
> Protokolle gerçek/sahte saati değiştirebiliyorum (Strategy/DI).

**S18. Aynı anda iki kronometre çalışırsa?**
> Engellendi: `seans_baslat` yeni seansı açmadan önce çalışan diğer görevlerin seansını
> kapatıp ödüllendirir — tek anda tek kronometre.

## E) Çukur sorular (dürüst + güçlü cevaplar)

**S19. Tek kullanıcı ama her tabloda user_id var, gereksiz değil mi?**
> Bilinçli bir karar: çoklu profil ileride şemayı bozmadan eklenebilsin diye. Şu an
> `DEFAULT_USER_ID` sabit; ileride sadece kullanıcı seçimi eklenir.

**S20. Kod neden Türkçe, profesyonelce mi?**
> Alan dili Türkçe (domain language tutarlılığı). Yerleşik teknik terimler (repository,
> instance, commit) İngilizce bırakıldı. Okuyan herkes Türkçe; okunabilirliği artırdı.

**S21. En zor kısım neydi / nerede zorlandın?**
> (Kendi cümlenle) Tekrarlı görevlerin "mantıksal gün", seri ve telafi etkileşimi; ve
> düşman hasarını her XP kaynağına yaymayı kodu kirletmeden çözmek — onu Decorator ile çözdüm.

**S22. Hata olursa veri bozulur mu / yedek var mı?**
> Repository'lerde her yazma `commit` ile atomik. Ayrıca `infrastructure/backup` yedekleme
> var; açılışta bekleyen geri yükleme uygulanıyor (`bekleyen_geri_yukleme_uygula`).

**S23. Ölçeklenir mi / SQLite yeterli mi?**
> Tek kullanıcılı masaüstü uygulaması için SQLite ideal (gömülü, sunucusuz). Repository
> deseni sayesinde ihtiyaç olursa PostgreSQL'e geçiş yalnızca infrastructure'ı etkiler.
```
