#!/usr/bin/env python3
"""
Apache Web Server Access Log Generator
Generates 10,000 synthetic log lines in Apache Combined Log Format
Output: spooling_dir/access.log
"""

import random
import datetime
import os

# ── Configuration ──────────────────────────────────────────────────
TOTAL_LINES    = 10_000
OUTPUT_DIR     = "/opt/spooling_dir"
OUTPUT_FILE    = os.path.join(OUTPUT_DIR, "access.log")

# ── Sample Data ────────────────────────────────────────────────────
IP_POOL = [
    "192.168.1.{}".format(i) for i in range(1, 50)
] + [
    "10.0.0.{}".format(i) for i in range(1, 30)
] + [
    "172.16.{}.{}".format(a, b) for a in range(1, 5) for b in range(1, 10)
] + [
    "203.0.113.{}".format(i) for i in range(1, 20)
]

HTTP_METHODS  = ["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"]
HTTP_VERSIONS = ["HTTP/1.0", "HTTP/1.1", "HTTP/2.0"]

ENDPOINTS = [
    "/", "/index.html", "/about", "/contact", "/login", "/logout",
    "/dashboard", "/api/v1/users", "/api/v1/products", "/api/v1/orders",
    "/api/v2/search", "/api/v2/auth/token", "/static/css/main.css",
    "/static/js/app.js", "/static/img/logo.png", "/favicon.ico",
    "/robots.txt", "/sitemap.xml", "/health", "/metrics",
    "/admin", "/admin/users", "/admin/reports", "/admin/settings",
    "/products", "/products/detail/123", "/cart", "/checkout",
    "/blog", "/blog/post/1", "/blog/post/2", "/blog/post/3",
    "/search?q=apache", "/search?q=hadoop", "/search?q=flume",
    "/download/report.pdf", "/upload", "/api/v1/logs",
]

STATUS_WEIGHTS = {
    200: 55,   # OK
    201: 5,    # Created
    204: 3,    # No Content
    301: 3,    # Moved Permanently
    302: 3,    # Found
    304: 5,    # Not Modified
    400: 5,    # Bad Request
    401: 4,    # Unauthorized
    403: 3,    # Forbidden
    404: 8,    # Not Found
    405: 2,    # Method Not Allowed
    429: 1,    # Too Many Requests
    500: 1,    # Internal Server Error
    502: 1,    # Bad Gateway
    503: 1,    # Service Unavailable
}

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_1 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Android 14; Mobile; rv:121.0) Gecko/121.0 Firefox/121.0',
    'curl/8.4.0',
    'python-requests/2.31.0',
    'PostmanRuntime/7.36.0',
    'Apache-HttpClient/4.5.14 (Java/17)',
    'Googlebot/2.1 (+http://www.google.com/bot.html)',
    'Bingbot/2.0; +http://www.bing.com/bingbot.htm',
    'facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)',
]

REFERRERS = [
    "-", "-", "-", "-",   # most requests have no referrer
    "https://www.google.com/",
    "https://www.bing.com/",
    "https://example.com/",
    "https://github.com/",
    "https://stackoverflow.com/",
]

# ── Helpers ────────────────────────────────────────────────────────
def weighted_choice(weight_dict):
    population = list(weight_dict.keys())
    weights    = list(weight_dict.values())
    return random.choices(population, weights=weights, k=1)[0]

def random_bytes(status_code):
    if status_code in (204, 304):
        return 0
    if status_code >= 400:
        return random.randint(100, 2048)
    return random.randint(512, 51200)

def format_timestamp(dt):
    offset = "+0530"
    return dt.strftime(f"%d/%b/%Y:%H:%M:%S {offset}")

def generate_line(dt):
    ip          = random.choice(IP_POOL)
    ident       = "-"
    user        = "-"
    timestamp   = format_timestamp(dt)
    method      = random.choice(HTTP_METHODS)
    endpoint    = random.choice(ENDPOINTS)
    version     = random.choice(HTTP_VERSIONS)
    status      = weighted_choice(STATUS_WEIGHTS)
    size        = random_bytes(status)
    referrer    = random.choice(REFERRERS)
    user_agent  = random.choice(USER_AGENTS)

    return (
        f'{ip} {ident} {user} [{timestamp}] '
        f'"{method} {endpoint} {version}" '
        f'{status} {size} "{referrer}" "{user_agent}"'
    )

# ── Main ───────────────────────────────────────────────────────────
def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Spread 10 000 events across last 7 days
    end_dt   = datetime.datetime.now()
    start_dt = end_dt - datetime.timedelta(days=7)
    span_sec = int((end_dt - start_dt).total_seconds())

    print(f"[generate_logs] Generating {TOTAL_LINES:,} log lines …")
    print(f"[generate_logs] Time range : {start_dt}  →  {end_dt}")
    print(f"[generate_logs] Output     : {OUTPUT_FILE}")

    timestamps = sorted(
        start_dt + datetime.timedelta(seconds=random.randint(0, span_sec))
        for _ in range(TOTAL_LINES)
    )

    with open(OUTPUT_FILE, "w", encoding="utf-8") as fh:
        for dt in timestamps:
            fh.write(generate_line(dt) + "\n")

    # Verify
    with open(OUTPUT_FILE, "r") as fh:
        count = sum(1 for _ in fh)

    print(f"[generate_logs] ✅  Done!  {count:,} lines written to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
