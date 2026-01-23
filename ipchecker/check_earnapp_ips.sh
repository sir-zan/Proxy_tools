#!/usr/bin/env bash
set -euo pipefail

IN_FILE="ips.txt"              # proxies-to-check (output writes the full line)
PROXIES_FILE="proxies.txt"     # proxies-to-use for requests (curl --proxy)
BASE_URL="https://earnapp.com/dashboard/api/check_ip"

# Timing
START_DELAY_SEC=3
PER_ITEM_DELAY_SEC=0.7

# Rotate the outgoing proxy after N requests
ROTATE_EVERY=15

# Curl timeouts
CONNECT_TIMEOUT_SEC=3
MAX_TIME_SEC=10

# Output files
WHITELIST_FILE="whitelisted.txt"
BLACKLIST_FILE="blacklisted.txt"
TIMEOUT_FILE="timeouted.txt"

die() { echo "Error: $*" >&2; exit 1; }

[[ -f "$IN_FILE" ]] || die "$IN_FILE not found."
[[ -f "$PROXIES_FILE" ]] || die "$PROXIES_FILE not found."

# Load request proxies into an array (skip blanks/comments)
mapfile -t REQ_PROXIES < <(
  sed -e 's/^[[:space:]]*//; s/[[:space:]]*$//' "$PROXIES_FILE" \
  | sed '/^$/d;/^#/d'
)
(( ${#REQ_PROXIES[@]} > 0 )) || die "No proxies found in $PROXIES_FILE."

# Clear output files each run (comment out if you want to append)
: > "$WHITELIST_FILE"
: > "$BLACKLIST_FILE"
: > "$TIMEOUT_FILE"

extract_host() {
  # Extract host/IP from a proxy line:
  #   scheme://user:pass@host:port
  #   scheme://host:port
  #   user:pass@host:port
  #   host:port
  # Also removes all whitespace.
  local s="$1"

  # Remove ALL whitespace (segment spaces etc.)
  s="$(printf "%s" "$s" | tr -d ' \t\r\n')"

  # Drop scheme if present
  s="$(printf "%s" "$s" | sed -E 's#^[a-zA-Z0-9+.-]+://##')"

  # If creds exist, keep substring after last '@'
  if [[ "$s" == *"@"* ]]; then
    s="${s##*@}"
  fi

  # IPv6 in brackets: [2001:db8::1]:1080
  if [[ "$s" == \[*\]* ]]; then
    printf "%s" "${s#\[}" | sed -E 's#\].*$##'
    return 0
  fi

  # Otherwise take up to first ':' (port) or '/' (path)
  printf "%s" "$s" | sed -E 's#[:/].*$##'
}

echo "Starting... waiting ${START_DELAY_SEC}s before first request."
sleep "$START_DELAY_SEC"

printf "%-18s  %-10s  %-30s  %s\n" "IP" "Blocked?" "RequestProxy" "Response"
printf "%-18s  %-10s  %-30s  %s\n" "------------------" "----------" "------------------------------" "--------"

req_count=0
proxy_idx=0
current_req_proxy="${REQ_PROXIES[$proxy_idx]}"

while IFS= read -r raw || [[ -n "$raw" ]]; do
  # Preserve original line (this is what we write to output files)
  original="${raw#"${raw%%[![:space:]]*}"}"
  original="${original%"${original##*[![:space:]]}"}"

  [[ -z "$original" ]] && continue
  [[ "$original" == \#* ]] && continue

  # Rotate outgoing request proxy every ROTATE_EVERY requests
  if (( req_count > 0 && req_count % ROTATE_EVERY == 0 )); then
    proxy_idx=$(( (proxy_idx + 1) % ${#REQ_PROXIES[@]} ))
    current_req_proxy="${REQ_PROXIES[$proxy_idx]}"
  fi

  host="$(extract_host "$original")"
  if [[ -z "$host" ]]; then
    printf "%-18s  %-10s  %-30s  %s\n" "(unparsed)" "timeouted" "$current_req_proxy" "could not parse host"
    printf "%s\n" "$original" >> "$TIMEOUT_FILE"
    req_count=$((req_count + 1))
    sleep "$PER_ITEM_DELAY_SEC"
    continue
  fi

  url="${BASE_URL}/${host}"

  resp=""
  if ! resp="$(curl -sS \
      --connect-timeout "$CONNECT_TIMEOUT_SEC" \
      --max-time "$MAX_TIME_SEC" \
      --proxy "$current_req_proxy" \
      "$url" 2>/dev/null)"; then
    printf "%-18s  %-10s  %-30s  %s\n" "$host" "timeouted" "$current_req_proxy" "(request failed/timeout)"
    printf "%s\n" "$original" >> "$TIMEOUT_FILE"
    req_count=$((req_count + 1))
    sleep "$PER_ITEM_DELAY_SEC"
    continue
  fi

  resp_one_line="$(echo "$resp" | tr '\n' ' ' | sed 's/[[:space:]]\{1,\}/ /g')"

  if echo "$resp" | grep -q '"ip_blocked"[[:space:]]*:[[:space:]]*false'; then
    blocked="false"
    printf "%s\n" "$original" >> "$WHITELIST_FILE"
  else
    blocked="true"
    printf "%s\n" "$original" >> "$BLACKLIST_FILE"
  fi

  printf "%-18s  %-10s  %-30s  %s\n" "$host" "$blocked" "$current_req_proxy" "$resp_one_line"

  req_count=$((req_count + 1))
  sleep "$PER_ITEM_DELAY_SEC"
done < "$IN_FILE"

echo
echo "Done."
echo "Whitelisted  -> $WHITELIST_FILE"
echo "Blacklisted  -> $BLACKLIST_FILE"
echo "Timeouted    -> $TIMEOUT_FILE"
