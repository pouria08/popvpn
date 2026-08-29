import base64
import os
import urllib.parse
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


LINKS_FILE = "links.txt"
OUTPUT_DIR = "outputs"

MAIN_CONFIG_FILE = "working_configs.txt"
MAIN_BASE64_FILE = "base64.txt"
STATS_FILE = "stats.txt"


def create_session():
    """
    ساخت Session با Retry برای جلوگیری از خراب شدن آپدیت
    در صورت خطای موقت اینترنت یا سرور.
    """

    session = requests.Session()

    retry_strategy = Retry(
        total=3,
        connect=3,
        read=3,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        raise_on_status=False,
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)

    session.mount("http://", adapter)
    session.mount("https://", adapter)

    session.headers.update({
        "User-Agent": "POPVPN-AutoUpdater/1.0"
    })

    return session


SESSION = create_session()


def fetch_configs_from_url(url):
    """
    دریافت Subscription از یک URL
    """

    url = url.strip()

    if not url:
        return []

    try:
        print(f"در حال دریافت: {url}")

        response = SESSION.get(
            url,
            timeout=(10, 30),
            allow_redirects=True
        )

        response.raise_for_status()

        content = response.text.strip()

        if not content:
            print(f"پاسخ خالی بود: {url}")
            return []

        # بعضی Subscription ها به صورت Base64 هستند.
        try:
            decoded = base64.b64decode(
                content,
                validate=True
            ).decode("utf-8")

            if decoded.strip():
                content = decoded

        except Exception:
            # اگر Base64 نبود، همان متن اصلی استفاده می‌شود.
            pass

        configs = []

        for line in content.splitlines():

            line = line.strip()

            if not line:
                continue

            if line.startswith("#"):
                continue

            configs.append(line)

        print(f"دریافت شد: {len(configs)} کانفیگ")

        return configs

    except requests.RequestException as e:
        print(f"خطا در دریافت لینک:")
        print(f"{url}")
        print(f"{e}")
        return []

    except Exception as e:
        print(f"خطای غیرمنتظره در {url}: {e}")
        return []


def load_links():
    """
    خواندن Subscription URL ها از links.txt
    """

    if not os.path.exists(LINKS_FILE):
        print(f"فایل {LINKS_FILE} وجود ندارد.")
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

                links.append(line)

        print(f"تعداد لینک‌های Subscription: {len(links)}")

        return links

    except Exception as e:

        print(
            f"خطا در خواندن {LINKS_FILE}: {e}"
        )

        return []


def remove_duplicates(configs):
    """
    حذف کانفیگ‌های تکراری
    """

    unique_configs = []
    seen = set()

    for config in configs:

        # حذف اسم بعد از #
        base = config.split("#", 1)[0].strip()

        if not base:
            continue

        if base in seen:
            continue

        seen.add(base)

        unique_configs.append(config)

    print(
        f"کانفیگ یکتا: {len(unique_configs)}"
    )

    return unique_configs


def test_and_filter_config(config):
    """
    فعلاً فقط اعتبار اولیه URI را بررسی می‌کند.

    توجه:
    تست واقعی Ping/سرعت نیازمند برقراری اتصال
    توسط کلاینت مربوط به هر پروتکل است.
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

    return config.startswith(supported_protocols)


def process_and_categorize(configs):
    """
    دسته‌بندی کانفیگ‌ها بر اساس Protocol
    """

    categories = {
        "vless": [],
        "vmess": [],
        "trojan": [],
        "shadowsocks": [],
    }

    counters = {
        key: 1
        for key in categories
    }

    for config in configs:

        if not test_and_filter_config(config):
            continue

        lower_cfg = config.lower()

        protocol = None

        if lower_cfg.startswith("vless://"):
            protocol = "vless"

        elif lower_cfg.startswith("vmess://"):
            protocol = "vmess"

        elif lower_cfg.startswith("trojan://"):
            protocol = "trojan"

        elif (
            lower_cfg.startswith("ss://")
            or lower_cfg.startswith("shadowsocks://")
        ):
            protocol = "shadowsocks"

        if protocol is None:
            continue

        # حذف اسم قبلی کانفیگ
        base_config = config.split("#", 1)[0]

        new_name = (
            f"POP PING | {counters[protocol]}"
        )

        encoded_name = urllib.parse.quote(
            new_name,
            safe=""
        )

        final_config = (
            f"{base_config}#{encoded_name}"
        )

        categories[protocol].append(
            final_config
        )

        counters[protocol] += 1

    return categories


def write_file(path, content):
    """
    نوشتن امن فایل خروجی
    """

    directory = os.path.dirname(path)

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

        f.write(content)


def clear_old_output_files():
    """
    حذف فایل‌های خروجی قبلی تا کانفیگ‌های قدیمی
    در صورت صفر شدن نتایج باقی نمانند.
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

        if os.path.exists(path):

            try:
                os.remove(path)

            except Exception as e:

                print(
                    f"خطا در حذف {path}: {e}"
                )


