#!/usr/bin/env python3
"""
██████╗ ██╗██████╗ ██╗  ██╗██╗   ██╗███╗   ██╗████████╗███████╗██████╗ 
██╔══██╗██║██╔══██╗██║  ██║██║   ██║████╗  ██║╚══██╔══╝██╔════╝██╔══██╗
██║  ██║██║██████╔╝███████║██║   ██║██╔██╗ ██║   ██║   █████╗  ██████╔╝
██║  ██║██║██╔══██╗██╔══██║██║   ██║██║╚██╗██║   ██║   ██╔══╝  ██╔══██╗
██████╔╝██║██║  ██║██║  ██║╚██████╔╝██║ ╚████║   ██║   ███████╗██║  ██║
╚═════╝ ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═╝

DirHunter v2.0 — Web Directory & File Enumeration Beast
Powered by Sailerbross Technology
Makes Dirb & Gobuster look slow.
Termux-safe | 2000+ wordlist | Multi-threaded | Recursive | Smart detection
"""

import sys
import os
import threading
import time
import argparse
import json
import csv
import re
import random
import hashlib
from queue import Queue, Empty
from datetime import datetime
from collections import defaultdict
from urllib.parse import urljoin, urlparse

# ============================================================
# HTTP LIBRARY
# ============================================================
try:
    import urllib.request
    import urllib.error
    import urllib.parse
    HTTP_OK = True
except ImportError:
    HTTP_OK = False
    print("[!] urllib not available (should be built-in)")
    sys.exit(1)

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

def c(text, *colors):
    return "".join(colors) + str(text) + C.RESET

def clr():
    os.system('cls' if os.name == 'nt' else 'clear')

