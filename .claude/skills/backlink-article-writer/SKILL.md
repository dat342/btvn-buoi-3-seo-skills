---
name: backlink-article-writer
description: Viết bài guest post/PR chuẩn SEO để đi backlink — chèn 1-2 link về URL đích với anchor text tự nhiên theo quy tắc chống over-optimization, giọng văn khớp site sẽ đăng. Kích hoạt khi user muốn "viết bài đi backlink", "viết guest post", "viết bài PR chèn link", "content cho site vệ tinh", "bài viết đặt link", HOẶC đã có danh sách site cần đi link và cần bài viết cho từng site.
---

# Backlink Article Writer

Viết **bài đăng trên site khác** (guest post / PR) với mục tiêu đặt backlink về URL đích:
nội dung có giá trị thật để được duyệt đăng, link chèn tự nhiên đúng quy tắc anchor.

Skill này là kỹ năng viết (không cần script). Chất lượng phụ thuộc tuân thủ 2 file quy tắc.

## File bổ trợ (load-on-demand)
- `rules/anchor-rules.md` — quy tắc số link, vị trí link, phân bổ kiểu anchor, chống
  over-optimization. **BẮT BUỘC đọc trước khi viết** (Bước 1).
- `templates/article-template.md` — khung bài + metadata bàn giao. **Đọc ở Bước 2**.

## Quy trình

### Bước 0 — Thu thập input (hỏi lần lượt những gì còn thiếu)
1. **URL đích** cần trỏ link về (trang chủ / trang dịch vụ / bài viết?).
2. **Từ khóa chính** của bài + chủ đề bài viết mong muốn.
3. **Site sẽ đăng** (nếu biết — để khớp giọng văn + yêu cầu số từ/ảnh của vendor).
4. **Anchor text** user muốn, hoặc để skill tự đề xuất theo quy tắc phân bổ.
5. **Số link được chèn** theo gói đã mua (mặc định 1–2; "link do" hay "link no").
6. Nếu viết **nhiều bài cho nhiều site** (chiến dịch): xin danh sách site + URL đích từng bài,
   và viết TỪNG BÀI KHÁC NHAU — không xào 1 bài dùng lại.

### Bước 1 — Đọc quy tắc
ĐỌC `rules/anchor-rules.md`. Chốt với user: anchor dự kiến cho từng link (đưa đề xuất theo
bảng phân bổ; nếu user đã đi nhiều bài với anchor chính xác → khuyên đổi kiểu anchor).

### Bước 2 — Viết bài
1. ĐỌC `templates/article-template.md`, viết theo khung.
2. Độ dài mặc định 800–1200 từ (hoặc theo yêu cầu site đăng/vendor).
3. Nội dung PHẢI có giá trị độc lập (thông tin thật, mẹo cụ thể) — không viết vỏ rỗng quanh link.
4. Chèn link đúng vị trí + anchor đã chốt. Không chèn link vào heading.
5. Nếu chủ đề có yếu tố thời sự/số liệu → chỉ dùng thông tin chắc chắn, không bịa số liệu,
   không bịa tên tổ chức/nghiên cứu.

### Bước 3 — Giao bài
1. Lưu `outputs/article-<site-dang>-<keyword-slug>.md` (mỗi bài 1 file).
2. Báo user: tiêu đề, số từ, anchor + vị trí link, site đăng dự kiến.

## Tiêu chí chất lượng — Agent tự kiểm trước khi giao (Pre-Delivery Review)
- [ ] **Link đúng và đủ**: đúng URL đích, đúng số link theo gói, không link ở mở bài/heading.
- [ ] **Anchor đúng quy tắc**: kiểu anchor khớp đã chốt; 2 link trong bài không trùng kiểu.
- [ ] **Giá trị độc lập**: xóa link đi bài vẫn là bài đọc được — nếu không, viết lại.
- [ ] **Khớp site đăng**: giọng văn/độ dài/chủ đề hợp site + yêu cầu vendor (số từ, không bet/game...).
- [ ] **Không bịa**: số liệu/tên riêng kiểm chứng được; không chắc thì bỏ hoặc nói chung.
- [ ] **Không trùng lặp**: chiến dịch nhiều bài → các bài khác tiêu đề, khác outline, khác anchor.
- [ ] **Metadata đủ**: tiêu đề ≤65 ký tự, meta description 120–160, checklist bàn giao còn nguyên.

## Lỗi thường gặp — "vết xe đổ"
| Lỗi | Nguyên nhân | Cách xử lý |
|---|---|---|
| Bài bị vendor/báo từ chối | Nội dung quảng cáo lộ, link gượng ép | Tăng phần giá trị thông tin, đẩy link xuống giữa bài, giọng trung lập. |
| Anchor từ khóa chính xác lặp nhiều bài | Không theo dõi phân bổ toàn chiến dịch | Đọc lại anchor-rules; hỏi user các anchor đã dùng trước đó. |
| Bài vượt/thiếu số từ so quy định site | Không hỏi yêu cầu vendor | Bước 0 phải hỏi site đăng + yêu cầu gói (vd "bài PR dưới 1000 từ"). |
| 1 bài xào cho 10 site | Tiết kiệm công viết | Duplicate content — mỗi site 1 bài khác nhau thật sự. |
| Chèn link vào H2 | Tưởng nổi bật hơn | Quy tắc cấm — chuyển link vào đoạn văn. |
| Bịa số liệu "nghiên cứu cho thấy..." | Muốn bài thuyết phục | Chỉ dùng nguồn thật; không có thì diễn đạt định tính. |

## Định dạng đầu ra
- `outputs/article-<site>-<keyword>.md` theo `templates/article-template.md`: khối metadata
  (meta description, URL đích, anchor, số từ) → thân bài H2/H3 → checklist bàn giao.
- Nhiều bài = nhiều file riêng, đặt tên theo site đăng.
