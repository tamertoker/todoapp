"""Combo servisi — kısa aralıkta art arda odaklı görevler bonus verir.

15 dakika içinde, her biri en az 10 dakika kronometreyle yapılmış 3 görev
tamamlanınca combo tetiklenir: 1 saat boyunca ödüller ×1.5. Durum ayar deposunda
tutulur (uygulama kapanıp açılsa da combo sürer).
"""

from __future__ import annotations

from datetime import datetime, timedelta

from leveltodo.application.settings_service import SettingsService


class ComboServisi:
    BITIS = "combo_bitis"
    ZAMANLAR = "combo_zamanlar"
    PENCERE_DK = 15  # bu süre içinde
    GEREKEN = 3  # bu kadar görev
    MIN_SANIYE = 600  # her biri en az 10 dk kronometre
    SURE_DK = 60  # combo aktif kalma süresi
    MAKS_DK = 120  # makul üst sınır (hazine combo'su en fazla bu kadar); üstü bayat sayılır
    CARPAN = 1.5

    def __init__(self, settings: SettingsService) -> None:
        self._settings = settings

    def aktif_mi(self, simdi: datetime) -> bool:
        bitis = self._settings.get(self.BITIS)
        if not bitis:
            return False
        kalan = (datetime.fromisoformat(bitis) - simdi).total_seconds()
        # 0 < kalan <= üst sınır: gerçek combo. Çok büyük kalan = bayat kayıt
        # (ör. debug'da saat ileri kaydırılıp combo başlamış); aktif sayma.
        return 0 < kalan <= self.MAKS_DK * 60

    def carpan(self, simdi: datetime) -> float:
        return self.CARPAN if self.aktif_mi(simdi) else 1.0

    def odul_baslat(self, simdi: datetime, dakika: int | None = None) -> None:
        """Combo'yu ödül olarak zorla başlatır/uzatır (ör. hazineden çıkınca)."""
        sure = dakika if dakika is not None else self.SURE_DK
        self._settings.set(self.BITIS, (simdi + timedelta(minutes=sure)).isoformat())

    def kalan_dakika(self, simdi: datetime) -> int:
        bitis = self._settings.get(self.BITIS)
        if not bitis:
            return 0
        fark = datetime.fromisoformat(bitis) - simdi
        return max(0, int(fark.total_seconds() // 60))

    def tamamlama_bildir(self, calisilan_saniye: int, simdi: datetime) -> bool:
        """Görev tamamlandığını bildirir; combo yeni tetiklendiyse True döner."""
        if calisilan_saniye < self.MIN_SANIYE:
            return False
        sinir = simdi - timedelta(minutes=self.PENCERE_DK)
        zamanlar = [datetime.fromisoformat(z) for z in self._settings.get(self.ZAMANLAR)]
        zamanlar = [z for z in zamanlar if z >= sinir]
        zamanlar.append(simdi)
        if len(zamanlar) >= self.GEREKEN and not self.aktif_mi(simdi):
            self._settings.set(self.BITIS, (simdi + timedelta(minutes=self.SURE_DK)).isoformat())
            self._settings.set(self.ZAMANLAR, [])
            return True
        self._settings.set(self.ZAMANLAR, [z.isoformat() for z in zamanlar])
        return False
