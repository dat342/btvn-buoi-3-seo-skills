#!/usr/bin/env python3
"""
keyword-expand — Bước 1: mở rộng từ khóa + lấy search volume từ KeywordTool.io.

Chỉ dùng thư viện chuẩn (urllib) + openpyxl. Không cần requests/pandas.

Cách dùng:
    python3 expand.py --keywords "dịch vụ seo" "thiết kế web" --out ket_qua.xlsx
    python3 expand.py --file seed.txt --out ket_qua.xlsx
    python3 expand.py --keywords "abc" --mode production --apikey sk_xxx

Cấu hình mặc định đọc từ config.json đặt cạnh file này:
    { "api_key": "...", "mode": "sandbox", "country": "vn",
      "language": "vi", "location": 2704, "currency": "VND" }
"""
import argparse
import json
import os
import string
import sys
import time
import urllib.request
import urllib.parse
import urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(HERE, "config.json")

BASE = "https://api.keywordtool.io"
GOOGLE_SUGGEST = "https://suggestqueries.google.com/complete/search"

# Cụm từ nhiễu / phi thương mại — mặc định loại bỏ (so khớp không phân biệt hoa thường).
DEFAULT_NOISE = [
    "là gì", "la gi", "nghĩa là", "nghia la", "tiếng anh", "tieng anh", "tiếng trung",
    "tiếng nhật", "tiếng hàn", "tiếng việt là", "english", "đọc là", "doc la", "viết",
    "meme", "wiki", "wikipedia", "lyrics", "bài hát", "bai hat", "phim", "truyện",
    "truyen", "game", "nằm mơ", "nam mo", "mơ thấy", "mo thay", "bói", "boi", "trong mơ",
    "af1", "nike", "adidas", "jordan", "giày", "giay", "vẽ", "tô màu", "to mau",
    "hình xăm", "hinh xam", "tattoo",
]


def load_config():
    cfg = {
        "source": "google",
        "api_key": os.environ.get("KEYWORDTOOL_API_KEY", ""),
        "mode": "sandbox",
        "country": "vn",
        "language": "vi",
        "location": 2704,
        "currency": "VND",
    }
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg.update({k: v for k, v in json.load(f).items() if v not in ("", None)})
        except Exception as e:
            print(f"[!] Không đọc được config.json: {e}", file=sys.stderr)
    return cfg


def post(url, payload):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"content-type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        try:
            err = json.loads(body)
            msg = err.get("error", {}).get("message", body)
        except Exception:
            msg = body
        raise SystemExit(f"[x] API lỗi HTTP {e.code}: {msg}")
    except urllib.error.URLError as e:
        raise SystemExit(f"[x] Lỗi mạng: {e.reason}")


def endpoint(mode, path):
    seg = "v2-sandbox" if mode == "sandbox" else "v2"
    return f"{BASE}/{seg}/search/{path}/google"


# ---------- Nguồn FREE: Google Autocomplete (không cần key) ----------

def google_suggest(query, cfg):
    qs = urllib.parse.urlencode(
        {"client": "firefox", "hl": cfg["language"], "gl": cfg["country"], "q": query}
    )
    req = urllib.request.Request(
        f"{GOOGLE_SUGGEST}?{qs}", headers={"User-Agent": "Mozilla/5.0"}
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read().decode("utf-8", "replace"))
        return data[1] if isinstance(data, list) and len(data) > 1 else []
    except Exception:
        return []  # bỏ qua truy vấn lỗi, không làm hỏng cả lượt chạy


def expand_google(seeds, cfg, depth=1):
    """Mở rộng từ khóa bằng Google Autocomplete. depth=1 thêm hậu tố a-z + 0-9."""
    rows = []
    seen = set()
    suffixes = [""]
    if depth >= 1:
        suffixes += [" " + c for c in (string.ascii_lowercase + string.digits)]
    for seed in seeds:
        print(f"  → gợi ý cho: {seed}")
        for suf in suffixes:
            for s in google_suggest(seed + suf, cfg):
                if s and s not in seen:
                    seen.add(s)
                    rows.append({"Original Keyword": seed, "Suggested Keyword": s})
            time.sleep(0.15)
    return rows


