# Team SEO Agents cho Claude Code — BTVN Buổi 3 (+ nâng cấp Agents)

Không gian làm việc cá nhân gồm **2 sub-agents × 5 skills** phục vụ quy trình SEO khép kín:
**nghiên cứu từ khóa → audit on-page → phân tích backlink → chọn site đi link → viết bài đi link**.

## Kiến trúc team
```
Claude Code (orchestrator — nhận 1 nhiệm vụ lớn, tự phân bổ)
├── technical-seo-auditor  (Kỹ thuật SEO)
│   ├── onpage-audit          # Audit on-page 1 URL + Core Web Vitals
│   ├── backlink-analyzer     # Phân tích file Ahrefs Referring Domains
│   └── backlink-prospector   # Chấm điểm chọn site NÊN đi backlink (tiêu chí + ngân sách)
└── content-seo-strategist (Content SEO)
    ├── keyword-expand        # Mở rộng từ khóa (Google Autocomplete/KeywordTool API)
    └── backlink-article-writer  # Viết bài guest post/PR chèn link chuẩn anchor
```

**Ví dụ nhiệm vụ lớn (giao 1 câu, agents tự chia việc):**
> "Xây chiến dịch backlink cho website X thuộc ngành du lịch, ngân sách 3 triệu/link:
> audit on-page trang chủ, phân tích hồ sơ backlink hiện tại (file Ahrefs đính kèm),
> chọn danh sách site nên đi link từ file ứng viên của tôi, và viết sẵn 2 bài guest post
> cho 2 site tốt nhất."

→ `technical-seo-auditor` lo audit + phân tích + chấm site; `content-seo-strategist` lo
từ khóa + viết bài với anchor trỏ về các trang đích.

## Cấu trúc thư mục
```
.claude/
├── agents/                # 2 sub-agents (frontmatter + system prompt)
└── skills/                # 5 skills (mỗi skill: SKILL.md + file bổ trợ)
outputs/                   # Kết quả chạy skill (data thật bị gitignore)
```

⚠️ **Quy tắc dữ liệu:** skills chỉ chứa LOGIC. Data nội bộ (bảng giá vendor, export Ahrefs
khách hàng) do người dùng tự cung cấp lúc chạy và KHÔNG được commit — `.gitignore` đã chặn
`outputs/*.csv|xlsx|json`. File `sample-*` trong skill là dữ liệu giả để demo.

## 1. `keyword-expand`
Nhận từ khóa hạt nhân (hoặc 1 domain) → mở rộng thành nhiều từ khóa gợi ý → xuất Excel.
- **Kết nối ngoài:** Google Autocomplete (free) hoặc KeywordTool.io API (có volume).
- File bổ trợ: `expand.py`, `analyze_domain.py`, `config.json`.
- Gọi: `/keyword-expand` hoặc mô tả nhu cầu research từ khóa.

## 2. `onpage-audit`
Nhận 1 URL → crawl trang, đối chiếu checklist SEO on-page, đo Core Web Vitals → báo cáo có
Health Score + vấn đề theo mức ưu tiên.
- **Kết nối ngoài:** Google PageSpeed Insights API.
- File bổ trợ: `checklist/onpage-criteria.md`, `rules/scoring-rules.md`, `templates/report-template.md`.
- Script `audit.py` chỉ dùng thư viện chuẩn Python.
- Có PageSpeed API key thì thêm `--psi-key` để tránh rate-limit (429).

## 3. `backlink-analyzer`
Nhận file **Ahrefs Referring Domains export** (1 hoặc nhiều site) → phân tích chất lượng DR, tỷ lệ
dofollow/nofollow, cảnh báo domain độc/spam, Link Gap so với đối thủ → xuất Excel nhiều sheet + Markdown.
- File bổ trợ: `config/ahref-columns.md`, `rules/backlink-quality-rules.md`, `templates/backlink-report-template.md`.
- Script `analyze_backlinks.py` cần `openpyxl` (tự dò UTF-16/tab của Ahrefs).

## 4. `backlink-prospector`
Nhận file CSV **danh sách domain ứng viên do người dùng cung cấp** (bảng giá vendor, link-gap...) →
chấm theo 3 tiêu chí bắt buộc + 5 tiêu chí cộng điểm → xếp hạng "Nên tiếp cận / Cân nhắc / Loại"
kèm lý do, có lọc ngân sách (`--budget`) và ngành (`--industry`).
- File bổ trợ: `rules/prospect-criteria.md`, `sample-candidates.csv` (data giả demo).
- Script `prospect.py` chỉ dùng thư viện chuẩn.

## 5. `backlink-article-writer`
Viết bài guest post/PR để đi backlink: chèn 1–2 link về URL đích với anchor tự nhiên, chống
over-optimization, giọng văn khớp site đăng. Skill thuần LLM (không script).
- File bổ trợ: `rules/anchor-rules.md`, `templates/article-template.md`.

## Yêu cầu môi trường
- Python 3.7+
- `pip3 install openpyxl` (cho keyword-expand & backlink-analyzer)
- (Tùy chọn) PageSpeed API key cho onpage-audit — biến môi trường `PAGESPEED_API_KEY` hoặc `--psi-key`.

## Chạy thử nhanh
```bash
python3 .claude/skills/onpage-audit/audit.py "https://example.com" --no-psi --json outputs/onpage.json
python3 .claude/skills/backlink-analyzer/analyze_backlinks.py "ahrefs-export.csv" --out outputs/backlink.xlsx --json outputs/backlink.json
```
