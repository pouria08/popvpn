import base64
import html
import json
import os
import re
import urllib.parse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# ============================================================
# POPVPN CONFIGURATION
# ============================================================

LINKS_FILE = "links.txt"
OUTPUT_DIR = "outputs"

MAIN_CONFIG_FILE = "working_configs.txt"
MAIN_BASE64_FILE = "base64.txt"
STATS_FILE = "stats.txt"


# ============================================================
# HIDDIFY PROFILE
# ============================================================

PROFILE_TITLE = "POPVPN"

# Update every 1 hour
PROFILE_UPDATE_INTERVAL = "1"

# Effectively unlimited traffic
UNLIMITED_TOTAL = "10737418240000000"

# Effectively unlimited expiration
UNLIMITED_EXPIRE = "2546249531"


# ============================================================
# SUPPORTED PROTOCOLS
# ============================================================

SUPPORTED_PROTOCOLS = (
    "vless://",
    "vmess://",
    "trojan://",
    "ss://",
    "shadowsocks://",
)

# URI schemes that belong to each protocol category.
# Shadowsocks is published under two different schemes.
PROTOCOL_SCHEMES = {
    "vless": ("vless",),
    "vmess": ("vmess",),
    "trojan": ("trojan",),
    "shadowsocks": (
        "ss",
        "shadowsocks",
    ),
}


# ============================================================
# HTTP SESSION
# ============================================================

def create_session():
    """
    Create a requests session with retry support.
    """

    session = requests.Session()

    retry_strategy = Retry(
        total=3,
        connect=3,
        read=3,
        backoff_factor=2,
        status_forcelist=[
            429,
            500,
            502,
            503,
            504,
        ],
        allowed_methods=[
            "GET",
        ],
        raise_on_status=False,
    )

    adapter = HTTPAdapter(
        max_retries=retry_strategy
    )

    session.mount(
        "http://",
        adapter
    )

    session.mount(
        "https://",
        adapter
    )

    # Some providers block unknown agents or serve
    # different content to non-browser clients.
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/127.0.0.0 Safari/537.36"
        ),
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "Cache-Control": "no-cache",
    })

    return session


SESSION = create_session()


# ============================================================
# CLEAN CONFIG
# ============================================================

def clean_config(config):
    """
    Clean and normalize a VPN configuration.

    Important:
    Some subscription sources return HTML-escaped URLs such as:

        &amp;

    instead of:

        &

    Hiddify/Xray needs the real URL format, so HTML entities
    are decoded here before the config is used.
    """

    if not config:
        return None

    config = config.strip()

    if not config:
        return None

    # Decode HTML entities:
    #
    # &amp;  -> &
    # &quot; -> "
    # &lt;   -> <
    # &gt;   -> >
    #
    config = html.unescape(config)

    # Remove accidental surrounding quotes
    config = config.strip(
        "\"'"
    )

    # Remove whitespace accidentally inserted into the URI
    config = config.replace(
        "\r",
        ""
    )

    config = config.replace(
        "\n",
        ""
    )

    config = config.strip()

    if not config:
        return None

    # Must be a supported VPN URI
    lower = config.lower()

    if not lower.startswith(
        SUPPORTED_PROTOCOLS
    ):
        return None

    return config


# ============================================================
# HIDDIFY METADATA
# ============================================================

def build_hiddify_metadata():
    """
    Metadata understood by Hiddify.
    """

    return [
        f"#profile-title: {PROFILE_TITLE}",
        f"#profile-update-interval: {PROFILE_UPDATE_INTERVAL}",
        (
            "#subscription-userinfo: "
            "upload=0; "
            "download=0; "
            f"total={UNLIMITED_TOTAL}; "
            f"expire={UNLIMITED_EXPIRE}"
        ),
        "",
    ]


def add_hiddify_metadata(configs):
    """
    Add Hiddify metadata to subscription.
    """

    return (
        build_hiddify_metadata()
        + configs
    )


