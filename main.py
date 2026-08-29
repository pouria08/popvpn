import base64
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
# HIDDIFY PROFILE SETTINGS
# ============================================================

PROFILE_TITLE = "POPVPN"

# Hiddify will automatically update this subscription every 1 hour.
PROFILE_UPDATE_INTERVAL = "1"

# Very large value for unlimited traffic compatibility.
# This is intentionally used instead of total=0 because some
# Hiddify versions treat total=0 incorrectly.
UNLIMITED_TOTAL = "10737418240000000"

# Far future timestamp for unlimited expiration compatibility.
# Hiddify uses this style for effectively unlimited subscriptions.
UNLIMITED_EXPIRE = "2546249531"

# Optional support / website URLs.
# Leave empty if you don't want these buttons in Hiddify.
SUPPORT_URL = ""
WEB_PAGE_URL = ""


# ============================================================
# HTTP SESSION
# ============================================================

def create_session():
    """
    Create HTTP session with retry support.
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
            504
        ],
        allowed_methods=[
            "GET"
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
        "User-Agent": "POPVPN-AutoUpdater/1.0"
    })

    return session


SESSION = create_session()


# ============================================================
# HIDDIFY METADATA
# ============================================================

def build_hiddify_headers():
    """
    Build Hiddify-compatible metadata.

    These are placed inside the first lines of the generated
    subscription file because GitHub Pages/raw GitHub cannot
    provide custom HTTP response headers for us.
    """

    headers = [
        f"#profile-title: {PROFILE_TITLE}",
        f"#profile-update-interval: {PROFILE_UPDATE_INTERVAL}",
        (
            "#subscription-userinfo: "
            "upload=0; "
            "download=0; "
            f"total={UNLIMITED_TOTAL}; "
            f"expire={UNLIMITED_EXPIRE}"
        )
    ]

    if SUPPORT_URL:
        headers.append(
            f"#support-url: {SUPPORT_URL}"
        )

    if WEB_PAGE_URL:
        headers.append(
            f"#profile-web-page-url: {WEB_PAGE_URL}"
        )

    headers.append("")

    return headers


def add_hiddify_metadata(configs):
    """
    Add Hiddify metadata to a list of configs.
    """

    metadata = build_hiddify_headers()

    return (
        metadata
        + configs
    )


# ============================================================
# FETCH SUBSCRIPTION
# ============================================================

def fetch_configs_from_url(url):
    """
    Download subscription from URL.

    Supports:
    - Plain text subscriptions
    - Base64 subscriptions
    - Hiddify metadata lines
    """

    url = url.strip()

    if not url:
        return []

    try:

        print(
            f"در حال دریافت: {url}"
        )

        response = SESSION.get(
            url,
            timeout=(10, 30),
            allow_redirects=True
        )

        response.raise_for_status()

        content = response.text.strip()

        if not content:

            print(
                f"پاسخ خالی بود: {url}"
            )

            return []

        # ----------------------------------------------------
        # Remove Hiddify metadata from source if present.
        # We will add our own metadata to the final output.
        # ----------------------------------------------------

        cleaned_lines = []

        for line in content.splitlines():

            line = line.strip()

            if not line:
                continue

            if line.startswith(
                "#profile-title:"
            ):
                continue

            if line.startswith(
                "#profile-update-interval:"
            ):
                continue

            if line.startswith(
                "#subscription-userinfo:"
            ):
                continue

            if line.startswith(
                "#support-url:"
            ):
                continue

            if line.startswith(
                "#profile-web-page-url:"
            ):
                continue

            if line.startswith("#"):
                continue

            cleaned_lines.append(
                line
            )

        cleaned_content = "\n".join(
            cleaned_lines
        ).strip()

        # ----------------------------------------------------
        # If content is Base64 encoded
        # ----------------------------------------------------

        if cleaned_content:

            try:

                decoded = base64.b64decode(
                    cleaned_content,
                    validate=True
                ).decode(
                    "utf-8"
                )

                decoded_lines = []

                for line in decoded.splitlines():

                    line = line.strip()

                    if not line:
                        continue

                    if line.startswith("#"):
                        continue

                    decoded_lines.append(
                        line
                    )

                if decoded_lines:

                    cleaned_lines = decoded_lines

            except Exception:
                # Not Base64, keep original content.
                pass

        configs = []

        for line in cleaned_lines:

            line = line.strip()

            if not line:
                continue

            if line.startswith("#"):
                continue

            configs.append(
                line
            )

        print(
            f"دریافت شد: {len(configs)} کانفیگ"
        )

        return configs

    except requests.RequestException as e:

        print(
            "خطا در دریافت لینک:"
        )

        print(url)

        print(e)

        return []

    except Exception as e:

        print(
            f"خطای غیرمنتظره در {url}: {e}"
        )

        return []


# ============================================================
# LOAD LINKS
# ============================================================

def load_links():
    """
    Read subscription URLs from links.txt.
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
        ) as f:

            links = []

            for line in f:

                line = line.strip()

                if not line:
                    continue

                if line.startswith("#"):
                    continue

                links.append(
                    line
                )

        print(
            f"تعداد لینک‌های Subscription: {len(links)}"
        )

        return links

    except Exception as e:

        print(
            f"خطا در خواندن {LINKS_FILE}: {e}"
        )

        return []


