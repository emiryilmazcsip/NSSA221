#!/usr/bin/env python3
#Emir T. Yilmaz
#October 18th, 2025
#Script 4

#Used copoilet to make comments for da script so it be easier to read.

import os # For os operations
import re # For regex operations
from datetime import datetime # For date and time
from geoip import geolite2 # For IP to country lookup

os.system("clear") # Clear the terminal screen

logfile = "/home/student/syslog.log" # Path to the log file
ip_pattern = r"(\d+\.\d+\.\d+\.\d+)" # Regex pattern to match IP addresses
attempts = {}   # Dictionary to store failed attempts per IP

with open(logfile, "r") as file: # Open the log file for reading
    for line in file: # Read each line in the log file
        if "Failed password" in line: # Look for failed password attempts
            match = re.search(ip_pattern, line) # Search for IP address in the line
            if match: # If an IP address is found
                ip = match.group(1) # Extract the IP address
                attempts[ip] = attempts.get(ip, 0) + 1 # Increment the count for this IP

print("Attacker Report") # Report title
print("Date:", datetime.now().strftime("%Y-%m-%d")) # Print current date
print("-" * 50) # Separator line
print(f"{'Count':<8}{'IP Address':<20}{'Country'}") # Table header
print("-" * 50) # Separator line

for ip, count in sorted(attempts.items(), key=lambda x: x[1]): # Sort IPs by count
    if count >= 10: # Only show IPs with 10 or more attempts
        match = geolite2.lookup(ip) # Lookup country for the IP
        country = match.country if match else "Unknown" # Get country or mark as Unknown
        print(f"{count:<8}{ip:<20}{country}") # Print the count, IP address, and country

print("-" * 50) # Separator line
print("End of Report") # End of report message