# ============================================================
# BASE64 HELPER
# ============================================================

def try_decode_base64(content):
    """
    Try to decode a subscription body that may be Base64.

    Tolerates the real-world variations that a strict
    validate=True decode rejects:

    - line breaks / spaces inside the payload
    - missing '=' padding
    - URL-safe alphabet ('-' and '_')

    Returns the decoded text, or None when the content is
    not Base64 (i.e. it is already plain text).
    """

    if not content:
        return None

    # A plain-text subscription starts with a protocol or a
    # '#' metadata header, so never treat it as Base64.
    stripped = content.lstrip()

    if stripped.startswith("#"):
        return None

    if stripped.lower().startswith(
        SUPPORTED_PROTOCOLS
    ):
        return None

    # Remove all whitespace before decoding.
    compact = re.sub(
        r"\s+",
        "",
        content
    )

    if len(compact) < 16:
        return None

    if not re.fullmatch(
        r"[A-Za-z0-9+/\-_=]+",
        compact
    ):
        return None

    # Restore padding to a multiple of 4.
    padding = (-len(compact)) % 4

    candidate = compact + ("=" * padding)

    for decoder in (
        base64.b64decode,
        base64.urlsafe_b64decode,
    ):

        try:

            decoded = decoder(
                candidate
            ).decode(
                "utf-8",
                errors="ignore"
            )

        except Exception:

            continue

        # Only accept the result if it actually looks
        # like a config list.
        if decoded and (
            decoded.lstrip().lower().startswith(
                SUPPORTED_PROTOCOLS
            )
            or "://" in decoded
        ):

            return decoded

    return None


# ============================================================
# FETCH SUBSCRIPTION
# ============================================================

def fetch_configs_from_url(url):
    """
    Download and decode a subscription URL.

    Supports:
    - Plain text
    - Base64
    - HTML escaped configs
    """

    url = url.strip()

    if not url:
        return []

    try:

        print()
        print(
            f"در حال دریافت: {url}"
        )

        response = SESSION.get(
            url,
            timeout=(
                10,
                30
            ),
            allow_redirects=True,
        )

        response.raise_for_status()

        content = response.text.strip()

        if not content:

            print(
                "پاسخ خالی بود."
            )

            return []

        # ----------------------------------------------------
        # Detect error pages served with HTTP 200.
        # ----------------------------------------------------

        head = content[:600].lower()

        if head.startswith("<!doctype html") or head.startswith("<html"):

            print(
                "پاسخ یک صفحه HTML بود، نه Subscription."
            )

            return []

        if "error 1027" in head or "rate limited" in head:

            print(
                "منبع توسط Cloudflare محدود شده است."
            )

            return []

        # ----------------------------------------------------
        # First decode HTML entities.
        # ----------------------------------------------------

        content = html.unescape(
            content
        )

        # ----------------------------------------------------
        # Try Base64 decoding.
        # ----------------------------------------------------

        decoded_content = try_decode_base64(
            content
        )

        if decoded_content:

            content = html.unescape(
                decoded_content
            )

        # ----------------------------------------------------
        # Parse lines
        # ----------------------------------------------------

        configs = []

        for line in content.splitlines():

            line = line.strip()

            if not line:
                continue

            # Ignore comments / metadata from source.
            if line.startswith("#"):
                continue

            cleaned = clean_config(
                line
            )

            if cleaned:

                configs.append(
                    cleaned
                )

        print(
            f"کانفیگ دریافت شد: "
            f"{len(configs)}"
        )

        return configs

    except requests.RequestException as e:

        print()
        print(
            "خطا در دریافت Subscription:"
        )

        print(
            url
        )

        print(
            str(e)
        )

        return []

    except Exception as e:

        print()
        print(
            f"خطای غیرمنتظره: {e}"
        )

        return []


# ============================================================
# LOAD LINKS
# ============================================================

