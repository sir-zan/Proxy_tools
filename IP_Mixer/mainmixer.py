import random
import ipaddress
from collections import defaultdict, deque
import sys
import os

# ================= FILES =================
INPUT_FILE = "proxies.txt"
EXCEPTIONS_FILE = "exceptions.txt"
OUTPUT_PREFIX = "set"
# ========================================


def extract_ip(line: str):
    """
    Extract IPv4 from ANY proxy format.
    Returns ipaddress.IPv4Address or None.
    """
    tokens = (
        line.replace("://", " ")
            .replace("@", " ")
            .replace(":", " ")
            .split()
    )
    for t in tokens:
        try:
            return ipaddress.ip_address(t)
        except ValueError:
            pass
    return None


# ---------- user input ----------
try:
    SETS = int(input("Enter number of sets to generate: "))
    IPS_PER_SET = int(input("Enter IPs per set: "))
except ValueError:
    print("❌ Numbers only.")
    sys.exit(1)

if SETS <= 0 or IPS_PER_SET <= 0:
    print("❌ Values must be > 0.")
    sys.exit(1)


# ---------- load exceptions ----------
excluded = set()
if os.path.exists(EXCEPTIONS_FILE):
    with open(EXCEPTIONS_FILE, "r", encoding="utf-8") as f:
        excluded = {
            line.strip()
            for line in f
            if line.strip() and not line.startswith("#")
        }

print(f"\nExcluded proxies loaded   : {len(excluded)}")


# ---------- load proxies ----------
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    raw_lines = [
        line.strip()
        for line in f
        if line.strip() and not line.startswith("#")
    ]

print(f"Loaded proxies            : {len(raw_lines)}")


# ---------- main → subnet → proxies ----------
# main_key = first two octets (147.90)
# subnet_key = /24 (147.90.96.0/24)

tree = defaultdict(lambda: defaultdict(deque))

for line in raw_lines:
    if line in excluded:
        continue

    ip = extract_ip(line)
    if not ip:
        continue

    octets = str(ip).split(".")
    main_key = f"{octets[0]}.{octets[1]}"
    subnet_key = ipaddress.ip_network(f"{ip}/24", strict=False)

    tree[main_key][subnet_key].append(line)


# shuffle inside each subnet
for main in tree:
    for subnet in tree[main]:
        items = list(tree[main][subnet])
        random.shuffle(items)
        tree[main][subnet] = deque(items)

print(f"Detected main groups      : {len(tree)}")


# ---------- generate sets ----------
for set_index in range(1, SETS + 1):
    current_set = []

    # build active subnet queues per main group
    active = {
        main: deque(subnets.keys())
        for main, subnets in tree.items()
        if any(tree[main][s] for s in subnets)
    }

    while len(current_set) < IPS_PER_SET and active:
        for main in list(active.keys()):
            if len(current_set) >= IPS_PER_SET:
                break

            subnet_queue = active[main]
            if not subnet_queue:
                del active[main]
                continue

            subnet = subnet_queue.popleft()

            if tree[main][subnet]:
                current_set.append(tree[main][subnet].popleft())

            # requeue subnet ONLY if it still has proxies
            if tree[main][subnet]:
                subnet_queue.append(subnet)

            # remove empty main group
            if not any(tree[main][s] for s in tree[main]):
                del active[main]

    random.shuffle(current_set)

    outfile = f"{OUTPUT_PREFIX}{set_index}.txt"
    with open(outfile, "w", encoding="utf-8") as f:
        f.write("\n".join(current_set))

    print(f"✅ Written {outfile:<10} ({len(current_set)} proxies)")


print("\n--------------------------------------------------")
print("Done.")
print("--------------------------------------------------")
