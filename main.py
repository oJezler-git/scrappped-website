import os
import re

# File extensions to process
TARGET_EXTENSIONS = {'.html', '.htm'}

# Keywords that identify telemetry/analytics scripts
INLINE_BLACKLIST = [
    "posthog.init", "posthog.identify",
    "intercomSettings", "intercom.io",
    "ttq.load", "TiktokAnalyticsObject", "analytics.tiktok.com"
]

SRC_BLACKLIST_PATTERNS = [
    re.compile(r"(surveys|recorder|autocapture|config|intercom|posthog|analytics).*\.js", re.IGNORECASE)
]

# Matches both inline <script>...</script> and external <script src="..."></script>
SCRIPT_TAG_PATTERN = re.compile(r'<script\b[^>]*>(.*?)</script\s*>', re.DOTALL | re.IGNORECASE)
SCRIPT_SRC_PATTERN = re.compile(r'<script\b[^>]*\bsrc\s*=\s*["\']([^"\']+)["\'][^>]*>\s*</script\s*>', re.IGNORECASE)

def should_remove_inline(script_body):
    return any(keyword in script_body for keyword in INLINE_BLACKLIST)

def should_remove_src(src):
    return any(pattern.search(src) for pattern in SRC_BLACKLIST_PATTERNS)

def clean_html(content):
    # Remove external <script src="..."></script> if it matches known trackers
    content = re.sub(SCRIPT_SRC_PATTERN, 
                     lambda m: "" if should_remove_src(m.group(1)) else m.group(0), 
                     content)

    # Remove inline <script> blocks with suspicious content
    def inline_replacer(match):
        full_tag = match.group(0)
        body = match.group(1)
        return "" if should_remove_inline(body) else full_tag

    content = re.sub(SCRIPT_TAG_PATTERN, inline_replacer, content)

    return content

def clean_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        original = f.read()
    cleaned = clean_html(original)

    if cleaned != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(cleaned)
        print(f"[Cleaned] {file_path}")
    else:
        print(f"[Unchanged] {file_path}")

def clean_all_files():
    root = os.getcwd()
    for dirpath, _, filenames in os.walk(root):
        for filename in filenames:
            if os.path.splitext(filename)[1].lower() in TARGET_EXTENSIONS:
                clean_file(os.path.join(dirpath, filename))

if __name__ == "__main__":
    clean_all_files()
