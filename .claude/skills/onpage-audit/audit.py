#!/usr/bin/env python3
"""
onpage-audit / audit.py

Crawl 1 URL và trích các tín hiệu SEO on-page kiểm được từ 1 lần fetch HTML,
cộng thêm Core Web Vitals qua Google PageSpeed Insights API (tùy chọn).

Chỉ dùng thư viện chuẩn (urllib, html.parser, json, re) — KHÔNG cần cài thêm.

Cách dùng:
    python3 audit.py <url> [--json out.json] [--no-psi] [--psi-key KEY]

In JSON ra stdout (và ghi file nếu có --json). Agent đọc JSON này rồi đối chiếu
checklist/onpage-criteria.md + rules/scoring-rules.md để viết báo cáo.
"""
import sys, json, re, time, argparse, os
from urllib import request, parse
from urllib.error import URLError, HTTPError
from html.parser import HTMLParser

UA = "Mozilla/5.0 (compatible; OnpageAuditBot/1.0; +https://example.com/bot)"


class SEOParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = None
        self._in_title = False
        self.meta = []            # list of dict attrs
        self.links = []           # <link> attrs
        self.headings = []        # (tag, text)
        self._cur_heading = None
        self._cur_heading_text = []
        self.images_total = 0
        self.images_without_alt = 0
        self.a_internal = 0
        self.a_external = 0
        self.a_external_no_rel = 0
        self.jsonld_blocks = []
        self._in_jsonld = False
        self._jsonld_buf = []
        self.text_chunks = []
        self.has_search_form = False
        self._script_src = []
        self._inline_script = []
        self._in_script = False
        self._cur_script_attrs = {}

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title":
            self._in_title = True
        elif tag == "meta":
            self.meta.append(a)
        elif tag == "link":
            self.links.append(a)
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self._cur_heading = tag
            self._cur_heading_text = []
        elif tag == "img":
            self.images_total += 1
            if not a.get("alt", "").strip():
                self.images_without_alt += 1
        elif tag == "a":
            href = a.get("href", "")
            rel = (a.get("rel") or "").lower()
            if href.startswith("http"):
                self.a_external += 1
                if "nofollow" not in rel and "noreferrer" not in rel:
                    self.a_external_no_rel += 1
            elif href and not href.startswith(("#", "mailto:", "tel:", "javascript:")):
                self.a_internal += 1
        elif tag == "input":
            if a.get("type", "").lower() == "search" or "search" in (a.get("name", "").lower()):
                self.has_search_form = True
        elif tag == "script":
            self._cur_script_attrs = a
            if a.get("type", "").lower() == "application/ld+json":
                self._in_jsonld = True
                self._jsonld_buf = []
            else:
                self._in_script = True
                if a.get("src"):
                    self._script_src.append(a["src"])

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6") and self._cur_heading:
            self.headings.append((self._cur_heading, "".join(self._cur_heading_text).strip()))
            self._cur_heading = None
        elif tag == "script":
            if self._in_jsonld:
                self.jsonld_blocks.append("".join(self._jsonld_buf))
                self._in_jsonld = False
            self._in_script = False

    def handle_data(self, data):
        if self._in_title:
            self.title = (self.title or "") + data
        if self._cur_heading is not None:
            self._cur_heading_text.append(data)
        if self._in_jsonld:
            self._jsonld_buf.append(data)
        if self._in_script:
            self._inline_script.append(data)
        else:
            s = data.strip()
            if s:
                self.text_chunks.append(s)


def fetch(url):
    req = request.Request(url, headers={"User-Agent": UA, "Accept-Language": "vi,en;q=0.8"})
    t0 = time.time()
    resp = request.urlopen(req, timeout=20)
    body = resp.read()
    elapsed_ms = int((time.time() - t0) * 1000)
    headers = {k.lower(): v for k, v in resp.getheaders()}
    charset = resp.headers.get_content_charset() or "utf-8"
    try:
        html = body.decode(charset, errors="replace")
    except LookupError:
        html = body.decode("utf-8", errors="replace")
    return {
        "final_url": resp.geturl(),
        "status_code": resp.status,
        "headers": headers,
        "html": html,
        "response_time_ms": elapsed_ms,
        "charset": charset,
    }


