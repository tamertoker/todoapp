"""Gün sonu günlüğü — saf kurallar (PyQt/DB yok).

İki şey burada yaşar:
- HAVUZ: iradeyi/yansımayı kışkırtan hazır sorular. Kullanıcının kendi eklediği
  sorularla birleştirilip her gün BİRİ gösterilir; seçim takvim gününe bağlıdır
  (deterministik dönüşüm) — aynı geçmiş gün hep aynı soruyu gösterir.
- Ödül eğrisi: günlük yazmanın XP'si sabit değil; her dolu günlük günüyle küçük
  bir tık artar. İleri seviyelerde level eşiği büyüdüğü için ödül de büyür.
"""

from __future__ import annotations

from datetime import date

# Hazır yansıtma soruları havuzu (sıra sabit; dönüşümün belkemiği).
HAVUZ: tuple[str, ...] = (
    "Bugün iradeni en çok nerede zorladın?",
    "Ertelemek istediğin bir şeyi yine de yaptın mı? Neydi?",
    "Bugünün seni en çok yoran anı neydi, nasıl atlattın?",
    "Yarının sen'i, bugünden ne yapmanı isterdi?",
    "Bugün kendine verdiğin bir sözü tuttun mu?",
    "Hangi küçük zafer bugün gözden kaçtı?",
    "Bugün enerjini en çok ne çaldı?",
    "Bugün öğrendiğin tek şey ne oldu?",
    "Şu an minnettar olduğun bir şeyi yaz.",
    "Bugünkü halin, bir hafta önceki halinden nerede ayrıştı?",
    "Yarın tek bir şeyi daha iyi yapacak olsan, ne olurdu?",
    "Bugün hangi alışkanlığın seni ileri taşıdı, hangisi geri çekti?",
)

TABAN_ODUL = 40  # ilk dolu günlüğün XP'si
GUNLUK_ARTIS = 1  # her ek dolu günlük günü için +XP


def gunun_sorusu(sorular: list[str], gun: date) -> str | None:
    """Verilen soru listesinden o güne düşeni döndürür (deterministik dönüşüm)."""
    if not sorular:
        return None
    return sorular[gun.toordinal() % len(sorular)]


def gunluk_odulu(onceki_dolu_gun: int) -> int:
    """Bu günlüğün XP'si: daha önce kaç dolu günlük günü varsa o kadar tık fazla."""
    return TABAN_ODUL + GUNLUK_ARTIS * onceki_dolu_gun
