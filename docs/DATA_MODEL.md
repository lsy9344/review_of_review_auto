## 데이터 모델 (SQLite)

### 스키마
- `stores(store_id TEXT PRIMARY KEY, name TEXT)`
- `reviews(review_id TEXT, store_id TEXT, created_at TEXT, rating INT, text TEXT, has_owner_reply INT, UNIQUE(review_id, store_id))`
- `submissions(review_id TEXT, store_id TEXT, status TEXT, error TEXT, created_at TEXT)`
- `runs(run_id TEXT PRIMARY KEY, started_at TEXT, mode TEXT, success INT, fail INT, skipped INT)`

### 액세스 패턴
- 리뷰 upsert로 중복 방지
- 제출 성공 시 `submissions`에 기록하고 재시도 시 참조하여 스킵
- 실행마다 `runs`에 요약 카운트 기록

### 인덱스 제안
- `reviews(store_id, created_at)` 복합 인덱스
- `submissions(store_id, review_id)`

