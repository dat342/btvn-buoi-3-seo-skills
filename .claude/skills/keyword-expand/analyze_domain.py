#!/usr/bin/env python3
"""
analyze_domain.py — Đọc nội dung 1 website (trang chủ + vài trang từ sitemap),
rút ra các CỤM TỪ ỨNG VIÊN làm từ khóa hạt nhân, in ra JSON để Claude tinh chỉnh.

Chỉ dùng thư viện chuẩn. Không cào quá vài trang (lịch sự + nhanh).

Cách dùng:
    python3 analyze_domain.py hacom.vn
    python3 analyze_domain.py https://example.com --max-pages 8
"""
import argparse
import json
import re
import sys
import time
import urllib.request
import urllib.error
import urllib.parse
from collections import Counter
from html.parser import HTMLParser

UA = {"User-Agent": "Mozilla/5.0 (compatible; keyword-expand/1.0)"}

# Mục nav/điều hướng phổ biến — KHÔNG phải chủ đề, loại khỏi ứng viên seed.
NAV_STOP = {
    "trang chủ", "trang chu", "home", "liên hệ", "lien he", "giới thiệu", "gioi thieu",
    "về chúng tôi", "ve chung toi", "tin tức", "tin tuc", "blog", "đăng nhập", "dang nhap",
    "đăng ký", "dang ky", "giỏ hàng", "gio hang", "tài khoản", "tai khoan", "chính sách",
    "chinh sach", "điều khoản", "dieu khoan", "tuyển dụng", "tuyen dung", "sitemap",
    "tìm kiếm", "tim kiem", "search", "hotline", "khuyến mãi", "khuyen mai", "menu",
    "xem thêm", "xem them", "chi tiết", "chi tiet", "đọc tiếp", "doc tiep", "facebook",
    "youtube", "zalo", "english", "tiếng việt", "tieng viet", "câu hỏi thường gặp",
    "instagram", "tiktok", "facebook", "news", "feedback", "twitter", "telegram",
    "tra cứu đơn hàng", "giỏ hàng0", "0giỏ hàng", "xem giỏ hàng", "thanh toán",
}


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.meta_desc = ""
        self.meta_kw = ""
        self.og_title = ""
        self.og_site = ""
        self.h = {"h1": [], "h2": [], "h3": []}
        self.anchors = []
        self._stack = []
        self._buf = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "meta":
            name = (a.get("name") or a.get("property") or "").lower()
            content = (a.get("content") or "").strip()
            if name == "description":
                self.meta_desc = content
            elif name == "keywords":
                self.meta_kw = content
            elif name == "og:title":
                self.og_title = content
            elif name == "og:site_name":
                self.og_site = content
        if tag in ("title", "h1", "h2", "h3", "a"):
            self._stack.append(tag)
            self._buf = []

    def handle_data(self, data):
        if self._stack:
            self._buf.append(data)

    def handle_endtag(self, tag):
        if self._stack and self._stack[-1] == tag:
            text = re.sub(r"\s+", " ", "".join(self._buf)).strip()
            if tag == "title":
                self.title = text
            elif tag in self.h and text:
                self.h[tag].append(text)
            elif tag == "a" and text:
                self.anchors.append(text)
            self._stack.pop()
            self._buf = []


def fetch(url, timeout=20):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        ctype = r.headers.get_content_charset() or "utf-8"
        return r.read().decode(ctype, "replace")


def normalize_base(domain):
    domain = domain.strip()
    if not domain.startswith("http"):
        domain = "https://" + domain
    p = urllib.parse.urlparse(domain)
    return f"{p.scheme}://{p.netloc}", p.netloc


def get_sitemap_urls(base, limit=6):
    """Tìm sitemap qua robots.txt + đường dẫn quen thuộc, trả vài URL trang chính."""
    candidates = []
    sitemaps = []
    # robots.txt
    try:
        robots = fetch(base + "/robots.txt", timeout=10)
        sitemaps += re.findall(r"(?i)sitemap:\s*(\S+)", robots)
    except Exception:
        pass
    sitemaps += [base + "/sitemap.xml", base + "/sitemap_index.xml"]

    seen_sm = set()
    for sm in sitemaps:
        if sm in seen_sm or len(candidates) >= 40:
            continue
        seen_sm.add(sm)
        try:
            xml = fetch(sm, timeout=15)
        except Exception:
            continue
        locs = re.findall(r"<loc>\s*([^<]+?)\s*</loc>", xml)
        # nếu là sitemap index (trỏ tới sitemap con) → lấy 1 sitemap con đầu
        if "<sitemapindex" in xml.lower() and locs:
            for child in locs[:2]:
                if child in seen_sm:
                    continue
                seen_sm.add(child)
                try:
                    cxml = fetch(child, timeout=15)
                    candidates += re.findall(r"<loc>\s*([^<]+?)\s*</loc>", cxml)
                except Exception:
                    pass
        else:
            candidates += locs
        if candidates:
            break

    # Ưu tiên URL đường dẫn ngắn (thường là trang danh mục), bỏ trang chủ
    candidates = [u for u in dict.fromkeys(candidates) if u.rstrip("/") != base.rstrip("/")]
    candidates.sort(key=lambda u: (urllib.parse.urlparse(u).path.count("/"), len(u)))
    return candidates[:limit]


def build_candidates(pages):
    """Gom heading + anchor (danh mục) thành cụm ứng viên, đếm tần suất."""
    counter = Counter()
    for pg in pages:
        weighted = pg["h1"] * 3 + pg["h2"] * 2 + pg["h3"] + pg["anchors"]
        for raw in weighted:
            t = re.sub(r"\s+", " ", raw).strip().lower()
            t = t.strip(" -|·•:•—")
            if not t or t in NAV_STOP:
                continue
            words = t.split()
            if len(t) < 3 or len(words) > 7 or len(words) < 1:
                continue
            if re.fullmatch(r"[\d\W]+", t):  # toàn số/ký hiệu
                continue
            counter[t] += 1
    return [w for w, _ in counter.most_common(40)]


def main():
    ap = argparse.ArgumentParser(description="Phân tích domain → cụm từ ứng viên")
    ap.add_argument("domain", help="vd: hacom.vn hoặc https://example.com")
    ap.add_argument("--max-pages", type=int, default=6, help="Số trang sitemap cào thêm")
    args = ap.parse_args()

    base, netloc = normalize_base(args.domain)
    urls = [base]
    try:
        urls += get_sitemap_urls(base, limit=args.max_pages)
    except Exception as e:
        print(f"[!] Không đọc được sitemap: {e}", file=sys.stderr)
    urls = list(dict.fromkeys(urls))

    pages = []
    for u in urls:
        try:
            html = fetch(u)
        except Exception as e:
            print(f"[!] Bỏ qua {u}: {e}", file=sys.stderr)
            continue
        p = PageParser()
        try:
            p.feed(html)
        except Exception:
            pass
        pages.append({
            "url": u,
            "title": p.title,
            "description": p.meta_desc,
            "keywords": p.meta_kw,
            "og_title": p.og_title,
            "og_site": p.og_site,
            "h1": p.h["h1"][:15],
            "h2": p.h["h2"][:25],
            "h3": p.h["h3"][:25],
            "anchors": p.anchors[:60],
        })
        time.sleep(0.2)

    result = {
        "domain": netloc,
        "base": base,
        "pages_fetched": len(pages),
        "site_name": next((p["og_site"] for p in pages if p["og_site"]), netloc),
        "candidates": build_candidates(pages),
        "pages": pages,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
