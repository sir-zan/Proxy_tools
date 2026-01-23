import ipaddress

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

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    proxies = [line.strip() for line in f if is_valid_proxy(line)]

proxies_sorted = sorted(proxies, key=extract_ip)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(proxies_sorted))

print(f"✅ Sorted {len(proxies_sorted)} proxies numerically")
print(f"📁 Output saved to {OUTPUT_FILE}")
