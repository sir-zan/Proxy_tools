USERNAME = "arkon"
PASSWORD = "ms12dcv015a"

BASE_IP_PREFIX = "65.86" # change this value
START_SUBNET = 160 # change this value
END_SUBNET = 177 # change this value

BASE_PORT = 3010
PORTS_PER_SUBNET = 253

OUTPUT_FILE = "proxies.txt"

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    for subnet in range(START_SUBNET, END_SUBNET + 1):
        subnet_base_port = BASE_PORT + (subnet - START_SUBNET) * PORTS_PER_SUBNET

        for host in range(2, 255):
            port = subnet_base_port + (host - 2)
            f.write(
                f"socks5://{USERNAME}:{PASSWORD}@"
                f"{BASE_IP_PREFIX}.{subnet}.{host}:{port}\n"
            )

print(f"Done. Proxies written to {OUTPUT_FILE}")
