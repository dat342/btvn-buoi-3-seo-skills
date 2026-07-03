---
name: keyword-expand
description: Mở rộng/đề xuất từ khóa SEO rồi xuất Excel. Kích hoạt khi user muốn "mở rộng từ khóa", "tìm từ khóa gợi ý", "keyword suggestions", "research từ khóa", "nghiên cứu từ khóa SEO", HOẶC đưa một domain/website và muốn "tự đề xuất từ khóa", "gợi ý từ khóa cho website/domain này". Nguồn free (Google Autocomplete) hoặc KeywordTool.io (có volume).
---

# Keyword Expand (Bước 1)

Skill này nhận một hoặc nhiều **từ khóa hạt nhân** do user gõ trực tiếp, mở rộng thành nhiều
**từ khóa gợi ý**, rồi xuất ra một file **Excel**. Không lọc, không bước 2.

Có **2 nguồn dữ liệu** (chọn bằng `--source` hoặc trường `source` trong config.json):

- **`google`** (MẶC ĐỊNH, free): Google Autocomplete. Không cần key, không tốn tiền.
  Chỉ trả **từ khóa gợi ý** (không có volume). Đào sâu bằng hậu tố a–z (`--depth 1`).
- **`keywordtool`**: KeywordTool.io. Có **search volume + CPC + lịch sử 12 tháng** nhưng
  cần API key trả phí.

Script: `expand.py` (chỉ dùng thư viện chuẩn + openpyxl, không cần cài thêm).
Cấu hình: `config.json` đặt cạnh script.

## Chế độ A — User đưa DOMAIN (tự đề xuất từ khóa hạt nhân)

Khi user đưa một **domain/URL website** và muốn skill tự đề xuất từ khóa, làm theo các bước:

1. **Phân tích website** — chạy:
   ```
   python3 ~/.claude/skills/keyword-expand/analyze_domain.py <domain> --max-pages 6
   ```
   Script cào trang chủ + vài trang từ sitemap, in JSON gồm: `site_name`, `title`/`description`/
   `keywords` mỗi trang, các heading, và mảng `candidates` (cụm từ ứng viên theo tần suất).

2. **Tinh chỉnh seed (KẾT HỢP)** — ĐỌC kỹ JSON đó. Dựa vào `title`, `description`, `og_title`,
   các heading và `candidates`, tự đề xuất **5–15 từ khóa hạt nhân** sạch, đúng ngành/sản phẩm
   chính của website. Bỏ mục điều hướng (giỏ hàng, liên hệ, tên chi nhánh/showroom, mạng xã hội).
   Đặt seed theo cách người Việt tìm kiếm (vd "laptop gaming", "linh kiện máy tính"), không chỉ
   copy nguyên cụm trên web.

3. **DỪNG cho user duyệt** — trình bày danh sách seed đề xuất, hỏi:
   > Đây là các từ khóa hạt nhân mình đề xuất từ website. Bạn muốn **giữ/bớt/thêm** gì không?
   > Duyệt xong mình sẽ mở rộng từng từ thành hàng trăm từ khóa.
   ĐỢI user xác nhận/sửa. KHÔNG tự mở rộng trước khi user duyệt.

4. **Mở rộng** — sau khi user chốt, chạy `expand.py` với danh sách seed đã duyệt (xem Chế độ B,
   Bước 2). Mặc định nguồn `google` (free).

## Chế độ B — User gõ thẳng từ khóa hạt nhân

### Bước 0 — Chọn nguồn / kiểm tra key
Mặc định dùng `google` (free) — chạy được ngay, KHÔNG cần hỏi key. Chỉ khi user muốn **số liệu
volume thật** mới chuyển sang `keywordtool` và đọc `config.json`. Nếu lúc đó `api_key` rỗng:

> 🔑 Cần API key của KeywordTool.io (dịch vụ trả phí — không có key miễn phí công khai).
> Lấy key tại: https://keywordtool.io/ → tài khoản → API.
> Bạn dán key vào đây để mình lưu vào `config.json` nhé (lần sau tự dùng lại).

Khi user đưa key → ghi vào trường `api_key` của `config.json`.

Mặc định `mode: "sandbox"` (rẻ nhất — trả dữ liệu mẫu, không tiêu query credit thật).
Chỉ đổi sang `"production"` khi user muốn số liệu volume **thật** (tốn credit).

### Bước 1 — Hỏi từ khóa hạt nhân
Nếu user chưa cung cấp, hỏi:
> Bạn muốn mở rộng (các) từ khóa nào? Gõ trực tiếp, cách nhau bằng dấu phẩy hoặc xuống dòng.

