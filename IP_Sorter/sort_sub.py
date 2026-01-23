import ipaddress
from collections import defaultdict

INPUT_FILE = "proxies_jumbled.txt"
OUTPUT_FILE = "proxies_sorted.txt"

def extract_ip(line):
    """Extract IP from various proxy formats"""
    # Remove protocol if present (socks5://, http://, https://)
    if "://" in line:
        line = line.split("://")[-1]
    
    # Remove credentials if present (user:pass@)
    if "@" in line:
        line = line.split("@")[-1]
    
    # Remove port if present (IP:PORT)
    ip_part = line.split(":")[0]
    
    return ipaddress.ip_address(ip_part)

def is_valid_proxy(line):
    """Check if line is a valid proxy line"""
    line = line.strip()
    if not line or line.startswith("#"):
        return False
    try:
        extract_ip(line)
        return True
    except:
        return False

def extract_subnet(ip):
    return ipaddress.ip_network(f"{ip}/24", strict=False)

# Read proxies
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    proxies = [line.strip() for line in f if is_valid_proxy(line)]

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
