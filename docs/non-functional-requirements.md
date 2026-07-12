# 3. Non-Functional Requirements (NFR)

Ngữ cảnh: **dự án học tập / portfolio**, chạy single-machine, PostgreSQL local. NFR được đặt **thực tế** với scale seed tới 1M rows, không giả vờ hệ thống production enterprise.

---

## 3.1 Performance

| ID | Yêu cầu | Mục tiêu đo |
|----|---------|-------------|
| NFR-PERF-01 | Dashboard load KPI với filter mặc định (30 ngày) | < 3s trên dataset 100K orders (local SSD) |
| NFR-PERF-02 | Top-N & monthly trend queries | < 2s với index phù hợp ở 100K–1M order_items |
| NFR-PERF-03 | ETL load batch 10K rows | < 30s (insert multi-row / copy khi phù hợp) |
| NFR-PERF-04 | Seed 100K scale | hoàn tất trong thời gian chấp nhận được (< 10 phút máy dev trung bình) |
| NFR-PERF-05 | Tránh N+1 | Repository dùng join/selectinload có chủ đích; dashboard query aggregate ở SQL |

### Chiến lược

- Index trên FK và cột filter/report (`order_date`, `store_id`, `customer_id`, …)
- Composite index cho pattern phổ biến: `(store_id, order_date)`, `(product_id, order_date)`
- Aggregate nặng ưu tiên **SQL** thay vì load full frame pandas
- Streamlit `@st.cache_data` cho query theo filter key
- EXPLAIN ANALYZE trong phase SQL Optimization

### Không cam kết

- Sub-second concurrent multi-user
- Horizontal scaling

---

## 3.2 Security

Phạm vi portfolio — **đủ an toàn local**, không pretent SOC2.

| ID | Yêu cầu |
|----|---------|
| NFR-SEC-01 | Credentials DB chỉ qua `.env`, không commit secret |
| NFR-SEC-02 | `.env.example` không chứa password thật |
| NFR-SEC-03 | SQLAlchemy/psycopg parameterized queries — **cấm** f-string SQL với input user |
| NFR-SEC-04 | Streamlit không expose raw exception stack cho end-user (log server-side) |
| NFR-SEC-05 | File import: validate path trong thư mục `data/` cho phép; reject path traversal |
| NFR-SEC-06 | Không log PII đầy đủ (mask email/phone trong log nếu cần) |

### Out of scope security

- OAuth, JWT, encryption at rest nâng cao, WAF

---

## 3.3 Reliability

| ID | Yêu cầu |
|----|---------|
| NFR-REL-01 | ETL mỗi batch trong transaction; fail → rollback batch, ghi reject |
| NFR-REL-02 | Migration Alembic reversible (downgrade) cho mọi revision chính |
| NFR-REL-03 | Idempotent seed/ETL ở mức document: clear-and-reload hoặc upsert theo natural key |
| NFR-REL-04 | CLI exit code ≠ 0 khi lỗi nghiêm trọng |
| NFR-REL-05 | Dashboard handle empty dataset (message thân thiện, không crash) |

---

## 3.4 Scalability

| ID | Yêu cầu | Cách tiếp cận |
|----|---------|----------------|
| NFR-SCL-01 | Hỗ trợ scale seed 100 → 1M | Generator batch, bulk insert |
| NFR-SCL-02 | Query plan ổn ở 1M order_items | Index + tránh SELECT * |
| NFR-SCL-03 | Code không phụ thuộc “load all into memory” cho report lớn | Chunking / SQL aggregate |

**Giới hạn có chủ đích:** single PostgreSQL instance, single process ETL, không sharding.

---

## 3.5 Maintainability

| ID | Yêu cầu |
|----|---------|
| NFR-MNT-01 | Cấu trúc package rõ (config, db, models, repositories, services, …) |
| NFR-MNT-02 | Type hints + mypy (strict vừa phải, cấu hình trong pyproject) |
| NFR-MNT-03 | Ruff + Black format |
| NFR-MNT-04 | Metric definitions tập trung (một module) |
| NFR-MNT-05 | Docs trong `docs/` đồng bộ với implementation khi phase xong |
| NFR-MNT-06 | SQL files có naming convention và catalog index |

---

## 3.6 Data Quality

