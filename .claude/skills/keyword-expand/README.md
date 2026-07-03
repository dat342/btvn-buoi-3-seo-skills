# keyword-expand

Skill mở rộng / đề xuất từ khóa SEO (tiếng Việt) rồi xuất Excel.
Chỉ dùng thư viện chuẩn Python + `openpyxl`. Không cần cài thêm gì khác.

## Nội dung gói
```
keyword-expand/
├── SKILL.md          # Hướng dẫn cho Claude (Cowork tự đọc)
├── expand.py         # Mở rộng từ khóa + (tùy chọn) volume → Excel
├── analyze_domain.py # Đọc website → rút cụm ứng viên làm seed
├── config.json       # Cấu hình nguồn + API key
└── README.md
```

## Cài đặt
Chép cả thư mục `keyword-expand/` vào một trong hai nơi:
- `~/.claude/skills/` → dùng cho mọi dự án.
- `<project>/.claude/skills/` → chỉ dùng trong dự án đó.

Yêu cầu: Python 3.8+ và `openpyxl` (`pip3 install openpyxl`).

## Cách 1 — Gọi trong Cowork / Claude Code
Skill tự kích hoạt khi bạn nói tự nhiên, hoặc gõ `/keyword-expand`. Ví dụ:
- "mở rộng từ khóa: dây thừng, dây neo tàu"
- "đề xuất từ khóa tiếng Việt cho website asiadragoncordage.com"

Claude sẽ: (với domain) phân tích site → đề xuất seed → **dừng cho bạn duyệt** → mở rộng → Excel.

## Cách 2 — Gọi trực tiếp từ dòng lệnh / code

**Mở rộng từ seed (free, Google Autocomplete):**
```bash
python3 expand.py --keywords "dây thừng" "dây neo tàu" --out ket_qua.xlsx
```

**Phân tích domain → in JSON ứng viên seed:**
```bash
python3 analyze_domain.py asiadragoncordage.com --max-pages 6
```

**Có search volume thật (cần API key KeywordTool.io trong config.json):**
```bash
python3 expand.py --keywords "dây thừng" --source keywordtool --mode production --out volume.xlsx
```

### Tham số expand.py
| Cờ | Ý nghĩa |
|---|---|
| `--keywords ...` | Danh sách seed (mỗi từ trong dấu nháy) |
| `--file seed.txt` | Đọc seed từ file, mỗi dòng một từ |
| `--out FILE.xlsx` | File Excel xuất ra |
| `--source google\|keywordtool` | Nguồn dữ liệu (mặc định `google`, free) |
| `--depth 0\|1` | 0 = nhanh, 1 = đào sâu thêm a–z (mặc định 1) |
| `--exclude "t1" "t2"` | Thêm cụm nhiễu cần loại |
| `--keep-all` | Tắt bộ lọc nhiễu mặc định |
| `--mode sandbox\|production` | Chỉ cho KeywordTool.io |
| `--apikey KEY` | Ghi đè API key KeywordTool.io |

### Dùng như module trong Python
```python
import sys; sys.path.insert(0, "path/to/keyword-expand")
import expand
cfg = expand.load_config()
rows = expand.expand_google(["dây thừng"], cfg, depth=1)
rows, removed = expand.filter_noise(rows)
expand.write_xlsx(rows, "ket_qua.xlsx")
```

## Nguồn dữ liệu
- **google** (mặc định, free): Google Autocomplete. Chỉ gợi ý, **không có volume**. Không cần key.
- **keywordtool**: KeywordTool.io — có volume + CPC + lịch sử 12 tháng, **cần API key trả phí**.

## Lọc nhiễu
Mặc định loại các cụm phi thương mại (là gì, tiếng anh, meme, wiki, giày, tattoo…).
Danh sách nằm trong `DEFAULT_NOISE` ở `expand.py`; thêm nhanh bằng `--exclude`.
