# Báo cáo Audit On-page — https://seongon.com (DEMO)

- **Ngày audit:** 07/07/2026
- **URL:** https://seongon.com | **Status:** 200 | **HTTPS:** có | **TTFB:** 471 ms
- **Health Score:** 68/100 *(nhóm Page Speed = INSUFFICIENT DATA — chạy `--no-psi`, đã loại khỏi mẫu số)*

## 1. Tóm tắt
Nền tảng on-page khá tốt: title chuẩn 51 ký tự, đúng 1 H1, canonical self-referencing, viewport/favicon đầy đủ, nội dung 8.396 từ không phụ thuộc JS. Vấn đề lớn nhất: **hoàn toàn không có schema JSON-LD**, meta description hơi ngắn, nhiều ảnh thiếu alt và external link chưa gắn nofollow.

## 2. Vấn đề theo mức ưu tiên

### 🔴 Critical (sửa ngay)
| Tiêu chí | Hiện trạng | Khắc phục đề xuất |
|---|---|---|
| Schema Organization (struct_05) | Không có JSON-LD nào trên trang chủ | Thêm Organization schema (name, url, logo, contactPoint) |
| GA4 (measure_02) | Không phát hiện G-XXXX (có GTM) | Kiểm tra GA4 đã gắn qua GTM chưa; nếu chưa, thêm tag GA4 |
| Ảnh thiếu alt (meta_06) | 82/414 ảnh không có alt | Bổ sung alt mô tả cho 82 ảnh nội dung |

### 🟠 High (trong 1 tháng)
| Tiêu chí | Hiện trạng | Khắc phục |
|---|---|---|
| Meta description (meta_02) | 102 ký tự (chuẩn 120–160) — mức warn | Viết lại dài hơn, thêm CTA |
| External nofollow (links_02) | 238 external link thiếu rel nofollow/noreferrer | Rà soát, thêm rel cho link ngoài không cần truyền equity |
| Open Graph (meta_07) | Thiếu tag (og_complete = false) | Bổ sung đủ og:title/description/image/url/type |
| HSTS (domain_02) | HTTPS có nhưng thiếu HSTS header | Bật Strict-Transport-Security trên server |
| BreadcrumbList (struct_04) | Không có | Thêm schema breadcrumb |
| TTFB (domain_03) | 471 ms (chuẩn <200) — mức warn | Xem cache server/CDN |

### 🟡 Medium
| Tiêu chí | Hiện trạng | Khắc phục |
|---|---|---|
| WebSite schema + SearchBox (struct_06) | Không có | Nice-to-have, thêm khi làm schema tổng |

## 3. Điểm đạt (pass)
Title 51 ký tự ✓ · H1 = 1 ✓ · Canonical đúng ✓ · Viewport ✓ · Charset UTF-8 ✓ · Favicon ✓ · URL thân thiện ✓ · Nội dung không phụ thuộc JS (8.396 từ) ✓ · GTM ✓ · Không noindex ✓

## 4. Page Speed
INSUFFICIENT DATA — demo chạy `--no-psi`. Chạy lại với `--psi-key` để có LCP/CLS/INP.

## 5. Cần kiểm bổ sung (ngoài phạm vi 1 URL)
- Duplicate title/meta toàn site (cần crawl nhiều trang)
- Redirect www/non-www, soft-404 (cần kiểm nhiều URL)
- Tương phản màu WCAG (kiểm thủ công)
- Log file analysis (cần access log)

---
*File demo cho skill `onpage-audit` — dữ liệu thật từ lần chạy `audit.py` ngày 07/07/2026, không chứa thông tin nội bộ.*
