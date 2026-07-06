---
name: backlink-prospector
description: Chấm điểm và xếp hạng danh sách domain ứng viên để chọn site NÊN đi backlink cho một website — theo 3 tiêu chí bắt buộc (không spam, DR đủ, còn traffic) + 5 tiêu chí cộng điểm (DR cao, traffic tốt, dofollow, không link farm, đúng ngành), có lọc ngân sách. Kích hoạt khi user muốn "tìm site đi backlink", "chọn nơi đặt guest post", "lọc danh sách backlink", "site nào đáng mua link", "chấm điểm domain đi link", HOẶC đưa file bảng giá/danh sách domain và hỏi nên đi link ở đâu.
---

# Backlink Prospector

Nhận **file CSV danh sách domain ứng viên do người dùng cung cấp** (bảng giá vendor, link-gap
export từ backlink-analyzer, hoặc danh sách tự sưu tầm) → chấm theo bộ tiêu chí → xếp hạng
**"Nên tiếp cận" / "Cân nhắc" / "Loại"** kèm lý do từng site.

⚠️ **Quy tắc riêng tư:** skill KHÔNG chứa data. Bảng giá/danh sách nội bộ của user không được
commit lên repo public. File `sample-candidates.csv` là data GIẢ chỉ để demo.

## File bổ trợ (load-on-demand)
- `prospect.py` — script chấm điểm, chỉ dùng thư viện chuẩn. **Luôn chạy** ở Bước 2.
- `rules/prospect-criteria.md` — bộ tiêu chí + ngưỡng + cách xếp loại. **Đọc ở Bước 1 và khi
  diễn giải kết quả** (Bước 3).
- `sample-candidates.csv` — data giả để test khi user chưa có file thật.

## Quy trình

### Bước 0 — Thu thập input (hỏi lần lượt, không dồn 1 lúc)
1. **File ứng viên:** "Gửi mình file CSV danh sách domain ứng viên (bảng giá vendor / link-gap /
   danh sách tự có). Cần tối thiểu cột domain; tốt nhất có thêm DR, traffic, chủ đề, giá."
2. **Ngành của website cần đi link:** "Website bạn thuộc ngành gì? Cho 3–10 keyword chủ đề
   (vd: du lịch, khách sạn, tour)" → dùng cho `--industry` (tiêu chí đúng ngành).
3. **Ngân sách/link (tùy chọn):** nếu có → `--budget`.

### Bước 1 — Đọc tiêu chí
ĐỌC `rules/prospect-criteria.md` để nắm ngưỡng hiện hành (3 bắt buộc + 5 cộng, đạt ≥2 cộng
mới "Nên tiếp cận"). Nếu user muốn ngưỡng khác (vd DR ≥ 30) → dùng `--min-dr`.

### Bước 2 — Chạy chấm điểm
```
python3 ".claude/skills/backlink-prospector/prospect.py" "<candidates.csv>" \
  --industry "du lịch,khách sạn" --budget 5000000 \
  --out outputs/prospects-<site>.csv
```
Script tự dò encoding/delimiter và map cột linh hoạt (site/domain, DR, traffic, chủ đề, giá,
vendor). Nếu báo "Không tìm thấy cột domain" → xem tên cột thực tế trong thông báo lỗi và đổi
tên cột hoặc bổ sung alias trong `ALIASES` của script.

### Bước 3 — Diễn giải & giao kết quả
1. Đọc dòng `[✓]` tóm tắt: bao nhiêu "Nên tiếp cận" / "Cân nhắc" / "Loại".
2. Viết tóm tắt cho user: top site nên tiếp cận (kèm DR, giá, vendor nếu có), tổng ngân sách
   dự kiến nếu mua hết nhóm "Nên tiếp cận", các site "Cân nhắc" cần review tay.
3. File CSV kết quả nằm ở `outputs/` — nhắc user KHÔNG commit nếu chứa data nội bộ.

## Tiêu chí chất lượng — Agent tự kiểm trước khi giao (Pre-Delivery Review)
- [ ] **Số dòng khớp**: tổng "Nên tiếp cận + Cân nhắc + Loại" = số ứng viên có domain trong file vào.
- [ ] **Mỗi site "Loại" có lý do** (`fail_reasons` không rỗng).
- [ ] **Không suy diễn**: site thiếu DR/traffic bị loại vì "thiếu dữ liệu" — nêu rõ là thiếu,
      không phải "site xấu".
- [ ] **Đúng ngành đã bật**: nếu user cung cấp ngành mà quên `--industry` → chạy lại.
- [ ] **Ngân sách áp dụng đúng**: có `--budget` thì site vượt giá phải ở nhóm "Loại".
- [ ] **Nhắc riêng tư**: kết quả chứa bảng giá nội bộ → dặn user không đưa lên public.

## Lỗi thường gặp — "vết xe đổ"
| Lỗi | Nguyên nhân | Cách xử lý |
|---|---|---|
| "Không tìm thấy cột domain/site" | Tên cột lạ | Xem danh sách cột in ra, thêm alias vào `ALIASES` trong `prospect.py`. |
| Tất cả bị "Loại" vì thiếu DR/traffic | File chỉ có tên domain | Báo user bổ sung metrics (export Ahrefs/tool khác); đừng tự bịa DR. |
| "Đúng ngành" = 0 site | Keyword ngành quá hẹp/sai ngôn ngữ so với cột chủ đề | Nới keyword (thêm từ đồng nghĩa, tiếng Việt không dấu nếu data không dấu). |
| Giá parse sai (30002...) | Ô giá chứa text ghi chú | Script đã bỏ ô nhiều chữ cái; site đó sẽ không có giá — kiểm cột `price_vnd` trống. |
| Encoding lỗi (mojibake) | File UTF-16/khác | Script tự dò; nếu vẫn lỗi kiểm bằng `file <path>`. |
| Kết quả bị commit lên repo | Quên gitignore | `outputs/*.csv` đã bị chặn; kiểm `git status` trước khi push. |

## Định dạng đầu ra
- `outputs/prospects-<site>.csv` — các cột: `site, verdict, bonus_score, bonus, fail_reasons,
  dr, traffic, topic, price_vnd, link_type, vendor, market`; sắp xếp: Nên tiếp cận → Cân nhắc →
  Loại, trong nhóm theo bonus giảm dần rồi DR giảm dần.
- Tóm tắt chat: số lượng từng nhóm + top 10 "Nên tiếp cận" + tổng chi phí dự kiến.
