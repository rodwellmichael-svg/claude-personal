#!/usr/bin/env python3
"""Facebook Marketplace value finder.

  python finder.py login   # one-time: sign in to a dedicated FB account in a persistent browser profile
  python finder.py run     # search, read listings, score value, write + open an HTML report

Automating Facebook breaks Meta's terms of service. Use a dedicated account, keep
volumes low, and expect selectors to need occasional maintenance.
"""
import argparse, html, json, os, random, re, smtplib, ssl, statistics, subprocess, sys, time, webbrowser
from email.message import EmailMessage
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

import yaml
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

ROOT = Path(__file__).parent
PROFILE = ROOT / ".profile"
RESULTS = ROOT / "results"
SEEN = ROOT / ".seen.json"


BADGE = re.compile(r"^(just listed|free shipping|sponsored|pending|sold|price drop|new|\u00b7|ships.*|in stock)$", re.I)


def pause(a=1.5, b=3.5):
    time.sleep(random.uniform(a, b))


def launch(p, headless):
    opts = dict(headless=headless, viewport={"width": 1280, "height": 900}, locale="en-US")
    try:  # prefer the real Chrome app if installed: far more stable on Facebook than bundled Chromium
        return p.chromium.launch_persistent_context(str(PROFILE), channel="chrome", **opts)
    except Exception:
        return p.chromium.launch_persistent_context(str(PROFILE), **opts)


def cmd_login(_):
    with sync_playwright() as p:
        ctx = launch(p, headless=False)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto("https://www.facebook.com/marketplace/")
        input("Log in to your DEDICATED Facebook account in the browser, then press Enter here...")
        ctx.close()
    print("Session saved to", PROFILE)


def parse_price(text):
    m = re.search(r"(\d[\d,]*(?:\.\d+)?)", text.replace(" ", " "))
    return float(m.group(1).replace(",", "")) if m else None


def search_url(cfg, s):
    loc = (cfg.get("location") or "").strip().strip("/")
    base = f"https://www.facebook.com/marketplace/{loc}/search" if loc else "https://www.facebook.com/marketplace/search"
    u = f"{base}?query={quote(s['query'])}"
    if s.get("min_price") is not None:
        u += f"&minPrice={s['min_price']}"
    if s.get("max_price") is not None:
        u += f"&maxPrice={s['max_price']}"
    return u + "&sortBy=creation_time_descend&exact=false"


def collect(page, cfg, s):
    page.goto(search_url(cfg, s), wait_until="domcontentloaded")
    pause(3, 5)
    if "login" in page.url or page.locator("input[name=email]").count():
        sys.exit("Not logged in. Run: python finder.py login")
    items, last, stalls = {}, -1, 0
    for _ in range(10):  # scroll to load more
        for a in page.locator("a[href*='/marketplace/item/']").all():
            href = a.get_attribute("href") or ""
            m = re.search(r"/marketplace/item/(\d+)", href)
            if not m or m.group(1) in items:
                continue
            lines = [l.strip() for l in a.inner_text().split("\n") if l.strip()]
            lines = [l for l in lines if not BADGE.match(l)]
            price_re = re.compile(r"^(free|[£$€]\s*[\d,]+(\.\d+)?)", re.I)
            price_lines = [l for l in lines if price_re.match(l)]
            if not price_lines:
                continue
            price_line = price_lines[0]
            rest = [l for l in lines if not price_re.match(l)]
            if not rest:
                continue
            items[m.group(1)] = {
                "id": m.group(1),
                "url": f"https://www.facebook.com/marketplace/item/{m.group(1)}/",
                "price_text": price_line,
                "price": 0.0 if price_line.lower().startswith("free") else parse_price(price_line),
                "title": rest[0],
                "location": rest[1] if len(rest) > 1 else "",
                "description": "",
                "search": s["name"],
            }
        if len(items) >= cfg["max_listings_per_search"]:
            break
        stalls = stalls + 1 if len(items) == last else 0
        if stalls >= 3:
            break
        last = len(items)
        page.mouse.move(820, 520)  # cursor must be over the results pane or the wheel scrolls nothing
        page.mouse.wheel(0, 3000)
        page.keyboard.press("End")
        pause(3, 5)
    RESULTS.mkdir(exist_ok=True)
    shot = RESULTS / "last_search.png"
    try:
        page.screenshot(path=str(shot))
    except Exception:
        pass
    print(f"  page: {page.url}\n  screenshot: {shot}")
    return list(items.values())[: cfg["max_listings_per_search"]]


