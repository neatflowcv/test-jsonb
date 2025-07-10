from sqlalchemy import create_engine, Column, Integer, String, text, JSON, TypeDecorator
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.dialects.postgresql import JSONB
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

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


def get_engine():
    """데이터베이스 엔진 생성"""
    # PostgreSQL 연결 (JSONB를 위해 권장)
    # 환경 변수에서 DATABASE_URL을 읽거나 기본값 사용
    database_url = os.getenv(
        "DATABASE_URL", "postgresql://username:password@localhost/jsonb_test"
    )

    try:
        engine = create_engine(database_url, echo=True)
        # 연결 테스트
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ PostgreSQL 연결 성공!")
        return engine
    except Exception as e:
        print(f"❌ PostgreSQL 연결 실패: {e}")
        print("💡 SQLite를 사용합니다 (JSONB 대신 JSON 사용)")
        # SQLite 대체 (개발용)
        return create_engine("sqlite:///jsonb_example.db", echo=True)


def create_sample_data(session):
    """샘플 데이터 생성"""

    # 사용자 데이터 생성
    users_data = [
        {
            "name": "김철수",
            "profile": {
                "age": 28,
                "email": "kim@example.com",
                "address": {"city": "서울", "district": "강남구", "zipcode": "06292"},
                "hobbies": ["독서", "영화감상", "프로그래밍"],
                "is_active": True,
            },
            "settings": {
                "theme": "dark",
                "language": "ko",
                "notifications": {"email": True, "push": False, "sms": True},
            },
        },
        {
            "name": "이영희",
            "profile": {
                "age": 25,
                "email": "lee@example.com",
                "address": {"city": "부산", "district": "해운대구", "zipcode": "48094"},
                "hobbies": ["요리", "등산", "사진"],
                "is_active": True,
            },
            "settings": {
                "theme": "light",
                "language": "ko",
                "notifications": {"email": False, "push": True, "sms": False},
            },
        },
    ]

    for user_data in users_data:
        user = User(**user_data)
        session.add(user)

    # 제품 데이터 생성
    products_data = [
        {
            "name": "노트북",
            "product_info": {
                "category": "전자제품",
                "price": 1500000,
                "specs": {"cpu": "Intel i7", "ram": "16GB", "storage": "512GB SSD"},
                "tags": ["고성능", "업무용", "게임"],
                "ratings": [5, 4, 5, 4, 5],
                "available": True,
            },
        },
        {
            "name": "스마트폰",
            "product_info": {
                "category": "전자제품",
                "price": 800000,
                "specs": {"screen": "6.1인치", "camera": "48MP", "battery": "4000mAh"},
                "tags": ["휴대폰", "카메라", "통신"],
                "ratings": [4, 5, 4, 4, 5],
                "available": True,
            },
        },
    ]

    for product_data in products_data:
        product = Product(**product_data)
        session.add(product)

    session.commit()
    print("✅ 샘플 데이터 생성 완료!")


