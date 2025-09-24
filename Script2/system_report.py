#

import os
import platform
import socket
import subprocess
from datetime import datetime
from pathlib import Path
import re

# ---------- helpers ----------

def run(cmd: list[str]) -> str:
    """Run a command and return decoded stdout (strip trailing newline)."""
    try:
        out = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        return out.stdout.strip()
    except Exception:
        return ""

def dotted_mask(prefix: int) -> str:
    bits = (0xffffffff << (32 - prefix)) & 0xffffffff
    return ".".join(str((bits >> (i * 8)) & 0xff) for i in [3, 2, 1, 0])

def first_match(pattern: str, text: str) -> str | None:
    m = re.search(pattern, text, re.M)
    return m.group(1) if m else None

# ---------- hostname & log path ----------

hostname = platform.node() or socket.gethostname() or "unknown-host"
log_path = Path.home() / f"{hostname}_system_report.log"

# ---------- date header ----------

now = datetime.now().strftime("%B %d, %Y")

# ---------- OS / kernel ----------

# /etc/os-release is the canonical source on Rocky 9
os_release = {}
try:
    with open("/etc/os-release") as f:
        for line in f:
            if "=" in line:
                k, v = line.rstrip().split("=", 1)
                os_release[k] = v.strip('"')
except FileNotFoundError:
    pass

os_name = os_release.get("NAME") or platform.system()
os_version = os_release.get("VERSION_ID") or (platform.version() or "")
kernel_version = platform.release()

# ---------- network: IP, gateway, mask, DNS, domain ----------

# default route (gateway and interface)
ip_route = run(["ip", "route", "show", "default"])
gateway = first_match(r"default via ([0-9.]+)", ip_route) or "N/A"
iface = first_match(r"dev\s+(\S+)", ip_route)

# IPv4 address & prefix on that interface
ip_addr = "N/A"
netmask = "N/A"
if iface:
    addr_out = run(["ip", "-4", "addr", "show", "dev", iface])
    ip_cidr = first_match(r"inet\s+([0-9.]+)/(\d+)", addr_out)
    if ip_cidr:
        ip_addr = ip_cidr[0]
        netmask = dotted_mask(int(ip_cidr[1]))

# DNS + domain from resolv.conf
dns_servers: list[str] = []
domain = "N/A"
try:
    with open("/etc/resolv.conf") as f:
        for line in f:
            line = line.strip()
            if line.startswith("nameserver"):
                parts = line.split()
                if len(parts) >= 2:
                    dns_servers.append(parts[1])
            elif line.startswith("domain"):
                parts = line.split()
                if len(parts) >= 2:
                    domain = parts[1]
            elif line.startswith("search") and domain == "N/A":
                parts = line.split()
                if len(parts) >= 2:
                    domain = parts[1]
except FileNotFoundError:
    pass

# ---------- storage (root filesystem) ----------

# human-readable df for /
df_out = run(["df", "-h", "--output=size,used,avail,target", "/"])
# Skip header line
sys_total = sys_used = sys_free = "N/A"
if df_out:
    lines = df_out.splitlines()
    if len(lines) >= 2:
        _, size, used, avail, target = re.split(r"\s+", lines[1].strip(), maxsplit=4)
        sys_total, sys_used, sys_free = size, used, avail

# ---------- CPU info ----------

cpu_model = "N/A"
num_processors = 0
cores_per_socket = None
try:
    with open("/proc/cpuinfo") as f:
        text = f.read()
        # model name
        m = re.search(r"^model name\s*:\s*(.+)$", text, re.M)
        if m:
            cpu_model = m.group(1).strip()
        # logical CPUs
        num_processors = len(re.findall(r"^processor\s*:", text, re.M))
        # cores per socket (may repeat per physical id)
        m2 = re.search(r"^cpu cores\s*:\s*(\d+)$", text, re.M)
        if m2:
            cores_per_socket = int(m2.group(1))
except FileNotFoundError:
    pass

num_cores = cores_per_socket or num_processors or 0  # fall back

# ---------- memory (free -h) ----------

free_out = run(["free", "-h"])
mem_total = mem_avail = "N/A"
if free_out:
    for line in free_out.splitlines():
        if line.lower().startswith("mem:"):
            cols = line.split()
            # Mem: total used free shared buff/cache available
            if len(cols) >= 7:
                mem_total = cols[1]
                mem_avail = cols[6]
            break

# ---------- build report text ----------

def section(title: str) -> str:
    return f"{title}\n" + "-" * len(title)

lines: list[str] = []
lines.append(f"System Report - {now}\n")

# Device
lines.append(section("Device Information"))
lines.append(f"Hostname:            {hostname}")
lines.append(f"Domain:              {domain}\n")

# Network
lines.append(section("Network Information"))
lines.append(f"IP Address:          {ip_addr}")
lines.append(f"Gateway:             {gateway}")
lines.append(f"Network Mask:        {netmask}")
if dns_servers:
    # show up to two like the screenshot, but include more if present
    for i, dns in enumerate(dns_servers[:4], start=1):
        lines.append(f"DNS{i}:               {dns}")
else:
    lines.append("DNS:                 N/A")
lines.append("")

# OS
lines.append(section("Operating System Information"))
lines.append(f"Operating System:    {os_name}")
lines.append(f"OS Version:          {os_version}")
lines.append(f"Kernel Version:      {kernel_version}\n")

# Storage
lines.append(section("Storage Information"))
lines.append(f"System Drive Total:  {sys_total}")
lines.append(f"System Drive Used:   {sys_used}")
lines.append(f"System Drive Free:   {sys_free}\n")

# CPU
lines.append(section("Processor Information"))
lines.append(f"CPU Model:           {cpu_model}")
lines.append(f"Number of processors:{num_processors}")
lines.append(f"Number of cores:     {num_cores}\n")

# Memory
lines.append(section("Memory Information"))
lines.append(f"Total RAM:           {mem_total}")
lines.append(f"Available RAM:       {mem_avail}\n")

report = "\n".join(lines).rstrip() + "\n"

# ---------- output ----------

print(report, end="")

try:
    log_path.write_text(report)
    # echo a one-line hint at the end (still part of stdout)
    print(f"[Saved to] {log_path}")
except Exception as e:
    print(f"[WARN] Could not write log file: {e}")