# Báo cáo Audit On-page — {URL}

- **Ngày audit:** {date}
- **URL:** {url}
- **Status code:** {status_code} | **HTTPS:** {is_https} | **TTFB:** {response_time_ms} ms
- **Health Score:** {health_score}/100 {hoặc "INSUFFICIENT DATA"}

## 1. Tóm tắt
{2–4 câu: điểm mạnh nổi bật, vấn đề nghiêm trọng nhất cần xử lý.}

## 2. Vấn đề theo mức ưu tiên
### 🔴 Critical (sửa ngay)
| Tiêu chí | Hiện trạng | Khắc phục đề xuất |
|---|---|---|
| {name} | {giá trị thực tế} | {hành động cụ thể} |

### 🟠 High (trong 1 tháng)
| Tiêu chí | Hiện trạng | Khắc phục |
|---|---|---|

### 🟡 Medium (cải thiện dần)
| Tiêu chí | Hiện trạng | Khắc phục |
|---|---|---|

## 3. Chi tiết theo nhóm checklist
| # | Nhóm | Tiêu chí | Trạng thái | Giá trị |
|---|---|---|---|---|
| meta_01 | Metadata | Title tag | {pass/warn/fail} | {title_length} ký tự |
| ... | ... | ... | ... | ... |

## 4. Page Speed (PageSpeed Insights)
| Metric | Mobile | Desktop | Ngưỡng |
|---|---|---|---|
| Performance | {score} | {score} | ≥70 |
| LCP | {s} | {s} | <2.5s |
| CLS | {v} | {v} | <0.1 |
| INP | {ms} | {ms} | <200ms |

## 5. Cần kiểm bổ sung (ngoài phạm vi 1 URL)
- Duplicate title/meta toàn site (cần crawl nhiều trang)
- Redirect www/non-www, soft-404 (cần kiểm nhiều URL)
- Tương phản màu WCAG (kiểm thủ công)
- Log file analysis (cần access log)
