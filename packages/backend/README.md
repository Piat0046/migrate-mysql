# MySQL Migration Tool - Backend

FastAPI 기반 백엔드 서버

## 기술 스택

- **FastAPI** - 비동기 웹 프레임워크
- **SQLAlchemy** - ORM
- **PostgreSQL** - 히스토리/스케줄/사용자 데이터 저장
- **JWT** - 인증
- **WebSocket** - 실시간 진행률
- **APScheduler** - 스케줄링

## 설치

```bash
uv sync
```

## 실행

### 개발 서버

```bash
uv run uvicorn migrate_mysql.api.main:app --reload --host 0.0.0.0 --port 8000
```

### CLI

```bash
# Export
uv run migrate-mysql export \
  -h localhost -P 3306 -u root -p password \
  -d source_db -o dump.sql

# Import
uv run migrate-mysql import \
  -h localhost -P 3306 -u root -p password \
  -d target_db -i dump.sql
```

## 환경 변수

```bash
# .env 파일 생성
DATABASE_URL=postgresql://user:pass@localhost:5432/migrate_mysql
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## API 엔드포인트

### 인증
| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/api/auth/login` | 로그인 |
| POST | `/api/auth/logout` | 로그아웃 |
| GET | `/api/auth/me` | 현재 사용자 정보 |

### 연결 관리
| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/api/connections/test` | DB 연결 테스트 |
| POST | `/api/connections/tables` | 테이블 목록 조회 |
| POST | `/api/connections/columns` | 컬럼 목록 조회 |

### 마이그레이션
| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/api/migrations/export` | Export 시작 |
| POST | `/api/migrations/import` | Import 시작 |
| GET | `/api/migrations/{id}/status` | 상태 조회 |
| DELETE | `/api/migrations/{id}` | 작업 취소 |

### 히스토리
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/history` | 히스토리 목록 |
| GET | `/api/history/{id}` | 상세 조회 |

### 스케줄
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/schedules` | 스케줄 목록 |
| POST | `/api/schedules` | 스케줄 생성 |
| DELETE | `/api/schedules/{id}` | 스케줄 삭제 |

### WebSocket
| Endpoint | 설명 |
|----------|------|
| `WS /ws/migrations/{id}` | 실시간 진행률 |

## 테스트

```bash
# 전체 테스트
uv run pytest

# 특정 테스트
uv run pytest tests/test_api/test_auth.py

# 커버리지
uv run pytest --cov=migrate_mysql
```

## 프로젝트 구조

```
packages/backend/
├── pyproject.toml
├── migrate_mysql/
│   ├── __init__.py
│   ├── exporter.py          # DB Export 로직
│   ├── importer.py          # DB Import 로직
│   ├── cli.py               # CLI 인터페이스
│   └── api/
│       ├── __init__.py
│       ├── main.py          # FastAPI 앱
│       ├── database.py      # DB 연결
│       ├── models.py        # SQLAlchemy 모델
│       ├── schemas.py       # Pydantic 스키마
│       ├── auth.py          # JWT 인증
│       ├── websocket.py     # WebSocket 관리
│       └── routes/
│           ├── auth.py
│           ├── connections.py
│           ├── migrations.py
│           ├── history.py
│           └── schedules.py
└── tests/
    ├── conftest.py
    └── test_api/
        ├── test_auth.py
        ├── test_connections.py
        ├── test_migrations.py
        ├── test_history.py
        ├── test_schedules.py
        └── test_websocket.py
```

## 데이터 모델

### User
```python
- id: int
- username: str
- hashed_password: str
- is_active: bool
- created_at: datetime
```

### MigrationHistory
```python
- id: int
- user_id: int
- type: str (export/import)
- source_host: str
- source_database: str
- target_host: str (import only)
- target_database: str (import only)
- tables: JSON
- filters: JSON
- status: str (pending/running/completed/failed)
- row_count: int
- error_message: str
- started_at: datetime
- completed_at: datetime
```

### Schedule
```python
- id: int
- user_id: int
- name: str
- cron_expression: str
- config: JSON (마이그레이션 설정)
- is_active: bool
- last_run_at: datetime
- next_run_at: datetime
- created_at: datetime
```
