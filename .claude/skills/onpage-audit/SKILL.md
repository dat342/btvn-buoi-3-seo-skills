---
name: onpage-audit
description: Audit SEO on-page cho MỘT URL — crawl trang, đối chiếu checklist chuẩn, đo Core Web Vitals qua Google PageSpeed API, rồi xuất báo cáo Markdown. Kích hoạt khi user muốn "audit onpage", "kiểm tra SEO trang", "phân tích on-page", "check SEO cho URL", "soi title/meta/heading/schema", "đo Core Web Vitals", HOẶC dán một URL và muốn biết trang có vấn đề SEO on-page gì.
---

# Onpage Audit

Skill này audit **on-page SEO cho 1 URL**: chạy script `audit.py` để crawl trang và trích tín
hiệu SEO, gọi **Google PageSpeed Insights API** cho Core Web Vitals, rồi đối chiếu bộ checklist
để viết **báo cáo Markdown** có Health Score + danh sách vấn đề theo mức ưu tiên.

Chỉ dùng thư viện chuẩn của Python — KHÔNG cần cài thêm.

## File bổ trợ (load-on-demand — chỉ đọc khi tới bước dùng)
- `audit.py` — script crawl 1 URL + gọi PageSpeed, in JSON. **Luôn chạy** ở Bước 1.
- `checklist/onpage-criteria.md` — bộ tiêu chí kiểm được từ 1 URL (chắt lọc từ checklist chuẩn
  `seo-audit`). **Đọc ở Bước 2** để biết field nào ứng với tiêu chí nào.
- `rules/scoring-rules.md` — ngưỡng pass/warn/fail + cách tính Health Score. **Đọc ở Bước 2**.
- `templates/report-template.md` — khung báo cáo. **Đọc ở Bước 3** để dựng output.

## Quy trình

### Bước 0 — Lấy URL
Nếu user chưa đưa URL, hỏi:
> Bạn muốn audit on-page cho URL nào? Dán link đầy đủ (vd https://example.com/san-pham).

Hỏi thêm (tùy chọn): có cần đo PageSpeed không (mặc định có; cần mạng). Nếu user có
**PageSpeed API key** thì dùng `--psi-key` để tránh rate-limit.

### Bước 1 — Chạy crawl
```
python3 ".claude/skills/onpage-audit/audit.py" "<URL>" --json outputs/onpage-<slug>.json
```
- Bỏ PageSpeed: thêm `--no-psi` (nhanh, không cần mạng ra Google).
- Có key: thêm `--psi-key <KEY>` (hoặc đặt env `PAGESPEED_API_KEY`).
- Script in `[✓]` khi xong. Nếu `errors` không rỗng → xem bảng lỗi bên dưới.

### Bước 2 — Đối chiếu checklist & chấm điểm
1. ĐỌC `checklist/onpage-criteria.md` và `rules/scoring-rules.md`.
2. Đọc JSON vừa tạo. Với mỗi tiêu chí, map sang `field` tương ứng, gán **pass/warn/fail/n/a**
   theo ngưỡng trong scoring-rules.
3. Tính **Health Score /100**. Nếu thiếu dữ liệu PageSpeed → loại nhóm speed khỏi mẫu số và ghi
   "INSUFFICIENT DATA cho Page Speed" (KHÔNG bịa số CWV).
4. Phân loại vấn đề thành Critical / High / Medium.

### Bước 3 — Xuất báo cáo
1. ĐỌC `templates/report-template.md`, điền dữ liệu thực tế.
2. Ghi ra `outputs/onpage-<slug>.md`. Nếu user muốn `.docx` → dùng skill xuất Word.
3. Báo user: Health Score, số vấn đề Critical/High, đường dẫn báo cáo.

## Tiêu chí chất lượng — Agent tự kiểm trước khi giao (Pre-Delivery Review)
Chạy checklist này TRƯỚC khi giao báo cáo:
- [ ] **JSON có dữ liệu thật**: `status_code` = 200 và `title`/`headings` không rỗng. Nếu status
      ≠ 200 → báo user URL lỗi/redirect, KHÔNG viết báo cáo dựa trên trang lỗi.
- [ ] **Mọi tiêu chí có trạng thái**: không bỏ trống; field thiếu → `n/a` + nêu lý do.
- [ ] **Không bịa số**: mọi con số trong báo cáo truy được về JSON hoặc PageSpeed. CWV thiếu →
      ghi INSUFFICIENT DATA, không đoán.
- [ ] **Critical đúng nghĩa**: chỉ xếp Critical cho tiêu chí `mandatory` đang fail.
- [ ] **Khắc phục cụ thể**: mỗi vấn đề có hành động rõ ràng, không chung chung ("tối ưu SEO").
- [ ] **Nêu phần ngoài phạm vi**: báo cáo có mục "cần kiểm bổ sung" (duplicate toàn site, log...).
- [ ] **File tồn tại**: báo cáo `.md` đã ghi ra `outputs/`, dung lượng > 0.

## Lỗi thường gặp — "vết xe đổ"
| Lỗi | Nguyên nhân | Cách xử lý |
|---|---|---|
| `HTTPError 403/429` khi fetch | Site chặn bot theo User-Agent | Thử lại; nếu vẫn chặn, báo user site chặn crawl, không bịa dữ liệu. |
| `status_code` = 301/302 | URL redirect | Script tự theo redirect; kiểm `final_url` — nếu khác domain, xác nhận với user. |
| PageSpeed trả `HTTP 429` | Rate-limit khi không có API key | Thêm `--psi-key`; hoặc `--no-psi` và ghi INSUFFICIENT DATA cho speed. |
| `word_count` rất thấp (<100) | Trang render bằng JS (SPA) | Ghi cảnh báo js_01 fail — nội dung phụ thuộc JS, khó cho Googlebot. |
| `structured_data_valid` = false | JSON-LD lỗi cú pháp | Báo struct_11 fail, nêu cần sửa schema. |
| Ảnh alt = 0 nhưng site có ảnh nền CSS | Ảnh nền không tính `<img>` | Bình thường; chỉ chấm ảnh `<img>` nội dung. |
| `ModuleNotFoundError` | Không xảy ra — script chỉ dùng stdlib | Nếu gặp, kiểm Python ≥ 3.7. |
| Timeout khi fetch | Mạng chậm / site chậm | Thử lại; TTFB cao cũng là 1 phát hiện (domain_03 warn/fail). |

## Định dạng đầu ra
- `outputs/onpage-<slug>.json` — dữ liệu thô (bằng chứng, minh bạch).
- `outputs/onpage-<slug>.md` — báo cáo theo `templates/report-template.md`: Tóm tắt → vấn đề theo
  ưu tiên (Critical/High/Medium) → bảng chi tiết theo nhóm → Page Speed → phần cần kiểm bổ sung.