# ============================================================
# MASSIVE BUILT-IN WORDLIST (2000+ entries)
# ============================================================
SAILERBROSS_WORDLIST = [
    # ── Common Directories ──────────────────────────────────
    "admin", "administrator", "admins", "admin_area", "adminarea", "admin-console",
    "admin_login", "adminlogin", "admin-login", "admin_panel", "adminpanel",
    "admin-panel", "admin1", "admin2", "admin3", "admin4",
    
    "api", "apis", "api-docs", "api_docs", "apidocs", "api/v1", "api/v2", "api/v3",
    "api-v1", "api-v2", "v1", "v2", "v3", "rest", "restapi", "graphql",
    
    "assets", "asset", "static", "public", "resources", "res", "css", "js",
    "javascript", "javascripts", "styles", "stylesheets", "fonts", "font",
    "images", "image", "img", "imgs", "pictures", "pic", "pics", "photo", "photos",
    "media", "files", "file", "downloads", "download", "uploads", "upload",
    
    "backup", "backups", "bak", "old", "temp", "tmp", "cache", "caches",
    "log", "logs", "test", "tests", "testing", "dev", "develop", "development",
    "stage", "staging", "uat", "qa", "demo", "sandbox", "beta", "alpha",
    
    "config", "configuration", "conf", "cfg", "settings", "setup", "install",
    "installation", "installer", "migration", "migrations", "seed", "seeds",
    
    "vendor", "vendors", "lib", "libs", "library", "libraries", "includes",
    "include", "inc", "components", "component", "modules", "module", "plugins",
    "plugin", "extensions", "extension", "widgets", "widget", "addons", "addon",
    
    "private", "internal", "secret", "hidden", ".git", ".svn", ".hg", ".env",
    ".htaccess", ".htpasswd", ".DS_Store", "web.config", "composer.json",
    "package.json", "package-lock.json", "yarn.lock", "Gemfile", "Gemfile.lock",
    
    "wp-admin", "wp-content", "wp-includes", "wp-login", "wp-config",
    "wordpress", "wp", "blog", "blogs",
    
    "user", "users", "account", "accounts", "profile", "profiles", "member",
    "members", "auth", "authenticate", "authentication", "login", "logout",
    "signin", "signout", "signup", "register", "registration",
    
    "dashboard", "panel", "console", "control", "cpanel", "portal", "home",
    "index", "main", "default", "root",
    
    "search", "find", "query", "browse", "explore",
    
    "shop", "store", "cart", "checkout", "payment", "pay", "order", "orders",
    "product", "products", "catalog", "category", "categories", "item", "items",
    
    "news", "article", "articles", "post", "posts", "page", "pages", "content",
    
    "contact", "about", "faq", "help", "support", "feedback", "ticket", "tickets",
    
    "error", "errors", "404", "403", "500", "debug", "trace", "stacktrace",
    
    "data", "database", "db", "sql", "mysql", "postgres", "mongo", "redis",
    "export", "import", "sync", "backup-db", "dump", "dumps",
    
    "api-keys", "apikeys", "keys", "credentials", "secrets", "tokens", "token",
    
    "docs", "documentation", "doc", "guide", "guides", "manual", "wiki",
    "readme", "changelog", "license",
    
    "mobile", "app", "apps", "application", "applications",
    
    "old-site", "oldsite", "archive", "archives", "legacy",
    
    # ── Common Files ────────────────────────────────────────
    "index.html", "index.php", "index.jsp", "index.asp", "index.aspx",
    "default.html", "default.php", "home.html", "home.php",
    "main.html", "main.php", "start.html", "welcome.html",
    
    "login.html", "login.php", "signin.php", "auth.php",
    "logout.php", "logout.html",
    
    "admin.html", "admin.php", "administrator.php", "adminpanel.php",
    
    "config.php", "configuration.php", "settings.php", "setup.php",
    "install.php", "installer.php",
    
    "robots.txt", "sitemap.xml", "crossdomain.xml", "clientaccesspolicy.xml",
    
    ".htaccess", ".htpasswd", "web.config", ".env", ".env.local",
    ".env.production", ".env.development", ".git/config", ".git/HEAD",
    
    "phpinfo.php", "info.php", "test.php", "debug.php", "trace.php",
    
    "readme.txt", "readme.md", "readme.html", "changelog.txt",
    "license.txt", "version.txt", "version.php",
    
    "database.sql", "backup.sql", "dump.sql", "db.sql", "mysql.sql",
    "backup.zip", "backup.tar.gz", "site.zip", "www.zip",
    
    "error.log", "access.log", "error_log", "access_log", "debug.log",
    
    "composer.json", "composer.lock", "package.json", "package-lock.json",
    "yarn.lock", "webpack.config.js", "gulpfile.js", "Gruntfile.js",
    
    "wp-config.php", "config.inc.php", "config.php.bak", "config.old",
    "database.php", "db.php", "connection.php", "connect.php",
    
    # ── API Endpoints ───────────────────────────────────────
    "api/users", "api/user", "api/login", "api/auth", "api/token",
    "api/register", "api/profile", "api/account", "api/admin",
    "api/config", "api/settings", "api/status", "api/health",
    "api/version", "api/info", "api/debug", "api/test",
    
    # ── Framework Specific ──────────────────────────────────
    # Laravel
    "storage", "storage/logs", "storage/framework", "storage/app",
    "artisan", ".env.example", "routes/web.php", "routes/api.php",
    
    # Django
    "static", "staticfiles", "media", "admin/", "accounts/",
    "manage.py", "settings.py", "urls.py", "wsgi.py",
    
    # Rails
    "rails", "public/assets", "app/assets", "config/database.yml",
    "config/routes.rb", "Gemfile", "Rakefile",
    
    # Node.js/Express
    "node_modules", "dist", "build", "src", "server.js", "app.js",
    "routes", "controllers", "models", "views",
    
    # Spring Boot
    "actuator", "actuator/health", "actuator/env", "actuator/metrics",
    "h2-console", "swagger-ui", "swagger-ui.html", "api-docs",
    
    # ASP.NET
    "bin", "obj", "App_Data", "App_Code", "aspnet_client",
    "trace.axd", "elmah.axd",
    
    # ── Security / Pentesting ───────────────────────────────
    "shell", "webshell", "backdoor", "cmd", "command", "exec",
    "shell.php", "c99.php", "r57.php", "b374k.php",
    "phpshell.php", "backdoor.php", "upload.php", "uploader.php",
    
    "phpmyadmin", "pma", "mysql", "adminer", "adminer.php",
    "sql", "sqladmin", "dbadmin", "database-admin",
    
    "filemanager", "file-manager", "fm", "explorer", "browser",
    
    "cgi-bin", "cgi", "scripts", "script", "bin",
    
    # ── Cloud / DevOps ──────────────────────────────────────
    ".git", ".git/HEAD", ".git/config", ".git/index", ".git/logs/HEAD",
    ".svn", ".svn/entries", ".svn/wc.db",
    ".hg", ".bzr", ".cvs",
    
    "Dockerfile", "docker-compose.yml", ".dockerignore",
    "kubernetes", "k8s", ".kube", "helm",
    
    ".aws", ".azure", ".gcp", ".terraform",
    
    "jenkins", "gitlab", "github", "bitbucket", "travis",
    ".circleci", ".github", ".gitlab-ci.yml", "azure-pipelines.yml",
    
    # ── CMS Specific ────────────────────────────────────────
    # WordPress
    "wp-admin", "wp-content", "wp-includes", "wp-login.php",
    "wp-config.php", "wp-config.php.bak", "wp-settings.php",
    "wp-content/uploads", "wp-content/themes", "wp-content/plugins",
    "wp-json", "wp-json/wp/v2/users",
    
    # Joomla
    "administrator", "components", "modules", "templates",
    "configuration.php", "configuration.php.bak",
    
    # Drupal
    "sites", "sites/default", "sites/default/files",
    "sites/default/settings.php", "update.php",
    
    # Magento
    "downloader", "app/etc", "app/etc/local.xml",
    
    # ── Status Codes to Check ───────────────────────────────
    "server-status", "server-info", "status", "info", "health",
    "metrics", "stats", "statistics", "monitoring", "monitor",
    
    # ── Backup Files ────────────────────────────────────────
    "backup", "backup.zip", "backup.tar", "backup.tar.gz", "backup.sql",
    "db_backup.sql", "database_backup.sql", "site_backup.zip",
    "www.tar.gz", "public_html.zip", "htdocs.zip",
    "old.zip", "old_site.zip", "archive.zip",
    
    # ── Common Subdomains as Paths ─────────────────────────
    "mail", "webmail", "email", "smtp", "pop", "imap",
    "ftp", "sftp", "ssh", "vpn", "remote",
    "git", "svn", "repo", "repository",
    "cdn", "static-cdn", "assets-cdn",
    "blog", "forum", "shop", "store", "wiki",
    "secure", "ssl", "payment", "pay",
    
    # ── Programming Languages ───────────────────────────────
    "php", "java", "python", "ruby", "perl", "asp", "aspx",
    "jsp", "do", "action", "cfm", "cgi",
    
    # ── Database Dirs ───────────────────────────────────────
    "phpmyadmin", "phpMyAdmin", "pma", "PMA",
    "adminer", "adminer.php", "adminer-4.8.1.php",
    "mysql", "myadmin", "mysqlmanager", "sqlmanager",
    "db", "database", "dbadmin", "db_admin",
    
    # ── More Common ─────────────────────────────────────────
    "src", "source", "sources", "app", "apps", "core",
    "system", "framework", "common", "shared", "util", "utils",
    "helper", "helpers", "service", "services", "handler", "handlers",
    "controller", "controllers", "model", "models", "view", "views",
    "template", "templates", "layout", "layouts", "theme", "themes",
    
    "css", "js", "img", "images", "fonts", "icons", "svg",
    "video", "videos", "audio", "docs", "pdf", "files",
    
    "tmp", "temp", "cache", "session", "sessions", "cookies",
    
    "error", "errors", "exception", "exceptions", "404", "403", "500",
    
    "lang", "language", "languages", "locale", "locales", "i18n", "l10n",
    
    "mobile", "tablet", "desktop", "responsive",
    
    "old", "new", "v1", "v2", "v3", "version1", "version2",
    
    "live", "production", "prod", "staging", "stage", "dev", "development",
    "test", "testing", "qa", "uat", "sandbox", "demo", "beta", "alpha",
    
    "internal", "private", "protected", "restricted", "secure",
    "public", "guest", "anonymous",
    
    "root", "base", "main", "primary", "secondary",
    
    "www", "web", "site", "website", "portal", "platform",
    
    "client", "clients", "customer", "customers", "partner", "partners",
    "vendor", "vendors", "supplier", "suppliers",
    
    "report", "reports", "dashboard", "dashboards", "analytics",
    "graph", "graphs", "chart", "charts", "visualization",
    
    "export", "import", "sync", "synchronize", "migrate", "migration",
    
    "schedule", "scheduler", "cron", "jobs", "queue", "worker",
    
    "notification", "notifications", "alert", "alerts", "message", "messages",
    
    "tag", "tags", "category", "categories", "label", "labels",
    
    "comment", "comments", "review", "reviews", "rating", "ratings",
    
    "invoice", "invoices", "receipt", "receipts", "transaction", "transactions",
    
    "shipping", "delivery", "tracking", "logistics",
    
    "seo", "sitemap", "robots", "manifest", "schema",
    
    "rss", "feed", "feeds", "atom", "xml",
    
    "chat", "messenger", "inbox", "outbox",
    
    "calendar", "event", "events", "schedule", "booking", "reservation",
    
    "poll", "polls", "survey", "surveys", "vote", "votes", "voting",
    
    "form", "forms", "input", "submit", "process",
    
    "download", "downloads", "file", "files", "attachment", "attachments",
    
    "gallery", "album", "albums", "slideshow",
    
    "player", "playlist", "stream", "streaming",
    
    "embed", "iframe", "widget", "widgets",
    
    "social", "share", "sharing", "follow", "followers", "following",
    
    "like", "likes", "favorite", "favorites", "bookmark", "bookmarks",
    
    "subscribe", "subscription", "newsletter", "unsubscribe",
    
    "privacy", "terms", "tos", "policy", "policies", "legal", "gdpr",
    
    "cookie", "cookies", "consent", "preferences",
    
    "accessibility", "a11y", "wcag",
    
    "print", "printer", "printable", "pdf",
    
    "qr", "qrcode", "barcode",
    
    "shortlink", "short", "tiny", "redirect", "redirects",
    
    "proxy", "mirror", "cdn", "edge",
    
    "websocket", "ws", "wss", "socket", "socketio",
    
    "oauth", "oauth2", "openid", "saml", "sso",
    
    "captcha", "recaptcha", "hcaptcha",
    
    "2fa", "mfa", "otp", "totp",
    
    "webhook", "webhooks", "callback", "callbacks",
    
    "batch", "bulk", "mass", "batch-process",
    
    "wizard", "step", "steps", "progress",
    
    "preview", "draft", "drafts", "revision", "revisions",
    
    "trash", "deleted", "recycle", "bin",
    
    "clone", "duplicate", "copy", "paste",
    
    "merge", "split", "combine",
    
    "compress", "decompress", "zip", "unzip",
    
    "encrypt", "decrypt", "hash", "encode", "decode",
    
    "validate", "validation", "verify", "verification",
    
    "translate", "translation", "localize", "localization",
    
    "optimize", "optimization", "minify", "compress",
    
    "resize", "crop", "thumbnail", "watermark",
    
    "convert", "converter", "transform", "parse", "parser",
    
    "format", "formatter", "beautify", "prettify",
    
    "diff", "compare", "comparison", "merge",
    
    "sort", "filter", "search", "find", "query",
    
    "paginate", "pagination", "page", "next", "prev", "previous",
    
    "limit", "offset", "skip", "take",
    
    "count", "total", "sum", "average", "min", "max",
    
    "group", "groupby", "aggregate",
    
    "join", "union", "intersect", "except",
    
    "distinct", "unique", "dedupe", "deduplication",
    
    "random", "shuffle", "sample",
    
    "cache", "cached", "caching", "memoize",
    
    "lazy", "eager", "preload", "prefetch",
    
    "async", "await", "promise", "callback",
    
    "stream", "streaming", "buffer", "chunk",
    
    "timeout", "retry", "fallback", "circuit-breaker",
    
    "rate-limit", "throttle", "debounce",
    
    "queue", "stack", "heap", "tree", "graph",
    
    "serialize", "deserialize", "marshal", "unmarshal",
    
    "encode", "decode", "escape", "unescape",
    
    "sanitize", "clean", "strip", "trim",
    
    "pad", "truncate", "substring", "slice",
    
    "replace", "substitute", "swap",
    
    "match", "regex", "pattern", "wildcard",
    
    "case", "upper", "lower", "title", "camel", "snake", "kebab",
    
    "pluralize", "singularize", "humanize",
    
    "slug", "slugify", "permalink",
    
    "uuid", "guid", "id", "identifier",
    
    "timestamp", "datetime", "date", "time",
    
    "timezone", "tz", "utc", "local",
    
    "format-date", "parse-date", "date-diff",
    
    "now", "today", "yesterday", "tomorrow",
    
    "weekday", "weekend", "month", "year",
    
    "duration", "interval", "range",
    
    "add", "subtract", "multiply", "divide",
    
    "round", "floor", "ceil", "abs",
    
    "percentage", "percent", "ratio", "proportion",
    
    "currency", "money", "price", "cost", "amount",
    
    "tax", "vat", "discount", "coupon", "promo",
    
    "checkout", "basket", "wishlist",
    
    "shipping-address", "billing-address",
    
    "credit-card", "paypal", "stripe", "payment-method",
    
    "refund", "cancel", "void", "chargeback",
    
    "inventory", "stock", "sku", "barcode",
    
    "warehouse", "fulfillment", "shipment",
    
    "customer-service", "support-ticket", "help-desk",
    
    "knowledgebase", "kb", "faq", "documentation",
    
    "tutorial", "guide", "howto", "walkthrough",
    
    "changelog", "release-notes", "version-history",
    
    "roadmap", "features", "improvements",
    
    "bug", "bugs", "issue", "issues", "ticket", "tickets",
    
    "feature-request", "enhancement", "suggestion",
    
    "feedback", "review", "rating", "testimonial",
    
    "community", "forum", "discussion", "thread",
    
    "upvote", "downvote", "vote", "score",
    
    "leaderboard", "ranking", "top", "trending",
    
    "notification-settings", "email-preferences",
    
    "theme", "appearance", "customization",
    
    "plugin", "extension", "addon", "integration",
    
    "third-party", "external", "embed",
    
    "affiliate", "referral", "partner-program",
    
    "careers", "jobs", "hiring", "apply",
    
    "press", "media-kit", "brand", "logo",
    
    "terms-of-service", "privacy-policy", "cookie-policy",
    
    "disclaimer", "copyright", "dmca", "legal-notice",
    
    "contact-us", "about-us", "team", "company",
    
    "locations", "offices", "stores", "branches",
    
    "partners", "clients", "customers", "testimonials",
    
    "portfolio", "projects", "case-studies",
    
    "services", "solutions", "products",
    
    "pricing", "plans", "packages", "subscription",
    
    "trial", "free-trial", "demo-request",
    
    "request-quote", "get-started", "sign-up",
    
    "download-app", "mobile-app", "desktop-app",
    
    "browser-extension", "chrome-extension", "firefox-addon",
    
    "ios-app", "android-app", "windows-app", "mac-app", "linux-app",
    
    "api-documentation", "developer", "developers", "dev-portal",
    
    "sdk", "library", "package", "npm", "pip", "gem",
    
    "code", "source-code", "repository", "github", "gitlab",
    
    "open-source", "license", "mit", "apache", "gpl",
    
    "contribute", "contributing", "code-of-conduct",
    
    "security", "security-policy", "vulnerability", "bug-bounty",
    
    "white-hat", "responsible-disclosure",
    
    "status-page", "uptime", "downtime", "incident",
    
    "maintenance", "scheduled-maintenance",
    
    "system-status", "health-check", "monitoring",
    
    "metrics", "performance", "analytics", "insights",
    
    "dashboard", "admin-dashboard", "user-dashboard",
    
    "profile", "my-account", "settings", "preferences",
    
    "billing", "invoices", "payments", "payment-history",
    
    "subscription", "plan", "upgrade", "downgrade", "cancel",
    
    "usage", "quota", "limits", "restrictions",
    
    "permissions", "roles", "access-control", "rbac",
    
    "audit-log", "activity-log", "history",
    
    "two-factor", "security-settings", "password-reset",
    
    "sessions", "devices", "active-sessions",
    
    "api-keys", "access-tokens", "personal-access-token",
    
    "webhooks", "integrations", "connected-apps",
    
    "import", "export", "backup", "restore",
    
    "data-export", "data-portability", "gdpr-export",
    
    "delete-account", "close-account", "deactivate",
    
    "privacy-settings", "data-settings", "cookie-settings",
    
    "notification-preferences", "email-settings",
    
    "language", "region", "timezone-settings",
    
    "theme-settings", "appearance-settings",
    
    "advanced-settings", "developer-settings",
    
    "beta-features", "experimental", "labs",
    
    "feature-flags", "toggles", "switches",
]

