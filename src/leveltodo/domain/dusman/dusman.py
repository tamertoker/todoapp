"""Düşman (Şeytan) tanımları, can eğrisi ve hazine ödülü — saf.

Şeytan, tembelliğin görsel düşmanıdır. Görev yaptıkça "biriken hasar" toplanır;
kullanıcı Düşman sekmesinde "Vur" deyince bu hasarın tamamı bir darbede iner.
Canı biterse bir üst tier (daha çok canlı) düşman gelir ve geride bir hazine
bırakır.

Tier ↔ düşman eşlemesi: Her düşman karakteri ardışık 3 tier boyunca aynı kalır,
yalnızca BOYUTU büyür (1-2-3 aynı karakter; 4-5-6 sıradaki, vb.). Dört karakter
döngüsü bitince başa dönülür ama maksimum can her tier'da arttığı için oyun
gitgide zorlaşır — yani hiç bitmez. Hiç hasar almadan geçen her gün düşman biraz
iyileşir (tembellik onu güçlendirir).
"""

from __future__ import annotations

from dataclasses import dataclass

BASE_HP = 100
# Maksimum can her tier'da bu oranda DOĞRUSAL artar (sonsuz ama makul zorluk eğrisi).
TIER_HP_ARTIS = 0.35
# Kazanılan XP'nin hasara çevrilirken çarpıldığı katsayı (denge ayarı).
HASAR_KATSAYISI = 1.0
# Hasar almadan geçen her gün düşman maksimum canının bu oranı kadar iyileşir.
GUNLUK_IYILESME_ORANI = 0.03
# Bir düşman karakterinin kaç tier boyunca (boyut büyüyerek) sahnede kaldığı.
KADEME = 3
# Tier'ın kademe içindeki sırasına göre sprite büyütme çarpanı (1-2-3. boyut).
BOYUT_CARPANLARI = (1.0, 1.25, 1.55)


@dataclass(frozen=True, slots=True)
class Dusman:
    anahtar: str  # sprite dosya adı (örn. "erteleyici")
    ad: str  # ekranda görünen ad
    lore: str


DUSMANLAR: list[Dusman] = [
    Dusman("erteleyici", "Erteletici", "'Bir dakikaya başlarım' dedirtir, sonra gün biter."),
    Dusman("dagilan_golge", "Dağılgan", "Aklını dört bir yana çeker; bir türlü odaklanamazsın."),
    Dusman("tembel_devi", "Tembel Dev", "Üstüne ağırlık çöker; kıpırdamak bile zahmet olur."),
    Dusman("karanlik_erteleme", "Rehavet Ustası", "Tatlı tatlı her şeyi erteletir; en sinsisi."),
]


# Düşmanın ara sıra fısıldadığı kışkırtmalar — seni tembelliğe çağıran ses.
KISKIRTMALAR: tuple[str, ...] = (
    "Amaan, bugün de olmadı; yarın nasılsa yaparsın.",
    "Otursana, görevler kaçmıyor ya.",
    "Bir mola daha iyi gider, hak etmedin mi?",
    "Yarın bol bol vaktin var, acelesi ne.",
    "Bugünlük bu kadar yeter, kendini yorma.",
    "Pek havanda değilsin bugün, zorlama.",
    "Şöyle biraz uzan; dünya başına yıkılmaz.",
)


# Darbe yediğinde söylediği laf (sohbet baloncuğunda görünür).
LANETLER: tuple[str, ...] = (
    "Ay! Yine mi kalktın yahu?",
    "Dur biraz, bu kadar üstüme gelme.",
    "Canımı acıttın ama daha bitmedi bu iş.",
    "Nereden buluyorsun bu enerjiyi sen?",
    "Otursana, ne acelen var böyle...",
    "Her seferinde biraz daha eriyorum, farkında mısın?",
    "İnatçısın, onu kabul ediyorum.",
    "Bunu yanına bırakmam, haberin olsun.",
)


# Devrildiğinde söylediği son söz.
SON_SOZLER: tuple[str, ...] = (
    "Tamam tamam, bugün sen kazandın.",
    "Beni devirdin ama tembellik kolay kolay bitmez.",
    "Bu son değil; yarın yine buradayım.",
    "Pekâlâ... bir dahakine hazır ol.",
)


# Hazineden çıkabilecek ödül türleri.
ODUL_TURLERI: tuple[str, ...] = ("puan", "xp", "combo")


@dataclass(frozen=True, slots=True)
class HazineOdulu:
    tur: str  # "puan" | "xp" | "combo"
    miktar: int  # puan/xp adedi; combo için süre (dakika)
    mesaj: str  # kullanıcıya gösterilecek epik metin


def dusman_getir(tier: int) -> Dusman:
    """tier'a karşılık gelen düşman karakteri (her karakter KADEME tier sürer)."""
    return DUSMANLAR[(tier // KADEME) % len(DUSMANLAR)]


def boyut_carpani(tier: int) -> float:
    """Aynı karakterin kademe içindeki büyüme çarpanı (1., 2., 3. boyut)."""
    return BOYUT_CARPANLARI[tier % KADEME]


def max_hp(tier: int) -> int:
    return round(BASE_HP * (1 + TIER_HP_ARTIS * tier))


def hasar(xp: int) -> int:
    """Kazanılan XP'yi katsayıyla düşman hasarına çevirir."""
    return round(xp * HASAR_KATSAYISI)


def gunluk_iyilesme(maks_hp: int) -> int:
    """Bir hasarsız günde düşmanın iyileşeceği can miktarı."""
    return round(maks_hp * GUNLUK_IYILESME_ORANI)


def kiskirtma_sec(tohum: int) -> str:
    """Verilen tohuma (ör. günün sıra numarası) göre bir kışkırtma seçer."""
    return KISKIRTMALAR[tohum % len(KISKIRTMALAR)]


def lanet_sec(tohum: int) -> str:
    return LANETLER[tohum % len(LANETLER)]


def son_soz_sec(tohum: int) -> str:
    return SON_SOZLER[tohum % len(SON_SOZLER)]


def hazine_odulu(tier: int, secim: float, olcek: float) -> HazineOdulu:
    """tier'a göre artan bir hazine ödülü üretir.

    secim (0..1) ödül türünü, olcek (0..1) miktar varyansını belirler — böylece
    fonksiyon saf kalır (rastgeleliği çağıran verir).
    """
    tur = ODUL_TURLERI[min(int(secim * len(ODUL_TURLERI)), len(ODUL_TURLERI) - 1)]
    comert = 1.0 + 0.18 * tier  # tier büyüdükçe daha cömert
    varyans = 0.8 + 0.4 * olcek  # 0.8 .. 1.2
    if tur == "puan":
        m = round(25 * comert * varyans)
        return HazineOdulu("puan", m, f"💰 Hazineden {m} puan döküldü!")
    if tur == "xp":
        m = round(40 * comert * varyans)
        return HazineOdulu("xp", m, f"✨ Hazineden {m} XP parladı!")
    m = min(120, round(30 + 6 * tier))  # combo süresi (dakika)
    return HazineOdulu("combo", m, f"🔥 Combo ×1.5 açıldı — {m} dakika!")