def load_links():
    """
    Load subscription URLs from links.txt.
    """

    if not os.path.exists(
        LINKS_FILE
    ):

        print(
            f"فایل {LINKS_FILE} وجود ندارد."
        )

        return []

    try:

        with open(
            LINKS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            links = []

            for line in file:

                line = line.strip()

                if not line:
                    continue

                if line.startswith("#"):
                    continue

                links.append(
                    line
                )

        print(
            f"تعداد Subscription ها: "
            f"{len(links)}"
        )

        return links

    except Exception as e:

        print(
            f"خطا در خواندن {LINKS_FILE}: "
            f"{e}"
        )

        return []


# ============================================================
# REMOVE DUPLICATES
# ============================================================

def remove_duplicates(configs):
    """
    Remove duplicate VPN configs.
    """

    unique_configs = []

    seen = set()

    for config in configs:

        cleaned = clean_config(
            config
        )

        if not cleaned:
            continue

        # Remove existing fragment/name
        base = cleaned.split(
            "#",
            1
        )[0].strip()

        if not base:
            continue

        if base in seen:
            continue

        seen.add(
            base
        )

        unique_configs.append(
            cleaned
        )

    print(
        f"بعد از حذف تکراری‌ها: "
        f"{len(unique_configs)}"
    )

    return unique_configs


# ============================================================
# VALIDATE CONFIG
# ============================================================

def test_and_filter_config(config):
    """
    Basic URI validation.

    This does not establish a VPN connection.
    """

    cleaned = clean_config(
        config
    )

    if not cleaned:
        return False

    lower = cleaned.lower()

    if lower.startswith(
        "vless://"
    ):
        return validate_uri(
            cleaned,
            "vless"
        )

    if lower.startswith(
        "vmess://"
    ):
        return validate_uri(
            cleaned,
            "vmess"
        )

    if lower.startswith(
        "trojan://"
    ):
        return validate_uri(
            cleaned,
            "trojan"
        )

    if (
        lower.startswith("ss://")
        or
        lower.startswith(
            "shadowsocks://"
        )
    ):
        return validate_uri(
            cleaned,
            "shadowsocks"
        )

    return False


def validate_uri(
    config,
    protocol
):
    """
    Validate basic URI structure.

    We intentionally keep validation tolerant because
    different Xray/Sing-box configurations can use different
    optional parameters.
    """

    try:

        parsed = urllib.parse.urlparse(
            config
        )

        scheme = parsed.scheme.lower()

        # ----------------------------------------------------
        # Accept every scheme that maps to this protocol.
        # 'ss' and 'shadowsocks' are the same protocol, so a
        # plain string comparison would reject all ss:// URIs.
        # ----------------------------------------------------

        allowed_schemes = PROTOCOL_SCHEMES.get(
            protocol,
            (protocol,)
        )

        if scheme not in allowed_schemes:
            return False

        if protocol in (
            "vless",
            "trojan",
        ):

            if not parsed.hostname:
                return False

            if not parsed.port:
                return False

            return True

        if protocol == "vmess":

            return validate_vmess(
                config
            )

        if protocol == "shadowsocks":

            return validate_shadowsocks(
                config,
                parsed
            )

        return True

    except Exception:

        return False


def validate_vmess(config):
    """
    Validate a vmess:// config.

    VMess normally carries a Base64 encoded JSON body rather
    than a regular URI, so urlparse cannot find a host/port.
    Both the JSON form and the newer URI form are accepted.
    """

    body = config[len("vmess://"):].strip()

    if not body:
        return False

    # ----------------------------------------------------
    # Form 1: vmess://uuid@host:port?params
    # ----------------------------------------------------

    if "@" in body.split("?", 1)[0]:

        parsed = urllib.parse.urlparse(
            config
        )

        return bool(
            parsed.hostname
            and parsed.port
        )

    # ----------------------------------------------------
    # Form 2: vmess://<base64 json>
    # ----------------------------------------------------

    payload = body.split("#", 1)[0]

    compact = re.sub(
        r"\s+",
        "",
        payload
    )

    compact += "=" * ((-len(compact)) % 4)

    for decoder in (
        base64.b64decode,
        base64.urlsafe_b64decode,
    ):

        try:

            decoded = decoder(
                compact
            ).decode(
                "utf-8",
                errors="ignore"
            )

            data = json.loads(
                decoded
            )

        except Exception:

            continue

        if not isinstance(data, dict):
            continue

        address = str(
            data.get("add", "")
        ).strip()

        port = str(
            data.get("port", "")
        ).strip()

        uid = str(
            data.get("id", "")
        ).strip()

        if address and port and uid:
            return True

    return False


def validate_shadowsocks(
    config,
    parsed
):
    """
    Validate an ss:// or shadowsocks:// config.

    Supported shapes:
      ss://<base64 method:pass>@host:port
      ss://<method:pass>@host:port
      ss://<base64 of the whole method:pass@host:port>
    """

    if parsed.hostname and parsed.port:
        return True

    # Fully Base64 encoded body.

    body = config.split("://", 1)[1]

    payload = body.split("#", 1)[0].split("?", 1)[0]

    compact = re.sub(
        r"\s+",
        "",
        payload
    )

    compact += "=" * ((-len(compact)) % 4)

    for decoder in (
        base64.b64decode,
        base64.urlsafe_b64decode,
    ):

        try:

            decoded = decoder(
                compact
            ).decode(
                "utf-8",
                errors="ignore"
            )

        except Exception:

            continue

        if "@" not in decoded:
            continue

        host_part = decoded.rsplit("@", 1)[1]

        if ":" not in host_part:
            continue

        port = host_part.rsplit(":", 1)[1]

        if port.isdigit():
            return True

    return False


# ============================================================
# CATEGORIZE
# ============================================================

def rename_config(
    config,
    protocol,
    new_name
):
    """
    Apply the POPVPN display name to a config.

    For URI style configs the name lives in the fragment.
    For Base64 VMess configs it lives in the JSON 'ps' field,
    so the payload is re-encoded instead of getting a
    fragment appended, which some clients refuse to parse.
    """

    body = config.split("://", 1)[1]

    is_b64_vmess = (
        protocol == "vmess"
        and "@" not in body.split("?", 1)[0]
    )

    if is_b64_vmess:

        payload = body.split("#", 1)[0]

        compact = re.sub(
            r"\s+",
            "",
            payload
        )

        compact += "=" * ((-len(compact)) % 4)

        for decoder in (
            base64.b64decode,
            base64.urlsafe_b64decode,
        ):

            try:

                data = json.loads(
                    decoder(
                        compact
                    ).decode(
                        "utf-8",
                        errors="ignore"
                    )
                )

            except Exception:

                continue

            if not isinstance(data, dict):
                continue

            data["ps"] = new_name

            reencoded = base64.b64encode(
                json.dumps(
                    data,
                    ensure_ascii=False,
                    separators=(",", ":"),
                ).encode("utf-8")
            ).decode("utf-8")

            return f"vmess://{reencoded}"

        return None

    base_config = config.split(
        "#",
        1
    )[0]

    encoded_name = urllib.parse.quote(
        new_name,
        safe=""
    )

    return (
        f"{base_config}"
        f"#{encoded_name}"
    )


def process_and_categorize(
    configs
):
    """
    Categorize configs by protocol
    and generate readable names.
    """

    categories = {
        "vless": [],
        "vmess": [],
        "trojan": [],
        "shadowsocks": [],
    }

    counters = {
        "vless": 1,
        "vmess": 1,
        "trojan": 1,
        "shadowsocks": 1,
    }

    rejected = 0

    for config in configs:

        cleaned = clean_config(
            config
        )

        if not cleaned:

            rejected += 1

            continue

        if not test_and_filter_config(
            cleaned
        ):

            rejected += 1

            continue

        lower = cleaned.lower()

        protocol = None

        if lower.startswith(
            "vless://"
        ):

            protocol = "vless"

        elif lower.startswith(
            "vmess://"
        ):

            protocol = "vmess"

        elif lower.startswith(
            "trojan://"
        ):

            protocol = "trojan"

        elif (
            lower.startswith("ss://")
            or
            lower.startswith(
                "shadowsocks://"
            )
        ):

            protocol = "shadowsocks"

        if not protocol:

            rejected += 1

            continue

        # ----------------------------------------------------
        # Create POPVPN name
        # ----------------------------------------------------

        new_name = (
            f"POPVPN | "
            f"{protocol.upper()} | "
            f"{counters[protocol]}"
        )

        final_config = rename_config(
            cleaned,
            protocol,
            new_name
        )

        if not final_config:

            rejected += 1

            continue

        categories[
            protocol
        ].append(
            final_config
        )

        counters[
            protocol
        ] += 1

    print(
        f"کانفیگ رد شده: "
        f"{rejected}"
    )

    return categories


# ============================================================
# WRITE FILE
# ============================================================

def write_file(
    path,
    content
):
    """
    Write UTF-8 file.
    """

    directory = os.path.dirname(
        path
    )

    if directory:

        os.makedirs(
            directory,
            exist_ok=True
        )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            content
        )


