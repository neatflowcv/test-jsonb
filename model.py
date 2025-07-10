from typing import Annotated
from sqlalchemy import String, JSON, TypeDecorator
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB


# 베이스 클래스 생성 (SQLAlchemy 2.0 스타일)
class Base(DeclarativeBase):
    pass


# 호환 가능한 JSON 타입 정의
class CompatibleJSON(TypeDecorator):
    """PostgreSQL에서는 JSONB, 다른 DB에서는 JSON 사용"""

    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(JSONB())
        else:
            return dialect.type_descriptor(JSON())


# JSON을 사용하는 모델 정의 (SQLAlchemy 2.0 스타일)
class Character(Base):
    __tablename__ = "characters"

    name: Mapped[Annotated[str, mapped_column(String(), primary_key=True)]]
    profile: Mapped[Annotated[dict, mapped_column(CompatibleJSON)]]
