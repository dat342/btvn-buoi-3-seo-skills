#!/usr/bin/env python3
"""
backlink-prospector / prospect.py

Chấm điểm danh sách domain ứng viên để chọn site NÊN đi backlink.
Nguồn ứng viên: file CSV do NGƯỜI DÙNG cung cấp lúc chạy (bảng giá vendor đã
chuẩn hóa, link-gap từ backlink-analyzer, hoặc bất kỳ CSV nào có cột domain).
KHÔNG có data nào được nhúng trong skill — xem rules/prospect-criteria.md.

Cách dùng:
    python3 prospect.py <candidates.csv> \
        [--industry "du lịch,khách sạn,ẩm thực"] \
        [--budget 5000000] [--min-dr 20] \
        --out outputs/prospects.csv

Chỉ dùng thư viện chuẩn. CSV vào: tự dò delimiter + encoding.
"""
import sys, os, csv, io, re, argparse, json

ALIASES = {
    "site":    ["site", "domain", "website", "referring domain", "đầu báo", "báo"],
    "dr":      ["dr", "domain rating"],
    "traffic": ["traffic_num", "traffic", "organic traffic", "domain traffic"],
    "topic":   ["topic", "chủ đề", "niche", "chuyên mục"],
    "price":   ["price_net_vnd", "price_list_vnd", "giá", "price", "thành tiền", "đơn giá"],
    "vendor":  ["vendor", "đơn vị bán", "nguồn"],
    "link_type": ["link_type", "loại link", "loại"],
    "links_included": ["links_included", "số link", "link"],
    "spam":    ["toxic", "is_spam", "spam", "nghi độc"],
    "linked_domains": ["linked_domains", "dofollow linked domains"],
    "market":  ["market"],
}

def read_csv_flexible(path):
    raw = open(path, "rb").read()
    text = None
    for enc in ("utf-8-sig", "utf-16", "utf-8", "latin-1"):
        try:
            text = raw.decode(enc); break
        except Exception:
            continue
    first = text.splitlines()[0] if text.splitlines() else ""
    delim = "\t" if first.count("\t") > first.count(",") else ","
    return list(csv.DictReader(io.StringIO(text), delimiter=delim))

def build_map(fieldnames):
    lower = { (f or "").lower().strip(): f for f in fieldnames }
    m = {}
    for k, al in ALIASES.items():
        for a in al:
            if a in lower:
                m[k] = lower[a]; break
    return m

def num(x):
    if x is None: return None
    s = str(x)
    # ô dính ngày tháng (2024-08-03 00:00:00) -> không phải số liệu
    if re.search(r"\d{4}-\d{2}-\d{2}", s): return None
    t = re.sub(r"[^\d.]", "", s.replace(",", "."))
    if not t: return None
    try: return float(t)
    except ValueError: return None

def get(row, m, k):
    return (row.get(m[k]) or "").strip() if k in m else ""

def score_row(row, m, industry_kw, min_dr):
    reasons_fail, bonus = [], []
    dr = num(get(row, m, "dr"))
    if dr is not None and dr > 100: dr = None  # DR hợp lệ 0-100; ngoài khoảng = data bẩn
    traffic = num(get(row, m, "traffic"))
    if traffic is not None and traffic > 10**10: traffic = None
    spam = get(row, m, "spam").lower()
    linked = num(get(row, m, "linked_domains"))
    links_inc = get(row, m, "links_included").lower()
    topic = get(row, m, "topic").lower()

    # --- 3 tiêu chí BẮT BUỘC ---
    if spam in ("true", "yes", "1"):
        reasons_fail.append("bị gắn cờ spam/độc")
    if dr is None or dr < min_dr:
        reasons_fail.append(f"DR<{min_dr} hoặc thiếu")
    if traffic is None or traffic <= 0:
        reasons_fail.append("traffic=0 hoặc thiếu")

    # --- tiêu chí CỘNG ĐIỂM ---
    if dr is not None and dr >= 40: bonus.append("DR>=40")
    if traffic is not None and traffic >= 1000: bonus.append("traffic>=1k")
    if "do" in links_inc.replace("nofollow", "").replace("no", "") or " do" in links_inc or "link do" in links_inc:
        bonus.append("dofollow")
    if linked is not None and not (linked > 5000 and (dr or 0) < 20):
        bonus.append("không nghi link farm")
    if industry_kw and topic and any(kw in topic for kw in industry_kw):
        bonus.append("đúng ngành")

    if reasons_fail:
        verdict = "Loại"
    elif len(bonus) >= 2:
        verdict = "Nên tiếp cận"
    else:
        verdict = "Cân nhắc"
    return verdict, len(bonus), bonus, reasons_fail

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("--industry", default="", help="keyword ngành, phân cách dấu phẩy")
    ap.add_argument("--budget", type=float, default=None, help="ngân sách tối đa / 1 link (VND)")
    ap.add_argument("--min-dr", type=float, default=20)
    ap.add_argument("--out", default="outputs/prospects.csv")
    args = ap.parse_args()

    rows = read_csv_flexible(args.input)
    if not rows:
        print("[!] File rỗng hoặc không đọc được.", file=sys.stderr); sys.exit(1)
    m = build_map(rows[0].keys())
    if "site" not in m:
        print(f"[!] Không tìm thấy cột domain/site. Cột hiện có: {list(rows[0].keys())}", file=sys.stderr)
        sys.exit(1)
    industry_kw = [k.strip().lower() for k in args.industry.split(",") if k.strip()]

    results = []
    for r in rows:
        site = get(r, m, "site")
        if not site: continue
        price = num(get(r, m, "price"))
        verdict, sc, bonus, fails = score_row(r, m, industry_kw, args.min_dr)
        if args.budget is not None and price is not None and price > args.budget:
            verdict, fails = "Loại", fails + [f"vượt ngân sách {int(args.budget):,}đ"]
        results.append({
            "site": site, "verdict": verdict, "bonus_score": sc,
            "bonus": "; ".join(bonus), "fail_reasons": "; ".join(fails),
            "dr": get(r, m, "dr"), "traffic": get(r, m, "traffic"),
            "topic": get(r, m, "topic"), "price_vnd": int(price) if price else "",
            "link_type": get(r, m, "link_type"), "vendor": get(r, m, "vendor"),
            "market": get(r, m, "market"),
        })

    order = {"Nên tiếp cận": 0, "Cân nhắc": 1, "Loại": 2}
    results.sort(key=lambda x: (order[x["verdict"]], -x["bonus_score"],
                                -(num(x["dr"]) or 0)))

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        w.writeheader(); w.writerows(results)

    from collections import Counter
    c = Counter(x["verdict"] for x in results)
    print(f"[✓] Đã chấm {len(results)} ứng viên -> {args.out}")
    print(f"[✓] Nên tiếp cận: {c.get('Nên tiếp cận',0)} | Cân nhắc: {c.get('Cân nhắc',0)} | Loại: {c.get('Loại',0)}")
    top = [x for x in results if x["verdict"] == "Nên tiếp cận"][:10]
    for x in top:
        print(f"    {x['site'][:40]:42} DR={x['dr']:>4} bonus={x['bonus_score']} "
              f"giá={x['price_vnd'] or 'n/a'} ({x['vendor'][:20]})")

if __name__ == "__main__":
    main()
