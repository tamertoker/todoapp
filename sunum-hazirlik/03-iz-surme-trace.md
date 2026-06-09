# 03 — İz Sürme (Trace): Bir işlev arka planda nasıl gerçekleşiyor?

> Bu dosya senin öğrenme tarzına göre yazıldı: butona basıldığı andan başlayıp,
> katman katman, **gerçek sınıf ve metot adlarıyla** sonuca kadar izliyoruz.
> Hocaya bunlardan **birini** akıcı anlatabilirsen, hâkimiyetini kanıtlarsın.

---

## TRACE 1 — "Görev Oluştur" dediğimde ne oluyor?

**Senaryo:** Kullanıcı "+ Görev Ekle" diyalogunu doldurup kaydetti.

1. **Ekran (presentation):** `add_task_dialog` formdan başlık, tekrar tipi, stat,
   etiket, hatırlatma, hedef süre toplar; `DashboardViewModel.gorev_ekle(...)` çağrılır.

2. **ViewModel:** (`dashboard_viewmodel.py`)
   ```python
   def gorev_ekle(self, baslik, tekrar, ozel_odul, stat, parametre, tag_id, reminder, hedef_sure):
       self._gorevler.gorev_olustur(baslik, tekrar, ozel_odul, stat, parametre, tag_id, reminder, hedef_sure)
       self.changed.emit()        # "veri değişti" → ekran kendini yeniden çizer
   ```
   ViewModel hiç iş kuralı içermez; **servise iletir** ve `changed` sinyali yayar.

3. **Servis (application):** `GorevServisi.gorev_olustur(...)`
   ```python
   gorev_id = new_id()                       # shared/ids.py → ULID
   self._gorev.add_template(                 # tasks tablosuna ŞABLON yaz
       id=gorev_id, title=baslik.strip(), recurrence=tekrar.value,
       reward_override=ozel_odul, stat=..., created_at=self._saat.simdi(), ...)
   if tekrar is Tekrar.YOK:                  # tek seferlik görevse
       self._gorev.add_instance(             # bugüne hemen bir OLUŞUM yarat
           id=new_id(), task_id=gorev_id, day=self._bugun(), title=...)
   return gorev_id
   ```
   - **Dikkat:** Zamanı `self._saat.simdi()`'den alıyor (asla `datetime.now()` değil).
   - **Dikkat:** Tekrarlı görevse (her gün vb.) **şimdi instance yaratmaz**; o günler
     geldikçe tembel üretilir.

4. **Repository (infrastructure):** `SqlTaskRepository.add_template` SQLAlchemy ile
   `tasks` tablosuna satır ekler ve commit eder. SQLite'a yazılır.

5. **Geri dönüş:** `changed.emit()` → `DashboardView` listeyi `bugunku_gorevler()` ile
   yeniden çeker → yeni görev ekranda belirir.

**Özet zincir:** `View → ViewModel.gorev_ekle → GorevServisi.gorev_olustur →
SqlTaskRepository.add_template → SQLite` (+ tek seferlikse bir instance).

---

## TRACE 2 — "Görev Tamamla" + "Seviye atladığını sistem nasıl biliyor?" ⭐⭐⭐

Bu, sunumun en güçlü anlatımı. Kullanıcı bir görevin yanındaki tamamla'ya bastı.

### Adım adım `GorevServisi.tamamla(kayit_id, elle_dakika)`

