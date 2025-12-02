# TODO - MySQL Migration Tool

## 개발 방법론
- TDD (Test-Driven Development) 방식으로 진행
- 테스트 먼저 작성 → 구현 → 리팩토링

---

## 1단계: Backend 테스트 환경 및 기본 구조

### 테스트 환경
- [ ] `packages/backend/pyproject.toml` - pytest, pytest-asyncio, httpx 의존성 추가
- [ ] `packages/backend/tests/conftest.py` - 테스트 fixtures (DB, client)

### 기본 구조
- [ ] `packages/backend/migrate_mysql/api/__init__.py`
- [ ] `packages/backend/migrate_mysql/api/main.py` - FastAPI 앱 설정
- [ ] `packages/backend/migrate_mysql/api/database.py` - PostgreSQL 연결
- [ ] `packages/backend/migrate_mysql/api/models.py` - SQLAlchemy 모델
- [ ] `packages/backend/migrate_mysql/api/schemas.py` - Pydantic 스키마

---

## 2단계: Backend 인증 (TDD)

### 테스트 케이스
- [ ] `test_login_success` - 올바른 자격증명 → JWT 토큰 반환
- [ ] `test_login_invalid_password` - 잘못된 비밀번호 → 401
- [ ] `test_login_user_not_found` - 존재하지 않는 사용자 → 401
- [ ] `test_get_me_authenticated` - 유효한 토큰 → 사용자 정보
- [ ] `test_get_me_unauthenticated` - 토큰 없음 → 401
- [ ] `test_logout` - 로그아웃 → 성공

### 구현
- [ ] `packages/backend/tests/test_api/test_auth.py`
- [ ] `packages/backend/migrate_mysql/api/auth.py` - JWT 로직
- [ ] `packages/backend/migrate_mysql/api/routes/auth.py` - 인증 API

---

## 3단계: Backend 연결 API (TDD)

### 테스트 케이스
- [ ] `test_connection_success` - 유효한 DB 정보 → 연결 성공
- [ ] `test_connection_failure` - 잘못된 정보 → 실패 메시지
- [ ] `test_get_tables` - 테이블 목록 반환
- [ ] `test_get_columns` - 컬럼 목록 반환

### 구현
- [ ] `packages/backend/tests/test_api/test_connections.py`
- [ ] `packages/backend/migrate_mysql/api/routes/connections.py`

---

## 4단계: Backend 마이그레이션 API (TDD)

### 테스트 케이스
- [ ] `test_export_start` - Export 요청 → 작업 ID 반환
- [ ] `test_export_with_filter` - 필터 적용 Export
- [ ] `test_import_start` - Import 요청 → 작업 ID 반환
- [ ] `test_get_migration_status` - 진행 상태 조회
- [ ] `test_cancel_migration` - 작업 취소

### 구현
- [ ] `packages/backend/tests/test_api/test_migrations.py`
- [ ] `packages/backend/migrate_mysql/api/routes/migrations.py`

---

## 5단계: Backend 히스토리/스케줄 API (TDD)

### 테스트 케이스 - 히스토리
- [ ] `test_get_history_list` - 페이지네이션된 히스토리 조회
- [ ] `test_get_history_detail` - 상세 정보 조회

### 테스트 케이스 - 스케줄
- [ ] `test_create_schedule` - 스케줄 생성
- [ ] `test_get_schedules` - 스케줄 목록 조회
- [ ] `test_delete_schedule` - 스케줄 삭제

### 구현
- [ ] `packages/backend/tests/test_api/test_history.py`
- [ ] `packages/backend/tests/test_api/test_schedules.py`
- [ ] `packages/backend/migrate_mysql/api/routes/history.py`
- [ ] `packages/backend/migrate_mysql/api/routes/schedules.py`

---

## 6단계: Backend WebSocket (TDD)

### 테스트 케이스
- [ ] `test_websocket_connect` - WebSocket 연결 성공
- [ ] `test_websocket_progress_updates` - 진행률 메시지 수신
- [ ] `test_websocket_completion` - 완료 메시지 수신

