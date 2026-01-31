import pandas as pd
import ipaddress
import os

# ================= CONFIG =================
CSV_FILE = "proxy_results.csv"

USERNAME = "arkon"
PASSWORD = "ms12dcv015a"

BASE_PORT = 3010          # port for x.x.x.2
PORTS_PER_SUBNET = 253    # .2 → .254

OUTPUT_DIR = "regenerated_proxies"
# ========================================

os.makedirs(OUTPUT_DIR, exist_ok=True)

df = pd.read_csv(CSV_FILE)

# -------- helper to rebuild SOCKS URL --------
def build_socks(ip):
    ip_obj = ipaddress.ip_address(ip)
    subnet = int(str(ip_obj).split(".")[2])
    host = ip_obj.packed[-1]  # last octet

    port = BASE_PORT + (subnet * PORTS_PER_SUBNET) + (host - 2)

    return f"socks5://{USERNAME}:{PASSWORD}@{ip}:{port}"

# -------- group by subnet & ip type --------
grouped = df.groupby(["subnet", "ip_type"])

for (subnet, ip_type), group in grouped:
    safe_subnet = subnet.replace("/", "_")
    filename = f"{safe_subnet}_{ip_type.lower()}.txt"
    filepath = os.path.join(OUTPUT_DIR, filename)

    with open(filepath, "w") as f:
        for ip in group["ip"]:
            f.write(build_socks(ip) + "\n")

    print(f"[OK] {filepath} ({len(group)} proxies)")