```python
kayit = self._gorev.get_instance(kayit_id)          # 1) o günün oluşumunu getir
simdi = self._saat.simdi()
# 2) ÇALIŞILAN SÜREYİ bul: elle girildi mi, yoksa kronometreden mi?
islenmis_saniye = canli_sure(kayit.committed_seconds,
                             kayit.segment_started_at if kayit.timer_running else None, simdi)
sablon = self._gorev.get_template(kayit.task_id)    # 3) şablonu getir (özel ödül? stat?)
ozel = sablon.reward_override

telafi_mi = kayit.day < self._bugun()               # 4) geçmiş günü mü kapatıyoruz?
odul = odul_hesapla(islenmis_saniye, ozel)          # 5) DOMAIN: ödülü hesapla (saf)
kritik = self._sans.kritik_mi(KRITIK_OLASILIK)      # 6) %10 kritik şansı
carpan = self._combo.carpan(simdi) * (KRITIK_CARPAN if kritik else 1)
if telafi_mi: carpan *= TELAFI_CARPAN                # geçmiş telafi → 2 kat
if carpan != 1.0:
    odul = Odul(xp=round(odul.xp*carpan), puan=round(odul.puan*carpan))

ok = self._gorev.complete_instance(...)             # 7) instance'ı 'done' yap, ödülü yaz
# 8) Seri: yalnızca BUGÜNKÜ tekrarlı görev tamamlanınca ilerler
if sablon and sablon.recurrence != "none" and kayit.day == self._bugun():
    self._gorev_serisi_isle(sablon, kayit.day)

self._defter.record(                                # 9) DEFTERE YAZ (xp_events + points)
    source="task_completion", xp=odul.xp, points=odul.puan, stat=sablon.stat, ...)
combo_tetik = self._combo.tamamlama_bildir(islenmis_saniye, simdi)  # 10) combo güncelle
self._rozet.tamamlama_arttir()                      # 11) rozet sayaçları
self._olay_hatti.publish(TaskCompleted(...))        # 12) OLAY yayınla
self._seviye_dondurma_kontrol()                     # 13) SEVİYE KONTROLÜ ← kilit nokta
return odul
```

### Önemli noktalar (her birini açıklayabil)

- **(5) Ödül saf domain'de hesaplanır** (`odul_hesapla`): özel ödül varsa o, yoksa
  kronometre çalıştıysa "dakika başına 1 birim (en az 1)", hiç çalışmadıysa sabit 5.
- **(6) Kritik (`Sans`):** %10 şansla ödül 2 katı. Şans dışarıdan enjekte (`self._sans`),
  böylece testte sahte şansla deterministik test yazılabilir.
- **(9) `self._defter` aslında `HasarliDefter`!** (Decorator). `record()` çağrılınca:
  önce gerçek deftere XP/puan yazılır, **sonra `dusman.hasar_biriktir(xp)`** çağrılır →
  düşmana otomatik hasar birikir. Görev kodu bunu hiç bilmez.

### (13) "Seviye atladığını sistem nasıl biliyor?" — cevabın tam burası

`_seviye_dondurma_kontrol()`:
```python
def _seviye_dondurma_kontrol(self):
    profil, _ = self.profil_durumu()     # GÜNCEL profil seviyesini hesapla
    self._dondurma.seviye_odulu(profil)  # önceki seviyeyle karşılaştır
```

**Profil seviyesi nasıl hesaplanıyor?** (`profil_durumu`)
```python
toplamlar = self._defter.stat_xp_toplamlari(user_id)   # her stat'ın TOPLAM XP'si (DB'den SUM)
profil = sum(seviye_hesapla(toplamlar.get(anahtar, 0)).seviye
             for anahtar in self._stat_anahtarlari())  # her stat'ın seviyesini topla
```
- Yani **profil seviyesi = tüm statların seviyelerinin toplamı.** Ayrı bir "seviye"
  sayacı tutulmaz; her zaman defterden hesaplanır (yine tek doğruluk kaynağı).
- `seviye_hesapla(toplam_xp)` saf domain: seviye eğrisi `(8 + 0.4×seviye)×60` XP. Üst
  seviyeler giderek daha pahalı.

**Atlamayı kim tespit ediyor?** `DondurmaServisi.seviye_odulu(profil)`:
```python
onceki = int(self._settings.get("dondurma_son_seviye"))   # en son kaydedilen seviye
if profil > onceki:                                        # YÜKSELDİ Mİ?
    kazanim = (profil // 3) - (onceki // 3)                # her 3 levelde +1 jeton
    if kazanim > 0: self.ekle(kazanim)
    self._settings.set("dondurma_son_seviye", profil)      # yeni seviyeyi sakla
    self._olay_hatti.publish(SeviyeAtlandi(yeni_seviye=profil))   # OLAY!
```
**Cevap özeti:** Sistem her XP kazanımından sonra profil seviyesini defterden yeniden
hesaplar, ayarlarda sakladığı "son seviye" ile karşılaştırır; büyükse **`SeviyeAtlandi`
olayını yayınlar** ve her 3 seviyede bir dondurma jetonu verir.