def jsonb_query_examples(session):
    """JSON 쿼리 예제들 (데이터베이스 호환성 고려)"""

    print("\n" + "=" * 50)
    print("🔍 JSON 쿼리 예제들")
    print("=" * 50)

    # 1. Python에서 JSON 필터링 - 나이가 25인 사용자 찾기
    print("\n1️⃣ 나이가 25인 사용자 찾기:")
    users = session.query(User).all()
    filtered_users = [user for user in users if user.profile.get("age") == 25]
    for user in filtered_users:
        print(f"   👤 {user.name}: 나이 {user.profile['age']}")

    # 2. 중첩된 JSON 데이터 쿼리 - 서울에 사는 사용자
    print("\n2️⃣ 서울에 사는 사용자 찾기:")
    users = session.query(User).all()
    seoul_users = [
        user for user in users if user.profile.get("address", {}).get("city") == "서울"
    ]
    for user in seoul_users:
        address = user.profile["address"]
        print(f"   🏠 {user.name}: {address['city']} {address['district']}")

    # 3. JSON 배열 쿼리 - 취미에 '프로그래밍'이 포함된 사용자
    print("\n3️⃣ 취미에 '프로그래밍'이 포함된 사용자 찾기:")
    users = session.query(User).all()
    programming_users = [
        user for user in users if "프로그래밍" in user.profile.get("hobbies", [])
    ]
    for user in programming_users:
        hobbies = ", ".join(user.profile["hobbies"])
        print(f"   🎯 {user.name}: 취미 - {hobbies}")

    # 4. JSON 키 존재 여부 확인
    print("\n4️⃣ 설정에 'theme' 키가 있는 사용자:")
    users = session.query(User).all()
    theme_users = [user for user in users if "theme" in user.settings]
    for user in theme_users:
        theme = user.settings.get("theme", "N/A")
        print(f"   🎨 {user.name}: 테마 - {theme}")

    # 5. 복잡한 조건 쿼리 - 가격이 1,000,000원 이상이고 사용 가능한 제품
    print("\n5️⃣ 가격이 1,000,000원 이상이고 사용 가능한 제품:")
    products = session.query(Product).all()
    expensive_products = [
        product
        for product in products
        if (
            product.product_info.get("price", 0) >= 1000000
            and product.product_info.get("available", False)
        )
    ]
    for product in expensive_products:
        price = product.product_info["price"]
        category = product.product_info["category"]
        print(f"   💰 {product.name}: {price:,}원 ({category})")

    # 6. JSON 배열 요소 검색 - 평점에 5점이 포함된 제품
    print("\n6️⃣ 평점에 5점이 포함된 제품:")
    products = session.query(Product).all()
    five_star_products = [
        product for product in products if 5 in product.product_info.get("ratings", [])
    ]
    for product in five_star_products:
        ratings = product.product_info["ratings"]
        avg_rating = sum(ratings) / len(ratings)
        print(f"   ⭐ {product.name}: 평균 {avg_rating:.1f}점 (최고 5점)")

    # 7. JSON 데이터 통계 분석
    print("\n7️⃣ JSON 데이터 통계 분석:")
    users = session.query(User).all()
    ages = [user.profile.get("age", 0) for user in users]
    avg_age = sum(ages) / len(ages) if ages else 0
    print(f"   📊 평균 나이: {avg_age:.1f}세")

    cities = [user.profile.get("address", {}).get("city", "") for user in users]
    city_count = {}
    for city in cities:
        if city:
            city_count[city] = city_count.get(city, 0) + 1
    print(f"   🏙️ 도시별 사용자 수: {city_count}")


def json_update_examples(session):
    """JSON 업데이트 예제들"""

    print("\n" + "=" * 50)
    print("✏️  JSON 업데이트 예제들")
    print("=" * 50)

    # 1. JSON 필드 일부 업데이트
    print("\n1️⃣ 사용자 나이 업데이트:")
    user = session.query(User).filter(User.name == "김철수").first()
    if user:
        old_age = user.profile["age"]
        # JSON 객체 수정
        user.profile = {**user.profile, "age": 29}
        session.commit()
        print(f"   👤 {user.name}: {old_age}세 → {user.profile['age']}세")

    # 2. 중첩된 JSON 객체 업데이트
    print("\n2️⃣ 알림 설정 업데이트:")
    user = session.query(User).filter(User.name == "이영희").first()
    if user:
        # 중첩된 객체 수정
        new_settings = user.settings.copy()
        new_settings["notifications"]["email"] = True
        new_settings["notifications"]["push"] = False
        user.settings = new_settings
        session.commit()
        notifications = user.settings["notifications"]
        print(f"   📧 {user.name}: 이메일 알림 활성화 - {notifications}")

    # 3. JSON 배열에 요소 추가
    print("\n3️⃣ 취미 추가:")
    user = session.query(User).filter(User.name == "김철수").first()
    if user:
        old_hobbies = user.profile["hobbies"].copy()
        new_profile = user.profile.copy()
        new_profile["hobbies"] = old_hobbies + ["운동"]
        user.profile = new_profile
        session.commit()
        print(f"   🎯 {user.name}: 취미 추가 - {user.profile['hobbies']}")


def main():
    """메인 함수"""
    print("🚀 SQLAlchemy JSONB 예제 시작!")

    # 데이터베이스 엔진 생성
    engine = get_engine()

    # 테이블 생성
    Base.metadata.create_all(engine)
    print("📋 테이블 생성 완료!")

    # 세션 생성
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # 기존 데이터 삭제 (예제용)
        session.query(User).delete()
        session.query(Product).delete()
        session.commit()

        # 샘플 데이터 생성
        create_sample_data(session)

        # JSON 쿼리 예제 실행
        jsonb_query_examples(session)

        # JSON 업데이트 예제 실행
        json_update_examples(session)

        print("\n" + "=" * 50)
        print("✅ 모든 예제 완료!")
        print("=" * 50)

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        session.rollback()
    finally:
        session.close()


if __name__ == "__main__":
    main()
