import asyncio
import aiohttp
import aiohttp_socks
import random
import time
from collections import deque, defaultdict
from itertools import cycle

# ================= CONFIG =================
IPS_FILE = "ips.txt"
PROXIES_FILE = "proxies.txt"
BASE_URL = "https://earnapp.com/dashboard/api/check_ip"

CONCURRENCY = 8
MAX_RETRIES = 15 # 15 max

RETRY_DELAYS = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30]  # seconds
PROXY_COOLDOWN_SOCKS = 10         # seconds
PROXY_COOLDOWN_423 = 20           # seconds

CONNECT_TIMEOUT = 5
READ_TIMEOUT = 10

WHITELIST_FILE = "whitelisted.txt"
BLACKLIST_FILE = "blacklisted.txt"
TIMEOUT_FILE = "timeouted.txt"
# =========================================

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0",
    "Mozilla/5.0 (X11; Linux x86_64) Firefox/123.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; rv:122.0) Gecko/20100101 Firefox/122.0",
]

# ---------------- helpers ----------------
def extract_host(line: str) -> str:
    s = line.strip().replace(" ", "")
    s = s.split("://")[-1]
    if "@" in s:
        s = s.split("@")[-1]
    return s.split(":")[0].split("/")[0]

def write_line(path, line):
    with open(path, "a", encoding="utf-8") as f:
        f.write(line + "\n")

# ---------------- load files ----------------
with open(IPS_FILE, encoding="utf-8") as f:
    raw_ips = [l.strip() for l in f if l.strip() and not l.startswith("#")]

with open(PROXIES_FILE, encoding="utf-8") as f:
    proxies = [l.strip() for l in f if l.strip() and not l.startswith("#")]

if not raw_ips or not proxies:
    raise SystemExit("Missing ips.txt or proxies.txt")

ip_queue = deque(raw_ips)
retry_count = defaultdict(int)

proxy_cycle = cycle(proxies)
proxy_cooldown_until = {}

print(f"IPs loaded        : {len(raw_ips)}")
print(f"Request proxies  : {len(proxies)}")
print(f"Concurrency      : {CONCURRENCY}")
print("-" * 75)

# clear outputs
open(WHITELIST_FILE, "w").close()
open(BLACKLIST_FILE, "w").close()
open(TIMEOUT_FILE, "w").close()

# ---------------- core logic ----------------
async def get_proxy():
    while True:
        p = next(proxy_cycle)
        now = time.time()
        if proxy_cooldown_until.get(p, 0) <= now:
            return p
        await asyncio.sleep(0.1)

async def worker(worker_id):
    timeout = aiohttp.ClientTimeout(
        total=None,
        sock_connect=CONNECT_TIMEOUT,
        sock_read=READ_TIMEOUT
    )

    async with aiohttp.ClientSession(timeout=timeout) as session:
        while True:
            try:
                ip_raw = ip_queue.popleft()
            except IndexError:
                return

            ip = extract_host(ip_raw)
            proxy = await get_proxy()

            await asyncio.sleep(random.uniform(0.1, 0.4))  # jitter

            headers = {"User-Agent": random.choice(USER_AGENTS)}
            url = f"{BASE_URL}/{ip}"

            try:
                connector = aiohttp_socks.ProxyConnector.from_url(proxy)
                async with aiohttp.ClientSession(
                    connector=connector,
                    timeout=timeout,
                    headers=headers
                ) as proxied:

                    async with proxied.get(url) as resp:
                        if resp.status == 423:
                            raise aiohttp.ClientResponseError(
                                resp.request_info, (), status=423
                            )

                        if resp.status != 200:
                            raise aiohttp.ClientError(f"HTTP {resp.status}")

                        data = await resp.json()
                        blocked = data.get("ip_blocked")

                        if blocked is False:
                            write_line(WHITELIST_FILE, ip_raw)
                            print(f"[OK]   {ip:<15} blocked=False via {proxy}")
                        else:
                            write_line(BLACKLIST_FILE, ip_raw)
                            print(f"[OK]   {ip:<15} blocked=True  via {proxy}")

            except aiohttp.ClientResponseError as e:
                if e.status == 423:
                    proxy_cooldown_until[proxy] = time.time() + PROXY_COOLDOWN_423
                    reason = "HTTP 423 (locked)"
                else:
                    reason = f"HTTP {e.status}"

                if retry_count[ip_raw] < MAX_RETRIES:
                    delay = RETRY_DELAYS[retry_count[ip_raw]]
                    retry_count[ip_raw] += 1
                    print(f"[RETRY] {ip:<15} via {proxy} ({reason}) +{delay}s")
                    await asyncio.sleep(delay)
                    ip_queue.append(ip_raw)
                else:
                    write_line(TIMEOUT_FILE, ip_raw)

            except Exception as e:
                proxy_cooldown_until[proxy] = time.time() + PROXY_COOLDOWN_SOCKS

                if retry_count[ip_raw] < MAX_RETRIES:
                    delay = RETRY_DELAYS[retry_count[ip_raw]]
                    retry_count[ip_raw] += 1
                    print(f"[RETRY] {ip:<15} via {proxy} (SOCKS) +{delay}s")
                    await asyncio.sleep(delay)
                    ip_queue.append(ip_raw)
                else:
                    write_line(TIMEOUT_FILE, ip_raw)

# ---------------- start ----------------
async def main():
    tasks = [asyncio.create_task(worker(i)) for i in range(CONCURRENCY)]
    await asyncio.gather(*tasks)

asyncio.run(main())

print("\nDone.")
print(f"Whitelisted → {WHITELIST_FILE}")
print(f"Blacklisted → {BLACKLIST_FILE}")
print(f"Timeouted   → {TIMEOUT_FILE}")
