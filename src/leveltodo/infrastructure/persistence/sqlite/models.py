"""Veritabanı tabloları (Faz 0).

İki tablo:
- users: Kişiler. Şimdilik tek bir varsayılan kullanıcı var, ama tüm tablolar
  baştan user_id taşır; ileride çoklu profil eklemek kolay olsun diye.
- settings: Kullanıcı ayarları. "anahtar = değer" biçiminde tutulur (değer JSON
  metni olarak saklanır). Yeni bir ayar eklemek için tabloyu değiştirmek
  gerekmez — sadece yeni bir anahtar yazılır.
"""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from leveltodo.infrastructure.persistence.sqlite.base import Base

# Tek kullanıcılı sürümde sabit kullanıcı kimliği (çoklu profil Faz V2).
DEFAULT_USER_ID = "default"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    name: Mapped[str] = mapped_column(String(120), default="Oyuncu")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Setting(Base):
    __tablename__ = "settings"
    __table_args__ = (UniqueConstraint("user_id", "key", name="uq_settings_user_key"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    key: Mapped[str] = mapped_column(String(80))
    value: Mapped[str] = mapped_column(String)  # JSON metni


class Task(Base):
    """Görev şablonu. Tek seferlik ya da her gün tekrar eden bir görevin tanımı.
    Asıl 'yapılacak' kayıtları (TaskInstance) bundan üretilir."""

    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(200))
    recurrence: Mapped[str] = mapped_column(String(10))  # none|daily|every_x|weekly|monthly
    recurrence_param: Mapped[str | None] = mapped_column(String(60), nullable=True)
    reward_override: Mapped[int | None] = mapped_column(Integer, nullable=True)
    stat: Mapped[str | None] = mapped_column(String(20), nullable=True)
    tag_id: Mapped[str | None] = mapped_column(String(26), nullable=True)  # etiket (proje)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    streak_count: Mapped[int] = mapped_column(Integer, default=0)
    streak_last_day: Mapped[date | None] = mapped_column(Date, nullable=True)


class TaskInstance(Base):
    """Bir görevin belirli bir güne düşen somut kaydı. Kronometre süresi, durum
    ve kazanılan ödül burada yaşar; geçmiş bozulmaz."""

    __tablename__ = "task_instances"
    __table_args__ = (UniqueConstraint("task_id", "day", name="uq_instance_task_day"),)

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    task_id: Mapped[str] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    day: Mapped[date] = mapped_column(Date)
    title: Mapped[str] = mapped_column(String(200))  # o anki başlık (anlık görüntü)
    status: Mapped[str] = mapped_column(String(10), default="pending")

    committed_seconds: Mapped[int] = mapped_column(Integer, default=0)
    timer_running: Mapped[bool] = mapped_column(Boolean, default=False)
    segment_started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    reward_xp: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reward_points: Mapped[int | None] = mapped_column(Integer, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class XpEvent(Base):
    """Kazanılan her XP'nin kaydı (denetim/grafik için kaynak)."""

    __tablename__ = "xp_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    day: Mapped[date] = mapped_column(Date)
    source: Mapped[str] = mapped_column(String(40))
    ref_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    amount: Mapped[int] = mapped_column(Integer)
    stat: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class WillAct(Base):
    """İrade eylemi — Disiplin statını besleyen, iradeyi zorlayan bir eylem kaydı."""

    __tablename__ = "will_acts"

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    day: Mapped[date] = mapped_column(Date)
    title: Mapped[str] = mapped_column(String(200))
    xp: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Streak(Base):
    """Seri (streak) kaydı. type='login' giriş serisi, type='task' görev serisi.
    Kullanıcı + tip başına tek satır."""

    __tablename__ = "streaks"
    __table_args__ = (UniqueConstraint("user_id", "type", name="uq_streak_user_type"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    type: Mapped[str] = mapped_column(String(10))
    current_count: Mapped[int] = mapped_column(Integer, default=0)
    best_count: Mapped[int] = mapped_column(Integer, default=0)
    last_day: Mapped[date | None] = mapped_column(Date, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class PointTransaction(Base):
    """Kazanılan/harcanan her puanın kaydı."""

    __tablename__ = "point_transactions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    day: Mapped[date] = mapped_column(Date)
    source: Mapped[str] = mapped_column(String(40))
    ref_id: Mapped[str | None] = mapped_column(String(26), nullable=True)
    amount: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class RoutineField(Base):
    """Rutin alan TANIMI — kullanıcının her gün takip ettiği bir ölçüt.
    kind='number' (kaç bardak/sayfa) ya da 'bool' (yaptım mı ✓). Sayısal alanda
    direction='min'/'max' ve target hedefi belirler; hedefi tutturunca seçilen
    stata reward_xp kadar XP yazılır. Silme = is_active False (geçmiş bozulmaz)."""

    __tablename__ = "routine_fields"

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(200))
    kind: Mapped[str] = mapped_column(String(10))  # number|bool
    direction: Mapped[str | None] = mapped_column(String(3), nullable=True)  # min|max
    target: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reward_xp: Mapped[int] = mapped_column(Integer)
    stat: Mapped[str] = mapped_column(String(20))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class RoutineEntry(Base):
    """Bir rutin alanının belirli bir güne düşen değeri. Sayıda girilen sayı,
    evet/hayır'da 0/1. rewarded: o gün hedef tutturulup XP verildi mi (gün başına
    en çok bir kez; geri alınmaz). Alan + gün başına tek satır."""

    __tablename__ = "routine_entries"
    __table_args__ = (UniqueConstraint("field_id", "day", name="uq_routine_field_day"),)

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    field_id: Mapped[str] = mapped_column(ForeignKey("routine_fields.id", ondelete="CASCADE"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    day: Mapped[date] = mapped_column(Date)
    value: Mapped[int] = mapped_column(Integer, default=0)
    value_text: Mapped[str | None] = mapped_column(String, nullable=True)  # METIN türü için
    rewarded: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class JournalEntry(Base):
    """Gün sonu günlüğü — gün başına tek kayıt (user_id+day benzersiz). text dolu
    kaydedilince Farkındalık'a reward_xp kadar XP verilir (gün başına bir kez);
    reward_xp o günün ilk dolduruşunda sabitlenir, böylece boşaltıp tekrar
    doldurmada tutarlı kalır. rewarded: şu an ödül duruyor mu (boşaltınca geri
    alınır → False)."""

    __tablename__ = "journal_entries"
    __table_args__ = (UniqueConstraint("user_id", "day", name="uq_journal_user_day"),)

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    day: Mapped[date] = mapped_column(Date)
    text: Mapped[str] = mapped_column(String, default="")
    reward_xp: Mapped[int] = mapped_column(Integer, default=0)
    rewarded: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class WalletTransaction(Base):
    """Cüzdan işlemi — gerçek para (uygulama-içi Puan'dan ayrı). amount KURUŞ olarak
    saklanır (kayan nokta hatasından kaçınmak için tam sayı). tur='gelir'|'gider'."""

    __tablename__ = "wallet_transactions"

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    day: Mapped[date] = mapped_column(Date)
    amount: Mapped[int] = mapped_column(Integer)  # kuruş, pozitif
    tur: Mapped[str] = mapped_column(String(6))  # gelir|gider
    aciklama: Mapped[str] = mapped_column(String(200), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class WishlistItem(Base):
    """İstek listesi öğesi — almak istediğin gerçek bir şey. price KURUŞ. İlerleme,
    cüzdan bakiyesi / fiyat oranıyla hesaplanır (ayrı kumbara yok). image_path varsa
    görsel soldan sağa açılır. Silme = is_active False."""

    __tablename__ = "wishlist_items"

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(200))
    price: Mapped[int] = mapped_column(Integer)  # kuruş
    image_path: Mapped[str | None] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Tag(Base):
    """Etiket (proje) — renkli bir nokta + ad. Görevler buna bağlanır (Task.tag_id)."""

    __tablename__ = "tags"

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(80))
    color: Mapped[str] = mapped_column(String(9))  # hex
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class StoreReward(Base):
    """Mağaza ödülü — Puan ile dakika satın alınan gerçek-hayat ödülü. cost_per_min
    dk başına puan maliyeti (kullanıcı belirler, tabandan düşemez). Silme=is_active False."""

    __tablename__ = "store_rewards"

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(200))
    cost_per_min: Mapped[int] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class StorePurchase(Base):
    """Mağaza satın alma kaydı (geçmiş). Harcanan puan ayrıca point_transactions'a
    negatif olarak yazılır; bu tablo 'ne, kaç dk, kaç puan' detayını tutar."""

    __tablename__ = "store_purchases"

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    reward_name: Mapped[str] = mapped_column(String(200))
    minutes: Mapped[int] = mapped_column(Integer)
    cost: Mapped[int] = mapped_column(Integer)  # puan
    day: Mapped[date] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class WakeLog(Base):
    """Uyandırma kaydı — gün başına tek. Hedef ve gerçek kalkış saati (HH:MM) ile
    o günün başarılı olup olmadığı. Başarılı günler Disiplin'e XP yazar."""

    __tablename__ = "wake_logs"
    __table_args__ = (UniqueConstraint("user_id", "day", name="uq_wake_user_day"),)

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    day: Mapped[date] = mapped_column(Date)
    hedef: Mapped[str] = mapped_column(String(5))
    gercek: Mapped[str] = mapped_column(String(5))
    basarili: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class ReflectionQuestion(Base):
    """Kullanıcının eklediği yansıtma sorusu. Hazır havuz koda gömülüdür; bu tablo
    yalnızca kullanıcının kendi eklediklerini tutar. Silme = is_active False."""

    __tablename__ = "reflection_questions"

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    text: Mapped[str] = mapped_column(String(300))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
