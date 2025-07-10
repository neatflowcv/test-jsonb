# SQLAlchemy JSON/JSONB 예제

SQLAlchemy에서 JSON 및 JSONB 데이터 타입을 사용하는 방법을 보여주는 예제 프로젝트입니다.

## 🚀 기능

- **호환성**: PostgreSQL의 JSONB와 SQLite의 JSON을 자동으로 선택
- **CRUD 작업**: JSON 데이터의 생성, 조회, 수정, 삭제
- **복잡한 쿼리**: 중첩된 JSON 객체 및 배열 쿼리
- **실제 사용 사례**: 사용자 프로필, 제품 정보 등

## 📋 요구사항

- Python 3.13+
- SQLAlchemy 2.0+
- PostgreSQL (권장) 또는 SQLite (대체)

## 🛠 설치

```bash
# 가상환경 활성화
source .venv/bin/activate

# 의존성 설치
uv add sqlalchemy psycopg2-binary python-dotenv
```

## 💡 사용법

```bash
# 예제 실행
python main.py
```

### PostgreSQL 연결 설정

환경 변수로 PostgreSQL 연결을 설정할 수 있습니다:

```bash
export DATABASE_URL="postgresql://username:password@localhost:5432/database_name"
```

PostgreSQL 연결이 실패하면 자동으로 SQLite를 사용합니다.

## 📊 예제 내용

### 1. 데이터 모델

- **User**: 사용자 정보 (프로필, 설정)
- **Product**: 제품 정보 (사양, 평점, 메타데이터)

### 2. JSON 쿼리 예제

- 특정 값으로 필터링 (나이, 도시 등)
- 중첩된 JSON 객체 접근
- JSON 배열 검색
- 키 존재 여부 확인
- 복잡한 조건 쿼리
- 통계 분석

### 3. JSON 업데이트 예제

- 개별 필드 수정
- 중첩된 객체 업데이트
- 배열에 요소 추가

## 🔧 주요 특징

### 호환성 JSON 타입

```python
class CompatibleJSON(TypeDecorator):
    """PostgreSQL에서는 JSONB, 다른 DB에서는 JSON 사용"""
    
    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(JSONB())
        else:
            return dialect.type_descriptor(JSON())
```

### Python 레벨 JSON 쿼리

데이터베이스 호환성을 위해 Python에서 JSON 필터링:

```python
# 나이가 25인 사용자 찾기
users = session.query(User).all()
filtered_users = [user for user in users if user.profile.get('age') == 25]
```

## 📁 프로젝트 구조

```
jsonb/
├── main.py              # 메인 예제 코드
├── pyproject.toml       # 프로젝트 설정
├── README.md           # 프로젝트 설명
└── jsonb_example.db    # SQLite 데이터베이스 (자동 생성)
```

## 🎯 실행 결과

예제를 실행하면 다음과 같은 내용을 확인할 수 있습니다:

- ✅ 데이터베이스 연결 및 테이블 생성
- 📊 샘플 데이터 생성
- 🔍 다양한 JSON 쿼리 예제
- ✏️ JSON 데이터 업데이트 예제
- 📈 통계 분석 결과

## 🚨 참고사항

- PostgreSQL이 JSONB의 모든 기능을 제공합니다
- SQLite는 JSON 기본 기능만 지원합니다
- 실제 운영 환경에서는 PostgreSQL 사용을 권장합니다