# ============================================================
# REMOVE DUPLICATES
# ============================================================

def remove_duplicates(configs):
    """
    Remove duplicate configs.
    """

    unique_configs = []

    seen = set()

    for config in configs:

        base = config.split(
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
            config
        )

    print(
        f"کانفیگ یکتا: {len(unique_configs)}"
    )

    return unique_configs


# ============================================================
# CONFIG VALIDATION
# ============================================================

def test_and_filter_config(config):
    """
    Basic protocol validation.

    This does NOT establish a real VPN connection.
    """

    if not config:
        return False

    config = config.strip().lower()

    supported_protocols = (
        "vless://",
        "vmess://",
        "trojan://",
        "ss://",
        "shadowsocks://",
    )

    return config.startswith(
        supported_protocols
    )


# ============================================================
# CATEGORIZE CONFIGS
# ============================================================

def process_and_categorize(configs):
    """
    Categorize configs by protocol.
    """

    categories = {
        "vless": [],
        "vmess": [],
        "trojan": [],
        "shadowsocks": []
    }

    counters = {
        key: 1
        for key in categories
    }

    for config in configs:

        if not test_and_filter_config(
            config
        ):
            continue

        lower_cfg = config.lower()

        protocol = None

        if lower_cfg.startswith(
            "vless://"
        ):

            protocol = "vless"

        elif lower_cfg.startswith(
            "vmess://"
        ):

            protocol = "vmess"

        elif lower_cfg.startswith(
            "trojan://"
        ):

            protocol = "trojan"

        elif (
            lower_cfg.startswith("ss://")
            or
            lower_cfg.startswith(
                "shadowsocks://"
            )
        ):

            protocol = "shadowsocks"

        if protocol is None:
            continue

        # Remove previous name.
        base_config = config.split(
            "#",
            1
        )[0]

        new_name = (
            f"POP PING | "
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
    ) as f:

        f.write(
            content
        )


# ============================================================
# CLEAR OLD OUTPUTS
# ============================================================

def clear_old_output_files():
    """
    Remove old protocol output files.
    """

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    output_files = [

        "vless_configs.txt",
        "vless_base64.txt",

        "vmess_configs.txt",
        "vmess_base64.txt",

        "trojan_configs.txt",
        "trojan_base64.txt",

        "shadowsocks_configs.txt",
        "shadowsocks_base64.txt",

    ]

    for filename in output_files:

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
                    f"خطا در حذف {path}: {e}"
                )


# ============================================================
# WRITE PROTOCOL OUTPUTS
# ============================================================