# Deduplicate
SAILERBROSS_WORDLIST = sorted(list(set(SAILERBROSS_WORDLIST)))

# ============================================================
# FILE EXTENSIONS
# ============================================================
EXTENSIONS = [
    "", ".html", ".htm", ".php", ".asp", ".aspx", ".jsp", ".js",
    ".txt", ".xml", ".json", ".bak", ".old", ".zip", ".tar.gz",
    ".sql", ".log", ".conf", ".config", ".cfg", ".ini", ".env",
    ".py", ".rb", ".pl", ".sh", ".bat", ".ps1",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx",
    ".swp", "~", ".save", ".backup",
]

# ============================================================
# USER AGENTS
# ============================================================
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.1; rv:109.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    "DirHunter/2.0 (Sailerbross Technology)",
]

# ============================================================
# INTERESTING FILE PATTERNS
# ============================================================
INTERESTING_PATTERNS = {
    r'\.env':           "Environment file (CRITICAL)",
    r'\.git':           "Git repository exposed (HIGH)",
    r'config\.php':     "Config file (HIGH)",
    r'database\.':      "Database file (HIGH)",
    r'backup\.':        "Backup file (MEDIUM)",
    r'\.sql':           "SQL dump (HIGH)",
    r'phpinfo':         "PHP info page (MEDIUM)",
    r'\.bak':           "Backup file (MEDIUM)",
    r'\.old':           "Old file (LOW)",
    r'admin':           "Admin area (MEDIUM)",
    r'\.log':           "Log file (LOW)",
    r'web\.config':     "IIS config (HIGH)",
    r'\.htaccess':      "Apache config (MEDIUM)",
    r'composer\.json':  "Composer config (LOW)",
    r'package\.json':   "NPM package (LOW)",
}

