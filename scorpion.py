#!/usr/bin/env python3
"""
 ____  _   _ ____    ____                        _
|  _ \| \ | / ___|  / ___|  ___ ___  _ __ _ __ (_) ___  _ __
| | | |  \| \___ \  \___ \ / __/ _ \| '__| '_ \| |/ _ \| '_ \
| |_| | |\  |___) |  ___) | (_| (_) | |  | |_) | | (_) | | | |
|____/|_| \_|____/  |____/ \___\___/|_|  | .__/|_|\___/|_| |_|
                                          |_|
dns_scorpion.py  v1.1 FINAL
Powered by Sailerbross Technology
The DNS tool that makes dig obsolete.
Termux-safe | 15+ record types | ASN | SSL | Headers |
Spoof-test | Auto-recon | HTML report | Industry-grade
"""

import sys
import os
import json
import csv
import time
import socket
import ssl
import random
import string
import threading
import argparse
import re
import hashlib
from queue       import Queue, Empty
from datetime    import datetime
from collections import defaultdict

# ============================================================
# DEPENDENCY CHECK
# ============================================================
try:
    import dns.resolver
    import dns.reversename
    import dns.zone
    import dns.query
    import dns.rdatatype
    import dns.exception
    import dns.flags
    DNS_OK = True
except ImportError:
    DNS_OK = False

try:
    import urllib.request
    import urllib.error
    HTTP_OK = True
except ImportError:
    HTTP_OK = False

# ============================================================
# COLORS
# ============================================================
class C:
    RED     = '\033[91m'
    GREEN   = '\033[92m'
    YELLOW  = '\033[93m'
    BLUE    = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN    = '\033[96m'
    WHITE   = '\033[97m'
    RESET   = '\033[0m'
    BOLD    = '\033[1m'
    DIM     = '\033[2m'
    ORANGE  = '\033[38;5;208m'
    PURPLE  = '\033[38;5;141m'

def co(text, *colors):
    return "".join(colors) + str(text) + C.RESET

def clr():
    os.system('cls' if os.name == 'nt' else 'clear')

# ============================================================
# RECORD TYPE COLORS
# ============================================================
REC_COLOR = {
    'A':      C.GREEN,
    'AAAA':   C.CYAN,
    'MX':     C.YELLOW,
    'NS':     C.BLUE,
    'TXT':    C.MAGENTA,
    'CNAME':  C.ORANGE,
    'SOA':    C.PURPLE,
    'PTR':    C.WHITE,
    'SRV':    C.CYAN,
    'CAA':    C.RED,
    'DNSKEY': C.YELLOW,
    'DS':     C.YELLOW,
    'TLSA':   C.BLUE,
    'NAPTR':  C.MAGENTA,
}

# ============================================================
# FALLBACK NAMESERVERS (Termux-safe)
# ============================================================
FALLBACK_NS = [
    "8.8.8.8",          # Google Primary
    "8.8.4.4",          # Google Secondary
    "1.1.1.1",          # Cloudflare Primary
    "1.0.0.1",          # Cloudflare Secondary
    "9.9.9.9",          # Quad9
    "208.67.222.222",   # OpenDNS
]

# ============================================================
# GLOBAL PROPAGATION SERVERS
# ============================================================
PROP_SERVERS = {
    "Google (US)":        "8.8.8.8",
    "Google-2 (US)":      "8.8.4.4",
    "Cloudflare (US)":    "1.1.1.1",
    "Cloudflare-2 (US)":  "1.0.0.1",
    "Quad9 (US)":         "9.9.9.9",
    "OpenDNS (US)":       "208.67.222.222",
    "OpenDNS-2 (US)":     "208.67.220.220",
    "Comodo (US)":        "8.26.56.26",
    "Level3 (US)":        "209.244.0.3",
    "Verisign (US)":      "64.6.64.6",
    "CleanBrowsing (EU)": "185.228.168.9",
    "AdGuard (EU)":       "94.140.14.14",
    "dns.watch (DE)":     "84.200.69.80",
    "Freenom (AS)":       "80.80.80.80",
    "Alternate DNS":      "76.76.19.19",
}

# ============================================================
# DNS PROVIDER FINGERPRINTS
# ============================================================
DNS_PROVIDERS = {
    "cloudflare":        "Cloudflare",
    "awsdns":            "Amazon Route 53",
    "azure-dns":         "Microsoft Azure DNS",
    "googledomains":     "Google Domains",
    "google.com":        "Google Cloud DNS",
    "domaincontrol":     "GoDaddy",
    "namecheap":         "Namecheap",
    "name.com":          "Name.com",
    "dnsimple":          "DNSimple",
    "dynect":            "Dyn (Oracle)",
    "ultradns":          "UltraDNS",
    "nsone":             "NS1",
    "digitalocean":      "DigitalOcean",
    "linode":            "Linode/Akamai",
    "vultr":             "Vultr",
    "hurricane":         "Hurricane Electric",
    "rackspace":         "Rackspace",
    "wpengine":          "WP Engine",
    "netlify":           "Netlify",
    "vercel-dns":        "Vercel",
    "squarespace":       "Squarespace",
    "shopify":           "Shopify",
}

# ============================================================
# CDN FINGERPRINTS
# ============================================================
CDN_FINGERPRINTS = {
    "cloudflare":        "Cloudflare CDN",
    "akamai":            "Akamai",
    "fastly":            "Fastly",
    "cloudfront":        "Amazon CloudFront",
    "edgekey":           "Akamai EdgeSuite",
    "edgesuite":         "Akamai EdgeSuite",
    "azureedge":         "Microsoft Azure CDN",
    "stackpathdns":      "StackPath CDN",
    "maxcdn":            "MaxCDN",
    "incapdns":          "Imperva Incapsula",
    "sucuri":            "Sucuri WAF/CDN",
    "googlehosted":      "Google Hosted",
    "wpengine":          "WP Engine CDN",
    "netlify":           "Netlify CDN",
    "vercel":            "Vercel Edge",
    "bunnycdn":          "BunnyCDN",
}

# ============================================================
# MAIL PROVIDER FINGERPRINTS
# ============================================================
MAIL_PROVIDERS = {
    "google":              "Google Workspace",
    "gmail":               "Gmail",
    "outlook":             "Microsoft 365",
    "hotmail":             "Microsoft Hotmail",
    "office365":           "Microsoft Office 365",
    "protection.outlook":  "Microsoft EOP",
    "yahoodns":            "Yahoo Mail",
    "mimecast":            "Mimecast",
    "proofpoint":          "Proofpoint",
    "barracuda":           "Barracuda",
    "mailgun":             "Mailgun",
    "sendgrid":            "SendGrid",
    "amazonses":           "Amazon SES",
    "zoho":                "Zoho Mail",
    "fastmail":            "FastMail",
    "protonmail":          "ProtonMail",
    "icloud":              "Apple iCloud Mail",
}

# ============================================================
# DKIM SELECTORS
# ============================================================
DKIM_SELECTORS = [
    "default", "google", "mail", "email",
    "k1", "k2", "k3",
    "selector1", "selector2",
    "s1", "s2",
    "dkim", "dkimmail",
    "smtp", "smtpapi",
    "sendgrid", "mailgun",
    "protonmail", "zoho", "mimecast",
    "20161025", "20210112", "20230601",
]

# ============================================================
# RECORD EXPLANATIONS
# ============================================================
RECORD_EXPLAIN = {
    'A':      "Maps domain to IPv4 address (web server location)",
    'AAAA':   "Maps domain to IPv6 address",
    'MX':     "Mail server — where emails are delivered",
    'NS':     "Nameservers — who controls DNS for this domain",
    'TXT':    "Text records — SPF, DKIM, verification tokens",
    'CNAME':  "Alias — points this name to another domain",
    'SOA':    "Start of Authority — DNS zone admin info",
    'PTR':    "Reverse DNS — maps IP back to hostname",
    'SRV':    "Service record — VoIP, XMPP, game servers",
    'CAA':    "Certificate Authority Authorization — SSL control",
    'DNSKEY': "DNSSEC public key — DNS signature verification",
    'DS':     "DNSSEC Delegation Signer",
    'TLSA':   "TLS certificate association (DANE)",
    'NAPTR':  "Naming Authority Pointer — VoIP/SIP routing",
}

# ============================================================
# HTTP SECURITY HEADERS
# ============================================================
SECURITY_HEADERS = {
    "Strict-Transport-Security": {
        "alias": "HSTS",
        "desc":  "Forces HTTPS connections",
        "risk":  "Without this, downgrade attacks possible",
    },
    "Content-Security-Policy": {
        "alias": "CSP",
        "desc":  "Controls resource loading, prevents XSS",
        "risk":  "Without this, XSS attacks easier",
    },
    "X-Frame-Options": {
        "alias": "XFO",
        "desc":  "Prevents clickjacking via iframes",
        "risk":  "Without this, clickjacking possible",
    },
    "X-Content-Type-Options": {
        "alias": "XCTO",
        "desc":  "Prevents MIME-type sniffing",
        "risk":  "Without this, MIME confusion attacks possible",
    },
    "Referrer-Policy": {
        "alias": "RP",
        "desc":  "Controls referrer info in requests",
        "risk":  "Without this, sensitive URLs may leak",
    },
    "Permissions-Policy": {
        "alias": "PP",
        "desc":  "Controls browser feature access",
        "risk":  "Without this, features may be abused",
    },
    "X-XSS-Protection": {
        "alias": "XSS",
        "desc":  "Legacy XSS filter (older browsers)",
        "risk":  "Deprecated but still checked",
    },
    "Cross-Origin-Opener-Policy": {
        "alias": "COOP",
        "desc":  "Isolates browsing context",
        "risk":  "Without this, Spectre-style attacks possible",
    },
    "Cross-Origin-Resource-Policy": {
        "alias": "CORP",
        "desc":  "Controls cross-origin resource access",
        "risk":  "Without this, cross-origin data leaks possible",
    },
}

