"""Rozet (badge) tanımları ve koşulları — saf, test edilebilir.

Her rozetin bir koşulu var; kullanıcının o anki durumuna (RozetDurumu) bakılarak
kazanılıp kazanılmadığı belirlenir.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Rozet:
    id: str
    ad: str
    aciklama: str


@dataclass(frozen=True, slots=True)
class RozetDurumu:
    tamamlama: int
    en_iyi_giris_serisi: int
    profil_seviye: int
    kritik_yasandi: bool
    combo_yasandi: bool


ROZETLER: list[Rozet] = [
    Rozet("ilk_adim", "İlk Adım", "İlk görevini tamamla"),
    Rozet("caliskan", "Çalışkan", "10 görev tamamla"),
    Rozet("maratoncu", "Maratoncu", "100 görev tamamla"),
    Rozet("kivilcim", "Kıvılcım", "3 günlük giriş serisi"),
    Rozet("alev", "Alev", "7 günlük giriş serisi"),
    Rozet("sansli", "Şanslı", "İlk kritik başarını yaşa"),
    Rozet("combocu", "Combocu", "Bir combo tetikle"),
    Rozet("yukselen", "Yükselen", "Profil seviye 5'e ulaş"),
    Rozet("cevher", "Cevher", "Profil seviye 9'a ulaş"),
]


def kosul_saglandi_mi(rozet_id: str, durum: RozetDurumu) -> bool:
    if rozet_id == "ilk_adim":
        return durum.tamamlama >= 1
    if rozet_id == "caliskan":
        return durum.tamamlama >= 10
    if rozet_id == "maratoncu":
        return durum.tamamlama >= 100
    if rozet_id == "kivilcim":
        return durum.en_iyi_giris_serisi >= 3
    if rozet_id == "alev":
        return durum.en_iyi_giris_serisi >= 7
    if rozet_id == "sansli":
        return durum.kritik_yasandi
    if rozet_id == "combocu":
        return durum.combo_yasandi
    if rozet_id == "yukselen":
        return durum.profil_seviye >= 5
    if rozet_id == "cevher":
        return durum.profil_seviye >= 9
    return False
