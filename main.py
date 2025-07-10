from sqlalchemy import create_engine, text
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
        # PostgreSQL JSONB 쿼리 (SQLite에서는 작동하지 않을 수 있음)

        # 모든 캐릭터의 직업 정보만 추출
        print("  🔍 모든 캐릭터의 직업:")
        for char in characters:
            armory = char.profile.get("ArmoryProfile", {})
            char_name = armory.get("CharacterName", char.name)
            char_class = armory.get("CharacterClassName", "Unknown")
            print(f"    - {char_name}: {char_class}")

    except Exception as e:
        print(f"  ⚠️ JSON 경로 쿼리 오류: {e}")

    # 4. 장비 정보 조회
    print("\n4️⃣ 캐릭터 장비 정보:")
    for char in characters:
        armory = char.profile.get("ArmoryProfile", {})
        char_name = armory.get("CharacterName", char.name)
        equipment = armory.get("ArmoryEquipment", [])

        print(f"  ⚔️ {char_name}의 주요 장비:")
        weapon = next((item for item in equipment if item.get("Type") == "무기"), None)
        if weapon:
            print(f"    🗡️ 무기: {weapon.get('Name')} ({weapon.get('Grade')})")

        armor_count = len(
            [
                item
                for item in equipment
                if item.get("Type") in ["투구", "상의", "하의", "장갑", "어깨"]
            ]
        )
        accessory_count = len(
            [
                item
                for item in equipment
                if item.get("Type") in ["목걸이", "귀걸이", "반지"]
            ]
        )
        print(f"    🛡️ 방어구: {armor_count}개, 💍 악세서리: {accessory_count}개")


def json_update_examples(session):
    """JSON 업데이트 예제들"""
    print("\n" + "=" * 50)
    print("✏️ JSON 업데이트 예제들")
    print("=" * 50)

    # 1. 새로운 필드 추가
    print("\n1️⃣ 캐릭터에 마지막 로그인 시간 추가:")
    from datetime import datetime

    hades = session.query(Character).filter(Character.name == "하데스").first()
    if hades:
        # 기존 프로필 데이터 복사
        updated_profile = hades.profile.copy()

        # 새로운 필드 추가
        updated_profile["LastLoginTime"] = datetime.now().isoformat()
        updated_profile["GameVersion"] = "2.0.1"
        updated_profile["CustomNote"] = "강력한 슬레이어 캐릭터"

        # 프로필 업데이트
        hades.profile = updated_profile

        print(f"  ✅ {hades.name}에 새로운 필드들이 추가되었습니다:")
        print(f"    - LastLoginTime: {updated_profile['LastLoginTime']}")
        print(f"    - GameVersion: {updated_profile['GameVersion']}")
        print(f"    - CustomNote: {updated_profile['CustomNote']}")

    # 2. 중첩된 JSON 데이터 수정
    print("\n2️⃣ 캐릭터 타이틀 변경:")
    huttal = session.query(Character).filter(Character.name == "후탈").first()
    if huttal:
        # 기존 프로필 데이터 복사
        updated_profile = huttal.profile.copy()

        # ArmoryProfile 내의 Title 수정
        if "ArmoryProfile" in updated_profile:
            original_title = updated_profile["ArmoryProfile"].get("Title", "None")
            updated_profile["ArmoryProfile"]["Title"] = "최강의 전사"
            updated_profile["ArmoryProfile"]["CustomRank"] = "S급"

            huttal.profile = updated_profile

            print(f"  ✅ {huttal.name}의 타이틀이 변경되었습니다:")
            print(f"    - 이전: {original_title}")
            print(f"    - 현재: {updated_profile['ArmoryProfile']['Title']}")
            print(
                f"    - 새로운 등급: {updated_profile['ArmoryProfile']['CustomRank']}"
            )

    # 3. 배열 데이터에 새 항목 추가
    print("\n3️⃣ 캐릭터 성향에 새로운 항목 추가:")
    harisona = session.query(Character).filter(Character.name == "해리소나").first()
    if harisona:
        # 기존 프로필 데이터 복사
        updated_profile = harisona.profile.copy()

        # Tendencies 배열에 새 항목 추가
        if (
            "ArmoryProfile" in updated_profile
            and "Tendencies" in updated_profile["ArmoryProfile"]
        ):
            tendencies = updated_profile["ArmoryProfile"]["Tendencies"]

            # 새로운 성향 추가
            new_tendency = {"Type": "행운", "Point": 777, "MaxPoint": 1000}
            tendencies.append(new_tendency)

            harisona.profile = updated_profile

            print(f"  ✅ {harisona.name}에 새로운 성향이 추가되었습니다:")
            print(f"    - 타입: {new_tendency['Type']}")
            print(f"    - 포인트: {new_tendency['Point']}/{new_tendency['MaxPoint']}")

    # 4. 조건부 업데이트
    print("\n4️⃣ 조건부 업데이트 (높은 레벨 캐릭터에 VIP 상태 추가):")
    all_characters = session.query(Character).all()
    vip_count = 0

    for char in all_characters:
        armory = char.profile.get("ArmoryProfile", {})
        char_level = armory.get("CharacterLevel", 0)
        char_name = armory.get("CharacterName", char.name)

        if char_level >= 70:  # 70레벨 이상인 캐릭터
            updated_profile = char.profile.copy()
            updated_profile["VIP_Status"] = True
            updated_profile["VIP_Since"] = datetime.now().isoformat()
            updated_profile["Benefits"] = [
                "경험치 보너스 +20%",
                "골드 보너스 +15%",
                "특별 이벤트 참여 가능",
            ]

            char.profile = updated_profile
            vip_count += 1

            print(f"  ⭐ {char_name} (Lv.{char_level})에게 VIP 상태가 부여되었습니다!")

    print(f"  ✅ 총 {vip_count}명의 캐릭터가 VIP로 업그레이드되었습니다!")

    # 변경사항 커밋
    session.commit()
    print("\n💾 모든 업데이트가 데이터베이스에 저장되었습니다!")


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
