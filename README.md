# EarnApp IP Checker

A comprehensive tool for generating, checking, and sorting proxy IP addresses for use with EarnApp. This project helps you validate proxy usability and organize them by subnet for optimal performance.

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Installation](#installation)
- [Workflow](#workflow)
- [Module Details](#module-details)
  - [IP_Generator](#ip_generator)
  - [IP_Checker](#ip_checker)
  - [IP_Sorter](#ip_sorter)
- [Usage Guide](#usage-guide)
- [Configuration](#configuration)
- [Output Files](#output-files)
- [Tips & Best Practices](#tips--best-practices)

## 🎯 Project Overview

This project provides three main functionalities:

1. **Generate** proxy IPs from known subnet ranges
2. **Check** proxy availability and performance using the EarnApp IP Checker API
3. **Sort** valid proxies by IP address and subnet for easy organization

The primary goal is to validate proxy usability while providing tools to generate and organize them efficiently.

## 📁 Project Structure

```
earnappIPchecker/
├── IP_Generator/
│   ├── Gen.py              # Generate proxies from subnet ranges
│   └── proxies.txt         # Output file with generated proxies
├── IP_Checker/
│   ├── checker.py          # Check proxy validity and status
│   ├── ips.txt             # Input file: IPs to check
│   ├── proxies.txt         # Input file: Proxies to use for checking
│   ├── whitelisted.txt     # Output: Valid proxies
│   ├── blacklisted.txt     # Output: Detected as proxies (invalid)
│   ├── timeouted.txt       # Output: Timed out proxies
│   └── retry_later.txt     # Temporary: Proxies being retried
└── IP_Sorter/
    ├── sort.py             # Sort proxies without subnet grouping
    ├── sort_sub.py         # Sort proxies with subnet grouping
    ├── proxies_jumbled.txt # Input file: Unsorted proxies
    └── proxies_sorted.txt  # Output file: Sorted proxies
```

## 📦 Requirements

- **Python 3.7+**
- **Required Python Libraries:**
  - `aiohttp`
  - `aiohttp-socks`
  - `ipaddress` (built-in)

### Install Dependencies

```bash
pip install aiohttp aiohttp-socks
```

## 🚀 Installation

1. Clone or download the repository
2. Install Python dependencies:
   ```bash
   pip install aiohttp aiohttp-socks
   ```

## 🔄 Workflow

The recommended workflow is:

```
1. Generate IPs → 2. Check Proxies → 3. Sort Results
```

However, you can run each module independently based on your needs.

## 📖 Module Details

### IP_Generator

**Purpose:** Generate proxy addresses from a given subnet range

**How it works:**
- Uses your credentials and base IP prefix
- Generates proxies for a range of subnets
- Creates IPs with sequential ports
- Outputs to `proxies.txt`

**Configuration Parameters:**
- `USERNAME`: Your proxy username
- `PASSWORD`: Your proxy password
- `BASE_IP_PREFIX`: First two octets (e.g., "65.86")
- `START_SUBNET`: Starting subnet number (3rd octet)
- `END_SUBNET`: Ending subnet number (3rd octet)
- `BASE_PORT`: Starting port number (default: 3010)
- `PORTS_PER_SUBNET`: Ports allocated per subnet (default: 253)

**Example:**
- BASE_IP_PREFIX = "65.86"
- START_SUBNET = 160
- END_SUBNET = 177
- Will generate IPs: 65.86.160.x to 65.86.177.x

---

### IP_Checker

**Purpose:** Check if proxies are valid and usable with EarnApp

**How it works:**
- Tests each IP in `ips.txt` using proxies from `proxies.txt`
- Uses the EarnApp Check IP API
- Implements retry logic with cooldowns
- Uses different proxies to avoid rate limiting
- Categorizes results into whitelisted, blacklisted, and timed out

**Configuration Parameters:**
- `CONCURRENCY`: Number of simultaneous checks (default: 8)
  - Recommended: 1 concurrency per 30-35 IPs
  - Example: For 250 IPs → 8 concurrency (covers ~16 subnets)
- `MAX_RETRIES`: Maximum retry attempts (default: 7)
- `RETRY_DELAYS`: Delay between retries in seconds [2, 4, 6]
- `PROXY_COOLDOWN_SOCKS`: Cooldown after SOCKS error (10 seconds)
- `PROXY_COOLDOWN_423`: Cooldown after rate limit (20 seconds)
- `CONNECT_TIMEOUT`: Connection timeout (5 seconds)
- `READ_TIMEOUT`: Read timeout (10 seconds)

**Important Notes:**
- The EarnApp API rate limits by subnet
- Using proxies from **different subnets** in `proxies.txt` reduces retries and speeds up checking
- Higher subnet diversity = Faster checking
- The terminal will show retry messages; this is normal behavior

**Input Files Required:**
- `ips.txt`: IPs to check (one per line, format: `IP:PORT`)
- `proxies.txt`: Proxies to use for checking (different subnets recommended)
  - **Optimal setup:** 231+ proxies covering 16+ different subnets
  - This is what the author used for smooth, fast operation
  - Fewer subnets = More rate limiting and retries
  - If you have fewer subnets, increase `PROXY_COOLDOWN_423` value

---

### IP_Sorter

**Purpose:** Organize and sort proxy lists for easy use

**Two Sorting Options:**

1. **sort.py** - Plain sorting without subnet headings
   - Best for: Copy-paste ready lists
   - Output: IPs sorted numerically by IP address
   - No extra formatting

2. **sort_sub.py** - Sorting with subnet grouping
   - Best for: Organized reference
   - Output: IPs grouped by /24 subnet with headers
   - Easy to see subnet breakdown

**Configuration:**
- `INPUT_FILE`: `proxies_jumbled.txt` (input unsorted proxies)
- `OUTPUT_FILE`: `proxies_sorted.txt` (output sorted proxies)

---

## 💻 Usage Guide

### Step 1: Generate Proxies

**Navigate to IP_Generator folder:**
```bash
cd IP_Generator
```

**Edit Gen.py** - Change these values:
```python
BASE_IP_PREFIX = "65.86"      # Change to your IP prefix
START_SUBNET = 160             # Change to your start subnet
END_SUBNET = 177               # Change to your end subnet
```

**Run the generator:**
```bash
python -u Gen.py
```

**Output:** `proxies.txt` will be created with generated proxies

---

### Step 2: Check Proxies

**Navigate to IP_Checker folder:**
```bash
cd ../IP_Checker
```

**Prepare input files:**
1. Put IPs to check in `ips.txt` (one IP per line)
   ```
   IP:PORT
   IP:PORT
   ```

2. Put proxies in `proxies.txt` (from IP_Generator or other source)
   - **Important:** Use IPs from different subnets
   - Recommended: 231+ proxies covering 16+ subnets
   - This reduces rate limiting and retries

**Edit checker.py** (Optional - customize these):
```python
CONCURRENCY = 8                # Adjust based on IP count
MAX_RETRIES = 7                # Increase for more thorough checking
RETRY_DELAYS = [2, 4, 6]      # Adjust retry timing
PROXY_COOLDOWN_SOCKS = 10      # Increase if rate limited
PROXY_COOLDOWN_423 = 20        # Increase if rate limited
```

**Run the checker:**
```bash
python -u checker.py
```

**What happens:**
- Checks each IP in `ips.txt`
- Uses proxies from `proxies.txt` for checking
- Shows retry messages in terminal (normal behavior)
- Creates output files with results

**Output Files:**
- `whitelisted.txt`: ✅ Valid, working proxies
- `blacklisted.txt`: ❌ Detected as proxies (invalid)
- `timeouted.txt`: ⏱️ Timed out (hit max retries)
- `retry_later.txt`: 🔄 Automatically handled by the script

---

### Step 3: Sort Results

**Navigate to IP_Sorter folder:**
```bash
cd ../IP_Sorter
```

**Prepare input:**
Put proxies to sort in `proxies_jumbled.txt`

**Option A: Sort with subnet grouping**
```bash
python -u sort_sub.py
```
Output: Proxies organized by subnet with headers

**Option B: Sort without grouping (copy-paste ready)**
```bash
python -u sort.py
```
Output: Plain sorted proxy list

**Output:** `proxies_sorted.txt` will contain the sorted proxies

---

## ⚙️ Configuration

### IP_Generator Configuration

Edit `IP_Generator/Gen.py`:
```python
USERNAME = "arkon"              # Keep this constant
PASSWORD = "ms12dcv015a"        # Keep this constant
BASE_IP_PREFIX = "65.86"        # Change this (first 2 octets)
START_SUBNET = 160              # Change this (3rd octet - start)
END_SUBNET = 177                # Change this (3rd octet - end)
BASE_PORT = 3010                # Adjust if needed for different subnets
PORTS_PER_SUBNET = 253          # Proxies per subnet
```

### IP_Checker Configuration

Edit `IP_Checker/checker.py`:
```python
CONCURRENCY = 8                 # Threads for simultaneous checks
MAX_RETRIES = 7                 # Max retry attempts per IP
RETRY_DELAYS = [2, 4, 6]       # Wait times between retries (seconds)
PROXY_COOLDOWN_SOCKS = 10       # Cooldown after SOCKS error (seconds)
PROXY_COOLDOWN_423 = 20         # Cooldown after rate limit (seconds)
CONNECT_TIMEOUT = 5             # Connection timeout (seconds)
READ_TIMEOUT = 10               # Read timeout (seconds)
```

### IP_Sorter Configuration

Both sort scripts have fixed configuration:
```python
INPUT_FILE = "proxies_jumbled.txt"
OUTPUT_FILE = "proxies_sorted.txt"
```

No changes needed unless you want different file names.

---

## 📤 Output Files

### From IP_Generator
- **proxies.txt**: Generated proxy list in format `socks5://user:pass@IP:PORT`

### From IP_Checker
- **whitelisted.txt**: ✅ Proxies that passed validation
- **blacklisted.txt**: ❌ Proxies detected as proxies (API blocked them)
- **timeouted.txt**: ⏱️ Proxies that exceeded max retries
- **retry_later.txt**: 🔄 Temporary file (auto-handled by script)

### From IP_Sorter
- **proxies_sorted.txt**: 
  - If from `sort.py`: Plain sorted list
  - If from `sort_sub.py`: Sorted list with subnet groupings

---

## 💡 Tips & Best Practices

### For IP_Checker
1. **More subnets = Faster checking**
   - Use proxies from different subnets to avoid subnet-level rate limiting
   - The author used 231 proxies spanning 16 subnets

2. **Concurrency tuning**
   - Formula: Use 1 concurrency per 30-35 IPs
   - For 250 IPs → 8 concurrency

3. **Retry Logic**
   - Don't set MAX_RETRIES too low (minimum 5-7 recommended)
   - Proxies get re-queued unless they hit max retries
   - Terminal shows retry messages—this is normal!

4. **Cooldown Management**
   - If you see many 423 errors, increase `PROXY_COOLDOWN_423`
   - If you see many SOCKS errors, increase `PROXY_COOLDOWN_SOCKS`

### For IP_Generator
1. Adjust `BASE_PORT` if using different subnets
2. Keep `PORTS_PER_SUBNET = 253` unless you have specific requirements
3. Generator accounts for IPs 2-254 per subnet (253 IPs total)

### For IP_Sorter
1. Use `sort.py` for final export lists
2. Use `sort_sub.py` for organizing and reviewing proxies by subnet

### General Tips
- Always use `-u` flag when running Python: `python -u script.py`
- This ensures output appears in real-time
- Run scripts from their respective directories to avoid path issues
- Check input file format before running scripts

---

## ⚠️ Common Issues

**Issue:** Script says file not found
- **Solution:** Make sure you're in the correct directory. Use full `cd` command as shown in usage guide.

**Issue:** Too many retries during IP_Checker
- **Solution:** Add more proxies from different subnets to `proxies.txt`

**Issue:** Rate limiting (HTTP 423 errors)
- **Solution:** Increase `PROXY_COOLDOWN_423` or use more diverse proxies

---

## � Credits & Attribution

**⭐ This project is a branch/fork from [Asster's Original Repository](https://github.com/kdans1887-byte/earnappIPchecker)**

Huge thanks to **Asster** for creating the original IP checking tool and making it available to the community. This project builds upon their excellent work!

---

## 📝 License

This project is branched from Asster's work. Please respect the original creator's contributions.

---

## 🤝 Contributing

**Special thanks to Asster** for the original implementation and ongoing support!

If you'd like to contribute improvements or report issues:
1. Feel free to submit pull requests with enhancements
2. Report bugs and issues you encounter
3. Share optimization tips and best practices
4. Give credit to **Asster** if you're building upon this work

---

**Last Updated:** January 2026
