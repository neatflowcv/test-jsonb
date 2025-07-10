from sqlalchemy import create_engine, text, func
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from model import Base, Character
import json
from pathlib import Path

# 환경 변수 로드
load_dotenv()


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
    """examples 디렉토리의 JSON 파일들을 로드하고 데이터베이스에 삽입"""
    print("📁 examples 디렉토리에서 JSON 파일들을 로드합니다...")

    # examples 디렉토리의 모든 JSON 파일 찾기
    examples_dir = Path("examples")
    json_files = examples_dir.glob("*.json")

    characters_added = 0

    for json_file in json_files:
        try:
            # JSON 파일 읽기
            with open(json_file, "r", encoding="utf-8") as f:
                profile_data = json.load(f)

            # 파일명에서 캐릭터 이름 추출 (확장자 제거)
            character_name = json_file.stem

            print(f"  📊 {character_name} 캐릭터 데이터 처리 중...")

            # Character 객체 생성
            character = Character(name=character_name, profile=profile_data)

            # 데이터베이스에 추가
            session.add(character)
            characters_added += 1

            print(f"    ✅ {character_name} 캐릭터 추가 완료!")

        except Exception as e:
            print(f"    ❌ {json_file.name} 파일 처리 중 오류: {e}")
            continue

    # 변경사항 커밋
    session.commit()
    print(f"✅ 총 {characters_added}개 캐릭터 데이터가 성공적으로 삽입되었습니다!")
    print("✅ 샘플 데이터 생성 완료!")


def jsonb_query_examples(session):
    """JSON 쿼리 예제들 (데이터베이스 호환성 고려)"""
    print("\n" + "=" * 50)
    print("🔍 JSON 쿼리 예제들")
    print("=" * 50)

    # 1. 모든 캐릭터 목록 조회
    print("\n1️⃣ 모든 캐릭터 목록:")
    characters = session.query(Character).all()
    for char in characters:
        armory = char.profile.get("ArmoryProfile", {})
        char_name = armory.get("CharacterName", char.name)
        char_class = armory.get("CharacterClassName", "Unknown")
        char_level = armory.get("CharacterLevel", "Unknown")
        server = armory.get("ServerName", "Unknown")
        print(f"  📋 {char_name} ({char_class} Lv.{char_level}) - {server} 서버")

    # 2. 특정 캐릭터의 상세 정보 조회
    print("\n2️⃣ '하데스' 캐릭터 상세 정보:")
    hades = session.query(Character).filter(Character.name == "하데스").first()
    if hades:
        armory = hades.profile.get("ArmoryProfile", {})
        print(f"  🎭 캐릭터명: {armory.get('CharacterName')}")
        print(f"  ⚔️ 직업: {armory.get('CharacterClassName')}")
        print(f"  📊 레벨: {armory.get('CharacterLevel')}")
        print(f"  💪 전투력: {armory.get('CombatPower')}")
        print(f"  🏰 원정대 레벨: {armory.get('ExpeditionLevel')}")
        print(f"  🌍 서버: {armory.get('ServerName')}")

        # 스탯 정보
        stats = armory.get("Stats", [])
        print("  📈 주요 스탯:")
        for stat in stats[:4]:  # 처음 4개 스탯만 표시
            print(f"    - {stat.get('Type')}: {stat.get('Value')}")

    # 3. JSON 경로를 이용한 쿼리 (데이터베이스별 호환성 고려)
    print("\n3️⃣ JSON 경로 쿼리 예제:")
    try:
        # SQLite
        filtered_characters = session.query(Character).filter(
            func.json_extract(Character.profile, "$.ArmoryProfile.CharacterClassName")
            == "리퍼"
        ).all()

        # PostgreSQL
        # filtered_characters = session.query(Character).filter(
        #     Character.profile["ArmoryProfile"]["CharacterClassName"].astext == "리퍼"
        # ).all()
        print(f"  🔍 모든 캐릭터의 직업:")
        for char in filtered_characters:
            armory = char.profile.get("ArmoryProfile", {})
            char_name = armory.get("CharacterName", char.name)
            char_class = armory.get("CharacterClassName", "Unknown")
            print(f"    - {char_name}: {char_class}")

    except Exception as e:
        print(f"  ⚠️ JSON 경로 쿼리 오류: {e}")


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
        session.query(Character).delete()
        session.commit()

        # 샘플 데이터 생성
        create_sample_data(session)

        # JSON 쿼리 예제 실행
        jsonb_query_examples(session)

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