| ID | Yêu cầu |
|----|---------|
| NFR-DQ-01 | DB constraints: NOT NULL, CHECK, UNIQUE, FK |
| NFR-DQ-02 | Pydantic models cho inbound ETL rows |
| NFR-DQ-03 | Business rules: order total ≈ sum(items) ± tolerance; payment ≤ order total (policy) |
| NFR-DQ-04 | Reject file/log cho invalid rows; không im lặng drop |
| NFR-DQ-05 | Referential integrity: không orphan order_items |
| NFR-DQ-06 | Soft delete: query mặc định `deleted_at IS NULL` ở repository |
| NFR-DQ-07 | Timestamps `created_at`/`updated_at` tự set |
| NFR-DQ-08 | Seed data realistic distributions (không uniform 100%) |

### Data quality metrics (đo được)

- % rows rejected per ETL run  
- Count orphan checks = 0  
- Count negative quantities (invalid) = 0  
- Duplicate natural keys = 0  

---

## 3.7 Logging

| ID | Yêu cầu |
|----|---------|
| NFR-LOG-01 | loguru: console + rotating file `logs/app.log` |
| NFR-LOG-02 | Levels: DEBUG/INFO/WARNING/ERROR |
| NFR-LOG-03 | ETL log: source file, rows read/valid/rejected/loaded, duration |
| NFR-LOG-04 | SQL slow query optional log threshold (config) |
| NFR-LOG-05 | Structured message format có timestamp, module, level |

---

## 3.8 Error Handling

| ID | Yêu cầu |
|----|---------|
| NFR-ERR-01 | Exception hierarchy dự án (DomainError, ValidationError, DatabaseError, ETLError) |
| NFR-ERR-02 | CLI catch top-level, log + user-friendly message |
| NFR-ERR-03 | Dashboard: try/except quanh data load; `st.error` |
| NFR-ERR-04 | Không nuốt exception im lặng (`except: pass` cấm) |
| NFR-ERR-05 | DB connection errors có retry đơn giản (optional P2) hoặc fail-fast rõ ràng |

---

## 3.9 Usability (Dashboard & CLI)

| ID | Yêu cầu |
|----|---------|
| NFR-UX-01 | Dashboard sidebar filters luôn visible |
| NFR-UX-02 | Loading spinners cho query > 0.5s |
| NFR-UX-03 | CLI help text đầy đủ (`--help`) |
| NFR-UX-04 | README root hướng dẫn setup PostgreSQL + run demo |

---

## 3.10 Compatibility

| ID | Yêu cầu |
|----|---------|
| NFR-CMP-01 | Python 3.13+ |
| NFR-CMP-02 | PostgreSQL 15+ (khuyến nghị 16) |
| NFR-CMP-03 | OS: Linux (primary); macOS/Windows dev best-effort |
| NFR-CMP-04 | UTF-8 everywhere; timezone policy documented (store `TIMESTAMP WITH TIME ZONE` hoặc naive UTC — chốt trong DB design) |

---

## 3.11 Testability

| ID | Yêu cầu |
|----|---------|
| NFR-TST-01 | Unit test pure functions (cleaning, metrics) không cần DB |
| NFR-TST-02 | Integration test với PostgreSQL test DB hoặc transactional fixtures |
| NFR-TST-03 | Fixtures nhỏ deterministic cho SQL metric tests |
| NFR-TST-04 | Coverage mục tiêu core services ≥ 70% (không phải vanity 100%) |

---

## 3.12 Documentation quality

| ID | Yêu cầu |
|----|---------|
| NFR-DOC-01 | Mỗi phase có deliverables rõ trong roadmap |
| NFR-DOC-02 | ERD + schema mô tả trong `database-design.md` |
| NFR-DOC-03 | SQL catalog index trong `sql-roadmap.md` |

---

## 3.13 Tóm tắt trade-offs

| Chọn | Đánh đổi |
|------|----------|
| 3NF operational schema | Report có thể cần nhiều join (bù bằng view/SQL tốt) |
| Không Docker | Setup DB thủ công, portability kém hơn |
| Streamlit | Nhanh cho BI demo, không phải multi-page app enterprise |
| Single process ETL | Đơn giản, không parallel heavy |
| Soft delete master | Query phải nhớ filter deleted_at |
