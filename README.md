# MySQL Migration Tool

MySQL 데이터베이스 마이그레이션 도구 - 테이블 필터링, 실시간 진행률, 스케줄링 지원

## 기능

- **테이블 선택**: 특정 테이블만 선택하여 덤프
- **WHERE 필터**: 조건에 맞는 데이터만 추출
- **컬럼 선택**: 필요한 컬럼만 선택
- **다중 서버 지원**: 소스/대상 DB가 다른 서버에 있어도 가능
- **실시간 진행률**: WebSocket을 통한 실시간 상태 확인
- **히스토리 관리**: 마이그레이션 기록 조회
- **스케줄링**: 정기적인 마이그레이션 예약

## 프로젝트 구조

```
migrate_mysql/
├── packages/
│   ├── backend/          # FastAPI 백엔드
│   │   ├── migrate_mysql/
│   │   │   ├── api/      # REST API
│   │   │   ├── exporter.py
│   │   │   ├── importer.py
│   │   │   └── cli.py
│   │   └── tests/        # pytest 테스트
│   │
│   └── frontend/         # React 프론트엔드
│       └── src/
│           ├── components/
│           ├── pages/
│           └── hooks/
├── README.md
└── TODO.md
```

## 요구사항

- Python 3.10+
- Node.js 18+
- PostgreSQL (히스토리/스케줄 저장용)
- MySQL (마이그레이션 대상)

## 설치 및 실행

### Backend

```bash
cd packages/backend
uv sync
uv run uvicorn migrate_mysql.api.main:app --reload
```

### Frontend

```bash
cd packages/frontend
npm install
npm run dev
```

### CLI (직접 사용)

```bash
cd packages/backend
uv sync

# Export
uv run migrate-mysql export \
  -h localhost -P 3306 -u root -p password \
  -d mydb -o dump.sql \
  -t users -t orders \
  -f "users:created_at > '2024-01-01'"

# Import
uv run migrate-mysql import \
  -h localhost -P 3306 -u root -p password \
  -d target_db -i dump.sql
```

## 환경 변수

```bash
# Backend
DATABASE_URL=postgresql://user:pass@localhost:5432/migrate_mysql
SECRET_KEY=your-secret-key
MYSQL_DEFAULT_HOST=localhost
MYSQL_DEFAULT_PORT=3306

# Frontend
VITE_API_URL=http://localhost:8000
```

## API 문서

백엔드 실행 후 아래 URL에서 API 문서 확인:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 개발

### TDD 방식

이 프로젝트는 TDD(Test-Driven Development) 방식으로 개발됩니다.

1. **Red**: 실패하는 테스트 먼저 작성
2. **Green**: 테스트를 통과하는 최소한의 코드 작성
3. **Refactor**: 코드 리팩토링

### 테스트 실행

```bash
# Backend
cd packages/backend
uv run pytest

# Frontend
cd packages/frontend
npm run test
```

## 기술 스택

### Backend
- FastAPI
- SQLAlchemy
- PostgreSQL
- WebSocket
- JWT 인증
- APScheduler

### Frontend
- React 18
- TypeScript
- Vite
- TailwindCSS
- React Query
- React Router

## 라이선스

MIT
