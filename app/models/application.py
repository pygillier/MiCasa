from sqlalchemy import String, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.database import db


class Application(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    description: Mapped[str] = mapped_column(String(2000), nullable=True)
    url: Mapped[str] = mapped_column(String, unique=True)
    icon: Mapped[str]
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    position: Mapped[int] = mapped_column(Integer, unique=True)