### Olay yayınlandıktan sonra (UI/ses)
```
OlayHatti.publish(TaskCompleted / SeviyeAtlandi)
   → QtEventBridge._forward → Qt sinyali (domain_event)
      → MainWindow._ses_isle:
          TaskCompleted  → tamamlama sesi (kritik/combo'ya göre farklı wav)
          SeviyeAtlandi  → "seviye" sesi
          DusmanDevrildi → "dusman_devrildi" sesi
   → ViewModel.changed → DashboardView yeniden çizer (XP barı, unvan güncellenir)
```

**Tam zincir (ezber için):**
`tamamla → odul_hesapla(domain) → HasarliDefter.record(→ DB + düşman hasar) →
TaskCompleted yayınla → _seviye_dondurma_kontrol → profil_durumu(DB'den SUM) →
seviye_odulu(önceki ile kıyas) → SeviyeAtlandi yayınla → QtBridge → ses + ekran tazele`

---

## TRACE 3 — Düşmana hasar ve "Vur" + Hazine

**Tasarım fikri:** Görev tamamlandığında düşmana hasar **anında inmez**; "biriken hasar"a
eklenir. Kullanıcı Düşman sekmesinde "Vur" deyince hepsi **tek darbede** iner — "kendi
elinle devirdiğini" hissettirmek için.

1. **Hasar biriktirme (otomatik):** Her XP kazanımında `HasarliDefter.record` →
   `DusmanServisi.hasar_biriktir(xp)` → `settings["dusman_biriken_hasar"] += hasar(xp)`.
   (`hasar(xp)` saf domain, katsayıyla çarpar.)

2. **"Vur" (`DusmanServisi.vur`):**
   ```python
   self._iyilesme_uygula()             # önce: hasarsız geçen günlerde düşman iyileşmiş olabilir
   biriken = self.biriken_hasar()
   self._settings.set(BIRIKEN, 0)      # havuzu boşalt
   while kalan > 0:                    # darbe canı bitirir, taşan hasar bir sonraki düşmana geçer
       hp -= kalan
       if hp <= 0:
           self._hazine_ekle(tier)     # düşman devrildi → hazine bırak
           self._olay_hatti.publish(DusmanDevrildi(tier=tier))
           tier += 1; hp = max_hp(tier)  # üst tier düşman tam canla gelir
   ```
   - `max_hp(tier) = 100*(1 + 0.35*tier)` → her tier daha güçlü, **oyun hiç bitmez**.
   - Devrilince "son söz", devrilmediyse "lanet" baloncuğu (`son_soz_sec`/`lanet_sec`).
   - Sonuç `VurusSonucu` dataclass: verilen hasar, kalan/maks can, devrilen sayısı, konuşma.

3. **İyileşme:** Hasarsız geçen her gün düşman max canının %3'ü iyileşir
   (`gunluk_iyilesme`). "Tembellik düşmanı güçlendirir" metaforu. Okuma/vuruş öncesi
   `_iyilesme_uygula` ile bekleyen iyileşme önce uygulanır.

4. **Hazine aç (`hazine_ac`):** Bekleyen hazineyi açar; `hazine_odulu(tier, rastgele, rastgele)`
   tier'a göre artan **Puan / XP / Combo(×1.5)** ödülü verir ve ilgili deftere/servise yazar.
   (Hazine ödülü **ham deftere** yazılır — düşmanın kendini vurmaması için, çünkü
   `HasarliDefter` değil gerçek defter kullanılır.)

> **Tier ↔ karakter:** `dusman_getir(tier) = DUSMANLAR[(tier//3) % 4]`. Her karakter 3 tier
> boyunca kalır, sadece **boyutu** büyür (`BOYUT_CARPANLARI`); 4 karakter döngüsü başa sarar.
```
