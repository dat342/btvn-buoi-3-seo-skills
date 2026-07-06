# Bộ tiêu chí chọn site đi backlink

## 3 tiêu chí BẮT BUỘC (fail 1 cái là "Loại")
| # | Tiêu chí | Ngưỡng | Lý do |
|---|---|---|---|
| 1 | Không spam/độc | không bị gắn cờ spam/toxic | Link từ site rác gây hại hơn lợi |
| 2 | DR tối thiểu | DR ≥ 20 (chỉnh bằng `--min-dr`) | Dưới ngưỡng này giá trị link rất thấp |
| 3 | Site còn sống | Organic traffic > 0 | Site không traffic = site chết/bị phạt |

## 5 tiêu chí CỘNG ĐIỂM (mỗi cái +1)
| # | Tiêu chí | Ngưỡng |
|---|---|---|
| 4 | Domain mạnh | DR ≥ 40 |
| 5 | Traffic tốt | ≥ 1.000/tháng |
| 6 | Có link dofollow | thông tin link chứa "link do" |
| 7 | Không nghi link farm | linked_domains ≤ 5000 hoặc DR ≥ 20 (chỉ chấm khi có dữ liệu) |
| 8 | Đúng ngành | chủ đề site khớp keyword ngành user cung cấp (`--industry`) |

## Xếp loại
- **"Nên tiếp cận"** = đạt cả 3 bắt buộc **+ ≥ 2 điểm cộng**.
- **"Cân nhắc"** = đạt 3 bắt buộc nhưng < 2 điểm cộng.
- **"Loại"** = fail bất kỳ tiêu chí bắt buộc nào, hoặc vượt `--budget`.

## Ngân sách (tùy chọn)
`--budget <VND>`: ứng viên có giá > ngân sách/link sẽ bị "Loại" kèm lý do, dù điểm cao.

## Nguồn dữ liệu ứng viên — QUY TẮC RIÊNG TƯ
- Skill này **không chứa bất kỳ danh sách site/bảng giá nào**. Người dùng tự cung cấp file CSV lúc chạy
  (bảng giá vendor nội bộ, link-gap export, danh sách tự sưu tầm).
- File data nội bộ **không được commit** vào repo public (đã có .gitignore chặn `outputs/*`).
- File `sample-candidates.csv` trong skill là **dữ liệu giả lập** chỉ để demo/test.

## Giới hạn trung thực
- Tiêu chí #8 (đúng ngành) khớp theo keyword — không thay được đánh giá tay 100%; các site
  "Cân nhắc" nên được người phụ trách review lại.
- Nếu file thiếu cột (DR/traffic...), tiêu chí liên quan tính là **fail/không chấm** và ghi rõ —
  KHÔNG đoán số.
