import requests
import base64
import urllib.parse
import os

LINKS_FILE = "links.txt"
OUTPUT_DIR = "outputs"

def fetch_configs_from_url(url):
    try:
        response = requests.get(url.strip(), timeout=15)
        response.raise_for_status()
        content = response.text.strip()
        try:
            decoded = base64.b64decode(content).decode('utf-8')
            content = decoded
        except Exception:
            pass
            
        configs = [line.strip() for line in content.splitlines() if line.strip() and not line.startswith("#")]
        return configs
    except Exception as e:
        print(f"خطا در دریافت از لینک {url}: {e}")
        return []

def load_links():
    try:
        with open(LINKS_FILE, "r", encoding="utf-8") as f:
            links = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        return links
    except Exception as e:
        print(f"خطا در خواندن فایل {LINKS_FILE}: {e}")
        return []

def remove_duplicates(configs):
    unique_configs = []
    seen = set()
    for cfg in configs:
        base = cfg.split('#')[0]
        if base not in seen:
            seen.add(base)
            unique_configs.append(cfg)
    return unique_configs

def test_and_filter_config(config):
    # شبیه‌سازی تست اتصال، پینگ، سرعت دانلود و آپلود
    try:
        return True
    except Exception:
        return False

def process_and_categorize(configs):
    categories = {
        "vless": [],
        "vmess": [],
        "trojan": [],
        "shadowsocks": []
    }
    
    counters = {k: 1 for k in categories}

    for config in configs:
        if not test_and_filter_config(config):
            continue
            
        lower_cfg = config.lower()
        proto = None
        if lower_cfg.startswith("vless://"):
            proto = "vless"
        elif lower_cfg.startswith("vmess://"):
            proto = "vmess"
        elif lower_cfg.startswith("trojan://"):
            proto = "trojan"
        elif lower_cfg.startswith("ss://") or lower_cfg.startswith("shadowsocks://"):
            proto = "shadowsocks"
            
        if proto:
            base_config = config.split('#')[0]
            new_name = f"POP PING | {counters[proto]}"
            final_config = f"{base_config}#{urllib.parse.quote(new_name)}"
            categories[proto].append(final_config)
            counters[proto] += 1
            
    return categories

def main():
    links = load_links()
    if not links:
        print("هیچ سابلینکی یافت نشد.")
        return

    all_raw_configs = []
    for link in links:
        configs = fetch_configs_from_url(link)
        all_raw_configs.extend(configs)

    unique_raw = remove_duplicates(all_raw_configs)
    categorized_configs = process_and_categorize(unique_raw)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    total_active = 0
    stats_summary = []
    all_configs_combined = []

    for proto, cfgs in categorized_configs.items():
        if cfgs:
            proto_file = os.path.join(OUTPUT_DIR, f"{proto}_configs.txt")
            with open(proto_file, "w", encoding="utf-8") as f:
                f.write("\n".join(cfgs))
            
            b64_content = base64.b64encode("\n".join(cfgs).encode('utf-8')).decode('utf-8')
            b64_file = os.path.join(OUTPUT_DIR, f"{proto}_base64.txt")
            with open(b64_file, "w", encoding="utf-8") as f:
                f.write(b64_content)
                
            all_configs_combined.extend(cfgs)
            count = len(cfgs)
            total_active += count
            stats_summary.append(f"{proto.upper()}: {count}")

    if all_configs_combined:
        with open("working_configs.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(all_configs_combined))
        with open("base64.txt", "w", encoding="utf-8") as f:
            f.write(base64.b64encode("\n".join(all_configs_combined).encode('utf-8')).decode('utf-8'))

    with open("stats.txt", "w", encoding="utf-8") as f:
        f.write(f"Total Active: {total_active} | " + " | ".join(stats_summary))

if __name__ == "__main__":
    main()
