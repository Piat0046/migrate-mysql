# MySQL Migration Tool - Frontend

React + TypeScript 기반 프론트엔드

## 기술 스택

- **React 18** - UI 라이브러리
- **TypeScript** - 타입 안정성
- **Vite** - 빌드 도구
- **TailwindCSS** - 스타일링
- **React Query** - 서버 상태 관리
- **React Router** - 라우팅
- **Vitest** - 테스트
- **React Testing Library** - 컴포넌트 테스트

## 설치

```bash
npm install
```

## 실행

### 개발 서버

```bash
npm run dev
```

### 빌드

```bash
npm run build
```

### 미리보기

```bash
npm run preview
```

## 환경 변수

```bash
# .env 파일 생성
VITE_API_URL=http://localhost:8000
```

## 테스트

```bash
# 전체 테스트
npm run test

# Watch 모드
npm run test:watch

# 커버리지
npm run test:coverage
```

## 프로젝트 구조

```
packages/frontend/
├── package.json
├── vite.config.ts
├── vitest.config.ts
├── tailwind.config.js
├── tsconfig.json
├── index.html
└── src/
    ├── main.tsx
    ├── App.tsx
    ├── index.css
    │
    ├── api/
    │   ├── client.ts              # Axios 인스턴스
    │   └── __tests__/
    │       └── client.test.ts
    │
    ├── hooks/
    │   ├── useAuth.ts             # 인증 상태 관리
    │   ├── useWebSocket.ts        # WebSocket 연결
    │   └── __tests__/
    │       ├── useAuth.test.ts
    │       └── useWebSocket.test.ts
    │
    ├── components/
    │   ├── Layout.tsx             # 공통 레이아웃
    │   ├── ConnectionForm.tsx     # DB 연결 폼
    │   ├── TableSelector.tsx      # 테이블 선택
    │   ├── FilterConfig.tsx       # 필터 설정
    │   ├── MigrationProgress.tsx  # 진행률 표시
    │   └── __tests__/
    │       ├── ConnectionForm.test.tsx
    │       ├── TableSelector.test.tsx
    │       ├── FilterConfig.test.tsx
    │       └── MigrationProgress.test.tsx
    │
    ├── pages/
    │   ├── Login.tsx              # 로그인
    │   ├── Dashboard.tsx          # 대시보드
    │   ├── NewMigration.tsx       # 새 마이그레이션
    │   ├── History.tsx            # 히스토리
    │   ├── Schedules.tsx          # 스케줄 관리
    │   └── __tests__/
    │       ├── Login.test.tsx
    │       ├── Dashboard.test.tsx
    │       ├── NewMigration.test.tsx
    │       ├── History.test.tsx
    │       └── Schedules.test.tsx
    │
    └── types/
        └── index.ts               # TypeScript 타입 정의
```

## 페이지 구조

### 로그인 (`/login`)
- 사용자 인증
- JWT 토큰 저장

### 대시보드 (`/`)
- 진행 중인 마이그레이션 현황
- 최근 히스토리
- 빠른 작업 버튼

### 새 마이그레이션 (`/migrations/new`)
1. **소스 DB 연결** - 호스트, 포트, 사용자, 비밀번호, 데이터베이스
2. **테이블 선택** - 체크박스로 테이블 선택
3. **필터 설정** - WHERE 조건, 컬럼 선택
4. **대상 DB 연결** (Import 시)
5. **실행** - Export/Import 시작

### 히스토리 (`/history`)
- 마이그레이션 기록 목록
- 상세 정보 조회
- 페이지네이션

### 스케줄 (`/schedules`)
- 스케줄 목록
- 스케줄 생성/삭제
- Cron 표현식 입력

## 컴포넌트

### Layout
공통 레이아웃 (사이드바, 헤더)

### ConnectionForm
DB 연결 정보 입력 및 테스트

```tsx
<ConnectionForm
  onConnectionSuccess={(tables) => setTables(tables)}
  onConnectionError={(error) => setError(error)}
/>
```

### TableSelector
테이블 목록에서 선택

```tsx
<TableSelector
  tables={tables}
  selected={selectedTables}
  onChange={setSelectedTables}
/>
```

### FilterConfig
테이블별 필터 설정

```tsx
<FilterConfig
  table="users"
  columns={columns}
  onFilterChange={(filter) => updateFilter(table, filter)}
/>
```

### MigrationProgress
실시간 진행률 표시

```tsx
<MigrationProgress
  migrationId={migrationId}
  onComplete={() => navigate('/history')}
/>
```

## 상태 관리

### React Query
서버 데이터 캐싱 및 동기화

```tsx
const { data: history } = useQuery({
  queryKey: ['history'],
  queryFn: () => api.get('/api/history'),
});
```

### useAuth Hook
인증 상태 관리

```tsx
const { user, login, logout, isAuthenticated } = useAuth();
```

### useWebSocket Hook
WebSocket 연결 관리

```tsx
const { status, progress } = useWebSocket(migrationId);
```
