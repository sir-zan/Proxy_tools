import ipaddress

INPUT_FILE = "proxies_jumbled.txt"
OUTPUT_FILE = "proxies_sorted.txt"

def extract_ip(proxy_line):
    # socks5://user:pass@IP:PORT
    ip_part = proxy_line.split("@")[1].rsplit(":", 1)[0]
    return ipaddress.ip_address(ip_part)

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    proxies = [line.strip() for line in f if line.strip()]

proxies_sorted = sorted(proxies, key=extract_ip)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(proxies_sorted))

print(f"✅ Sorted {len(proxies_sorted)} proxies numerically")
print(f"📁 Output saved to {OUTPUT_FILE}")