# ============================================================
# SNAPSHOT DIRECTORY
# ============================================================
SNAPSHOT_DIR = os.path.join(
    os.path.expanduser("~"), ".dns_scorpion_snapshots"
)

# ============================================================
# BANNER
# ============================================================
def print_banner():
    print(f"""
{C.YELLOW}{C.BOLD}
  ____  _   _ ____    ____                        _
 |  _ \| \ | / ___|  / ___|  ___ ___  _ __ _ __ (_) ___  _ __
 | | | |  \| \___ \  \___ \ / __/ _ \| '__| '_ \| |/ _ \| '_ \\
 | |_| | |\  |___) |  ___) | (_| (_) | |  | |_) | | (_) | | | |
 |____/|_| \_|____/  |____/ \___\___/|_|  | .__/|_|\___/|_| |_|
                                           |_|
{C.RESET}{C.CYAN}{C.BOLD} DNS Scorpion v1.1 FINAL — Industry-Grade DNS Auditing Suite{C.RESET}
{C.MAGENTA}{C.BOLD} ⚡ Powered by Sailerbross Technology ⚡{C.RESET}
{C.DIM} Termux-safe | 15+ records | ASN | SSL | Headers | Spoof | Auto-recon{C.RESET}
""")

# ============================================================
# PROGRESS BAR
# ============================================================
class ProgressBar:
    def __init__(self, total, label="", width=40):
        self.total   = max(total, 1)
        self.label   = label
        self.width   = width
        self.done    = 0
        self.lock    = threading.Lock()
        self.start   = time.time()
        self._active = True

    def inc(self):
        with self.lock:
            self.done = min(self.done + 1, self.total)

    def render(self):
        with self.lock:
            pct     = self.done / self.total
            filled  = int(self.width * pct)
            bar     = '█' * filled + '░' * (self.width - filled)
            elapsed = time.time() - self.start
            rate    = self.done / max(elapsed, 0.001)
            eta     = (self.total - self.done) / max(rate, 0.001)
            print(
                f"\r{C.CYAN}[{bar}]{C.RESET} "
                f"{C.BOLD}{pct*100:.0f}%{C.RESET} "
                f"{C.DIM}{self.label} {self.done}/{self.total} "
                f"{rate:.0f}/s ETA:{eta:.0f}s{C.RESET}   ",
                end='', flush=True
            )

    def stop(self):
        self._active = False
        self.render()
        print()

    def loop(self, interval=0.25):
        while self._active:
            self.render()
            time.sleep(interval)

# ============================================================
# TERMUX-SAFE RESOLVER
# ============================================================
def make_resolver(custom_ns=None, timeout=5):
    r = dns.resolver.Resolver(configure=False)
    if custom_ns:
        r.nameservers = [
            ip.strip() for ip in custom_ns.split(',')
            if ip.strip()
        ]
    else:
        r.nameservers = FALLBACK_NS
    r.timeout  = timeout
    r.lifetime = timeout * 2
    return r

# ============================================================
# SAFE RESOLVE
# ============================================================
def safe_resolve(resolver, name, rtype):
    try:
        answers = resolver.resolve(name, rtype)
        return [(rr.to_text(), answers.ttl) for rr in answers]
    except Exception:
        return []

# ============================================================
# UI HELPERS
# ============================================================
def section(title, color=C.CYAN):
    w = 62
    print(f"\n{color}{C.BOLD}┌{'─'*(w-2)}┐{C.RESET}")
    pad = w - 4 - len(title)
    print(
        f"{color}{C.BOLD}│  {C.RESET}"
        f"{C.BOLD}{title}{' '*max(pad,0)}{color}  │{C.RESET}"
    )
    print(f"{color}{C.BOLD}└{'─'*(w-2)}┘{C.RESET}")

def box_line(label, value, lc=C.DIM, vc=C.WHITE):
    print(f"  {lc}{label:<22}{C.RESET} {vc}{value}{C.RESET}")

def warn(msg):
    print(f"  {C.RED}{C.BOLD}⚠  {msg}{C.RESET}")

def ok(msg):
    print(f"  {C.GREEN}✅ {msg}{C.RESET}")

def info(msg):
    print(f"  {C.CYAN}💡 {msg}{C.RESET}")

def tip(msg):
    print(f"  {C.YELLOW}ℹ  {msg}{C.RESET}")

# ============================================================
# INTELLIGENCE HELPERS
# ============================================================
def detect_dns_provider(ns_records):
    for ns_val, _ in ns_records:
        for key, provider in DNS_PROVIDERS.items():
            if key in ns_val.lower():
                return provider
    return "Unknown"

def detect_cdn(cname_records, a_records):
    for val, _ in cname_records + a_records:
        for key, cdn in CDN_FINGERPRINTS.items():
            if key in val.lower():
                return cdn
    return None

def detect_mail_provider(mx_records):
    for val, _ in mx_records:
        for key, provider in MAIL_PROVIDERS.items():
            if key in val.lower():
                return provider
    return "Unknown"

# ============================================================
# SPF ANALYZER
# ============================================================
def analyze_spf(txt_records):
    result = {
        "found": False, "raw": "", "ttl": 0,
        "warnings": [], "score": 0,
        "lookups": 0, "all_tag": "",
    }
    for val, ttl in txt_records:
        clean = val.strip('"')
        if clean.startswith("v=spf1"):
            result.update({"found": True, "raw": clean,
                           "ttl": ttl, "score": 20})
            all_m = re.search(r'([+\-~?])all', clean)
            if all_m:
                tag = all_m.group(1)
                result["all_tag"] = tag
                if tag == '+':
                    result["warnings"].append(
                        "SPF +all — ANYONE can send as you! Critical."
                    )
                elif tag == '?':
                    result["warnings"].append(
                        "SPF ?all — neutral, offers no real protection."
                    )
                elif tag == '~':
                    result["score"] += 5
                elif tag == '-':
                    result["score"] += 10
            lookups = re.findall(
                r'\b(include|a|mx|ptr|exists|redirect):', clean
            )
            result["lookups"] = len(lookups)
            if result["lookups"] > 10:
                result["warnings"].append(
                    f"SPF has {result['lookups']} lookups (max 10) — will break!"
                )
            else:
                result["score"] += 5
            break
    if not result["found"]:
        result["warnings"].append(
            "No SPF record — domain can be spoofed for phishing"
        )
    return result

# ============================================================
# DMARC ANALYZER
# ============================================================
def analyze_dmarc(resolver, domain):
    result = {
        "found": False, "raw": "", "policy": "",
        "pct": 100, "rua": "", "ruf": "",
        "warnings": [], "score": 0,
    }
    for val, ttl in safe_resolve(resolver, f"_dmarc.{domain}", 'TXT'):
        clean = val.strip('"')
        if "v=DMARC1" in clean:
            result.update({"found": True, "raw": clean, "score": 20})
            p = re.search(r'\bp=(\w+)', clean)
            if p:
                pol = p.group(1).lower()
                result["policy"] = pol
                if pol == "none":
                    result["warnings"].append(
                        "DMARC p=none — monitor only, emails NOT blocked"
                    )
                elif pol == "quarantine":
                    result["score"] += 8
                elif pol == "reject":
                    result["score"] += 15
            pct = re.search(r'\bpct=(\d+)', clean)
            if pct:
                result["pct"] = int(pct.group(1))
                if result["pct"] < 100:
                    result["warnings"].append(
                        f"DMARC pct={result['pct']}% — not fully enforced"
                    )
            for tag, attr in [('rua', 'rua'), ('ruf', 'ruf')]:
                m = re.search(rf'\b{tag}=([^\s;]+)', clean)
                if m:
                    result[attr] = m.group(1)
            break
    if not result["found"]:
        result["warnings"].append(
            "No DMARC record — no email authentication policy"
        )
    return result

# ============================================================
# DKIM CHECKER
# ============================================================
def check_dkim(resolver, domain, selectors=None):
    if selectors is None:
        selectors = DKIM_SELECTORS
    found = []
    for sel in selectors:
        for val, ttl in safe_resolve(
            resolver, f"{sel}._domainkey.{domain}", 'TXT'
        ):
            clean = val.strip('"')
            if "v=DKIM1" in clean or "p=" in clean:
                found.append({
                    "selector": sel,
                    "record":   clean[:80] + ("..." if len(clean) > 80 else ""),
                    "ttl":      ttl,
                })
                break
    return found

# ============================================================
# WILDCARD DETECTION
# ============================================================
def check_wildcard(resolver, domain):
    rand = ''.join(random.choices(string.ascii_lowercase, k=18))
    ips  = set()
    for val, _ in safe_resolve(resolver, f"{rand}.{domain}", 'A'):
        ips.add(val)
    return bool(ips), ips

# ============================================================
# ZONE TRANSFER
# ============================================================
def attempt_axfr(resolver, domain):
    ns_records = safe_resolve(resolver, domain, 'NS')
    if not ns_records:
        return [], "Could not find NS records"
    for ns_val, _ in ns_records:
        ns_host = ns_val.rstrip('.')
        try:
            ns_ip = socket.gethostbyname(ns_host)
            z = dns.zone.from_xfr(
                dns.query.xfr(ns_ip, domain, timeout=10)
            )
            records = [f"{name}.{domain}" for name in z.nodes]
            return records, f"SUCCESS on {ns_host}"
        except Exception:
            continue
    return [], "Refused by all nameservers (good)"

