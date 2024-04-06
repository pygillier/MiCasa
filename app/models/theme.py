from sqlalchemy.orm import Mapped, mapped_column
from app.database import db


class Theme(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    background: Mapped[str]
    primary: Mapped[str]
    accent: Mapped[str]
    is_custom: Mapped[bool]
