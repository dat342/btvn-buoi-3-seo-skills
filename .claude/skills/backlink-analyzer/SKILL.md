---
name: backlink-analyzer
description: Phân tích hồ sơ backlink từ file Excel/CSV "Referring Domains" export của Ahrefs — chất lượng DR, tỷ lệ dofollow/nofollow, cảnh báo domain độc/spam, link mới/mất, và Link Gap so với đối thủ — rồi xuất báo cáo Excel + Markdown. Kích hoạt khi user muốn "phân tích backlink", "phân tích ref domain", "kiểm tra backlink độc/spam", "so sánh backlink với đối thủ", "link gap", HOẶC đưa một file Ahrefs referring domains export.
---

# Backlink Analyzer

Nhận **file Ahrefs "Referring Domains" export** (1 hoặc nhiều site), phân tích chất lượng hồ sơ
backlink và xuất **báo cáo Excel nhiều sheet + Markdown**. Nếu có nhiều site + chỉ định site của
mình, tính thêm **Link Gap** (cơ hội xây link từ đối thủ).

Dùng `analyze_backlinks.py` (chỉ cần `openpyxl` — giống skill keyword-expand).

## File bổ trợ (load-on-demand)
- `analyze_backlinks.py` — đọc file Ahrefs, phân tích, xuất xlsx + JSON. **Luôn chạy** ở Bước 2.
- `config/ahref-columns.md` — bảng alias tên cột Ahrefs + quy ước encoding. **Đọc khi** file có
  tên cột lạ / thiếu cột / cần thêm alias.
- `rules/backlink-quality-rules.md` — ngưỡng DR, cờ nghi độc, ngưỡng spam ratio, quy tắc link gap.
  **Đọc ở Bước 3** để diễn giải số liệu.
- `templates/backlink-report-template.md` — khung báo cáo. **Đọc ở Bước 4**.

## Quy trình

### Bước 0 — Nhận file
Nếu user chưa đưa file, hỏi:
> Gửi mình file **Referring Domains export từ Ahrefs** (.csv/.xlsx). Muốn so sánh Link Gap thì
> gửi thêm file của (các) đối thủ và cho biết đâu là file của site bạn.

Ahrefs export thường là **UTF-16, phân tách TAB** dù đuôi `.csv` — script tự dò, không cần convert.

### Bước 1 — (khi cần) Kiểm cột
Nếu nghi file khác định dạng, ĐỌC `config/ahref-columns.md`. Sau khi chạy, nếu output báo
`Thiếu cột` → thêm alias vào cả `config/ahref-columns.md` và `ALIASES` trong script.

### Bước 2 — Chạy phân tích
Một site:
```
python3 ".claude/skills/backlink-analyzer/analyze_backlinks.py" "<file.csv>" \
  --out outputs/backlink-<site>.xlsx --json outputs/backlink-<site>.json
```
Nhiều site + link gap:
```
python3 ".claude/skills/backlink-analyzer/analyze_backlinks.py" \
  "site-cua-minh.csv" "doi-thu-1.csv" "doi-thu-2.csv" \
  --mine "site-cua-minh.csv" \
  --out outputs/backlink-compare.xlsx --json outputs/backlink-compare.json
```
Script in dòng `[✓]` tóm tắt mỗi site. Nếu báo thiếu openpyxl → `pip3 install openpyxl`.

### Bước 3 — Diễn giải theo quy tắc
1. ĐỌC `rules/backlink-quality-rules.md`.
2. Đọc JSON: `toxic_pct`, `dofollow_pct`, `dr_buckets`, `dr_median`, `top_domains`, `top_toxic`,
   `link_gap_top`.
3. Đánh giá: spam ratio thuộc mức nào (bình thường / rà soát / BÁO ĐỘNG >50%); phân bố DR;
   tỷ lệ dofollow; cơ hội link gap (nếu có).

### Bước 4 — Xuất báo cáo
1. ĐỌC `templates/backlink-report-template.md`, điền số liệu thực tế từ JSON.
2. Ghi `outputs/backlink-<site>.md`. File Excel `.xlsx` đã có sẵn từ Bước 2 (dữ liệu chi tiết
   + auto-filter theo từng site + sheet Link Gap).
3. Báo user: tổng ref domain, spam ratio + cảnh báo, số cơ hội link gap, đường dẫn 2 file.

## Tiêu chí chất lượng — Agent tự kiểm trước khi giao (Pre-Delivery Review)
- [ ] **Đọc đúng dữ liệu**: `total_ref_domains` khớp số dòng file (trừ header). Nếu = 0 → file sai
      định dạng/rỗng, báo user, KHÔNG giao báo cáo trống.
- [ ] **Không thiếu cột im lặng**: nếu `columns_missing` khác rỗng → nêu rõ trong báo cáo phần nào
      không đánh giá được, và bổ sung alias nếu chỉ do đổi tên cột.
- [ ] **Số liệu truy được**: mọi % trong báo cáo tính từ JSON, không ước lượng.
- [ ] **Cảnh báo spam đúng ngưỡng**: chỉ ghi "BÁO ĐỘNG" khi toxic_pct > 50% theo rules.
- [ ] **Link Gap đã lọc nghi độc**: không đề xuất đi xin link từ domain rác.
- [ ] **File tồn tại**: cả `.xlsx` và `.md` đã ghi ra `outputs/`, dung lượng > 0.
- [ ] **Khuyến nghị hành động cụ thể**: disavow gì, giữ/khai thác gì — không nói chung chung.

## Lỗi thường gặp — "vết xe đổ"
| Lỗi | Nguyên nhân | Cách xử lý |
|---|---|---|
| Đọc ra 1 cột / dữ liệu dồn 1 ô | Đoán sai delimiter (Ahrefs dùng TAB) | Script tự dò tab/phẩy; nếu vẫn sai, kiểm file có phải TSV. |
| Ký tự lỗi (mojibake) | File UTF-16 bị đọc như UTF-8 | Script thử utf-16 trước; nếu file lạ, kiểm `file <path>`. |
| `columns_missing: ['dr'...]` | Ahrefs đổi tên cột theo gói | Thêm alias vào `config/ahref-columns.md` + `ALIASES` trong script. |
| `ModuleNotFoundError: openpyxl` | Chưa cài openpyxl | `pip3 install openpyxl`. |
| Toxic ratio rất cao (>90%) | Hồ sơ thật sự nhiều link rác (negative SEO) | KHÔNG coi là lỗi — đây là phát hiện; khuyến nghị disavow. |
| Link Gap = None | Chỉ có 1 file hoặc `--mine` không khớp tên site | Cần ≥2 file và `--mine` trùng phần đầu tên file. |
| `dofollow_pct` cao bất thường (~100%) | Bản export chỉ gồm dofollow, hoặc thiếu cột dofollow | Nêu rõ giới hạn dữ liệu trong báo cáo. |

## Định dạng đầu ra
- `outputs/backlink-<site>.xlsx` — Sheet **Summary** (so sánh các site) + sheet **từng site**
  (Domain, DR, Traffic, Dofollow, Toxic, Reason, First seen, Lost; có auto-filter + freeze header)
  + sheet **Link Gap** (nếu có nhiều site).
- `outputs/backlink-<site>.json` — tóm tắt số liệu (bằng chứng cho báo cáo).
- `outputs/backlink-<site>.md` — báo cáo theo template: tổng quan → phân bố DR → top domain →
  cảnh báo nghi độc → link gap → khuyến nghị → ghi chú dữ liệu.