# ============================================================
# MAIL SECURITY SCORE
# ============================================================
def mail_security_score(spf, dmarc, dkim_found, mx_records, caa_records):
    score = 0
    if spf["found"]:
        score += 20
        score += (10 if spf["all_tag"] == '-'
                  else 5 if spf["all_tag"] == '~' else 0)
        if spf["lookups"] <= 10:
            score += 5
    if dmarc["found"]:
        score += 20
        score += (15 if dmarc["policy"] == "reject"
                  else 8 if dmarc["policy"] == "quarantine" else 0)
    if dkim_found:
        score += 15
    if mx_records:
        score += 5
    if caa_records:
        score += 5
    return min(score, 100)

def score_bar(score, width=30):
    filled = int(width * score / 100)
    bar    = '█' * filled + '░' * (width - filled)
    if score >= 90:
        cl, label = C.GREEN,   "EXCELLENT 🟢"
    elif score >= 70:
        cl, label = C.YELLOW,  "GOOD 🟡"
    elif score >= 50:
        cl, label = C.ORANGE,  "NEEDS WORK 🟠"
    else:
        cl, label = C.RED,     "VULNERABLE 🔴"
    return (
        f"{cl}[{bar}]{C.RESET} "
        f"{C.BOLD}{score}/100{C.RESET}  {cl}{label}{C.RESET}"
    )

# ============================================================
# ALL RECORD TYPES
# ============================================================
ALL_TYPES = [
    'A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME',
    'SOA', 'PTR', 'SRV', 'CAA', 'DNSKEY', 'DS', 'TLSA', 'NAPTR'
]

def lookup_records(resolver, domain, types=None):
    if types is None:
        types = ALL_TYPES
    return {
        rtype: recs
        for rtype in types
        for recs in [safe_resolve(resolver, domain, rtype)]
        if recs
    }

def print_records(records_dict, mode="normal"):
    if not records_dict:
        print(f"  {co('No records found.', C.RED)}")
        return
    for rtype, records in records_dict.items():
        color   = REC_COLOR.get(rtype, C.WHITE)
        explain = RECORD_EXPLAIN.get(rtype, "")
        print(
            f"\n  {color}{C.BOLD}"
            f"┌── {rtype} Records {'─'*(42-len(rtype))}┐{C.RESET}"
        )
        if explain and mode != "quiet":
            print(f"  {C.DIM}│  💡 {explain}{C.RESET}")
        for val, ttl in records:
            if mode == "expert":
                print(
                    f"  {color}│{C.RESET}  "
                    f"{C.BOLD}{val:<52}{C.RESET}  "
                    f"{C.DIM}TTL:{ttl}s{C.RESET}"
                )
            else:
                print(f"  {color}│{C.RESET}  {C.BOLD}{val}{C.RESET}")
        print(f"  {color}└{'─'*50}┘{C.RESET}")

# ============================================================
# ASN / IP OWNERSHIP LOOKUP
# ============================================================
def asn_lookup(ip):
    result = {
        "ip":       ip,
        "asn":      "",
        "as_name":  "",
        "country":  "",
        "prefix":   "",
        "registry": "",
        "abuse":    "",
    }

    if not HTTP_OK:
        return result

    try:
        url = (
            f"https://stat.ripe.net/data/prefix-overview/data.json"
            f"?resource={ip}&sourceapp=dns_scorpion"
        )
        req  = urllib.request.Request(
            url,
            headers={"User-Agent": "dns_scorpion/1.1 Sailerbross"}
        )
        resp = urllib.request.urlopen(req, timeout=8)
        data = json.loads(resp.read().decode())

        d = data.get("data", {})
        asns = d.get("asns", [])
        if asns:
            result["asn"]     = str(asns[0].get("asn", ""))
            result["as_name"] = asns[0].get("holder", "")
        result["prefix"] = d.get("resource", "")
    except Exception:
        pass

    # Country from ip-api (free, no key)
    try:
        url2 = f"http://ip-api.com/json/{ip}?fields=country,isp,org,as"
        req2  = urllib.request.Request(
            url2,
            headers={"User-Agent": "dns_scorpion/1.1"}
        )
        resp2 = urllib.request.urlopen(req2, timeout=6)
        data2 = json.loads(resp2.read().decode())
        result["country"]  = data2.get("country", "")
        result["as_name"]  = result["as_name"] or data2.get("org", "")
        result["asn"]      = result["asn"] or data2.get("as", "")
    except Exception:
        pass

    return result

def print_asn(result):
    section(f"ASN / IP Intelligence — {result['ip']}", C.BLUE)
    box_line("IP Address:",  result["ip"],      C.DIM, C.GREEN)
    box_line("ASN:",         result["asn"]      or "N/A", C.DIM, C.CYAN)
    box_line("Organization:",result["as_name"]  or "N/A", C.DIM, C.WHITE)
    box_line("Country:",     result["country"]  or "N/A", C.DIM, C.YELLOW)
    box_line("Prefix:",      result["prefix"]   or "N/A", C.DIM, C.DIM)

# ============================================================
# SSL / TLS CERTIFICATE INFO
# ============================================================
def ssl_info(domain, port=443, timeout=8):
    result = {
        "domain":       domain,
        "port":         port,
        "subject":      {},
        "issuer":       {},
        "san":          [],
        "not_before":   "",
        "not_after":    "",
        "days_left":    None,
        "version":      "",
        "serial":       "",
        "cipher":       "",
        "warnings":     [],
        "error":        "",
    }

    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((domain, port), timeout=timeout) as sock:
            with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
                cert   = ssock.getpeercert()
                cipher = ssock.cipher()

        result["cipher"]  = f"{cipher[0]} ({cipher[1]})"
        result["version"] = cert.get("version", "")
        result["subject"] = dict(
            x[0] for x in cert.get("subject", [])
        )
        result["issuer"]  = dict(
            x[0] for x in cert.get("issuer", [])
        )

        # SANs
        for tag, val in cert.get("subjectAltName", []):
            if tag == "DNS":
                result["san"].append(val)

        # Dates
        fmt = "%b %d %H:%M:%S %Y %Z"
        nb  = cert.get("notBefore", "")
        na  = cert.get("notAfter",  "")
        result["not_before"] = nb
        result["not_after"]  = na

        if na:
            try:
                exp  = datetime.strptime(na, fmt)
                now  = datetime.utcnow()
                days = (exp - now).days
                result["days_left"] = days
                if days < 0:
                    result["warnings"].append(
                        f"Certificate EXPIRED {abs(days)} days ago!"
                    )
                elif days < 14:
                    result["warnings"].append(
                        f"Certificate expires in {days} days — renew NOW!"
                    )
                elif days < 30:
                    result["warnings"].append(
                        f"Certificate expires in {days} days — plan renewal"
                    )
            except Exception:
                pass

        # Serial
        result["serial"] = str(cert.get("serialNumber", ""))

    except ssl.SSLCertVerificationError as e:
        result["error"] = f"SSL verification failed: {str(e)[:60]}"
        result["warnings"].append("Certificate verification error")
    except ConnectionRefusedError:
        result["error"] = f"Port {port} refused"
    except socket.timeout:
        result["error"] = "Connection timed out"
    except Exception as e:
        result["error"] = str(e)[:80]

    return result

def print_ssl(result):
    section(f"SSL/TLS Certificate — {result['domain']}:{result['port']}", C.GREEN)

    if result["error"]:
        warn(result["error"])
        return

    cn = result["subject"].get("commonName", "N/A")
    box_line("Common Name:", cn, C.DIM, C.CYAN)

    issuer_cn = result["issuer"].get("organizationName",
                result["issuer"].get("commonName", "N/A"))
    box_line("Issued By:",   issuer_cn, C.DIM, C.WHITE)
    box_line("Valid From:",  result["not_before"], C.DIM, C.DIM)
    box_line("Expires:",     result["not_after"],  C.DIM,
             C.RED if (result["days_left"] or 999) < 30 else C.GREEN)

    days = result["days_left"]
    if days is not None:
        dcolor = C.RED if days < 30 else C.GREEN
        box_line("Days Left:", str(days), C.DIM, dcolor)

    box_line("Cipher:",   result["cipher"],  C.DIM, C.YELLOW)
    box_line("Serial:",   result["serial"][:30], C.DIM, C.DIM)

    if result["san"]:
        print(f"\n  {C.BLUE}{C.BOLD}Subject Alternative Names ({len(result['san'])}):{C.RESET}")
        for san in result["san"][:20]:
            print(f"    {C.DIM}├─{C.RESET} {co(san, C.CYAN)}")
        if len(result["san"]) > 20:
            print(f"    {C.DIM}... and {len(result['san'])-20} more{C.RESET}")

    for w in result["warnings"]:
        warn(w)
    if not result["warnings"]:
        ok("Certificate looks healthy")

# ============================================================
# HTTP SECURITY HEADERS
# ============================================================
def check_headers(domain, timeout=8):
    result = {
        "domain":  domain,
        "url":     "",
        "status":  None,
        "server":  "",
        "found":   {},
        "missing": [],
        "score":   0,
        "grade":   "",
        "extras":  {},
        "error":   "",
    }

    url = None
    for scheme in ("https", "http"):
        try:
            test_url = f"{scheme}://{domain}"
            req = urllib.request.Request(
                test_url,
                headers={"User-Agent": "dns_scorpion/1.1 Sailerbross"}
            )
            resp = urllib.request.urlopen(req, timeout=timeout)
            url  = test_url
            result["status"] = resp.getcode()
            result["url"]    = test_url
            headers          = resp.headers

            # Collect all headers
            result["server"] = headers.get("Server", "")

            for hdr, meta in SECURITY_HEADERS.items():
                val = headers.get(hdr, "")
                if val:
                    result["found"][hdr] = val
                else:
                    result["missing"].append(hdr)

            # Extra interesting headers
            for extra in ["X-Powered-By", "X-AspNet-Version",
                          "X-Generator", "Via", "X-Cache",
                          "CF-Ray", "X-Amz-Cf-Id"]:
                v = headers.get(extra, "")
                if v:
                    result["extras"][extra] = v
            break
        except Exception as e:
            result["error"] = str(e)[:60]

    if not url:
        return result

    # Score: each present header = points
    per_header = 100 // len(SECURITY_HEADERS)
    result["score"] = len(result["found"]) * per_header

    # Grade
    s = result["score"]
    result["grade"] = (
        "A+" if s >= 90 else
        "A"  if s >= 80 else
        "B"  if s >= 60 else
        "C"  if s >= 40 else
        "D"  if s >= 20 else "F"
    )
    return result