def analyze(url, do_psi=True, psi_key=None):
    out = {"url": url, "errors": []}
    try:
        f = fetch(url)
    except HTTPError as e:
        out["status_code"] = e.code
        out["errors"].append(f"HTTPError {e.code}: {e.reason}")
        return out
    except (URLError, Exception) as e:
        out["errors"].append(f"Fetch failed: {e}")
        return out

    html = f["html"]
    final_url = f["final_url"]
    headers = f["headers"]
    out.update({
        "final_url": final_url,
        "status_code": f["status_code"],
        "response_time_ms": f["response_time_ms"],
        "is_https": final_url.lower().startswith("https://"),
        "hsts": "strict-transport-security" in headers,
        "x_robots_tag": headers.get("x-robots-tag", ""),
        "charset": f["charset"].lower(),
    })

    p = SEOParser()
    try:
        p.feed(html)
    except Exception as e:
        out["errors"].append(f"Parse warning: {e}")

    # Title / meta
    title = (p.title or "").strip()
    out["title"] = title
    out["title_length"] = len(title)

    metas = {}
    meta_robots = ""
    og_tags = {}
    viewport = charset_meta = ""
    for m in p.meta:
        name = (m.get("name") or "").lower()
        prop = (m.get("property") or "").lower()
        content = m.get("content", "")
        if name == "description":
            metas["description"] = content
        if name == "robots":
            meta_robots = content.lower()
        if name == "viewport":
            viewport = content
        if prop.startswith("og:"):
            og_tags[prop] = content
        if m.get("charset"):
            charset_meta = m.get("charset")
    desc = metas.get("description", "")
    out["meta_description"] = desc
    out["meta_description_length"] = len(desc)
    out["meta_robots"] = meta_robots
    out["viewport_meta"] = bool(viewport)
    out["charset_meta"] = charset_meta or out["charset"]
    out["og_tags"] = og_tags
    out["og_complete"] = all(f"og:{k}" in og_tags for k in ("title", "description", "image", "url", "type"))

    # canonical / favicon / hreflang
    canonical = ""
    favicon = False
    hreflang = []
    for l in p.links:
        rel = (l.get("rel") or "").lower()
        if "canonical" in rel:
            canonical = l.get("href", "")
        if "icon" in rel:
            favicon = True
        if "alternate" in rel and l.get("hreflang"):
            hreflang.append(l.get("hreflang"))
    out["canonical"] = canonical
    out["canonical_matches_url"] = bool(canonical) and canonical.rstrip("/").split("#")[0] in (
        final_url.rstrip("/"), url.rstrip("/"))
    out["favicon"] = favicon
    out["hreflang"] = hreflang

    # headings
    h1 = [t for (tag, t) in p.headings if tag == "h1"]
    out["h1_count"] = len(h1)
    out["h1_texts"] = h1
    out["headings"] = [{"tag": tag, "text": t[:120]} for (tag, t) in p.headings]

    # images / links
    out["images_total"] = p.images_total
    out["images_without_alt"] = p.images_without_alt
    out["internal_links"] = p.a_internal
    out["external_links"] = p.a_external
    out["external_links_without_nofollow"] = p.a_external_no_rel

    # word count (text ngoài script)
    words = re.findall(r"\w+", " ".join(p.text_chunks))
    out["word_count"] = len(words)

    # structured data
    sd_types, sd_valid = [], True
    for block in p.jsonld_blocks:
        try:
            data = json.loads(block)
            items = data if isinstance(data, list) else [data]
            for it in items:
                if isinstance(it, dict):
                    t = it.get("@type")
                    if isinstance(t, list):
                        sd_types.extend(t)
                    elif t:
                        sd_types.append(t)
        except Exception:
            sd_valid = False
    out["structured_data_types"] = sorted(set(sd_types))
    out["structured_data_valid"] = sd_valid if p.jsonld_blocks else None

    # URL friendliness
    path = parse.urlparse(final_url).path
    out["url_length"] = len(final_url)
    out["url_friendly"] = bool(re.fullmatch(r"[a-z0-9\-/._]*", path.lower())) and "_" not in path

    # analytics
    out["has_gtm"] = bool(re.search(r"GTM-[A-Z0-9]+", html))
    out["has_ga4"] = bool(re.search(r"G-[A-Z0-9]{6,}", html))
    out["has_search_form"] = p.has_search_form

    # PageSpeed
    if do_psi:
        out["pagespeed"] = pagespeed(final_url, psi_key)
    else:
        out["pagespeed"] = {"skipped": True}
    return out


def pagespeed(url, key=None):
    res = {}
    key = key or os.environ.get("PAGESPEED_API_KEY", "")
    for strategy in ("mobile", "desktop"):
        q = {"url": url, "strategy": strategy, "category": "PERFORMANCE"}
        if key:
            q["key"] = key
        api = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed?" + parse.urlencode(q)
        try:
            req = request.Request(api, headers={"User-Agent": UA})
            data = json.loads(request.urlopen(req, timeout=60).read().decode("utf-8"))
            lh = data.get("lighthouseResult", {})
            audits = lh.get("audits", {})
            score = lh.get("categories", {}).get("performance", {}).get("score")
            res[strategy] = {
                "performance_score": round(score * 100) if score is not None else None,
                "lcp": audits.get("largest-contentful-paint", {}).get("displayValue"),
                "cls": audits.get("cumulative-layout-shift", {}).get("displayValue"),
                "tbt": audits.get("total-blocking-time", {}).get("displayValue"),
            }
        except HTTPError as e:
            res[strategy] = {"error": f"HTTP {e.code} — có thể do rate-limit; thử --psi-key"}
        except Exception as e:
            res[strategy] = {"error": str(e)}
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--json", help="ghi JSON ra file")
    ap.add_argument("--no-psi", action="store_true", help="bỏ qua PageSpeed API")
    ap.add_argument("--psi-key", help="Google PageSpeed API key (hoặc dùng env PAGESPEED_API_KEY)")
    args = ap.parse_args()

    url = args.url if args.url.startswith("http") else "https://" + args.url
    result = analyze(url, do_psi=not args.no_psi, psi_key=args.psi_key)

    txt = json.dumps(result, ensure_ascii=False, indent=2)
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            fh.write(txt)
        n_err = len(result.get("errors", []))
        print(f"[✓] Audit xong: {url}")
        print(f"[✓] JSON: {args.json} ({'có ' + str(n_err) + ' cảnh báo' if n_err else 'không lỗi'})")
    else:
        print(txt)


if __name__ == "__main__":
    main()
