from sqlalchemy import Column, Integer, String, JSON, TypeDecorator
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import JSONB

# 베이스 클래스 생성
Base = declarative_base()


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


# JSON을 사용하는 모델 정의
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    profile = Column(CompatibleJSON)  # 호환 JSON 필드
    settings = Column(CompatibleJSON)  # 또 다른 호환 JSON 필드


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    product_info = Column(CompatibleJSON)  # 제품 정보를 호환 JSON으로 저장
