#!/usr/bin/env python3
#Emir T. Yilmaz
#Sep 24th, 2025
#Script 2

import os
import socket
import platform
import subprocess
from datetime import datetime
from pathlib import Path

def run(cmd_list):
    """Return command stdout as text, or '' on error."""
    try:
        return subprocess.check_output(cmd_list, stderr=subprocess.DEVNULL, text=True).strip()
    except Exception:
        return ""

def cidr_to_netmask(prefix):
    """Convert CIDR prefix (e.g., 24) to dotted mask (e.g., 255.255.255.0)."""
    try:
        prefix = int(prefix)
    except:
        return "N/A"
    bits = (0xffffffff << (32 - prefix)) & 0xffffffff
    parts = []
    for i in [24, 16, 8, 0]:
        parts.append(str((bits >> i) & 0xff))
    return ".".join(parts)

# ----- Hostname & log path -----
hostname = socket.gethostname() or "unknown-host"
log_path = Path.home() / f"{hostname}_system_report.log"

# ----- Date -----
today = datetime.now().strftime("%B %d, %Y")

# ----- OS info -----
os_name = platform.system()
os_version = platform.version()
try:
    with open("/etc/os-release") as f:
        for line in f:
            line = line.strip()
            if line.startswith("NAME=") and len(line.split("=", 1)) == 2:
                os_name = line.split("=", 1)[1].strip('"')
            if line.startswith("VERSION_ID=") and len(line.split("=", 1)) == 2:
                os_version = line.split("=", 1)[1].strip('"')
except:
    pass
kernel_version = platform.release()

# ----- Network (gateway, iface, IP, mask) -----
gateway = "N/A"
iface = None
default_route = run(["ip", "route", "show", "default"])
# Example: "default via 192.168.135.2 dev enp1s0 ..."
if default_route:
    parts = default_route.split()
    # find "via" and "dev" values
    if "via" in parts:
        idx = parts.index("via")
        if idx + 1 < len(parts):
            gateway = parts[idx + 1]
    if "dev" in parts:
        idx = parts.index("dev")
        if idx + 1 < len(parts):
            iface = parts[idx + 1]

ip_addr = "N/A"
netmask = "N/A"
if iface:
    addr_text = run(["ip", "-4", "addr", "show", "dev", iface])
    # Look for a line with "inet 192.168.x.y/24"
    for line in addr_text.splitlines():
        line = line.strip()
        if line.startswith("inet "):
            # "inet 192.168.1.10/24 ..."
            val = line.split()[1]  # "192.168.1.10/24"
            if "/" in val:
                ip_addr, prefix = val.split("/", 1)
                netmask = cidr_to_netmask(prefix)
            break

# ----- DNS + domain -----
dns_list = []
domain = "N/A"
try:
    with open("/etc/resolv.conf") as f:
        for raw in f:
            line = raw.strip()
            if line.startswith("#") or not line:
                continue
            parts = line.split()
            if len(parts) >= 2 and parts[0] == "nameserver":
                dns_list.append(parts[1])
            elif len(parts) >= 2 and parts[0] == "domain":
                domain = parts[1]
            elif len(parts) >= 2 and parts[0] == "search" and domain == "N/A":
                domain = parts[1]
except:
    pass

# ----- Storage (df -h /) -----
sys_total = sys_used = sys_free = "N/A"
df_out = run(["df", "-h", "--output=size,used,avail,target", "/"])
# Expect two lines: header and data
if df_out:
    lines = [l for l in df_out.splitlines() if l.strip()]
    if len(lines) >= 2:
        # size used avail target
        cols = lines[1].split()
        if len(cols) >= 4:
            sys_total, sys_used, sys_free = cols[0], cols[1], cols[2]

# ----- CPU info (/proc/cpuinfo) -----
cpu_model = "N/A"
num_processors = 0
num_cores = 0
try:
    with open("/proc/cpuinfo") as f:
        for line in f:
            if line.startswith("processor"):
                num_processors += 1
            if line.startswith("model name") and cpu_model == "N/A":
                # model name  : AMD Ryzen 7 ...
                parts = line.split(":", 1)
                if len(parts) == 2:
                    cpu_model = parts[1].strip()
            if line.startswith("cpu cores") and num_cores == 0:
                parts = line.split(":", 1)
                if len(parts) == 2:
                    try:
                        num_cores = int(parts[1].strip())
                    except:
                        pass
except:
    pass
# Fallback if we didn't get cores: use processors count
if num_cores == 0:
    num_cores = num_processors

# ----- Memory (free -h) -----
mem_total = mem_avail = "N/A"
free_out = run(["free", "-h"])
if free_out:
    for line in free_out.splitlines():
        s = line.strip().lower()
        if s.startswith("mem:"):
            cols = line.split()
            # Mem: total used free shared buff/cache available
            if len(cols) >= 7:
                mem_total = cols[1]
                mem_avail = cols[6]
            break

# ----- Build report -----
def section(title):
    return title + "\n" + ("-" * len(title))

report_lines = []
report_lines.append(f"System Report - {today}\n")

report_lines.append(section("Device Information"))
report_lines.append(f"Hostname:            {hostname}")
report_lines.append(f"Domain:              {domain}\n")

report_lines.append(section("Network Information"))
report_lines.append(f"IP Address:          {ip_addr}")
report_lines.append(f"Gateway:             {gateway}")
report_lines.append(f"Network Mask:        {netmask}")
if dns_list:
    for i, dns in enumerate(dns_list[:4], start=1):
        report_lines.append(f"DNS{i}:               {dns}")
else:
    report_lines.append("DNS:                 N/A")
report_lines.append("")

report_lines.append(section("Operating System Information"))
report_lines.append(f"Operating System:    {os_name}")
report_lines.append(f"OS Version:          {os_version}")
report_lines.append(f"Kernel Version:      {kernel_version}\n")

report_lines.append(section("Storage Information"))
report_lines.append(f"System Drive Total:  {sys_total}")
report_lines.append(f"System Drive Used:   {sys_used}")
report_lines.append(f"System Drive Free:   {sys_free}\n")

report_lines.append(section("Processor Information"))
report_lines.append(f"CPU Model:           {cpu_model}")
report_lines.append(f"Number of processors:{num_processors}")
report_lines.append(f"Number of cores:     {num_cores}\n")

report_lines.append(section("Memory Information"))
report_lines.append(f"Total RAM:           {mem_total}")
report_lines.append(f"Available RAM:       {mem_avail}\n")

report = "\n".join(report_lines).rstrip() + "\n"

# ----- Output -----
print(report, end="")
try:
    log_path.write_text(report)
    print(f"[Saved to] {log_path}")
except Exception as e:
    print(f"[WARN] Could not write log file: {e}")