### 구현
- [ ] `packages/backend/tests/test_api/test_websocket.py`
- [ ] `packages/backend/migrate_mysql/api/websocket.py`

---

## 7단계: Frontend 테스트 환경 및 기본 구조

### 환경 설정
- [ ] `packages/frontend/package.json` - 의존성 설정
- [ ] `packages/frontend/vite.config.ts`
- [ ] `packages/frontend/vitest.config.ts`
- [ ] `packages/frontend/tailwind.config.js`
- [ ] `packages/frontend/tsconfig.json`

### 기본 구조
- [ ] `packages/frontend/src/main.tsx`
- [ ] `packages/frontend/src/App.tsx` - React Router 설정
- [ ] `packages/frontend/src/types/index.ts` - TypeScript 타입 정의

---

## 8단계: Frontend API 클라이언트 (TDD)

### 테스트 케이스
- [ ] `client.test.ts` - 인터셉터 토큰 추가
- [ ] `client.test.ts` - 401 응답 시 리다이렉트
- [ ] `useAuth.test.ts` - 로그인 시 토큰 저장
- [ ] `useAuth.test.ts` - 로그아웃 시 토큰 제거
- [ ] `useWebSocket.test.ts` - WebSocket 연결/메시지

### 구현
- [ ] `packages/frontend/src/api/__tests__/client.test.ts`
- [ ] `packages/frontend/src/api/client.ts`
- [ ] `packages/frontend/src/hooks/__tests__/useAuth.test.ts`
- [ ] `packages/frontend/src/hooks/useAuth.ts`
- [ ] `packages/frontend/src/hooks/__tests__/useWebSocket.test.ts`
- [ ] `packages/frontend/src/hooks/useWebSocket.ts`

---

## 9단계: Frontend UI 컴포넌트 (TDD)

### Login
- [ ] `Login.test.tsx` - 폼 렌더링
- [ ] `Login.test.tsx` - 로그인 API 호출
- [ ] `Login.test.tsx` - 에러 메시지 표시
- [ ] `packages/frontend/src/pages/Login.tsx`

### Layout
- [ ] `packages/frontend/src/components/Layout.tsx`

### Dashboard
- [ ] `Dashboard.test.tsx` - 진행 중 작업 표시
- [ ] `Dashboard.test.tsx` - 최근 히스토리 표시
- [ ] `packages/frontend/src/pages/Dashboard.tsx`

### NewMigration
- [ ] `NewMigration.test.tsx` - 폼 렌더링
- [ ] `packages/frontend/src/pages/NewMigration.tsx`

### ConnectionForm
- [ ] `ConnectionForm.test.tsx` - 연결 테스트 동작
- [ ] `ConnectionForm.test.tsx` - 성공/실패 메시지
- [ ] `packages/frontend/src/components/ConnectionForm.tsx`

### TableSelector
- [ ] `TableSelector.test.tsx` - 체크박스 렌더링
- [ ] `TableSelector.test.tsx` - 선택 상태 변경
- [ ] `packages/frontend/src/components/TableSelector.tsx`

### FilterConfig
- [ ] `FilterConfig.test.tsx` - WHERE 조건 입력
- [ ] `FilterConfig.test.tsx` - 컬럼 선택 UI
- [ ] `packages/frontend/src/components/FilterConfig.tsx`

### MigrationProgress
- [ ] `MigrationProgress.test.tsx` - 진행률 바 표시
- [ ] `MigrationProgress.test.tsx` - WebSocket 메시지 반영
- [ ] `packages/frontend/src/components/MigrationProgress.tsx`

### History
- [ ] `History.test.tsx` - 히스토리 목록 표시
- [ ] `packages/frontend/src/pages/History.tsx`

### Schedules
- [ ] `Schedules.test.tsx` - 스케줄 목록/생성/삭제
- [ ] `packages/frontend/src/pages/Schedules.tsx`

---

## 완료된 항목

### 초기 설정 (완료)
- [x] 프로젝트 구조 설정
- [x] 기존 exporter.py, importer.py, cli.py 이동
- [x] README.md 작성
- [x] TODO.md 작성
