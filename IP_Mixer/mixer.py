import random
import ipaddress
from collections import defaultdict, deque
import os
import sys

# ================= FILES =================
INPUT_FILE = "proxies.txt"
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


# ---------- load proxies ----------
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    raw_lines = [
        line.strip()
        for line in f
        if line.strip() and not line.startswith("#")
    ]

print(f"\nLoaded proxies            : {len(raw_lines)}")

# ---------- group by /24 subnet ----------
subnets = defaultdict(deque)

for line in raw_lines:
    ip = extract_ip(line)
    if not ip:
        continue

    subnet = ipaddress.ip_network(f"{ip}/24", strict=False)
    subnets[subnet].append(line)

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
