# Bộ Skills SEO cho Claude Code — BTVN Buổi 3

Không gian làm việc cá nhân gồm **3 Claude Code skills** phục vụ quy trình SEO, nối thành 1 luồng:
**nghiên cứu từ khóa → audit on-page → phân tích backlink**.

## Cấu trúc
```
.claude/skills/
├── keyword-expand/        # Mở rộng từ khóa SEO → xuất Excel (kết nối API ngoài)
├── onpage-audit/          # Audit on-page 1 URL + Core Web Vitals → báo cáo Markdown
└── backlink-analyzer/     # Phân tích file Ahrefs Referring Domains → Excel + Markdown
outputs/                   # Kết quả các lần chạy thử skill
```

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

## Yêu cầu môi trường
- Python 3.7+
- `pip3 install openpyxl` (cho keyword-expand & backlink-analyzer)
- (Tùy chọn) PageSpeed API key cho onpage-audit — biến môi trường `PAGESPEED_API_KEY` hoặc `--psi-key`.

## Chạy thử nhanh
```bash
python3 .claude/skills/onpage-audit/audit.py "https://example.com" --no-psi --json outputs/onpage.json
python3 .claude/skills/backlink-analyzer/analyze_backlinks.py "ahrefs-export.csv" --out outputs/backlink.xlsx --json outputs/backlink.json
```
