import base64
import html
import os
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

    session.headers.update({
        "User-Agent": "POPVPN-AutoUpdater/2.0"
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
        # First decode HTML entities.
        # ----------------------------------------------------

        content = html.unescape(
            content
        )

        # ----------------------------------------------------
        # Try Base64 decoding.
        # ----------------------------------------------------

        decoded_content = None

        try:

            decoded_content = (
                base64.b64decode(
                    content,
                    validate=True
                )
                .decode(
                    "utf-8"
                )
            )

        except Exception:

            decoded_content = None

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

        if parsed.scheme.lower() != protocol:
            return False

        if protocol in (
            "vless",
            "vmess",
            "trojan",
        ):

            if not parsed.hostname:
                return False

            if not parsed.port:
                return False

        elif protocol == "shadowsocks":

            if not parsed.netloc:
                return False

        return True

    except Exception:

        return False


# ============================================================
# CATEGORIZE
# ============================================================

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
        # Remove old name
        # ----------------------------------------------------

        base_config = cleaned.split(
            "#",
            1
        )[0]

        # ----------------------------------------------------
        # Create POPVPN name
        # ----------------------------------------------------

        new_name = (
            f"POPVPN | "
            f"{protocol.upper()} | "
            f"{counters[protocol]}"
        )

        encoded_name = urllib.parse.quote(
            new_name,
            safe=""
        )

        final_config = (
            f"{base_config}"
            f"#{encoded_name}"
        )

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