def write_protocol_outputs(categorized_configs):
    """
    ساخت خروجی جداگانه برای هر Protocol
    """

    all_configs = []

    stats = []

    total_active = 0

    for protocol, configs in categorized_configs.items():

        # اگر برای این پروتکل چیزی وجود ندارد
        if not configs:

            stats.append(
                f"{protocol.upper()}: 0"
            )

            continue

        # فایل معمولی
        config_file = os.path.join(
            OUTPUT_DIR,
            f"{protocol}_configs.txt"
        )

        config_content = "\n".join(
            configs
        )

        write_file(
            config_file,
            config_content
        )

        # Base64
        base64_content = base64.b64encode(
            config_content.encode("utf-8")
        ).decode("utf-8")

        base64_file = os.path.join(
            OUTPUT_DIR,
            f"{protocol}_base64.txt"
        )

        write_file(
            base64_file,
            base64_content
        )

        all_configs.extend(configs)

        count = len(configs)

        total_active += count

        stats.append(
            f"{protocol.upper()}: {count}"
        )

    return all_configs, total_active, stats


def main():

    print("=" * 50)
    print("POPVPN AUTO UPDATE")
    print("=" * 50)

    links = load_links()

    if not links:

        print(
            "هیچ Subscription ای در links.txt پیدا نشد."
        )

        return 1

    all_raw_configs = []

    successful_links = 0

    failed_links = 0

    # دریافت تمام Subscription ها
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
        f"کل کانفیگ دریافتی: {len(all_raw_configs)}"
    )

    # اگر هیچ Subscription دریافت نشد،
    # خروجی قبلی را خراب نکنیم.
    #
    # این قسمت مهم است:
    # خطای موقت اینترنت نباید باعث حذف همه کانفیگ‌های سالم شود.
    if not all_raw_configs:

        print()
        print(
            "هیچ کانفیگی دریافت نشد."
        )

        print(
            "برای جلوگیری از از بین رفتن اطلاعات قبلی، "
            "فایل‌های خروجی تغییر داده نمی‌شوند."
        )

        write_file(
            STATS_FILE,
            "UPDATE FAILED | "
            f"Links: {len(links)} | "
            f"Successful: {successful_links} | "
            f"Failed: {failed_links} | "
            "No configs received"
        )

        return 1

    # حذف Duplicate
    unique_configs = remove_duplicates(
        all_raw_configs
    )

    # دسته‌بندی
    categorized_configs = process_and_categorize(
        unique_configs
    )

    # حذف خروجی‌های قدیمی
    clear_old_output_files()

    # ساخت خروجی‌ها
    (
        all_configs_combined,
        total_active,
        stats
    ) = write_protocol_outputs(
        categorized_configs
    )

    # فایل اصلی
    working_content = "\n".join(
        all_configs_combined
    )

    write_file(
        MAIN_CONFIG_FILE,
        working_content
    )

    # فایل Base64 اصلی
    main_base64 = base64.b64encode(
        working_content.encode("utf-8")
    ).decode("utf-8")

    write_file(
        MAIN_BASE64_FILE,
        main_base64
    )

    # آمار
    stats_text = (
        f"Total Active: {total_active} | "
        + " | ".join(stats)
        + f" | Links: {len(links)}"
        + f" | Successful: {successful_links}"
        + f" | Failed: {failed_links}"
    )

    write_file(
        STATS_FILE,
        stats_text
    )

    print()
    print("=" * 50)
    print("UPDATE COMPLETED")
    print("=" * 50)

    print(
        f"Total Active: {total_active}"
    )

    for item in stats:
        print(item)

    print(
        f"Successful Links: {successful_links}"
    )

    print(
        f"Failed Links: {failed_links}"
    )

    print("=" * 50)

    return 0


if __name__ == "__main__":

    exit_code = main()

    raise SystemExit(
        exit_code
    )
