# Checklist On-page (kiểm được từ 1 URL)

Nguồn gốc: chắt lọc từ bộ checklist chuẩn của plugin `seo-audit` (105+ tiêu chí, 14 nhóm)
trên máy. Ở đây chỉ giữ các tiêu chí **kiểm được từ 1 lần fetch HTML + PageSpeed API cho 1 URL**.
Các tiêu chí cần crawl nhiều trang (duplicate title toàn site), log file, hoặc kiểm thủ công
(contrast màu) được liệt kê ở cuối mục "Ngoài phạm vi 1 URL" để báo cáo nêu rõ.

Cột `field`: tên trường trong JSON mà `audit.py` xuất ra để đối chiếu.

## I. DOMAIN & GIAO THỨC
| id | Tiêu chí | Ngưỡng đạt | field | Ưu tiên |
|---|---|---|---|---|
| domain_02 | HTTP → HTTPS | URL cuối cùng dùng `https://`; HSTS header có càng tốt | `is_https`, `hsts` | mandatory |
| domain_03 | TTFB / tốc độ phản hồi | `response_time_ms` < 200ms tốt, < 600ms chấp nhận | `response_time_ms` | high |

## II. INDEXABILITY
| id | Tiêu chí | Ngưỡng đạt | field | Ưu tiên |
|---|---|---|---|---|
| index_03 | Không bị noindex | Không có `meta robots noindex` / `X-Robots-Tag: noindex` | `meta_robots`, `x_robots_tag` | mandatory |
| index_06 | Canonical đúng | Có canonical, self-referencing hoặc trỏ URL gốc hợp lệ | `canonical`, `canonical_matches_url` | mandatory |

## III. JAVASCRIPT SEO
| id | Tiêu chí | Ngưỡng đạt | field | Ưu tiên |
|---|---|---|---|---|
| js_01 | Nội dung render không cần JS | `word_count` > 100 trong HTML thô | `word_count` | high |

## IV. WEBSITE STRUCTURE / SCHEMA
| id | Tiêu chí | Ngưỡng đạt | field | Ưu tiên |
|---|---|---|---|---|
| struct_01 | URL ngắn gọn, thân thiện | ≤ 115 ký tự, dùng gạch ngang, không ký tự đặc biệt | `url_length`, `url_friendly` | mandatory |
| struct_04 | BreadcrumbList Schema | JSON-LD có `BreadcrumbList` | `structured_data_types` | high |
| struct_05 | Organization/LocalBusiness Schema (trang chủ) | JSON-LD có `Organization` hoặc `LocalBusiness` | `structured_data_types` | high |
| struct_11 | Schema không lỗi cú pháp | Mọi JSON-LD parse được | `structured_data_valid` | mandatory |

## VI. METADATA & ON-PAGE
| id | Tiêu chí | Ngưỡng đạt | field | Ưu tiên |
|---|---|---|---|---|
| meta_01 | Title tag | Có; 30–65 ký tự (TV), 50–65 (EN) | `title`, `title_length` | mandatory |
| meta_02 | Meta description | Có; 120–160 ký tự | `meta_description`, `meta_description_length` | mandatory |
| meta_04 | H1 đúng số lượng | Đúng 1 thẻ H1 | `h1_count` | mandatory |
| meta_05 | Cấu trúc heading | H1→H2→H3 không bỏ cấp | `headings` | high |
| meta_06 | Ảnh có alt | `images_without_alt` = 0 | `images_total`, `images_without_alt` | mandatory |
| meta_07 | Open Graph đầy đủ | Có og:title, og:description, og:image, og:url, og:type | `og_tags` | high |
| meta_08 | Viewport meta | Có `<meta name=viewport>` | `viewport_meta` | mandatory |
| meta_09 | Charset khai báo | Có `charset=utf-8` | `charset` | mandatory |
| meta_10 | Hreflang (nếu đa ngôn ngữ) | Có + self-ref + x-default | `hreflang` | mandatory* |
| meta_11 | Favicon | Có `<link rel=icon>` | `favicon` | high |

## V. LINKS
| id | Tiêu chí | Ngưỡng đạt | field | Ưu tiên |
|---|---|---|---|---|
| links_02 | External link có nofollow/noreferrer | Không có external link thiếu rel bảo vệ | `external_links_without_nofollow` | high |

## IX. PAGE SPEED (cần PageSpeed API)
| id | Tiêu chí | Ngưỡng đạt | field | Ưu tiên |
|---|---|---|---|---|
| speed_01 | Core Web Vitals | LCP < 2.5s, INP < 200ms, CLS < 0.1 | `cwv.lcp/inp/cls` | mandatory |
| speed_02 | Performance score mobile | ≥ 70 | `performance_score_mobile` | high |

## XI. MEASUREMENT
| id | Tiêu chí | Ngưỡng đạt | field | Ưu tiên |
|---|---|---|---|---|
| measure_01 | Google Tag Manager | Có GTM snippet | `has_gtm` | mandatory |
| measure_02 | Google Analytics 4 | Có G-XXXX | `has_ga4` | mandatory |

---
\* meta_10 chỉ bắt buộc khi site đa ngôn ngữ.

## Ngoài phạm vi 1 URL (báo cáo phải ghi "cần kiểm bổ sung")
- meta_03 Duplicate title/meta toàn site → cần crawl nhiều trang.
- domain_01 www/non-www redirect, index_05 soft-404 → cần kiểm nhiều URL/redirect.
- ui_02 Tương phản màu (WCAG) → kiểm thủ công.
- log_01..04 Log file analysis → cần access log server.