def extract_items(results):
    """results có thể là dict {category: [items]} HOẶC list [items]. Xử lý cả hai."""
    items = []
    if isinstance(results, dict):
        for value in results.values():
            if isinstance(value, list):
                items.extend(value)
            elif isinstance(value, dict):
                items.append(value)
    elif isinstance(results, list):
        items = results
    return items


def get_suggestions(seed, cfg):
    url = endpoint(cfg["mode"], "suggestions")
    payload = {
        "category": "web",
        "country": cfg["country"],
        "language": cfg["language"],
        "metrics": True,
        "metrics_network": "googlesearchnetwork",
        "metrics_currency": cfg["currency"],
        "metrics_location": [cfg["location"]],
        "type": "suggestions",
        "complete": False,
        "output": "json",
        "apikey": cfg["api_key"],
        "keyword": seed,
    }
    data = post(url, payload)
    out = []
    for item in extract_items(data.get("results")):
        if not isinstance(item, dict):
            continue
        text = item.get("string") or item.get("keyword")
        if not text:
            continue
        metrics = {k: v for k, v in item.items() if k not in ("string", "keyword")}
        out.append({"seed": seed, "suggestion": text, "metrics": metrics})
    return out


def get_volume(keywords, cfg):
    url = endpoint(cfg["mode"], "volume")
    payload = {
        "metrics_network": "googlesearchnetwork",
        "metrics_currency": cfg["currency"],
        "complete": True,
        "output": "json",
        "apikey": cfg["api_key"],
        "metrics_location": [cfg["location"]],
        "keyword": keywords,
        "metrics_language": [cfg["language"]],
    }
    data = post(url, payload)
    return data.get("results", {}) or {}


def chunked(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i : i + n]


def filter_noise(rows, extra_terms=None, use_default=True):
    """Bỏ các dòng có 'Suggested Keyword' chứa cụm nhiễu. Trả (giữ_lại, số_đã_bỏ)."""
    terms = []
    if use_default:
        terms += DEFAULT_NOISE
    if extra_terms:
        terms += [t.strip().lower() for t in extra_terms if t.strip()]
    if not terms:
        return rows, 0
    kept, removed = [], 0
    for r in rows:
        kw = str(r.get("Suggested Keyword", "")).lower()
        if any(t in kw for t in terms):
            removed += 1
        else:
            kept.append(r)
    return kept, removed


def write_xlsx(rows, out_path):
    from openpyxl import Workbook

    lead = ["Original Keyword", "Suggested Keyword", "volume", "cpc", "cmp", "trend"]
    present = set()
    for r in rows:
        present.update(r.keys())
    # giữ cột lead nếu có dữ liệu; luôn giữ 2 cột tên từ khóa
    headers = [h for h in lead if h in ("Original Keyword", "Suggested Keyword") or h in present]
    for r in rows:
        for k in r:
            if k not in headers:
                headers.append(k)

    wb = Workbook()
    ws = wb.active
    ws.title = "Keywords"
    ws.append(headers)
    for r in rows:
        ws.append([r.get(h, "") for h in headers])
    # freeze header + filter
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    wb.save(out_path)