def print_headers(result):
    section(f"HTTP Security Headers — {result['domain']}", C.BLUE)

    if result["error"] and not result["status"]:
        warn(f"Could not connect: {result['error']}")
        return

    gc = C.GREEN if result["grade"] in ("A+","A") else \
         C.YELLOW if result["grade"] in ("B","C") else C.RED

    box_line("URL:",    result["url"],    C.DIM, C.CYAN)
    box_line("Status:", str(result["status"] or "N/A"), C.DIM, C.GREEN)
    box_line("Server:", result["server"] or "Hidden", C.DIM,
             C.YELLOW if result["server"] else C.GREEN)
    box_line("Score:",  f"{result['score']}/100", C.DIM, gc)
    box_line("Grade:",  result["grade"], C.DIM, gc)

    if result["found"]:
        print(f"\n  {C.GREEN}{C.BOLD}✅ Present Headers:{C.RESET}")
        for hdr, val in result["found"].items():
            alias = SECURITY_HEADERS[hdr]["alias"]
            print(
                f"    {C.GREEN}[{alias}]{C.RESET} "
                f"{C.DIM}{hdr}{C.RESET}: "
                f"{C.WHITE}{val[:55]}{C.RESET}"
            )

    if result["missing"]:
        print(f"\n  {C.RED}{C.BOLD}⚠ Missing Headers:{C.RESET}")
        for hdr in result["missing"]:
            meta = SECURITY_HEADERS[hdr]
            print(
                f"    {C.RED}[{meta['alias']}]{C.RESET} "
                f"{C.DIM}{hdr}{C.RESET}"
                f"\n      {C.DIM}→ {meta['risk']}{C.RESET}"
            )

    if result["extras"]:
        print(f"\n  {C.YELLOW}{C.BOLD}ℹ Info-Disclosure Headers:{C.RESET}")
        for hdr, val in result["extras"].items():
            print(
                f"    {C.YELLOW}[!]{C.RESET} "
                f"{C.DIM}{hdr}:{C.RESET} {C.WHITE}{val[:60]}{C.RESET}"
            )
            if hdr in ("X-Powered-By","X-AspNet-Version","X-Generator"):
                warn(f"Technology exposed via {hdr} — consider hiding this")

# ============================================================
# EMAIL SPOOFING TEST
# ============================================================
def spoof_test(resolver, domain, txt_records=None):
    if txt_records is None:
        txt_records = safe_resolve(resolver, domain, 'TXT')

    spf   = analyze_spf(txt_records)
    dmarc = analyze_dmarc(resolver, domain)

    risks  = []
    blocks = []
    score  = 0

    # SPF evaluation
    if not spf["found"]:
        risks.append("No SPF — spoofed emails pass SPF check")
    elif spf["all_tag"] == '+':
        risks.append("SPF +all — SPF gives zero protection")
    elif spf["all_tag"] == '?':
        risks.append("SPF ?all — neutral, provides minimal protection")
    elif spf["all_tag"] == '~':
        score += 20
        blocks.append("SPF ~all softfails suspicious senders")
    elif spf["all_tag"] == '-':
        score += 35
        blocks.append("SPF -all hard-fails unauthorized senders")

    # DMARC evaluation
    if not dmarc["found"]:
        risks.append("No DMARC — no policy to act on SPF/DKIM failures")
    else:
        pol = dmarc.get("policy","")
        if pol == "none":
            score += 5
            risks.append(
                "DMARC p=none — monitoring only, spoofed mail NOT blocked"
            )
        elif pol == "quarantine":
            score += 30
            blocks.append("DMARC p=quarantine sends suspicious mail to spam")
        elif pol == "reject":
            score += 50
            blocks.append("DMARC p=reject blocks spoofed emails outright")

    # DKIM (bonus)
    dkim_found = check_dkim(resolver, domain)
    if dkim_found:
        score += 15
        blocks.append(
            f"DKIM signing active ({dkim_found[0]['selector']} selector)"
        )
    else:
        risks.append("No DKIM — unsigned emails harder to verify")

    score = min(score, 100)

    # Final verdict
    if score >= 80:
        verdict      = "PROTECTED"
        verdict_col  = C.GREEN
        can_spoof    = False
    elif score >= 40:
        verdict      = "PARTIALLY PROTECTED"
        verdict_col  = C.YELLOW
        can_spoof    = True
    else:
        verdict      = "SPOOFABLE"
        verdict_col  = C.RED
        can_spoof    = True

    return {
        "domain":     domain,
        "verdict":    verdict,
        "color":      verdict_col,
        "can_spoof":  can_spoof,
        "score":      score,
        "risks":      risks,
        "blocks":     blocks,
        "spf":        spf,
        "dmarc":      dmarc,
        "dkim":       dkim_found,
    }

def print_spoof(result):
    section(f"Email Spoofing Risk — {result['domain']}", C.RED)

    vc = result["color"]
    print(f"\n  {vc}{C.BOLD}VERDICT: {result['verdict']}{C.RESET}")
    print(f"  {vc}{'Can be spoofed: YES ⚠' if result['can_spoof'] else 'Spoofing blocked ✅'}{C.RESET}")
    print(f"  {C.DIM}Protection score: {C.RESET}{score_bar(result['score'])}\n")

    if result["blocks"]:
        print(f"  {C.GREEN}{C.BOLD}🛡 Protections Active:{C.RESET}")
        for b in result["blocks"]:
            print(f"    {C.GREEN}✅ {b}{C.RESET}")

    if result["risks"]:
        print(f"\n  {C.RED}{C.BOLD}⚠ Risk Factors:{C.RESET}")
        for r in result["risks"]:
            print(f"    {C.RED}⚠  {r}{C.RESET}")

    print(f"\n  {C.DIM}SPF policy  : {result['spf'].get('all_tag','none') or 'not found'}{C.RESET}")
    print(f"  {C.DIM}DMARC policy: {result['dmarc'].get('policy','not found') or 'not found'}{C.RESET}")
    print(f"  {C.DIM}DKIM found  : {'yes ('+result['dkim'][0]['selector']+')' if result['dkim'] else 'no'}{C.RESET}")