### Bước 2 — Chạy script
Gọi:
```
python3 ~/.claude/skills/keyword-expand/expand.py \
  --keywords "từ khóa 1" "từ khóa 2" \
  --out <đường-dẫn-output>.xlsx
```
- Nhiều từ khóa: mỗi từ là một tham số trong `--keywords` (đặt trong dấu nháy).
- Đặt `--out` ở thư mục làm việc hiện tại của user, tên gợi nhớ theo từ khóa.
- Mặc định nguồn `google` (free). Thêm `--source keywordtool` (+ `--mode production`) nếu user
  cần volume thật.
- `--depth 0` chạy nhanh (chỉ gợi ý gốc), `--depth 1` (mặc định) đào sâu thêm a–z → nhiều từ hơn.
- Có thể dùng `--file seed.txt` thay cho `--keywords` nếu user đưa file danh sách.

### Bước 3 — Báo kết quả
Đọc dòng `[✓]` từ output: số từ khóa thu được, đường dẫn file.
Báo cho user và đưa link file Excel. Nếu KeywordTool báo *"API key invalid"* → quay lại Bước 0 xin key mới.

## Cấu trúc file Excel
Mỗi dòng là một từ khóa gợi ý: `Original Keyword`, `Suggested Keyword`. Với nguồn `keywordtool`
có thêm `volume`, `cpc`, `cmp`, `trend` + lịch sử 12 tháng (`m1..m12`). Cột rỗng tự động bị ẩn.
Có sẵn auto-filter + freeze header.

## Lưu ý
- Nguồn `google`: mỗi seed gọi ~37 lượt autocomplete (1 gốc + 36 hậu tố), free, đã bỏ trùng.
- Nguồn `keywordtool`: tự xử lý cả 2 kiểu cấu trúc `results` (dict/list). Volume chỉ gọi bổ sung
  cho từ chưa có metrics inline (tiết kiệm gọi API).

## Tiêu chí chất lượng — Agent tự kiểm trước khi giao (Pre-Delivery Review)
Chạy checklist này TRƯỚC khi báo kết quả cho user. Nếu tiêu chí nào fail, sửa rồi mới giao —
KHÔNG giao file lỗi rồi mới xin lỗi.

- [ ] **File tồn tại**: đường dẫn `--out` đã được tạo thật (kiểm bằng `ls`), dung lượng > 0.
- [ ] **Có dữ liệu**: file Excel có ≥ 1 dòng từ khóa gợi ý (không phải chỉ header). Nếu 0 dòng →
      báo user seed có thể quá hẹp/sai chính tả, gợi ý seed khác, KHÔNG giao file rỗng.
- [ ] **Không trùng lặp**: các `Suggested Keyword` đã unique (script đã khử trùng — xác nhận lại
      nếu gộp nhiều seed).
- [ ] **Header đúng**: đúng cột theo nguồn (`google` → 2 cột; `keywordtool` → có `volume`, `cpc`...).
- [ ] **Đúng nguồn user yêu cầu**: nếu user cần volume thật mà đang chạy `google`/`sandbox` → cảnh báo
      rõ "đây là dữ liệu không có volume / dữ liệu mẫu", đừng để user hiểu nhầm là số liệu thật.
- [ ] **Seed đã được duyệt** (Chế độ A): không tự mở rộng khi user chưa xác nhận danh sách seed.
- [ ] **Báo cáo minh bạch**: nêu rõ số từ khóa thu được, nguồn dùng, đường dẫn file.

## Lỗi thường gặp — "vết xe đổ"
| Lỗi | Nguyên nhân | Cách xử lý |
|---|---|---|
| `ModuleNotFoundError: openpyxl` | Máy chưa cài openpyxl | Chạy `pip3 install openpyxl` rồi chạy lại. |
| File Excel 0 dòng (chỉ header) | Seed quá hẹp, sai chính tả, hoặc ngành quá ngách | Đề xuất seed rộng hơn / đúng chính tả; thử `--depth 1`. Không giao file rỗng. |
| Autocomplete trả rỗng / bị chặn tạm | Google rate-limit khi gọi quá nhiều seed liên tục | Giảm số seed mỗi lần, đợi vài giây rồi chạy lại; hoặc giảm `--depth 0`. |
| `API key invalid` (keywordtool) | Key sai/hết hạn/hết credit | Quay lại Bước 0 xin key mới, ghi lại vào `config.json`. |
| Số liệu volume = 0 hàng loạt | Đang chạy `mode: sandbox` (dữ liệu mẫu) | Đổi `--mode production` (tốn credit) nếu user cần volume thật. |
| `analyze_domain.py` trả `candidates` rỗng | Website chặn crawl, JS-render, hoặc không có sitemap | Xin user cung cấp seed thủ công; hoặc thử `--max-pages` lớn hơn. |
| Domain trả lỗi kết nối / timeout | Site chặn bot hoặc mạng chậm | Thử lại; nếu vẫn fail, chuyển sang Chế độ B (user gõ seed trực tiếp). |
| File `--out` không tạo được | Thư mục đích không tồn tại / không có quyền ghi | Đổi `--out` sang thư mục làm việc hiện tại của user. |