def write_protocol_outputs(
    categorized_configs
):
    """
    Create protocol-specific files.

    Every file gets Hiddify metadata.
    """

    all_configs = []

    stats = []

    total_active = 0

    for protocol, configs in (
        categorized_configs.items()
    ):

        stats.append(
            f"{protocol.upper()}: {len(configs)}"
        )

        if not configs:
            continue

        # ----------------------------------------------------
        # RAW CONFIG FILE
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
        # BASE64 CONFIG FILE
        # ----------------------------------------------------

        # IMPORTANT:
        # Metadata must be added BEFORE Base64 encoding.
        # Hiddify decodes the file and then reads the headers.

        base64_content = base64.b64encode(
            raw_content.encode(
                "utf-8"
            )
        ).decode(
            "utf-8"
        )

        base64_file = os.path.join(
            OUTPUT_DIR,
            f"{protocol}_base64.txt"
        )

        write_file(
            base64_file,
            base64_content
        )

        all_configs.extend(
            configs
        )

        total_active += len(
            configs
        )

    return (
        all_configs,
        total_active,
        stats
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)

    print(
        "POPVPN AUTO UPDATE"
    )

    print(
        "HIDDIFY COMPATIBLE SUBSCRIPTION"
    )

    print("=" * 60)

    links = load_links()

    if not links:

        print(
            "هیچ Subscription ای در links.txt پیدا نشد."
        )

        return 1

    all_raw_configs = []

    successful_links = 0

    failed_links = 0

    # --------------------------------------------------------
    # FETCH ALL SUBSCRIPTIONS
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
        f"لینک موفق: {successful_links}"
    )

    print(
        f"لینک ناموفق: {failed_links}"
    )

    print(
        f"کل کانفیگ دریافتی: "
        f"{len(all_raw_configs)}"
    )

    # --------------------------------------------------------
    # DO NOT DESTROY OLD WORKING OUTPUT
    # --------------------------------------------------------

    if not all_raw_configs:

        print()

        print(
            "هیچ کانفیگی دریافت نشد."
        )

        print(
            "خروجی قبلی حفظ می‌شود."
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
    # REMOVE DUPLICATES
    # --------------------------------------------------------

    unique_configs = remove_duplicates(
        all_raw_configs
    )

    # --------------------------------------------------------
    # CATEGORIZE
    # --------------------------------------------------------

    categorized_configs = (
        process_and_categorize(
            unique_configs
        )
    )

    # --------------------------------------------------------
    # CLEAR OLD OUTPUT
    # --------------------------------------------------------

    clear_old_output_files()

    # --------------------------------------------------------
    # CREATE PROTOCOL OUTPUTS
    # --------------------------------------------------------

    (
        all_configs_combined,
        total_active,
        stats
    ) = write_protocol_outputs(
        categorized_configs
    )

    # --------------------------------------------------------
    # MAIN RAW SUBSCRIPTION
    # --------------------------------------------------------

    main_lines = add_hiddify_metadata(
        all_configs_combined
    )

    main_content = "\n".join(
        main_lines
    )

    write_file(
        MAIN_CONFIG_FILE,
        main_content
    )

    # --------------------------------------------------------
    # MAIN BASE64 SUBSCRIPTION
    # --------------------------------------------------------

    main_base64 = base64.b64encode(
        main_content.encode(
            "utf-8"
        )
    ).decode(
        "utf-8"
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
    )

    write_file(
        STATS_FILE,
        stats_text
    )

    # --------------------------------------------------------
    # FINAL LOG
    # --------------------------------------------------------

    print()

    print("=" * 60)

    print(
        "UPDATE COMPLETED"
    )

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
        f"Update Interval: "
        f"{PROFILE_UPDATE_INTERVAL} hour"
    )

    print(
        f"Total Active: "
        f"{total_active}"
    )

    for item in stats:

        print(
            item
        )

    print(
        f"Successful Links: "
        f"{successful_links}"
    )

    print(
        f"Failed Links: "
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
