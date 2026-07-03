# Quy tắc đánh giá chất lượng backlink

## Phân nhóm DR (Domain Rating)
| Nhóm | DR | Ý nghĩa |
|---|---|---|
| Strong | 70–100 | Domain rất mạnh, link cực giá trị |
| Good | 30–69 | Domain tốt, đáng giữ/xây thêm |
| Low | 10–29 | Yếu, giá trị SEO thấp |
| Very low | 0–9 | Rất yếu, phần lớn ít/không giá trị |

## Cờ nghi độc/spam (mỗi dòng)
Một referring domain bị coi là **nghi độc (toxic)** nếu thỏa ÍT NHẤT 1 trong:
- `is_spam` = true (cờ của Ahrefs) — tín hiệu mạnh nhất.
- `dr` < 10 **và** `traffic` = 0 (domain rác không traffic).
- `linked_domains` rất lớn (> 5000) **và** `dr` < 20 (dấu hiệu link farm/PBN).

Chỉ số hồ sơ:
- **Spam ratio** = số domain nghi độc / tổng ref domain. Ngưỡng cảnh báo:
  - < 20%: bình thường.
  - 20–50%: cần rà soát, cân nhắc disavow.
  - **> 50%: báo động** — hồ sơ nhiều khả năng bị SEO bẩn/negative SEO, nên disavow.

## Tỷ lệ dofollow / nofollow
- `dofollow_links > 0` = domain dofollow; còn lại nofollow.
- Hồ sơ tự nhiên thường có **cả hai**; dofollow chiếm ~40–70%. 100% dofollow hoặc 100% nofollow
  đều là dấu hiệu bất thường (mua link / hoặc chỉ toàn link mạng xã hội nofollow).

## Link mới / mất
- `first_seen` trong 30/90 ngày gần nhất → **link mới** (đà tăng trưởng).
- `lost` có ngày → **link mất** (cần xem có phải link giá trị bị rớt không).

## Link Gap (khi có nhiều site)
- Referring domain trỏ về đối thủ mà chưa trỏ về mình → **cơ hội xây link**.
- Ưu tiên cơ hội theo: `dr` cao + `traffic` cao + KHÔNG phải nghi độc.
- Bỏ qua các domain nghi độc khỏi danh sách cơ hội (đừng đi xin link rác).

## Nguyên tắc trung thực
- Con số trong báo cáo phải khớp dữ liệu file. Không suy diễn "chất lượng" vượt quá dữ liệu.
- Nếu file thiếu cột nào đó (vd không có `traffic`) → nêu rõ "không đánh giá được [X] do thiếu cột",
  KHÔNG bịa.