def prefilter(items, s):
    must = [k.lower() for k in s.get("must_include", [])]
    bad = [k.lower() for k in s.get("exclude", [])]
    out = []
    for it in items:
        blob = f"{it['title']} {it['description']}".lower()
        if it["price"] is None or any(k in blob for k in bad):
            continue
        if must and not all(k in blob for k in must):
            continue
        out.append(it)
    return out


def in_area(it, s):
    areas = [a.lower() for a in s.get("areas", [])]
    if not areas:
        return True
    return any(a in it["location"].lower() for a in areas)


def fetch_detail(page, it):
    try:
        page.goto(it["url"], wait_until="domcontentloaded")
        pause(2, 4)
        main = page.locator("div[role=main]").first
        text = main.inner_text() if main.count() else page.inner_text("body")
        it["description"] = re.sub(r"\n{2,}", "\n", text)[:2500]
    except Exception as e:  # timeouts, page crashes: skip this listing, keep the run alive
        print("  skipped detail page:", type(e).__name__)


def year_filter(items, s):
    """Keep only the wanted model year, plus listings whose year is unknown."""
    want = s.get("only_year")
    if not want:
        return items
    keep = []
    for i in items:
        year = i.get("year")
        if year is None and "year" not in i:  # no AI: fall back to years named in the title
            found = {int(y) for y in re.findall(r"\b(20[01]\d|202\d)\b", i["title"])}
            year = None if not found or want in found else min(found)
        if year is None or int(year) == int(want):
            keep.append(i)
    print(f"  year filter ({want} or unknown): kept {len(keep)} of {len(items)}")
    return keep


def heuristic_score(items):
    prices = [i["price"] for i in items if i["price"]]
    med = statistics.median(prices) if prices else 0
    for i in items:
        ratio = (i["price"] / med) if med and i["price"] else 1
        i.update(value_score=max(0, min(100, int(100 - ratio * 50))),
                 verdict="maybe", fair_price=med,
                 reasons=f"Priced at {ratio:.0%} of the median ({med:.0f}) of this search (no AI scoring).",
                 red_flags="")
    return items


def claude_score(items, s, model):
    import anthropic
    slim = [{k: i[k] for k in ("id", "price_text", "title", "location", "description")} for i in items]
    prompt = f"""I'm buying: {s['name']}.
My brief: {s.get('wanted', '')}
Budget: {s.get('min_price', 0)} - {s.get('max_price', 'any')} (UK market, GBP).

Below are Facebook Marketplace listings as JSON (description is raw page text and may include
unrelated UI text). Judge VALUE: price vs. likely fair used-market price given the spec,
condition and completeness in the description, match to my brief, seller/scam red flags
(too-cheap, deposits, off-platform payment, stock photos, vague text). Be sceptical and
don't invent specs that aren't stated.

Also work out the MODEL YEAR of each machine. Use the year if the listing states it, otherwise
infer it only when the hardware makes it clear (CPU generation, GPU, display type, "Late 2015" etc.).
If it is genuinely ambiguous (e.g. only "2019/2020 style" or a model number shared by two years such
as A2115, which covers both 2019 and 2020), return null. Never guess.

Return ONLY a JSON array, one object per listing:
{{"id": str, "value_score": 0-100, "verdict": "buy"|"maybe"|"skip", "fair_price": number|null,
  "year": integer|null, "year_basis": "stated"|"inferred from hardware"|"unknown",
  "reasons": "1-2 sentences", "red_flags": "short or empty"}}

LISTINGS:
{json.dumps(slim, ensure_ascii=False)}"""
    resp = anthropic.Anthropic().messages.create(
        model=model, max_tokens=8000, messages=[{"role": "user", "content": prompt}])
    text = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
    data = json.loads(text[text.index("["): text.rindex("]") + 1])
    by_id = {str(d["id"]): d for d in data}
    for i in items:
        d = by_id.get(i["id"], {})
        i.update(value_score=d.get("value_score", 0), verdict=d.get("verdict", "skip"),
                 fair_price=d.get("fair_price"), year=d.get("year"),
                 year_basis=d.get("year_basis", "unknown"), reasons=d.get("reasons", "not scored"),
                 red_flags=d.get("red_flags", ""))
    return items