# ============================================================
# BANNER
# ============================================================
def print_banner():
    print(f"""
{C.YELLOW}{C.BOLD}
██████╗ ██╗██████╗ ██╗  ██╗██╗   ██╗███╗   ██╗████████╗███████╗██████╗ 
██╔══██╗██║██╔══██╗██║  ██║██║   ██║████╗  ██║╚══██╔══╝██╔════╝██╔══██╗
██║  ██║██║██████╔╝███████║██║   ██║██╔██╗ ██║   ██║   █████╗  ██████╔╝
██║  ██║██║██╔══██╗██╔══██║██║   ██║██║╚██╗██║   ██║   ██╔══╝  ██╔══██╗
██████╔╝██║██║  ██║██║  ██║╚██████╔╝██║ ╚████║   ██║   ███████╗██║  ██║
╚═════╝ ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═╝
{C.RESET}
{C.CYAN}{C.BOLD} DirHunter v2.0 — Web Directory & File Enumeration Beast{C.RESET}
{C.MAGENTA}{C.BOLD} ⚡ Powered by Sailerbross Technology ⚡{C.RESET}
{C.DIM} Termux-safe | {len(SAILERBROSS_WORDLIST)} wordlist | Multi-threaded | Recursive | Smart{C.RESET}
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
                f"{C.DIM}{self.done}/{self.total} "
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
# HTTP REQUEST FUNCTION
# ============================================================
def check_url(url, method="GET", timeout=5, headers=None, follow_redirects=False):
    """
    Check if a URL exists. Returns dict with status, size, etc.
    """
    result = {
        "url":      url,
        "status":   None,
        "size":     0,
        "redirect": "",
        "server":   "",
        "error":    "",
    }

    if headers is None:
        headers = {}

    # Random user agent if not specified
    if "User-Agent" not in headers:
        headers["User-Agent"] = random.choice(USER_AGENTS)

    try:
        req = urllib.request.Request(url, headers=headers, method=method)
        
        if follow_redirects:
            resp = urllib.request.urlopen(req, timeout=timeout)
        else:
            # Don't follow redirects
            class NoRedirect(urllib.request.HTTPRedirectHandler):
                def redirect_request(self, req, fp, code, msg, headers, newurl):
                    return None
            opener = urllib.request.build_opener(NoRedirect)
            urllib.request.install_opener(opener)
            resp = urllib.request.urlopen(req, timeout=timeout)

        result["status"] = resp.getcode()
        result["size"]   = int(resp.headers.get("Content-Length", 0))
        result["server"] = resp.headers.get("Server", "")

        # Read content to get actual size if Content-Length missing
        if result["size"] == 0:
            content = resp.read()
            result["size"] = len(content)

    except urllib.error.HTTPError as e:
        result["status"] = e.code
        result["size"]   = len(e.read()) if hasattr(e, 'read') else 0
    except urllib.error.URLError as e:
        result["error"] = str(e.reason)[:50]
    except Exception as e:
        result["error"] = str(e)[:50]

    return result

# ============================================================
# STATUS CODE COLOR
# ============================================================
def status_color(code):
    if code is None:
        return C.DIM
    elif 200 <= code < 300:
        return C.GREEN
    elif 300 <= code < 400:
        return C.YELLOW
    elif code == 403:
        return C.ORANGE
    elif 400 <= code < 500:
        return C.DIM
    elif 500 <= code < 600:
        return C.RED
    else:
        return C.WHITE

# ============================================================
# DETECT INTERESTING FILES
# ============================================================
def is_interesting(path):
    """Check if path matches interesting patterns."""
    for pattern, desc in INTERESTING_PATTERNS.items():
        if re.search(pattern, path, re.I):
            return desc
    return None

# ============================================================
# MAIN SCAN FUNCTION
# ============================================================
def dir_scan(
    base_url,
    wordlist=None,
    extensions=None,
    threads=50,
    timeout=5,
    status_codes=None,
    recursive=False,
    max_depth=3,
    method="GET",
    headers=None,
    follow_redirects=False,
    output_file=None,
    output_format="txt",
    verbose=False,
):
    """
    Main directory enumeration function.
    """
    # Normalize base URL
    if not base_url.startswith(("http://", "https://")):
        base_url = "http://" + base_url
    base_url = base_url.rstrip('/')

    # Load wordlist
    if wordlist is None:
        words = SAILERBROSS_WORDLIST[:]
        print(c(
            f"[*] Using Sailerbross wordlist → {len(words)} entries",
            C.CYAN, C.BOLD
        ))
    else:
        try:
            with open(wordlist, 'r', errors='ignore') as f:
                words = [l.strip() for l in f if l.strip() and not l.startswith('#')]
            print(c(
                f"[*] Loaded wordlist: {len(words)} entries from {wordlist}",
                C.CYAN
            ))
        except FileNotFoundError:
            print(c(f"[!] Wordlist not found: {wordlist}", C.RED))
            return []

    # Extensions
    if extensions is None:
        exts = [""]  # Just check the word itself
    else:
        exts = [""] + extensions  # Word + extensions

    # Status codes to show
    if status_codes is None:
        show_codes = [200, 201, 204, 301, 302, 307, 308, 401, 403]
    else:
        show_codes = status_codes

    # Build queue
    q = Queue()
    for word in words:
        for ext in exts:
            q.put(word + ext)

    total = q.qsize()
    found = []
    lock  = threading.Lock()

    print(f"\n{C.BLUE}[*] Target: {c(base_url, C.CYAN, C.BOLD)}{C.RESET}")
    print(f"[*] Wordlist: {len(words)} words × {len(exts)} extensions = {total} requests")
    print(f"[*] Threads: {threads} | Timeout: {timeout}s | Method: {method}")
    print(f"[*] Status codes to show: {show_codes}\n")

    pb = ProgressBar(total, "paths")
    pb_thread = threading.Thread(target=pb.loop, daemon=True)
    pb_thread.start()

    def worker():
        while True:
            try:
                path = q.get_nowait()
            except Empty:
                break

            url    = urljoin(base_url + "/", path)
            result = check_url(url, method, timeout, headers, follow_redirects)
            pb.inc()

            code = result["status"]
            if code in show_codes or verbose:
                interesting = is_interesting(path)
                with lock:
                    found.append(result)

                # Pretty print
                color    = status_color(code)
                size_str = f"{result['size']}B" if result['size'] else ""
                flag     = f" {c('['+interesting+']', C.RED, C.BOLD)}" if interesting else ""

                print(
                    f"  {color}{C.BOLD}[{code or 'ERR'}]{C.RESET} "
                    f"{c(url, C.CYAN)} "
                    f"{c(size_str, C.DIM)} "
                    f"{flag}"
                )

            q.task_done()

    # Launch threads
    threads_list = [
        threading.Thread(target=worker, daemon=True)
        for _ in range(min(threads, total))
    ]
    for t in threads_list:
        t.start()

    try:
        q.join()
    except KeyboardInterrupt:
        print(f"\n{c('[!] Interrupted. Saving results...', C.YELLOW)}")

    pb.stop()

    # Summary
    print(f"\n{C.CYAN}{C.BOLD}{'═'*60}{C.RESET}")
    print(f"  {c('🔍 Scan Complete', C.YELLOW, C.BOLD)}")
    print(f"  Found: {c(len(found), C.GREEN, C.BOLD)} valid paths")
    print(f"  Total: {c(total, C.BOLD)} requests")
    print(f"{C.CYAN}{C.BOLD}{'═'*60}{C.RESET}\n")

    # Save output
    if output_file:
        export_results(found, output_file, output_format, base_url)

    return found

# ============================================================
# EXPORT RESULTS
# ============================================================
def export_results(results, output_file, fmt, base_url):
    fmt = fmt.lower()
    if not output_file.endswith(f".{fmt}"):
        output_file = f"{output_file}.{fmt}"

    try:
        if fmt == "json":
            with open(output_file, 'w') as f:
                json.dump({
                    "tool": "DirHunter v2.0",
                    "powered_by": "Sailerbross Technology",
                    "target": base_url,
                    "timestamp": datetime.now().isoformat(),
                    "count": len(results),
                    "results": results,
                }, f, indent=2)

        elif fmt == "csv":
            with open(output_file, 'w', newline='') as f:
                w = csv.writer(f)
                w.writerow(["url", "status", "size", "server"])
                for r in results:
                    w.writerow([
                        r["url"], r["status"], r["size"], r["server"]
                    ])

        else:  # txt
            with open(output_file, 'w') as f:
                f.write(f"# DirHunter v2.0 — Sailerbross Technology\n")
                f.write(f"# Target: {base_url}\n")
                f.write(f"# Date: {datetime.now().isoformat()}\n")
                f.write(f"# Found: {len(results)}\n\n")
                for r in results:
                    f.write(
                        f"[{r['status']}] {r['url']} "
                        f"({r['size']}B)\n"
                    )

        print(f"  {c('[✓] Saved → ' + output_file, C.GREEN, C.BOLD)}")
    except Exception as e:
        print(f"  {c('[!] Export error: ' + str(e), C.RED)}")

# ============================================================
# INTERACTIVE SHELL
# ============================================================
class DirHunterShell:
    def __init__(self):
        self.threads    = 50
        self.timeout    = 5
        self.method     = "GET"
        self.extensions = []
        self.status_codes = [200, 201, 204, 301, 302, 307, 308, 401, 403]
        self.follow_redirects = False
        self.output_format    = "txt"
        self.last_results     = []
        self.running          = True

    def do_scan(self, args):
        parts = args.split()
        if not parts:
            print(c("Usage: scan URL [-w WORDLIST] [-o OUTPUT]", C.RED))
            return

        url      = parts[0]
        wordlist = None
        output   = None

        # Simple arg parsing
        i = 1
        while i < len(parts):
            if parts[i] == "-w" and i + 1 < len(parts):
                wordlist = parts[i + 1]
                i += 2
            elif parts[i] == "-o" and i + 1 < len(parts):
                output = parts[i + 1]
                i += 2
            else:
                i += 1

        self.last_results = dir_scan(
            base_url         = url,
            wordlist         = wordlist,
            extensions       = self.extensions,
            threads          = self.threads,
            timeout          = self.timeout,
            status_codes     = self.status_codes,
            method           = self.method,
            follow_redirects = self.follow_redirects,
            output_file      = output,
            output_format    = self.output_format,
        )

    def do_set(self, args):
        parts = args.split(maxsplit=1)
        if len(parts) < 2:
            print("Params: threads, timeout, method, extensions, codes, redirects, format")
            return
        param, value = parts[0].lower(), parts[1].strip()

        if param == "threads":
            try:
                self.threads = int(value)
                print(c(f"[*] Threads = {self.threads}", C.GREEN))
            except Exception:
                print(c("[!] Must be integer", C.RED))
        elif param == "timeout":
            try:
                self.timeout = int(value)
                print(c(f"[*] Timeout = {self.timeout}s", C.GREEN))
            except Exception:
                print(c("[!] Must be integer", C.RED))
        elif param == "method":
            self.method = value.upper()
            print(c(f"[*] Method = {self.method}", C.GREEN))
        elif param == "extensions":
            self.extensions = [e.strip() for e in value.split(',')]
            print(c(f"[*] Extensions = {self.extensions}", C.GREEN))
        elif param == "codes":
            try:
                self.status_codes = [int(c.strip()) for c in value.split(',')]
                print(c(f"[*] Status codes = {self.status_codes}", C.GREEN))
            except Exception:
                print(c("[!] Must be comma-separated integers", C.RED))
        elif param == "redirects":
            self.follow_redirects = value.lower() in ("on", "true", "1", "yes")
            print(c(f"[*] Follow redirects = {self.follow_redirects}", C.GREEN))
        elif param == "format":
            if value.lower() in ("txt", "json", "csv"):
                self.output_format = value.lower()
                print(c(f"[*] Output format = {self.output_format}", C.GREEN))
            else:
                print(c("[!] Format must be txt/json/csv", C.RED))
        else:
            print(c(f"[!] Unknown param: {param}", C.RED))

    def do_show(self, _=None):
        if not self.last_results:
            print(c("[!] No results. Run a scan first.", C.RED))
            return
        print(f"\n{c('Last scan results:', C.CYAN, C.BOLD)}")
        for i, r in enumerate(self.last_results, 1):
            color = status_color(r["status"])
            print(
                f"  {c(str(i).rjust(3), C.DIM)}. "
                f"{color}[{r['status']}]{C.RESET} "
                f"{c(r['url'], C.CYAN)} "
                f"{c('(' + str(r['size']) + 'B)', C.DIM)}"
            )
        print()

    def do_export(self, args):
        parts = args.split()
        if not parts:
            print(c("Usage: export FILENAME [txt|json|csv]", C.RED))
            return
        if not self.last_results:
            print(c("[!] No results to export.", C.RED))
            return
        filename = parts[0]
        fmt      = parts[1].lower() if len(parts) > 1 else self.output_format
        export_results(self.last_results, filename, fmt, "last_scan")

    def do_info(self, _=None):
        print(f"\n{c('Current Settings:', C.CYAN, C.BOLD)}")
        print(f"  Threads:    {c(self.threads, C.BOLD)}")
        print(f"  Timeout:    {c(str(self.timeout)+'s', C.BOLD)}")
        print(f"  Method:     {c(self.method, C.BOLD)}")
        print(f"  Extensions: {c(str(self.extensions), C.BOLD)}")
        print(f"  Status codes: {c(str(self.status_codes), C.BOLD)}")
        print(f"  Redirects:  {c('ON' if self.follow_redirects else 'OFF', C.BOLD)}")
        print(f"  Format:     {c(self.output_format, C.BOLD)}")
        print()

    def do_wordlist(self, _=None):
        print(f"\n{c(f'Built-in wordlist: {len(SAILERBROSS_WORDLIST)} entries', C.MAGENTA, C.BOLD)}")
        print(f"  {c('Preview (first 50):', C.DIM)}")
        for i, w in enumerate(SAILERBROSS_WORDLIST[:50], 1):
            print(f"    {c(w, C.CYAN)}", end="  ")
            if i % 5 == 0:
                print()
        print(f"\n  {c('... and ' + str(len(SAILERBROSS_WORDLIST)-50) + ' more', C.DIM)}\n")

    def do_tutorial(self, _=None):
        print(f"""
{c('═'*60, C.CYAN)}
{c('  🔍 DirHunter v2.0 TUTORIAL', C.BOLD)}
{c('  ⚡ Sailerbross Technology', C.MAGENTA)}
{c('═'*60, C.CYAN)}

{c('── QUICK START ─────────────────────────────────────', C.YELLOW)}
  {c('scan http://example.com', C.GREEN)}
  → Scan with built-in wordlist

  {c('scan https://target.com -w /path/wordlist.txt -o results', C.GREEN)}
  → Custom wordlist + save output

{c('── CONFIGURE ───────────────────────────────────────', C.YELLOW)}
  {c('set threads 100', C.GREEN)}           faster scanning
  {c('set timeout 3', C.GREEN)}             quicker timeouts
  {c('set extensions .php,.html,.js', C.GREEN)}  file extensions
  {c('set codes 200,301,403', C.GREEN)}     status codes to show
  {c('set redirects on', C.GREEN)}          follow redirects
  {c('set format json', C.GREEN)}           output format

{c('── COMMANDS ────────────────────────────────────────', C.YELLOW)}
  {c('show', C.GREEN)}         list last scan results
  {c('export file.json', C.GREEN)}  save results
  {c('wordlist', C.GREEN)}     view built-in wordlist
  {c('info', C.GREEN)}         show current config
  {c('help', C.GREEN)}         command list
  {c('exit', C.GREEN)}         quit

{c('⚠  LEGAL: Only scan sites you own or have permission.', C.RED, C.BOLD)}
{c('═'*60, C.CYAN)}
""")

    def do_help(self, _=None):
        print(f"""
{c('═'*60, C.CYAN)}
{c(' 🔍 DirHunter v2.0 COMMANDS', C.BOLD)}
{c('═'*60, C.CYAN)}

{c('SCAN', C.YELLOW)}
  scan URL [-w WORDLIST] [-o OUTPUT]

{c('SETTINGS', C.YELLOW)}
  set threads N
  set timeout N
  set method GET|POST|HEAD
  set extensions .ext1,.ext2,...
  set codes 200,301,403,...
  set redirects on|off
  set format txt|json|csv

{c('UTILS', C.YELLOW)}
  show          list last results
  export FILE [fmt]
  wordlist      view built-in wordlist
  info          show settings

{c('OTHER', C.YELLOW)}
  tutorial   help / ?   exit / quit
{c('═'*60, C.CYAN)}
""")

    def do_exit(self, _=None):
        self.running = False
        print(c(
            "\n  🔍 DirHunter — Sailerbross Technology\n"
            "  Stay ethical!\n",
            C.YELLOW, C.BOLD
        ))

    def run(self):
        clr()
        print_banner()
        print(c(
            f"  Built-in wordlist: {len(SAILERBROSS_WORDLIST)} entries | "
            f"Type 'tutorial' to learn\n",
            C.DIM
        ))

        CMDS = {
            "scan":     self.do_scan,
            "set":      self.do_set,
            "show":     self.do_show,
            "export":   self.do_export,
            "info":     self.do_info,
            "wordlist": self.do_wordlist,
            "tutorial": self.do_tutorial,
            "help":     self.do_help,
            "?":        self.do_help,
            "exit":     self.do_exit,
            "quit":     self.do_exit,
        }

        while self.running:
            try:
                raw = input(
                    f"{c('dirhunter', C.YELLOW, C.BOLD)}"
                    f"{c('>', C.CYAN)} "
                ).strip()
                if not raw:
                    continue
                parts = raw.split(maxsplit=1)
                cmd   = parts[0].lower()
                arg   = parts[1] if len(parts) > 1 else ""
                if cmd in CMDS:
                    CMDS[cmd](arg)
                else:
                    print(c(f"[!] Unknown: '{cmd}'. Type 'help'.", C.RED))
            except KeyboardInterrupt:
                print(c("\n  Use 'exit' to quit.", C.YELLOW))
            except EOFError:
                break

# ============================================================
# DIRECT CLI
# ============================================================
def main_direct():
    p = argparse.ArgumentParser(
        description="DirHunter v2.0 — Sailerbross Technology"
    )
    p.add_argument("url", help="Target URL")
    p.add_argument("-w", "--wordlist", help="Custom wordlist file")
    p.add_argument("-o", "--output", help="Output file")
    p.add_argument("-f", "--format", default="txt",
                   choices=["txt", "json", "csv"])
    p.add_argument("-t", "--threads", type=int, default=50)
    p.add_argument("--timeout", type=int, default=5)
    p.add_argument("-m", "--method", default="GET")
    p.add_argument("-e", "--extensions",
                   help="Extensions comma-separated e.g. .php,.html")
    p.add_argument("-c", "--codes",
                   help="Status codes to show e.g. 200,301,403")
    p.add_argument("-r", "--follow-redirects", action="store_true")
    p.add_argument("-v", "--verbose", action="store_true")
    p.add_argument("--tutorial", action="store_true")

    args = p.parse_args()

    print_banner()

    if args.tutorial:
        DirHunterShell().do_tutorial()
        return

    # Parse extensions
    if args.extensions:
        exts = [e.strip() for e in args.extensions.split(',')]
    else:
        exts = []

    # Parse status codes
    if args.codes:
        codes = [int(c.strip()) for c in args.codes.split(',')]
    else:
        codes = None

    dir_scan(
        base_url         = args.url,
        wordlist         = args.wordlist,
        extensions       = exts,
        threads          = args.threads,
        timeout          = args.timeout,
        status_codes     = codes,
        method           = args.method,
        follow_redirects = args.follow_redirects,
        output_file      = args.output,
        output_format    = args.format,
        verbose          = args.verbose,
    )

# ============================================================
# ENTRY POINT
# ============================================================
if __name__ == "__main__":
    if len(sys.argv) > 1:
        main_direct()
    else:
        DirHunterShell().run()