# ============================================================
# AUTO-RECON
# ============================================================
def auto_recon(resolver, domain, mode="normal",
               output_file=None, output_fmt="html"):
    print(f"\n{C.YELLOW}{C.BOLD}{'═'*62}{C.RESET}")
    print(f"{C.YELLOW}{C.BOLD}  🦂 DNS SCORPION AUTO-RECON — {domain}{C.RESET}")
    print(f"{C.YELLOW}{C.BOLD}  ⚡ Sailerbross Technology — Full Automated Audit{C.RESET}")
    print(f"{C.YELLOW}{C.BOLD}{'═'*62}{C.RESET}")
    print(f"  {C.DIM}Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{C.RESET}\n")

    report = {
        "tool":     "DNS Scorpion v1.1",
        "powered":  "Sailerbross Technology",
        "domain":   domain,
        "date":     datetime.now().isoformat(),
        "sections": {}
    }

    steps = [
        "DNS Records",
        "Deep Analysis",
        "SSL Certificate",
        "HTTP Headers",
        "Spoof Test",
        "ASN Lookup",
        "Propagation",
        "Zone Transfer",
    ]

    print(f"  {C.CYAN}Running {len(steps)} audit modules...{C.RESET}\n")

    def _step(n, title):
        print(f"\n{C.MAGENTA}{C.BOLD}[{n}] {title}{C.RESET}")
        print(f"  {C.DIM}{'─'*55}{C.RESET}")

    # Step 1
    _step(1, "DNS Records — All Types")
    records_dict = lookup_records(resolver, domain)
    print_records(records_dict, mode)
    report["sections"]["dns_records"] = {
        rt: [{"value": v, "ttl": t} for v, t in recs]
        for rt, recs in records_dict.items()
    }

    a_records   = records_dict.get('A', [])
    mx_records  = records_dict.get('MX', [])
    ns_records  = records_dict.get('NS', [])
    txt_records = records_dict.get('TXT', [])
    caa_records = records_dict.get('CAA', [])
    cname_recs  = records_dict.get('CNAME', [])

    # Step 2
    _step(2, "Deep DNS Analysis")
    
    # Manual deep analysis inline
    section("Intelligence", C.BLUE)
    dns_prov  = detect_dns_provider(ns_records)
    cdn       = detect_cdn(cname_recs, a_records)
    mail_prov = detect_mail_provider(mx_records)
    box_line("DNS Provider:",  dns_prov, C.DIM, C.CYAN)
    box_line("CDN:",           cdn or "None", C.DIM, C.GREEN if cdn else C.DIM)
    box_line("Mail Provider:", mail_prov, C.DIM, C.YELLOW)
    
    section("SPF Analysis", C.MAGENTA)
    spf = analyze_spf(txt_records)
    if spf["found"]:
        ok("SPF record found")
        box_line("All tag:", spf["all_tag"] or "none", C.DIM,
                 C.GREEN if spf["all_tag"] in ('-','~') else C.RED)
    else:
        warn("No SPF record")
    
    section("DMARC Analysis", C.MAGENTA)
    dmarc = analyze_dmarc(resolver, domain)
    if dmarc["found"]:
        ok("DMARC record found")
        box_line("Policy:", dmarc["policy"].upper(), C.DIM,
                 C.GREEN if dmarc["policy"] == "reject" else C.YELLOW)
    else:
        warn("No DMARC record")
    
    section("DKIM Check", C.MAGENTA)
    dkim = check_dkim(resolver, domain)
    if dkim:
        ok(f"DKIM found — selector: {dkim[0]['selector']}")
    else:
        warn("No DKIM found")
    
    section("Mail Security Score", C.YELLOW)
    ms = mail_security_score(spf, dmarc, dkim, mx_records, caa_records)
    print(f"\n  {score_bar(ms)}\n")
    
    analysis = {
        "intelligence": {
            "dns_provider": dns_prov,
            "cdn": cdn or "None",
            "mail_provider": mail_prov,
        },
        "spf": spf,
        "dmarc": dmarc,
        "dkim": dkim,
        "mail_security_score": ms,
        "warnings": spf["warnings"] + dmarc["warnings"],
    }
    report["sections"]["analysis"] = analysis

    # Step 3
    _step(3, "SSL/TLS Certificate")
    ssl_result = ssl_info(domain)
    print_ssl(ssl_result)
    report["sections"]["ssl"] = ssl_result

    # Step 4
    _step(4, "HTTP Security Headers")
    hdr_result = check_headers(domain)
    print_headers(hdr_result)
    report["sections"]["headers"] = hdr_result

    # Step 5
    _step(5, "Email Spoofing Risk Assessment")
    spoof_result = spoof_test(resolver, domain, txt_records)
    print_spoof(spoof_result)
    report["sections"]["spoof"] = spoof_result

    # Step 6
    _step(6, "ASN / IP Ownership")
    asn_results = []
    for ip, _ in a_records[:4]:
        asn_r = asn_lookup(ip)
        print_asn(asn_r)
        asn_results.append(asn_r)
    report["sections"]["asn"] = asn_results

    # Step 7
    _step(7, "DNS Propagation Check")
    prop = check_propagation(domain, 'A', timeout=5)
    report["sections"]["propagation"] = {k: v for k, v in prop.items()}

    # Step 8
    _step(8, "Zone Transfer Attempt")
    zt_recs, zt_status = attempt_axfr(resolver, domain)
    if zt_recs:
        warn(f"ZONE TRANSFER SUCCESSFUL! {len(zt_recs)} records exposed!")
        for r in zt_recs[:15]:
            print(f"  {co(r, C.GREEN)}")
    else:
        ok(f"Zone transfer: {zt_status}")
    report["sections"]["zone_transfer"] = {
        "status": zt_status, "records": zt_recs
    }

    # Summary
    print(f"\n{C.CYAN}{C.BOLD}{'═'*62}{C.RESET}")
    print(f"{C.YELLOW}{C.BOLD}  🦂 AUTO-RECON SUMMARY — {domain}{C.RESET}")
    print(f"{C.CYAN}{C.BOLD}{'═'*62}{C.RESET}\n")

    hs = hdr_result.get("score", 0)
    ss = spoof_result.get("score", 0)

    box_line("Mail Security Score:", score_bar(ms, width=20), C.DIM, "")
    box_line("HTTP Header Grade:",
             f"{hdr_result.get('grade','?')} ({hs}/100)", C.DIM,
             C.GREEN if hs >= 60 else C.RED)
    box_line("Spoof Protection:",
             f"{spoof_result['verdict']} ({ss}/100)",
             C.DIM, spoof_result.get("color", C.WHITE))

    if ssl_result.get("days_left") is not None:
        dc = C.GREEN if ssl_result["days_left"] >= 30 else C.RED
        box_line("SSL Expires in:",
                 f"{ssl_result['days_left']} days", C.DIM, dc)

    all_warnings = (
        analysis.get("warnings", []) +
        ssl_result.get("warnings", []) +
        spoof_result.get("risks", [])
    )

    if all_warnings:
        print(f"\n  {C.RED}{C.BOLD}⚠ Combined Warnings ({len(all_warnings)}):{C.RESET}")
        for i, w in enumerate(all_warnings, 1):
            print(f"  {co(str(i)+'.', C.RED)} {co(w, C.YELLOW)}")
    else:
        ok("No critical issues — domain is well configured!")

    print(f"\n{C.CYAN}{C.BOLD}{'═'*62}{C.RESET}")
    print(f"{C.MAGENTA}{C.BOLD}  ⚡ Auto-Recon complete — Sailerbross Technology{C.RESET}")
    print(f"{C.CYAN}{C.BOLD}{'═'*62}{C.RESET}\n")

    # Export
    if output_file is None:
        safe = domain.replace('.', '_')
        output_file = f"scorpion_{safe}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    export_results(report, output_file, output_fmt)
    return report

# ============================================================
# CORE FEATURES (unchanged)
# ============================================================
def reverse_lookup(resolver, ip):
    section(f"Reverse DNS — {ip}", C.CYAN)
    try:
        rev  = dns.reversename.from_address(ip)
        recs = safe_resolve(resolver, str(rev), 'PTR')
        if recs:
            for val, ttl in recs:
                print(
                    f"  {co(ip, C.GREEN)} → "
                    f"{co(val, C.CYAN, C.BOLD)}  "
                    f"{co('TTL:'+str(ttl)+'s', C.DIM)}"
                )
        else:
            print(f"  {co('No PTR record for ' + ip, C.RED)}")
    except Exception as e:
        print(f"  {co('[!] Error: ' + str(e), C.RED)}")

