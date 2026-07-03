# Quy tắc chấm điểm & phân loại vấn đề

## Trạng thái mỗi tiêu chí
- **pass** — đạt ngưỡng.
- **warn** — có nhưng chưa tối ưu (vd title 66–75 ký tự, TTFB 200–600ms).
- **fail** — không đạt / thiếu.
- **n/a** — không áp dụng (vd hreflang khi site 1 ngôn ngữ; PageSpeed khi không có kết quả).

## Ngưỡng cụ thể
| Tiêu chí | pass | warn | fail |
|---|---|---|---|
| Title length | 30–65 | 25–29 hoặc 66–75 | <25 hoặc >75 hoặc thiếu |
| Meta desc length | 120–160 | 80–119 hoặc 161–200 | <80 hoặc >200 hoặc thiếu |
| H1 count | =1 | — | 0 hoặc >1 |
| Images without alt | 0 | 1–2 | ≥3 |
| TTFB (response_time_ms) | <200 | 200–600 | >600 |
| URL length | ≤115 | 116–150 | >150 |
| Performance mobile | ≥70 | 50–69 | <50 |
| LCP | <2.5s | 2.5–4s | >4s |
| CLS | <0.1 | 0.1–0.25 | >0.25 |
| INP | <200ms | 200–500ms | >500ms |

## Điểm số tổng (Health Score /100)
- Mỗi tiêu chí `mandatory`: pass=+trọng số 2, warn=+1, fail=0.
- Mỗi tiêu chí `high`: pass=+1.5, warn=+0.75, fail=0.
- Mỗi tiêu chí `nicetohave`/khác: pass=+1, warn=+0.5, fail=0.
- Health Score = (tổng điểm đạt / tổng điểm tối đa của các tiêu chí áp dụng) × 100, làm tròn.
- Nếu thiếu dữ liệu PageSpeed (không có mạng/API) → loại nhóm speed khỏi mẫu số và ghi chú "INSUFFICIENT DATA cho Page Speed".

## Phân loại mức ưu tiên khắc phục (đưa vào báo cáo)
- **Critical (sửa ngay):** mọi tiêu chí `mandatory` đang **fail** (noindex, thiếu title, không HTTPS, CWV fail...).
- **High (sửa trong 1 tháng):** tiêu chí `high` fail + `mandatory` warn.
- **Medium (cải thiện dần):** các warn còn lại + nicetohave fail.

## Nguyên tắc trung thực (bắt buộc)
- KHÔNG bịa số. Field nào script không lấy được → trạng thái `n/a` + ghi rõ lý do, KHÔNG đoán là pass.
- Phân biệt rõ "không kiểm được" vs "kiểm và fail".
