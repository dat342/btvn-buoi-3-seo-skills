# Ánh xạ cột file Ahrefs — Referring Domains export

File export **Referring domains / subdomains** của Ahrefs thường:
- Mã hóa **UTF-16 LE có BOM**, phân tách bằng **TAB** (không phải dấu phẩy) — dù đuôi `.csv`.
- (Đôi khi là UTF-8-SIG, phẩy — script tự dò).

Mỗi dòng = 1 **referring domain** (không phải từng backlink). `analyze_backlinks.py` tự nhận diện
cột theo bảng alias dưới (không phân biệt hoa/thường, bỏ khoảng trắng thừa). Nếu Ahrefs đổi tên
cột ở gói/bản khác, **thêm alias vào đây** (đây là nguồn tham chiếu người đọc; alias thực thi nằm
trong `analyze_backlinks.py` — sửa cả 2 cho khớp).

| Trường chuẩn (internal) | Ý nghĩa | Alias tên cột Ahrefs |
|---|---|---|
| `domain` | Referring domain | Domain, Referring domain, Referring domains |
| `is_spam` | Cờ spam của Ahrefs (true/false) | Is spam, Spam |
| `dr` | Domain Rating (0–100) | DR, Domain rating, Domain Rating |
| `ref_domains` | Số ref domain của domain đó | Dofollow ref. domains, Referring domains |
| `linked_domains` | Số domain mà domain đó trỏ ra | Dofollow linked domains, Linked domains |
| `traffic` | Organic traffic của domain đó | Traffic, Domain traffic |
| `keywords` | Số keyword organic của domain | Keywords, Organic keywords |
| `links_to_target` | Số link trỏ về site đang phân tích | Links to target, Links to Target |
| `dofollow_links` | Số link dofollow trỏ về target | Dofollow links |
| `first_seen` | Lần đầu Ahrefs thấy link | First seen, First seen link |
| `lost` | Ngày mất link (rỗng = còn sống) | Lost, Last seen |

## Suy luận dofollow/nofollow
Ahrefs export refdomains không có cột "nofollow" tường minh. Quy ước:
- `dofollow_links > 0` → domain có ít nhất 1 link **dofollow** về target.
- `dofollow_links = 0` (mà `links_to_target > 0`) → toàn bộ link từ domain đó là **nofollow**.

## Trạng thái link
- `lost` rỗng → **live** (còn trỏ về).
- `lost` có ngày → **lost** (đã mất).

## File nhiều website (link gap)
Truyền nhiều file, mỗi file 1 website. Chỉ định file "của mình" bằng `--mine <đường-dẫn>`.
Link gap = referring domain xuất hiện ở (các) đối thủ nhưng KHÔNG có ở file của mình.