def build_html(results):
    rows = []
    for name, items in results.items():
        rows.append(f"<h2>{html.escape(name)}</h2>")
        if not items:
            rows.append("<p>No listings passed the filters.</p>")
        for n, i in enumerate(sorted(items, key=lambda x: -x["value_score"])):
            star = " ⭐ top pick" if n == 0 else ""
            fair = f" · est. fair {i['fair_price']:.0f}" if i.get("fair_price") else ""
            rows.append(
                f"<div class='c {i['verdict']}'><b>{i['value_score']}</b> "
                f"<a href='{i['url']}'>{html.escape(i['title'])}</a>{star}<br>"
                f"{html.escape(i['price_text'])}{fair} · {html.escape(i['location'])} · "
                f"<i>{i['verdict']}</i>{' · NEW' if i.get('new') else ''}"
                f" · {('model year ' + str(i['year']) + ' (' + i.get('year_basis', '') + ')') if i.get('year') else 'year unknown'}<br>"
                f"{html.escape(i['reasons'])}"
                + (f"<br><span class='f'>⚠ {html.escape(i['red_flags'])}</span>" if i["red_flags"] else "")
                + "</div>")
    return (
        "<meta charset=utf-8><title>Marketplace results</title><style>"
        "body{font:15px system-ui;max-width:820px;margin:2em auto;padding:0 1em}"
        ".c{border:1px solid #ccc;border-left:6px solid #aaa;border-radius:6px;padding:.6em .8em;margin:.6em 0}"
        ".buy{border-left-color:#2a9d3f}.maybe{border-left-color:#e0a800}.skip{opacity:.6}"
        ".f{color:#b00020}</style>"
        f"<h1>Marketplace results · {datetime.now():%Y-%m-%d %H:%M}</h1>" + "".join(rows))


def render(results, path):
    path.write_text(build_html(results))


def send_email(subject, text, html_body=None):
    host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    port = int(os.environ.get("SMTP_PORT", "587"))
    user, pw, to = os.environ.get("SMTP_USER"), os.environ.get("SMTP_PASSWORD"), os.environ.get("EMAIL_TO")
    if not (user and pw and to):
        raise RuntimeError("Set SMTP_USER, SMTP_PASSWORD and EMAIL_TO in marketplace-finder/.env")
    msg = EmailMessage()
    msg["Subject"], msg["From"], msg["To"] = subject, user, to
    msg.set_content(text)
    if html_body:
        msg.add_alternative(html_body, subtype="html")
    with smtplib.SMTP(host, port, timeout=30) as smtp:
        smtp.starttls(context=ssl.create_default_context())
        smtp.login(user, pw)
        smtp.send_message(msg)


def email_report(results, out):
    items = [i for lst in results.values() for i in lst]
    new = [i for i in items if i.get("new") and i["verdict"] != "skip"]
    buys = [i for i in new if i["verdict"] == "buy"]
    if new:
        subject = f"Marketplace iMacs: {len(new)} new ({len(buys)} buy)"
    else:
        subject = "Marketplace iMacs: no new listings"
    lines = [f"{len(items)} listings checked, {len(new)} new and worth a look.", ""]
    for i in sorted(new, key=lambda x: -x["value_score"])[:10]:
        lines.append(f"[{i['verdict']} {i['value_score']}] {i['price_text']} {i['title']} - {i['location']}\n  {i['url']}")
    lines.append(f"\nFull report: {out}")
    send_email(subject, "\n".join(lines), build_html(results))
    print("Email sent:", subject)


def notify(title, message):
    """macOS notification banner (no passwords needed). Silently does nothing off macOS."""
    try:
        subprocess.run(
            ["osascript", "-e", "on run argv", "-e", "display notification (item 1 of argv) with title (item 2 of argv)",
             "-e", "end run", message[:200], title[:100]], check=False, timeout=15)
    except Exception:
        pass


def summarise(results):
    items = [i for lst in results.values() for i in lst]
    new = [i for i in items if i.get("new") and i["verdict"] != "skip"]
    buys = [i for i in new if i["verdict"] == "buy"]
    best = max(new, key=lambda x: x["value_score"], default=None)
    return items, new, buys, best


