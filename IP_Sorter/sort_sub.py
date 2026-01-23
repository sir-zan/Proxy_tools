import ipaddress
from collections import defaultdict

INPUT_FILE = "proxies_jumbled.txt"
OUTPUT_FILE = "proxies_sorted.txt"

def extract_ip(proxy_line):
    # socks5://user:pass@IP:PORT
    ip_part = proxy_line.split("@")[1].rsplit(":", 1)[0]
    return ipaddress.ip_address(ip_part)

def extract_subnet(ip):
    return ipaddress.ip_network(f"{ip}/24", strict=False)

# Read proxies
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    proxies = [line.strip() for line in f if line.strip()]

# Sort proxies numerically by IP
proxies_sorted = sorted(proxies, key=extract_ip)

# Group by subnet
subnet_map = defaultdict(list)
for proxy in proxies_sorted:
    ip = extract_ip(proxy)
    subnet = extract_subnet(ip)
    subnet_map[subnet].append(proxy)

# Write output with headings
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    for subnet in sorted(subnet_map.keys()):
        f.write(f"# ===== Subnet: {subnet} =====\n")
        for proxy in subnet_map[subnet]:
            f.write(proxy + "\n")
        f.write("\n")

print(f"✅ Sorted {len(proxies_sorted)} proxies numerically")
print(f"📁 Grouped by subnet and saved to {OUTPUT_FILE}")