# ============================================================
# CLEAR OLD OUTPUT
# ============================================================

def clear_old_output_files():
    """
    Remove old protocol files.
    """

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    files = [

        "vless_configs.txt",
        "vless_base64.txt",

        "vmess_configs.txt",
        "vmess_base64.txt",

        "trojan_configs.txt",
        "trojan_base64.txt",

        "shadowsocks_configs.txt",
        "shadowsocks_base64.txt",

    ]

    for filename in files:

        path = os.path.join(
            OUTPUT_DIR,
            filename
        )

        if os.path.exists(
            path
        ):

            try:

                os.remove(
                    path
                )

            except Exception as e:

                print(
                    f"خطا در حذف {path}: "
                    f"{e}"
                )


# ============================================================
# WRITE PROTOCOL OUTPUTS
# ============================================================

def write_protocol_outputs(
    categorized_configs
):
    """
    Generate protocol-specific subscriptions.
    """

    all_configs = []

    stats = []

    total_active = 0

    for protocol, configs in (
        categorized_configs.items()
    ):

        count = len(
            configs
        )

        stats.append(
            f"{protocol.upper()}: {count}"
        )

        if count == 0:
            continue

        # ----------------------------------------------------
        # RAW FILE
        # ----------------------------------------------------

        raw_lines = add_hiddify_metadata(
            configs
        )

        raw_content = "\n".join(
            raw_lines
        )

        raw_file = os.path.join(
            OUTPUT_DIR,
            f"{protocol}_configs.txt"
        )

        write_file(
            raw_file,
            raw_content
        )

        # ----------------------------------------------------
        # BASE64 FILE
        # ----------------------------------------------------

        encoded_content = (
            base64.b64encode(
                raw_content.encode(
                    "utf-8"
                )
            )
            .decode(
                "utf-8"
            )
        )

        base64_file = os.path.join(
            OUTPUT_DIR,
            f"{protocol}_base64.txt"
        )

        write_file(
            base64_file,
            encoded_content
        )

        all_configs.extend(
            configs
        )

        total_active += count

    return (
        all_configs,
        total_active,
        stats
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 60)
    print("POPVPN AUTO UPDATE")
    print("HIDDIFY COMPATIBLE")
    print("=" * 60)

    links = load_links()

    if not links:

        print(
            "هیچ Subscription ای پیدا نشد."
        )

        return 1

    all_raw_configs = []

    successful_links = 0
    failed_links = 0

    # --------------------------------------------------------
    # FETCH ALL LINKS
    # --------------------------------------------------------

    for link in links:

        configs = fetch_configs_from_url(
            link
        )

        if configs:

            successful_links += 1

            all_raw_configs.extend(
                configs
            )

        else:

            failed_links += 1

    print()
    print(
        f"لینک موفق: "
        f"{successful_links}"
    )

    print(
        f"لینک ناموفق: "
        f"{failed_links}"
    )

    print(
        f"کل کانفیگ خام: "
        f"{len(all_raw_configs)}"
    )

    # --------------------------------------------------------
    # SAFETY
    # --------------------------------------------------------

    if not all_raw_configs:

        print()
        print(
            "هیچ کانفیگی دریافت نشد."
        )

        print(
            "خروجی قبلی حفظ خواهد شد."
        )

        write_file(
            STATS_FILE,
            (
                "UPDATE FAILED | "
                f"Links: {len(links)} | "
                f"Successful: {successful_links} | "
                f"Failed: {failed_links} | "
                "No configs received"
            )
        )

        return 1

    # --------------------------------------------------------
    # DEDUPLICATE
    # --------------------------------------------------------

    unique_configs = remove_duplicates(
        all_raw_configs
    )

    if not unique_configs:

        print(
            "هیچ کانفیگ معتبر و یکتایی پیدا نشد."
        )

        write_file(
            STATS_FILE,
            (
                "UPDATE FAILED | "
                "No valid configs"
            )
        )

        return 1

    # --------------------------------------------------------
    # CATEGORIZE
    # --------------------------------------------------------

    categorized = process_and_categorize(
        unique_configs
    )

    total_valid = sum(
        len(configs)
        for configs in categorized.values()
    )

    if total_valid == 0:

        print(
            "هیچ کانفیگ قابل استفاده‌ای پیدا نشد."
        )

        write_file(
            STATS_FILE,
            (
                "UPDATE FAILED | "
                "No valid protocol configs"
            )
        )

        return 1

    # --------------------------------------------------------
    # CLEAR OLD OUTPUT
    # --------------------------------------------------------

    clear_old_output_files()

    # --------------------------------------------------------
    # WRITE PROTOCOL FILES
    # --------------------------------------------------------

    (
        all_configs,
        total_active,
        stats
    ) = write_protocol_outputs(
        categorized
    )

    # --------------------------------------------------------
    # MAIN SUBSCRIPTION
    # --------------------------------------------------------

    main_lines = add_hiddify_metadata(
        all_configs
    )

    main_content = "\n".join(
        main_lines
    )

    write_file(
        MAIN_CONFIG_FILE,
        main_content
    )

    # --------------------------------------------------------
    # MAIN BASE64
    # --------------------------------------------------------

    main_base64 = (
        base64.b64encode(
            main_content.encode(
                "utf-8"
            )
        )
        .decode(
            "utf-8"
        )
    )

    write_file(
        MAIN_BASE64_FILE,
        main_base64
    )

    # --------------------------------------------------------
    # STATS
    # --------------------------------------------------------

    stats_text = (
        f"Total Active: {total_active} | "
        + " | ".join(stats)
        + f" | Links: {len(links)}"
        + f" | Successful: {successful_links}"
        + f" | Failed: {failed_links}"
        + " | Brand: POPVPN"
        + " | Traffic: Unlimited"
        + " | Expiry: Unlimited"
        + " | Hiddify: Compatible"
    )

    write_file(
        STATS_FILE,
        stats_text
    )

    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("UPDATE COMPLETED")
    print("=" * 60)

    print(
        f"Brand: {PROFILE_TITLE}"
    )

    print(
        "Traffic: Unlimited"
    )

    print(
        "Expiry: Unlimited"
    )

    print(
        "Update interval: 1 hour"
    )

    print(
        f"Total active: "
        f"{total_active}"
    )

    for item in stats:

        print(
            item
        )

    print(
        f"Successful links: "
        f"{successful_links}"
    )

    print(
        f"Failed links: "
        f"{failed_links}"
    )

    print("=" * 60)

    return 0


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    exit_code = main()

    raise SystemExit(
        exit_code
    )