def cmd_test_email(_):
    send_email("Marketplace finder: test email", "Email settings work.")
    print("Test email sent to", os.environ.get("EMAIL_TO"))


def load_env():
    """Read KEY=value lines from marketplace-finder/.env (git-ignored) so scheduled runs see them."""
    f = ROOT / ".env"
    if not f.exists():
        return
    for line in f.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip("\"'"))


def cmd_run(args):
    cfg = yaml.safe_load((ROOT / "config.yaml").read_text())
    seen = set(json.loads(SEEN.read_text())) if SEEN.exists() else set()
    use_ai = bool(os.environ.get("ANTHROPIC_API_KEY")) and not args.no_ai
    if not use_ai:
        print("ANTHROPIC_API_KEY not set (or --no-ai): using simple price heuristic.")
    results = {}
    run_seen = set()  # listing ids already reported by an earlier search in this run
    with sync_playwright() as p:
        ctx = launch(p, headless=args.headless)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        for s in cfg["searches"]:
            print(f"Searching: {s['name']}")
            try:
                scfg = {**cfg, "location": s.get("location", cfg.get("location", ""))}
                found = collect(page, scfg, s)
                nearby = [i for i in found if in_area(i, s) and i["id"] not in run_seen]
                run_seen.update(i["id"] for i in found)
                items = prefilter(nearby, s)
                print(f"  found {len(found)} listings, {len(nearby)} in your areas, {len(items)} passed filters")
            except Exception as e:
                print("Search failed:", type(e).__name__, str(e)[:200])
                results[s["name"]] = []
                continue
            for it in items[: cfg["max_detail_pages"]]:
                try:
                    fetch_detail(page, it)
                except Exception:
                    page = ctx.new_page()  # recover from a crashed tab
                pause()
            items = prefilter(items, s)
            for it in items:
                it["new"] = it["id"] not in seen
            if items:
                try:
                    items = claude_score(items, s, cfg["model"]) if use_ai else heuristic_score(items)
                except Exception as e:  # fall back rather than lose the run
                    print("AI scoring failed, using heuristic:", e)
                    items = heuristic_score(items)
            items = year_filter(items, s)
            results[s["name"]] = items
            seen.update(i["id"] for i in items)
        ctx.close()
    RESULTS.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M")
    out = RESULTS / f"{stamp}.html"
    render(results, out)
    (RESULTS / f"{stamp}.json").write_text(json.dumps(results, indent=2))
    SEEN.write_text(json.dumps(sorted(seen)))
    print("Report:", out)
    (RESULTS / "latest.html").write_text(out.read_text())  # always-current copy to open
    if args.notify:
        _, new, buys, best = summarise(results)
        if best:
            notify(f"iMacs: {len(new)} new ({len(buys)} buy)",
                   f"Best: {best['price_text']} {best['title']} - {best['location']}. Open results/latest.html")
        else:
            notify("iMacs: no new listings", "Nothing new since the last check.")
    if args.email:
        try:
            email_report(results, out)
        except Exception as e:
            print("Email failed:", type(e).__name__, e)
    if not args.no_open:
        webbrowser.open(out.as_uri())


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("login").set_defaults(fn=cmd_login)
    r = sub.add_parser("run")
    r.add_argument("--headless", action="store_true", help="hide the browser (more likely to be flagged)")
    r.add_argument("--no-ai", action="store_true")
    r.add_argument("--no-open", action="store_true")
    r.add_argument("--email", action="store_true", help="email a summary and the report when done")
    r.add_argument("--notify", action="store_true", help="show a macOS notification when done")
    r.set_defaults(fn=cmd_run)
    sub.add_parser("test-email").set_defaults(fn=cmd_test_email)
    load_env()
    a = ap.parse_args()
    try:
        a.fn(a)
    except BaseException as e:  # a scheduled run that dies silently is worse than an alert
        if getattr(a, "notify", False) and not isinstance(e, KeyboardInterrupt):
            notify("iMac search FAILED", f"{type(e).__name__}: {e}"[:150])
        if getattr(a, "email", False) and not isinstance(e, KeyboardInterrupt):
            try:
                send_email("Marketplace finder FAILED", f"{type(e).__name__}: {e}\n\nIf it says 'Not logged in', run: python finder.py login")
            except Exception:
                pass
        raise
