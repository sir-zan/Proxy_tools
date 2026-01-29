import random
import ipaddress
from collections import defaultdict, deque
import sys
import os

# ================= FILES =================
INPUT_FILE = "proxies.txt"
EXCEPTION_FILE = "exceptions.txt"
OUTPUT_PREFIX = "set"
# =========================================


def extract_ip(line: str):
    """
    Extract IPv4 address from ANY proxy format.
    Keeps original line unchanged.
    """
    parts = (
        line.replace("://", " ")
            .replace("@", " ")
            .replace(":", " ")
            .split()
    )
    for p in parts:
        try:
            return ipaddress.ip_address(p)
        except ValueError:
            continue
    return None


# ---------- ask user ----------
try:
    SETS = int(input("Enter number of sets to generate: ").strip())
    IPS_PER_SET = int(input("Enter IPs per set: ").strip())
except ValueError:
    print("❌ Invalid input. Enter numbers only.")
    sys.exit(1)

if SETS <= 0 or IPS_PER_SET <= 0:
    print("❌ Values must be greater than 0.")
    sys.exit(1)


# ---------- load exceptions ----------
excluded_ips = set()

if os.path.exists(EXCEPTION_FILE):
    with open(EXCEPTION_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            ip = extract_ip(line)
            if ip:
                excluded_ips.add(ip)

print(f"Excluded IPs loaded       : {len(excluded_ips)}")


# ---------- load proxies ----------
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    raw_lines = [
        line.strip()
        for line in f
        if line.strip() and not line.startswith("#")
    ]

print(f"Loaded proxies            : {len(raw_lines)}")

# ---------- group by /24 subnet ----------
subnets = defaultdict(deque)
skipped = 0

for line in raw_lines:
    ip = extract_ip(line)
    if not ip:
        continue

    if ip in excluded_ips:
        skipped += 1
        continue

    subnet = ipaddress.ip_network(f"{ip}/24", strict=False)
    subnets[subnet].append(line)

print(f"Skipped by exception      : {skipped}")
print(f"Detected /24 subnets      : {len(subnets)}")

# Shuffle inside each subnet
for subnet in subnets:
    items = list(subnets[subnet])
    random.shuffle(items)
    subnets[subnet] = deque(items)

# ---------- generate sets ----------
for set_index in range(1, SETS + 1):
    available = [s for s in subnets if subnets[s]]
    if not available:
        print("\n⚠ No proxies left — stopping early.")
        break

    current_set = []

    # 1-per-subnet round-robin
    while len(current_set) < IPS_PER_SET and available:
        for subnet in list(available):
            if len(current_set) >= IPS_PER_SET:
                break
            if subnets[subnet]:
                current_set.append(subnets[subnet].popleft())
            else:
                available.remove(subnet)

    random.shuffle(current_set)

    outfile = f"{OUTPUT_PREFIX}{set_index}.txt"
    with open(outfile, "w", encoding="utf-8") as f:
        f.write("\n".join(current_set))

    print(f"✅ Written {outfile:<10} ({len(current_set)} proxies)")

print("\n--------------------------------------------------")
print("Done.")
print("--------------------------------------------------")