def main():
    ap = argparse.ArgumentParser(description="Mở rộng từ khóa + volume (KeywordTool.io)")
    ap.add_argument("--keywords", nargs="*", default=[], help="Các từ khóa hạt nhân")
    ap.add_argument("--file", help="File .txt, mỗi dòng một từ khóa")
    ap.add_argument("--out", default="keyword_expand.xlsx", help="File Excel xuất ra")
    ap.add_argument(
        "--source",
        choices=["google", "keywordtool"],
        help="Nguồn dữ liệu: google (free, chỉ gợi ý) hoặc keywordtool (có volume, cần key)",
    )
    ap.add_argument("--depth", type=int, default=1, help="Độ đào sâu Google (0=nhanh, 1=thêm a-z)")
    ap.add_argument("--exclude", nargs="*", default=[], help="Cụm từ nhiễu cần loại thêm")
    ap.add_argument("--keep-all", action="store_true", help="Tắt bộ lọc nhiễu mặc định")
    ap.add_argument("--mode", choices=["sandbox", "production"], help="Ghi đè mode KeywordTool")
    ap.add_argument("--apikey", help="Ghi đè API key KeywordTool")
    args = ap.parse_args()

    cfg = load_config()
    if args.source:
        cfg["source"] = args.source
    if args.mode:
        cfg["mode"] = args.mode
    if args.apikey:
        cfg["api_key"] = args.apikey

    seeds = list(args.keywords)
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            seeds += [ln.strip() for ln in f if ln.strip()]
    seeds = list(dict.fromkeys(seeds))  # bỏ trùng, giữ thứ tự
    if not seeds:
        raise SystemExit("[x] Chưa có từ khóa nào. Dùng --keywords hoặc --file.")

    # ===== Nguồn FREE: Google Autocomplete (chỉ gợi ý, không volume) =====
    if cfg["source"] == "google":
        print(f"[i] Nguồn: Google Autocomplete (free) | {len(seeds)} từ khóa hạt nhân | depth={args.depth}")
        rows = expand_google(seeds, cfg, depth=args.depth)
        if not rows:
            raise SystemExit("[x] Không lấy được gợi ý nào (mạng lỗi?).")
        rows, removed = filter_noise(rows, args.exclude, use_default=not args.keep_all)
        write_xlsx(rows, args.out)
        print(f"[✓] Xuất {len(rows)} từ khóa gợi ý (đã lọc bỏ {removed} từ nhiễu) → {args.out}")
        return

    # ===== Nguồn KeywordTool.io (có volume, cần key) =====
    if not cfg["api_key"]:
        raise SystemExit(
            "[x] Chưa có API key KeywordTool. Điền vào config.json hoặc dùng --apikey / biến môi trường KEYWORDTOOL_API_KEY."
        )

    print(f"[i] Nguồn: KeywordTool.io | Mode: {cfg['mode']} | {len(seeds)} từ khóa hạt nhân")

    # 1) Lấy gợi ý
    all_sug = []
    for seed in seeds:
        print(f"  → gợi ý cho: {seed}")
        all_sug.extend(get_suggestions(seed, cfg))
        time.sleep(0.3)

    # bỏ trùng theo text gợi ý (giữ bản đầu tiên kèm seed của nó)
    seen, unique = set(), []
    for s in all_sug:
        if s["suggestion"] not in seen:
            seen.add(s["suggestion"])
            unique.append(s)
    print(f"[i] {len(unique)} từ khóa gợi ý sau khi lọc trùng")

    # 2) Bổ sung volume cho những gợi ý chưa có metrics inline
    need_volume = [s["suggestion"] for s in unique if "volume" not in s["metrics"]]
    vol_map = {}
    if need_volume:
        print(f"[i] Lấy volume cho {len(need_volume)} từ (chia {((len(need_volume)-1)//800)+1} nhóm)")
        for batch in chunked(need_volume, 800):
            vol_map.update(get_volume(batch, cfg))
            time.sleep(0.3)

    # 3) Gộp thành các dòng
    rows = []
    for s in unique:
        row = {"Original Keyword": s["seed"], "Suggested Keyword": s["suggestion"]}
        metrics = dict(s["metrics"])
        if s["suggestion"] in vol_map and isinstance(vol_map[s["suggestion"]], dict):
            metrics.update(vol_map[s["suggestion"]])
        for k, v in metrics.items():
            row[k] = v
        rows.append(row)

    rows, removed = filter_noise(rows, args.exclude, use_default=not args.keep_all)
    write_xlsx(rows, args.out)
    with_vol = sum(1 for r in rows if r.get("volume") not in (None, "", 0))
    print(f"[✓] Xuất {len(rows)} từ khóa ({with_vol} có volume, đã lọc {removed} nhiễu) → {args.out}")


if __name__ == "__main__":
    main()