def check_propagation(domain, rtype='A', timeout=5):
    section(f"DNS Propagation — {domain} ({rtype})", C.YELLOW)
    print(f"  {C.DIM}Checking {len(PROP_SERVERS)} global servers...{C.RESET}\n")

    results = {}
    lock    = threading.Lock()
    pb      = ProgressBar(len(PROP_SERVERS), "servers")
    pb_t    = threading.Thread(target=pb.loop, daemon=True)
    pb_t.start()

    def check_one(name, ip):
        try:
            r    = make_resolver(ip, timeout)
            recs = safe_resolve(r, domain, rtype)
            vals = [v for v, _ in recs]
        except Exception:
            vals = []
        with lock:
            results[name] = vals
        pb.inc()

    threads = [
        threading.Thread(target=check_one, args=(n, ip), daemon=True)
        for n, ip in PROP_SERVERS.items()
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    pb.stop()

    groups = defaultdict(list)
    for name, vals in results.items():
        key = "|".join(sorted(vals)) if vals else "NO_RECORD"
        groups[key].append(name)

    if len(groups) == 1:
        ok("Fully propagated — all servers agree ✅")
    else:
        warn(f"Inconsistent! {len(groups)} different answers")

    print()
    for answer, servers in groups.items():
        disp = (co("No record", C.RED) if answer == "NO_RECORD"
                else co(answer.replace("|", ", "), C.GREEN))
        print(f"  {C.BOLD}Answer:{C.RESET} {disp}")
        for s in servers:
            print(f"    {C.DIM}├─ {s}{C.RESET}")
    return results

def compare_domains(resolver, domain_a, domain_b, types=None):
    if types is None:
        types = ['A','MX','NS','TXT','CNAME']
    section(f"Compare: {domain_a} vs {domain_b}", C.MAGENTA)
    recs_a = lookup_records(resolver, domain_a, types)
    recs_b = lookup_records(resolver, domain_b, types)
    all_t  = sorted(set(list(recs_a) + list(recs_b)))
    w = 28
    print(f"\n  {C.BOLD}{'TYPE':<8}  {domain_a:<{w}}  {domain_b:<{w}}{C.RESET}")
    print(f"  {'─'*72}")
    for rtype in all_t:
        color  = REC_COLOR.get(rtype, C.WHITE)
        va     = [v for v,_ in recs_a.get(rtype, [])]
        vb     = [v for v,_ in recs_b.get(rtype, [])]
        same   = sorted(va) == sorted(vb)
        status = co("=", C.GREEN) if same else co("≠", C.RED)
        a_str  = (", ".join(va))[:w-2] if va else co("(none)", C.DIM)
        b_str  = (", ".join(vb))[:w-2] if vb else co("(none)", C.DIM)
        print(
            f"  {color}{C.BOLD}{rtype:<8}{C.RESET} {status}  "
            f"{C.WHITE}{a_str:<{w}}{C.RESET}  {C.WHITE}{b_str}{C.RESET}"
        )

def save_snapshot(domain, records_dict):
    os.makedirs(SNAPSHOT_DIR, exist_ok=True)
    path = os.path.join(
        SNAPSHOT_DIR,
        domain.replace('.','_') + ".json"
    )
    snap = {
        "domain":    domain,
        "timestamp": datetime.now().isoformat(),
        "records": {
            rt: [{"value": v, "ttl": t} for v, t in recs]
            for rt, recs in records_dict.items()
        },
    }
    with open(path, 'w') as f:
        json.dump(snap, f, indent=2)
    print(f"\n  {co('Snapshot saved → ' + path, C.GREEN, C.BOLD)}")

def load_snapshot(domain):
    path = os.path.join(
        SNAPSHOT_DIR,
        domain.replace('.','_') + ".json"
    )
    if not os.path.exists(path):
        return None, None
    with open(path) as f:
        snap = json.load(f)
    records = {
        rt: [(r["value"], r["ttl"]) for r in recs]
        for rt, recs in snap["records"].items()
    }
    return records, snap["timestamp"]

def diff_snapshot(domain, current):
    section(f"DNS Diff — {domain}", C.YELLOW)
    old, ts = load_snapshot(domain)
    if old is None:
        print(f"  {co('No snapshot. Run: snapshot '+domain, C.RED)}")
        return
    print(f"  {C.DIM}Snapshot from: {ts}{C.RESET}\n")
    changed = False
    for rtype in sorted(set(list(old) + list(current))):
        ov = sorted(v for v,_ in old.get(rtype, []))
        nv = sorted(v for v,_ in current.get(rtype, []))
        if ov == nv:
            continue
        changed = True
        color = REC_COLOR.get(rtype, C.WHITE)
        print(f"  {color}{C.BOLD}{rtype} changed:{C.RESET}")
        for v in ov:
            if v not in nv:
                print(f"    {co('- ' + v, C.RED)}")
        for v in nv:
            if v not in ov:
                print(f"    {co('+ ' + v, C.GREEN)}")
        print()
    if not changed:
        ok("No DNS changes since last snapshot")

def bulk_lookup(resolver, filepath, types=None, output_file=None):
    if types is None:
        types = ['A','MX','NS']
    section(f"Bulk Lookup — {filepath}", C.CYAN)
    try:
        with open(filepath, 'r', errors='ignore') as f:
            domains = [
                l.strip() for l in f
                if l.strip() and not l.startswith('#')
            ]
    except FileNotFoundError:
        print(f"  {co('File not found: ' + filepath, C.RED)}")
        return {}

    print(f"  {co(str(len(domains)) + ' domains', C.CYAN)}\n")

    all_r = {}
    lock  = threading.Lock()
    pb    = ProgressBar(len(domains), "domains")
    pb_t  = threading.Thread(target=pb.loop, daemon=True)
    pb_t.start()
    q     = Queue()
    for d in domains:
        q.put(d)

    def worker():
        lr = make_resolver(
            resolver.nameservers[0]
            if resolver.nameservers else None
        )
        while True:
            try:
                dom = q.get_nowait()
            except Empty:
                break
            recs = lookup_records(lr, dom, types)
            with lock:
                all_r[dom] = recs
            pb.inc()
            q.task_done()

    threads = [
        threading.Thread(target=worker, daemon=True)
        for _ in range(min(50, len(domains)))
    ]
    for t in threads:
        t.start()
    q.join()
    pb.stop()

    print()
    for dom, recs in all_r.items():
        if recs:
            a  = ", ".join(v for v,_ in recs.get('A',[]))
            mx = ", ".join(v for v,_ in recs.get('MX',[]))
            print(f"  {co(dom, C.CYAN, C.BOLD)}")
            if a:  print(f"    {co('A:',  C.GREEN)}  {a}")
            if mx: print(f"    {co('MX:', C.YELLOW)} {mx}")
        else:
            print(f"  {co(dom, C.DIM)}  {co('(no records)', C.RED)}")

    if output_file:
        export_results(
            {"bulk": {
                d: {rt: [v for v,_ in r]
                    for rt, r in recs.items()}
                for d, recs in all_r.items()
            }},
            output_file, "json"
        )
    return all_r

# ============================================================
# EXPORT ENGINE
# ============================================================
def export_results(data, output_file, fmt="html"):
    fmt = fmt.lower()
    if not output_file.endswith(f".{fmt}"):
        output_file = f"{output_file}.{fmt}"

    try:
        if fmt == "json":
            _export_json(data, output_file)
        elif fmt == "csv":
            _export_csv(data, output_file)
        elif fmt == "html":
            _export_html(data, output_file)
        else:
            _export_txt(data, output_file)
        print(f"\n  {co('Exported → ' + output_file, C.GREEN, C.BOLD)}")
    except Exception as e:
        print(f"  {co('Export error: ' + str(e), C.RED)}")

def _export_json(data, path):
    def _clean(obj):
        if isinstance(obj, dict):
            return {k: _clean(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_clean(i) for i in obj]
        if isinstance(obj, set):
            return list(obj)
        return obj

    with open(path, 'w') as f:
        json.dump({
            "tool":       "DNS Scorpion v1.1",
            "powered_by": "Sailerbross Technology",
            "exported":   datetime.now().isoformat(),
            "data":       _clean(data),
        }, f, indent=2)

def _export_txt(data, path):
    with open(path, 'w') as f:
        f.write("# DNS Scorpion v1.1 — Sailerbross Technology\n")
        f.write(f"# Domain : {data.get('domain','')}\n")
        f.write(f"# Date   : {datetime.now().isoformat()}\n\n")
        records = data.get("sections",{}).get("dns_records",
                  data.get("records",{}))
        for rtype, recs in records.items():
            f.write(f"\n[{rtype}]\n")
            for r in recs:
                if isinstance(r, dict):
                    f.write(f"  {r.get('value','')}  TTL:{r.get('ttl','')}\n")
                else:
                    f.write(f"  {r}\n")

def _export_csv(data, path):
    records = data.get("sections",{}).get("dns_records",
              data.get("records",{}))
    domain  = data.get("domain","unknown")
    with open(path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(["domain","record_type","value","ttl"])
        for rtype, recs in records.items():
            for r in recs:
                if isinstance(r, dict):
                    w.writerow([domain, rtype,
                                r.get("value",""), r.get("ttl","")])

def _export_html(data, path):
    domain   = data.get("domain","unknown")
    date_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    secs     = data.get("sections", {})
    analysis = secs.get("analysis", data)
    ssl_r    = secs.get("ssl", {})
    hdr_r    = secs.get("headers", {})
    spoof_r  = secs.get("spoof", {})
    asn_list = secs.get("asn", [])
    records  = secs.get("dns_records", data.get("records",{}))
    warnings = analysis.get("warnings",[]) if isinstance(analysis,dict) else []
    ms       = (analysis.get("mail_security_score", 0)
                if isinstance(analysis, dict) else 0)
    hs       = hdr_r.get("score", 0)
    ss       = spoof_r.get("score", 0)

    sc  = ("#2ecc71" if ms >= 90 else
           "#f1c40f" if ms >= 70 else
           "#e67e22" if ms >= 50 else "#e74c3c")

    rec_rows = ""
    for rtype, recs in records.items():
        for r in recs:
            v = r.get("value","") if isinstance(r,dict) else str(r)
            t = r.get("ttl","")   if isinstance(r,dict) else ""
            rec_rows += (
                f"<tr><td class='rtype'>{rtype}</td>"
                f"<td>{v}</td><td>{t}s</td></tr>"
            )

    warn_rows = (
        "".join(
            f"<li>⚠ {w}</li>" for w in warnings
        ) or "<li style='color:#2ecc71'>✅ No critical issues</li>"
    )

    ssl_html = ""
    if ssl_r and not ssl_r.get("error"):
        dl = ssl_r.get("days_left","?")
        dc = "#2ecc71" if isinstance(dl,int) and dl >= 30 else "#e74c3c"
        ssl_html = f"""
        <div class='card'>
          <h3>🔒 SSL Certificate</h3>
          <table>
            <tr><td>Common Name</td>
                <td>{ssl_r.get('subject',{}).get('commonName','N/A')}</td></tr>
            <tr><td>Issuer</td>
                <td>{ssl_r.get('issuer',{}).get('organizationName','N/A')}</td></tr>
            <tr><td>Expires</td>
                <td>{ssl_r.get('not_after','N/A')}</td></tr>
            <tr><td>Days Left</td>
                <td style='color:{dc}'>{dl}</td></tr>
            <tr><td>Cipher</td>
                <td>{ssl_r.get('cipher','N/A')}</td></tr>
          </table>
          <p><b>SANs:</b> {', '.join(ssl_r.get('san',[])[:10])}</p>
        </div>"""

    hdr_html = ""
    if hdr_r:
        gc = ("#2ecc71" if hs >= 80 else
              "#f1c40f" if hs >= 60 else "#e74c3c")
        found_h = "".join(
            f"<li style='color:#2ecc71'>✅ {h}</li>"
            for h in hdr_r.get("found",{})
        )
        miss_h = "".join(
            f"<li style='color:#e74c3c'>⚠ {h} — "
            f"{SECURITY_HEADERS.get(h,{}).get('risk','')}</li>"
            for h in hdr_r.get("missing",[])
        )
        hdr_html = f"""
        <div class='card'>
          <h3>🛡 HTTP Security Headers</h3>
          <p>Grade: <strong style='color:{gc}'>{hdr_r.get('grade','?')}</strong>
             &nbsp; Score: {hs}/100</p>
          <ul>{found_h}{miss_h}</ul>
        </div>"""

    spoof_html = ""
    if spoof_r:
        vc = ("#2ecc71" if spoof_r.get("score",0) >= 80 else
              "#f1c40f" if spoof_r.get("score",0) >= 40 else "#e74c3c")
        spoof_html = f"""
        <div class='card'>
          <h3>📧 Email Spoofing Risk</h3>
          <p style='color:{vc}; font-size:1.2rem; font-weight:bold'>
            {spoof_r.get('verdict','N/A')}
          </p>
          <p>Protection Score: {ss}/100</p>
          <ul>
            {''.join('<li style="color:#e74c3c">⚠ '+r+'</li>'
                     for r in spoof_r.get('risks',[]))}
            {''.join('<li style="color:#2ecc71">✅ '+b+'</li>'
                     for b in spoof_r.get('blocks',[]))}
          </ul>
        </div>"""

    asn_html = ""
    if asn_list:
        rows = ""
        for a in asn_list:
            rows += (
                f"<tr><td>{a.get('ip','')}</td>"
                f"<td>{a.get('asn','')}</td>"
                f"<td>{a.get('as_name','')}</td>"
                f"<td>{a.get('country','')}</td></tr>"
            )
        asn_html = f"""
        <div class='card'>
          <h3>🌐 ASN / IP Intelligence</h3>
          <table>
            <tr><th>IP</th><th>ASN</th><th>Organization</th><th>Country</th></tr>
            {rows}
          </table>
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>DNS Scorpion — {domain}</title>
<style>
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{
    font-family:'Courier New',monospace;
    background:#0d1117; color:#c9d1d9;
    padding:2rem; max-width:960px; margin:auto;
  }}
  h1 {{ color:#f0c040; font-size:1.8rem; margin-bottom:.3rem; }}
  h2 {{ color:#58a6ff; border-bottom:1px solid #30363d;
        padding-bottom:.3rem; margin:1.5rem 0 .8rem; }}
  h3 {{ color:#79c0ff; margin-bottom:.5rem; }}
  .meta {{ color:#8b949e; font-size:.85rem; margin-bottom:1.5rem; }}
  .badge {{
    display:inline-block; padding:.15rem .5rem;
    border-radius:4px; font-size:.75rem;
    background:#161b22; color:#58a6ff;
    border:1px solid #30363d; margin:.1rem;
  }}
  .scorecard {{
    display:flex; gap:1rem; flex-wrap:wrap; margin:1rem 0;
  }}
  .score-box {{
    flex:1; min-width:140px;
    background:#161b22; border:1px solid #30363d;
    border-radius:8px; padding:1rem; text-align:center;
  }}
  .score-box .val {{
    font-size:2rem; font-weight:bold; color:{sc};
  }}
  .score-box .lbl {{ font-size:.75rem; color:#8b949e; }}
  .card {{
    background:#161b22; border:1px solid #30363d;
    border-radius:8px; padding:1.2rem; margin:1rem 0;
  }}
  table {{ width:100%; border-collapse:collapse; }}
  th {{
    background:#0d1117; color:#58a6ff;
    padding:.4rem .6rem; text-align:left;
    font-size:.85rem;
  }}
  td {{ padding:.35rem .6rem; border-bottom:1px solid #21262d;
        font-size:.85rem; }}
  tr:hover td {{ background:#21262d; }}
  .rtype {{ color:#f0c040; font-weight:bold; }}
  ul {{ list-style:none; padding:0; }}
  li {{ padding:.25rem 0; font-size:.85rem; }}
  .warn-list li {{ color:#e74c3c; }}
  footer {{
    margin-top:3rem; text-align:center;
    color:#8b949e; font-size:.8rem;
    border-top:1px solid #30363d; padding-top:1rem;
  }}
</style>
</head>
<body>
<h1>🦂 DNS Scorpion Report</h1>
<p class="meta">
  <span class="badge">Target: {domain}</span>
  <span class="badge">Generated: {date_str}</span>
  <span class="badge">DNS Scorpion v1.1</span>
  <span class="badge">Sailerbross Technology</span>
</p>

<h2>📊 Executive Summary</h2>
<div class="scorecard">
  <div class="score-box">
    <div class="val">{ms}</div>
    <div class="lbl">Mail Security<br>/100</div>
  </div>
  <div class="score-box">
    <div class="val" style="color:{'#2ecc71' if hs>=60 else '#e74c3c'}">{hs}</div>
    <div class="lbl">HTTP Headers<br>/100</div>
  </div>
  <div class="score-box">
    <div class="val" style="color:{('#2ecc71' if ss>=80 else '#f1c40f' if ss>=40 else '#e74c3c')}">{ss}</div>
    <div class="lbl">Spoof Protection<br>/100</div>
  </div>
  <div class="score-box">
    <div class="val" style="color:{'#2ecc71' if not warnings else '#e74c3c'}">
      {len(warnings)}
    </div>
    <div class="lbl">Warnings<br>found</div>
  </div>
</div>

<h2>⚠ Security Warnings</h2>
<div class="card">
  <ul class="warn-list">{warn_rows}</ul>
</div>

<h2>🔍 DNS Records</h2>
<div class="card">
  <table>
    <tr><th>Type</th><th>Value</th><th>TTL</th></tr>
    {rec_rows}
  </table>
</div>

<h2>🔬 Deep Analysis</h2>
{ssl_html}
{hdr_html}
{spoof_html}
{asn_html}

<footer>
  Generated by DNS Scorpion v1.1 &nbsp;|&nbsp;
  ⚡ Powered by Sailerbross Technology &nbsp;|&nbsp;
  {date_str}
</footer>
</body>
</html>"""

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)

# ============================================================
# INTERACTIVE SHELL
# ============================================================
class ScorpionShell:
    def __init__(self):
        self.custom_ns    = None
        self.timeout      = 5
        self.mode         = "normal"
        self.output_fmt   = "html"
        self.last_results = {}
        self.last_domain  = ""
        self.running      = True
        self.resolver     = make_resolver(self.custom_ns, self.timeout)

    def _refresh(self):
        self.resolver = make_resolver(self.custom_ns, self.timeout)

    def do_lookup(self, args):
        parts  = args.split()
        if not parts:
            print(co("Usage: lookup DOMAIN [TYPE ...]", C.RED))
            return
        domain = parts[0]
        types  = [t.upper() for t in parts[1:]] or None
        self.last_domain = domain
        section(
            f"Lookup: {domain}"
            + (f" [{', '.join(types)}]" if types else " [ALL]"),
            C.CYAN
        )
        recs = lookup_records(self.resolver, domain, types)
        print_records(recs, self.mode)
        self.last_results = {
            "domain": domain,
            "records": {
                rt: [{"value": v, "ttl": t} for v, t in rs]
                for rt, rs in recs.items()
            }
        }

    def do_reverse(self, args):
        ip = args.strip()
        if not ip:
            print(co("Usage: reverse IP", C.RED)); return
        reverse_lookup(self.resolver, ip)

    def do_propagation(self, args):
        p = args.split()
        if not p:
            print(co("Usage: propagation DOMAIN [TYPE]", C.RED)); return
        check_propagation(
            p[0],
            p[1].upper() if len(p) > 1 else 'A',
            self.timeout
        )

    def do_axfr(self, args):
        domain = args.strip()
        if not domain:
            print(co("Usage: axfr DOMAIN", C.RED)); return
        section(f"Zone Transfer — {domain}", C.RED)
        recs, status = attempt_axfr(self.resolver, domain)
        if recs:
            warn(f"SUCCESS! {len(recs)} records")
            for r in recs:
                print(f"  {co(r, C.GREEN)}")
        else:
            ok(f"{status}")

    def do_compare(self, args):
        p = args.split()
        if len(p) < 2:
            print(co("Usage: compare DOMAIN_A DOMAIN_B [types]", C.RED))
            return
        types = [t.upper() for t in p[2:]] or None
        compare_domains(self.resolver, p[0], p[1], types)

    def do_snapshot(self, args):
        domain = args.strip()
        if not domain:
            print(co("Usage: snapshot DOMAIN", C.RED)); return
        section(f"Snapshot — {domain}", C.YELLOW)
        save_snapshot(domain, lookup_records(self.resolver, domain))

    def do_diff(self, args):
        domain = args.strip()
        if not domain:
            print(co("Usage: diff DOMAIN", C.RED)); return
        diff_snapshot(domain, lookup_records(self.resolver, domain))

    def do_bulk(self, args):
        p = args.split()
        if not p:
            print(co("Usage: bulk FILE [types]", C.RED)); return
        types = [t.upper() for t in p[1:]] or None
        bulk_lookup(self.resolver, p[0], types)

    def do_asn(self, args):
        ip = args.strip()
        if not ip:
            print(co("Usage: asn IP_ADDRESS", C.RED)); return
        r = asn_lookup(ip)
        print_asn(r)

    def do_ssl(self, args):
        p = args.split()
        if not p:
            print(co("Usage: ssl DOMAIN [PORT]", C.RED)); return
        port = int(p[1]) if len(p) > 1 else 443
        r    = ssl_info(p[0], port, self.timeout)
        print_ssl(r)

    def do_headers(self, args):
        domain = args.strip()
        if not domain:
            print(co("Usage: headers DOMAIN", C.RED)); return
        r = check_headers(domain, self.timeout)
        print_headers(r)

    def do_spoof(self, args):
        domain = args.strip()
        if not domain:
            print(co("Usage: spoof DOMAIN", C.RED)); return
        r = spoof_test(self.resolver, domain)
        print_spoof(r)

    def do_autorecon(self, args):
        p = args.split()
        if not p:
            print(co("Usage: autorecon DOMAIN [output_file] [fmt]", C.RED))
            return
        domain = p[0]
        outf   = p[1] if len(p) > 1 else None
        fmt    = p[2].lower() if len(p) > 2 else self.output_fmt
        self.last_results = auto_recon(
            self.resolver, domain, self.mode, outf, fmt
        )
        self.last_domain = domain

    def do_export(self, args):
        p = args.split()
        if not p:
            print(co("Usage: export FILE [txt|json|csv|html]", C.RED)); return
        if not self.last_results:
            print(co("[!] No results yet.", C.RED)); return
        fmt = p[1].lower() if len(p) > 1 else self.output_fmt
        export_results(self.last_results, p[0], fmt)

    def do_set(self, args):
        p = args.split(maxsplit=1)
        if len(p) < 2:
            print(
                "Params: resolver [IP,IP | auto] | "
                "timeout N | mode [normal|expert|quiet] | "
                "output [txt|json|csv|html]"
            )
            return
        param, val = p[0].lower(), p[1].strip()
        if param == "resolver":
            self.custom_ns = None if val.lower() == "auto" else val
            self._refresh()
            print(co(f"[*] Resolver = {val}", C.GREEN))
        elif param == "timeout":
            try:
                self.timeout = int(val)
                self._refresh()
                print(co(f"[*] Timeout = {self.timeout}s", C.GREEN))
            except Exception:
                print(co("[!] Must be integer", C.RED))
        elif param == "mode":
            if val in ("normal","expert","quiet"):
                self.mode = val
                print(co(f"[*] Mode = {self.mode}", C.GREEN))
            else:
                print(co("[!] Mode: normal | expert | quiet", C.RED))
        elif param == "output":
            if val in ("txt","json","csv","html"):
                self.output_fmt = val
                print(co(f"[*] Output = {self.output_fmt}", C.GREEN))
            else:
                print(co("[!] Format: txt | json | csv | html", C.RED))
        else:
            print(co(f"[!] Unknown param: {param}", C.RED))

    def do_info(self, _=None):
        print(f"\n{co('Settings:', C.CYAN, C.BOLD)}")
        ns = ", ".join(self.resolver.nameservers[:3])
        box_line("Nameservers:", ns,             C.DIM, C.GREEN)
        box_line("Timeout:",     f"{self.timeout}s", C.DIM, C.WHITE)
        box_line("Mode:",        self.mode,      C.DIM, C.YELLOW)
        box_line("Output:",      self.output_fmt, C.DIM, C.WHITE)
        print()

    def do_tutorial(self, _=None):
        print(f"""
{co('═'*62, C.CYAN)}
{co('  🦂 DNS SCORPION v1.1 TUTORIAL', C.BOLD)}
{co('  ⚡ Sailerbross Technology', C.MAGENTA)}
{co('═'*62, C.CYAN)}

{co('── QUICK START ─────────────────────────────────────', C.YELLOW)}
  {co('lookup google.com', C.GREEN)}              all DNS records
  {co('autorecon example.com', C.GREEN)}          FULL audit + HTML report

{co('── NEW v1.1 POWER FEATURES ─────────────────────────', C.YELLOW)}
  {co('asn 216.58.223.206', C.GREEN)}             IP owner, ASN, country
  {co('ssl google.com', C.GREEN)}                 certificate + expiry
  {co('headers github.com', C.GREEN)}             security header grade
  {co('spoof example.com', C.GREEN)}              can domain be spoofed?

{co('── CLASSIC FEATURES ────────────────────────────────', C.YELLOW)}
  {co('reverse 8.8.8.8', C.GREEN)}                PTR lookup
  {co('propagation example.com A', C.GREEN)}      15 global DNS check
  {co('axfr example.com', C.GREEN)}              zone transfer test
  {co('compare google.com bing.com', C.GREEN)}    side-by-side

{co('── SETTINGS ─────────────────────────────────────────', C.YELLOW)}
  {co('set resolver 1.1.1.1,8.8.8.8', C.GREEN)}
  {co('set mode expert', C.GREEN)}               show TTL + raw
  {co('set output html', C.GREEN)}               default export
  {co('info', C.GREEN)}                          show config

{co('⚠  LEGAL: Only audit domains you own or have permission.', C.RED, C.BOLD)}
{co('═'*62, C.CYAN)}
""")

    def do_help(self, _=None):
        print(f"""
{co('═'*62, C.CYAN)}
{co(' 🦂 DNS SCORPION v1.1 — ALL COMMANDS', C.BOLD)}
{co('═'*62, C.CYAN)}

{co('CORE', C.YELLOW)}
  lookup DOMAIN [TYPE ...]
  reverse IP
  propagation DOMAIN [TYPE]
  axfr DOMAIN

{co('v1.1 NEW', C.GREEN+C.BOLD)}
  asn IP
  ssl DOMAIN [PORT]
  headers DOMAIN
  spoof DOMAIN
  autorecon DOMAIN [out] [fmt]

{co('UTILS', C.YELLOW)}
  compare A B [types]
  snapshot / diff DOMAIN
  bulk FILE [types]
  export FILE [fmt]

{co('CONFIG', C.YELLOW)}
  set resolver|timeout|mode|output
  info

{co('HELP', C.YELLOW)}
  tutorial   help / ?   exit / quit
{co('═'*62, C.CYAN)}
""")

    def do_exit(self, _=None):
        self.running = False
        print(co(
            "\n  🦂 DNS Scorpion — Sailerbross Technology\n"
            "  Stay ethical. Stay sharp.\n",
            C.YELLOW, C.BOLD
        ))

    def run(self):
        clr()
        print_banner()

        if not DNS_OK:
            print(co(
                "[!] dnspython missing!\n"
                "    pip install dnspython",
                C.RED, C.BOLD
            ))
            sys.exit(1)

        ns = ", ".join(FALLBACK_NS[:3])
        print(co(
            f"  Termux-safe | Nameservers: {ns} ...\n",
            C.CYAN
        ))
        print(co(
            "  Type {co('autorecon DOMAIN', C.GREEN)} for full audit | "
            "'tutorial' to learn | 'help' for commands\n",
            C.DIM
        ))

        CMDS = {
            "lookup":      self.do_lookup,
            "reverse":     self.do_reverse,
            "propagation": self.do_propagation,
            "prop":        self.do_propagation,
            "axfr":        self.do_axfr,
            "compare":     self.do_compare,
            "snapshot":    self.do_snapshot,
            "diff":        self.do_diff,
            "bulk":        self.do_bulk,
            "asn":         self.do_asn,
            "ssl":         self.do_ssl,
            "headers":     self.do_headers,
            "spoof":       self.do_spoof,
            "autorecon":   self.do_autorecon,
            "export":      self.do_export,
            "set":         self.do_set,
            "info":        self.do_info,
            "tutorial":    self.do_tutorial,
            "help":        self.do_help,
            "?":           self.do_help,
            "exit":        self.do_exit,
            "quit":        self.do_exit,
        }

        while self.running:
            try:
                raw = input(
                    f"\n{co('scorpion', C.YELLOW, C.BOLD)}"
                    f"{co('>', C.CYAN)} "
                ).strip()
                if not raw:
                    continue
                parts = raw.split(maxsplit=1)
                cmd   = parts[0].lower()
                arg   = parts[1] if len(parts) > 1 else ""
                if cmd in CMDS:
                    CMDS[cmd](arg)
                else:
                    print(co(
                        f"[!] Unknown: '{cmd}'. Type 'help'.",
                        C.RED
                    ))
            except KeyboardInterrupt:
                print(co("\n  Use 'exit' to quit.", C.YELLOW))
            except EOFError:
                break

# ============================================================
# DIRECT CLI
# ============================================================
def main_direct():
    p = argparse.ArgumentParser(
        description="DNS Scorpion v1.1 FINAL — Sailerbross Technology"
    )
    sub = p.add_subparsers(dest="command")

    for cmd in ["lookup", "reverse", "propagation", "axfr", "compare",
                "bulk", "asn", "ssl", "headers", "spoof", "autorecon"]:
        sp = sub.add_parser(cmd)
        if cmd == "lookup":
            sp.add_argument("domain")
            sp.add_argument("types", nargs="*")
        elif cmd == "compare":
            sp.add_argument("domain_a")
            sp.add_argument("domain_b")
            sp.add_argument("types", nargs="*")
        elif cmd == "bulk":
            sp.add_argument("file")
            sp.add_argument("types", nargs="*")
        elif cmd == "propagation":
            sp.add_argument("domain")
            sp.add_argument("type", nargs="?", default="A")
        elif cmd == "ssl":
            sp.add_argument("domain")
            sp.add_argument("port", nargs="?", type=int, default=443)
        elif cmd in ["reverse", "asn"]:
            sp.add_argument("ip")
        else:
            sp.add_argument("domain")

    p.add_argument("--resolver")
    p.add_argument("--timeout", type=int, default=5)
    p.add_argument("--mode", default="normal",
                   choices=["normal","expert","quiet"])
    p.add_argument("--output")
    p.add_argument("--format", default="html",
                   choices=["txt","json","csv","html"])

    args = p.parse_args()
    print_banner()

    if not DNS_OK:
        print(co("[!] pip install dnspython", C.RED))
        sys.exit(1)

    resolver = make_resolver(args.resolver, args.timeout)
    cmd      = args.command

    if cmd == "lookup":
        types = [t.upper() for t in args.types] or None
        recs  = lookup_records(resolver, args.domain, types)
        section(f"Lookup: {args.domain}", C.CYAN)
        print_records(recs, args.mode)
        if args.output:
            export_results(
                {"domain": args.domain,
                 "records": {rt: [{"value":v,"ttl":t} for v,t in rs]
                             for rt,rs in recs.items()}},
                args.output, args.format
            )
    elif cmd == "reverse":
        reverse_lookup(resolver, args.ip)
    elif cmd == "propagation":
        check_propagation(args.domain, args.type, args.timeout)
    elif cmd == "axfr":
        section(f"Zone Transfer — {args.domain}", C.RED)
        recs, status = attempt_axfr(resolver, args.domain)
        (warn(f"SUCCESS! {len(recs)} records") if recs
         else ok(status))
        for r in recs:
            print(f"  {co(r, C.GREEN)}")
    elif cmd == "compare":
        types = [t.upper() for t in args.types] or None
        compare_domains(resolver, args.domain_a, args.domain_b, types)
    elif cmd == "bulk":
        types = [t.upper() for t in args.types] or None
        bulk_lookup(resolver, args.file, types, args.output)
    elif cmd == "asn":
        print_asn(asn_lookup(args.ip))
    elif cmd == "ssl":
        print_ssl(ssl_info(args.domain, args.port, args.timeout))
    elif cmd == "headers":
        print_headers(check_headers(args.domain, args.timeout))
    elif cmd == "spoof":
        print_spoof(spoof_test(resolver, args.domain))
    elif cmd == "autorecon":
        auto_recon(
            resolver, args.domain, args.mode,
            args.output, args.format
        )
    else:
        p.print_help()
        print(f"\n{co('Quick examples:', C.YELLOW)}")
        print(f"  {co('python dns_scorpion.py autorecon google.com', C.GREEN)}")
        print(f"  {co('python dns_scorpion.py ssl cloudflare.com', C.GREEN)}")
        print(f"  {co('python dns_scorpion.py headers github.com', C.GREEN)}")
        print(f"  {co('python dns_scorpion.py spoof example.com', C.GREEN)}")
        print(f"  {co('python dns_scorpion.py asn 8.8.8.8', C.GREEN)}")

# ============================================================
# ENTRY POINT
# ============================================================
if __name__ == "__main__":
    if len(sys.argv) > 1:
        main_direct()
    else:
        ScorpionShell().run()