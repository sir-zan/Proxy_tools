import random
from collections import defaultdict

INPUT_FILE = "whitelisted.txt"
EXCLUDED_FILE = "excluded.txt"
OUTPUT_FILE = "whitelisted_random_30_per_subnet.txt"

PER_SUBNET = 30
EXCLUDED_SUBNET = 168


def normalize(s):
    return s.strip().replace("\r", "").replace("\n", "")


def extract_ip(proxy):
    # socks5://user:pass@IP:PORT
    return proxy.split("@")[1].rsplit(":", 1)[0]


# ---------- load excluded proxies ----------
with open(EXCLUDED_FILE, "r", encoding="utf-8") as f:
    excluded_proxies = {
        normalize(line)
        for line in f
        if line.strip() and not line.startswith("#")
    }

print(f"Excluded proxies loaded : {len(excluded_proxies)}")

# ---------- load whitelisted proxies ----------
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    proxies = [
        normalize(line)
        for line in f
        if line.strip() and not line.startswith("#")
    ]

print(f"Whitelisted loaded      : {len(proxies)}")

# ---------- group by subnet ----------
subnets = defaultdict(list)

for proxy in proxies:
    if proxy in excluded_proxies:
        continue

    ip = extract_ip(proxy)
    subnet = int(ip.split(".")[2])

    if subnet == EXCLUDED_SUBNET:
        continue

    subnets[subnet].append(proxy)

# ---------- select random per subnet ----------
selected = []

for subnet in sorted(subnets):
    pool = subnets[subnet]
    if not pool:
        continue

    chosen = random.sample(pool, min(PER_SUBNET, len(pool)))
    selected.extend(chosen)

# ---------- write output ----------
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(selected))

print("--------------------------------------------------")
print(f"✅ Final proxies saved : {len(selected)}")
print(f"📁 Output file        : {OUTPUT_FILE}")
print("--------------------------------------------------")
