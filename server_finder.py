#!/usr/bin/env python3
"""
Minecraft Server Finder for Maltese IP ranges
This script scans IP ranges associated with Malta and identifies active Minecraft servers.
"""

import ipaddress
import socket
import time
import json
import os
import datetime
import random
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from mcstatus import JavaServer
from colorama import init, Fore, Style

# Init colorama
init()

# Try to import nmap make it optional
NMAP_AVAILABLE = False
try:
    import nmap
    NMAP_AVAILABLE = True
except ImportError:
    pass

# Optional - Path to nmap executable if not in PATH
NMAP_PATH = r"C:\Program Files (x86)\Nmap\nmap.exe"  # Common Windows location
# NMAP_PATH = "/usr/bin/nmap"  # Common Unix/Linux location

# Configuration - Complete list of Maltese IP ranges
MALTA_IP_RANGES = [
       "46.11.0.0/16",      # Melita Limited
    "77.243.128.0/20",   # Melita Limited
    "80.71.112.0/20",    # GO p.l.c.
    "80.77.160.0/20",    # GO p.l.c.
    "78.110.48.0/20",    # Vodafone Malta
    "85.232.192.0/19",   # Melita Limited
    "185.144.116.0/22",  # Ozone Malta
    "194.158.64.0/19",   # GO p.l.c.
    "213.217.128.0/20",  # Melita Limited

    # Additional Maltese ranges
   
    "37.114.168.0/21",   # Epic Malta
    "62.173.32.0/19",    # Melita Limited
    "83.142.248.0/21",   # GO p.l.c.
    "85.119.128.0/19",   # Epic Malta
    "91.198.127.0/24",   # University of Malta
    "94.138.224.0/19",   # GO p.l.c.
    "159.20.0.0/16",     # Malta Government ranges
    "195.234.240.0/22",  # Malta Information Technology Agency
    "212.56.128.0/19",   # Epic Malta
    "217.22.176.0/20",   # GO p.l.c.
    "195.158.96.0/19",   # Vodafone Malta

    # Newly identified Maltese IP ranges
    "2.59.131.0/24",     # Vanilla Telecoms Ltd.
    "5.62.86.0/24",      # Vanilla Telecoms Ltd.
    "5.180.27.0/24",     # Vanilla Telecoms Ltd.
    "37.75.32.0/19",     # Epic Malta
    "37.77.175.0/24",    # Epic Malta
    "37.114.72.0/21",    # Epic Malta
    "37.233.120.0/21",   # Epic Malta
    "38.108.97.0/24",    # Epic Malta
    "66.212.239.0/24",   # Epic Malta
    "66.212.244.0/24",   # Epic Malta
    "69.6.32.0/19",      # Epic Malta
    "74.85.218.0/24",    # Epic Malta
    "77.25.128.0/17",    # Epic Malta
    "77.71.128.0/17",    # Epic Malta
    "77.81.118.0/24",    # Epic Malta
    "77.243.64.0/20",    # Melita Limited
    "78.110.16.0/20",    # Vodafone Malta NOTE - VODAFONE ISNTIN MALTA ANYMORE 
    "78.110.0.0/20",     # Vodafone Malta (fixed from 78.110.20.0/20)
    "78.110.31.0/24",    # Vodafone Malta
    "78.133.0.0/17",     # Vodafone Malta
    "79.135.109.0/24",   # Vodafone Malta
    "79.135.111.0/24",   # Vodafone Malta

]

# Default Minecraft port
DEFAULT_MC_PORT = 25565

# Output dir for reports
OUTPUT_DIR = "discovered_servers"

# Scan settings
THREADS = 200  # Increased for faster scanning
TIMEOUT = 1.5  #  faster timeout
SCAN_LIMIT = None  # NO LIMIT - scan all IPs
USE_NMAP = True  # Set to False to disable nmap functionality even if available

#  scanning settings
CONTINUOUS_SCANNING = True  # Set to True to enable continuous scanning
SCAN_INTERVAL = 3600  # Time in seconds between scans (default: 1 hour)
RANDOMIZE_IPS = True  # Randomize IP order for each scan
MAX_SCAN_COUNT = None  # Set to None for unlimited scans or a number to limit

ADDITIONAL_PORTS = [25565, 25566, 25567, 25575]  # Default is 25565, added some common alternatives
AGGRESSIVE_SCAN = False  # Set to True to check all additional ports for every IP (significantly increases scan time)


class MinecraftServerFinder:
    # the class muahahuaHUAHUHAUAUHHUAHUAHA

    def __init__(self):
        # Initialize the Minecraft server finder
        self.discovered_servers = []
        self.scan_count = 0
        self.known_servers = set()  # Track servers that were found
        self.create_output_directory()
        
        # Init nmap scanner if available
        self.nmap_enabled = NMAP_AVAILABLE and USE_NMAP
        self.nm = None
        
        if self.nmap_enabled:
            try:
                # Use provided nmap if exists
                if NMAP_PATH and os.path.exists(NMAP_PATH):
                    self.nm = nmap.PortScanner(nmap_search_path=[NMAP_PATH])
                    print(f"{Fore.GREEN}Using nmap from specified path: {NMAP_PATH}{Style.RESET_ALL}")
                else:
                    self.nm = nmap.PortScanner()
                
                # Test nmap 
                self.nm.scan('127.0.0.1', arguments='-sP')
            except Exception as e:
                print(f"{Fore.YELLOW}Warning: nmap is installed but the executable was not found.{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Error details: {str(e)}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Continuing without nmap enhanced scanning.{Style.RESET_ALL}")
                self.nmap_enabled = False
                
        # Calculate IP space
        self.total_maltese_ips = 0
        for ip_range in MALTA_IP_RANGES:
            network = ipaddress.ip_network(ip_range)
            self.total_maltese_ips += network.num_addresses - 2  # removed network n broadcast addresses
            
        print(f"{Fore.CYAN}Loaded {len(MALTA_IP_RANGES)} Maltese IP ranges with approximately {self.total_maltese_ips:,} addresses{Style.RESET_ALL}")

    def create_output_directory(self):
        ## output dir creation
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
        print(f"{Fore.GREEN}Output directory created at {os.path.abspath(OUTPUT_DIR)}{Style.RESET_ALL}")

    def get_maltese_ips(self):
        # Generate random ip adresses that are in maltas ranges
        all_ips = []
        for ip_range in MALTA_IP_RANGES:
            network = ipaddress.ip_network(ip_range)
            all_ips.extend([str(ip) for ip in network.hosts()])
        
        print(f"{Fore.YELLOW}Generated {len(all_ips):,} Maltese IP addresses for scanning{Style.RESET_ALL}")
        
        # Randomize the order of IPs if requested
        if RANDOMIZE_IPS:
            random.shuffle(all_ips)
                
        return all_ips

    def check_minecraft_server(self, ip):
        # check if an IP is running minecraft
        ports_to_check = [DEFAULT_MC_PORT]
        
        if AGGRESSIVE_SCAN:
            ports_to_check = ADDITIONAL_PORTS
            
        for port in ports_to_check:
            try:
                # First do a check if port is open
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(TIMEOUT)
                result = sock.connect_ex((ip, port))
                sock.close()
                
                if result != 0:
                    continue
                    
                # Use mcstatus for server info
                server = JavaServer(ip, port)
                status = server.status()
                
                # If we got here its a Minecraft server
                server_info = {
                    "ip": ip,
                    "port": port,
                    "version": status.version.name,
                    "protocol": status.version.protocol,
                    "players_online": status.players.online,
                    "players_max": status.players.max,
                    "description": status.description,
                    "ping_ms": status.latency,
                    "discovery_time": datetime.datetime.now().isoformat()
                }
                
                #  more details with nmap if available
                if self.nmap_enabled and self.nm:
                    try:
                        self.nm.scan(ip, str(port), arguments="-sV -Pn --script minecraft-info -T4")
                        if ip in self.nm.all_hosts():
                            if str(port) in self.nm[ip]['tcp']:
                                server_info["nmap_info"] = self.nm[ip]['tcp'][port]
                    except Exception:
                       
                        pass
                    
                return server_info
            except Exception:
                # Failed for this port; try next 
                continue
                
        return None  # No Minecraft server found on any port

    def save_server_info(self, server_info):
        # Save details in JSON file
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{OUTPUT_DIR}/minecraft_server_{server_info['ip']}_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(server_info, f, indent=4)
        
        print(f"{Fore.CYAN}Server information saved to {filename}{Style.RESET_ALL}")

    def display_server_info(self, server_info, is_new=True):
        # display if discovered a server
        status = "NEW" if is_new else "KNOWN"
        print(f"\n{Fore.GREEN}=== MINECRAFT SERVER {status} ==={Style.RESET_ALL}")
        print(f"{Fore.YELLOW}IP:{Style.RESET_ALL} {server_info['ip']}:{server_info['port']}")
        print(f"{Fore.YELLOW}Version:{Style.RESET_ALL} {server_info['version']} (Protocol: {server_info['protocol']})")
        print(f"{Fore.YELLOW}Players:{Style.RESET_ALL} {server_info['players_online']}/{server_info['players_max']}")
        print(f"{Fore.YELLOW}Description:{Style.RESET_ALL} {server_info['description']}")
        print(f"{Fore.YELLOW}Ping:{Style.RESET_ALL} {server_info['ping_ms']}ms")
        print(f"{Fore.GREEN}============================={Style.RESET_ALL}")

    def scan_ip(self, ip):
        # scan single ip and check if its a minecraft server
        server_info = self.check_minecraft_server(ip)
        if server_info:
            server_key = f"{server_info['ip']}:{server_info['port']}"
            is_new = server_key not in self.known_servers
            
            self.discovered_servers.append(server_info)
            self.display_server_info(server_info, is_new)
            
            # Save detailed info for new servers 
            if is_new:
                self.save_server_info(server_info)
                self.known_servers.add(server_key)
                
        return server_info

    def run_single_scan(self):
        # run a scan cycle for every ip range
        self.discovered_servers = []  # Reset for scan cycle
        
        print(f"{Fore.BLUE}Minecraft Server Seeker - Malta Edition{Style.RESET_ALL}")
        print(f"{Fore.BLUE}====================================={Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Scan #{self.scan_count + 1} - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}")
        
        # Display nmap status
        if not NMAP_AVAILABLE:
            print(f"{Fore.YELLOW}nmap is not installed. Running with basic scanning only.{Style.RESET_ALL}")
        elif not self.nmap_enabled:
            print(f"{Fore.YELLOW}nmap is disabled or not functioning. Running with basic scanning only.{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}nmap is enabled for enhanced scanning.{Style.RESET_ALL}")
        
        print(f"{Fore.YELLOW}Generating list of Maltese IP addresses...{Style.RESET_ALL}")
        ips = self.get_maltese_ips()
        total_ips = len(ips)
        
        print(f"{Fore.GREEN}Scanning ALL {total_ips:,} Maltese IPs with NO LIMIT.{Style.RESET_ALL}")
        if AGGRESSIVE_SCAN:
            print(f"{Fore.YELLOW}AGGRESSIVE MODE: Checking ports {', '.join(map(str, ADDITIONAL_PORTS))} on each IP{Style.RESET_ALL}")
        
        print(f"{Fore.YELLOW}Starting scan of {total_ips:,} Maltese IPs...{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Using {THREADS} threads with {TIMEOUT}s timeout{Style.RESET_ALL}")
        
        # Estimate scan time
        estimated_time = (total_ips * TIMEOUT / THREADS) / 60
        print(f"{Fore.CYAN}Estimated scan time: {estimated_time:.1f} minutes{Style.RESET_ALL}")
        
        # Show a countdown before starting
        for i in range(3, 0, -1):
            print(f"{Fore.RED}Starting in {i}...{Style.RESET_ALL}")
            time.sleep(1)
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=THREADS) as executor:
            list(tqdm(executor.map(self.scan_ip, ips), total=total_ips, desc="Scanning IP addresses"))
        
        end_time = time.time()
        scan_duration = end_time - start_time
        
        print(f"\n{Fore.GREEN}Scan #{self.scan_count + 1} completed in {scan_duration:.2f} seconds{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Scanned {total_ips:,} IPs at {total_ips/scan_duration:.1f} IPs/second{Style.RESET_ALL}")
        new_servers = sum(1 for s in self.discovered_servers if f"{s['ip']}:{s['port']}" not in self.known_servers)
        print(f"{Fore.GREEN}Found {len(self.discovered_servers)} Minecraft servers ({new_servers} new) in Maltese IP ranges{Style.RESET_ALL}")
        
        # Final report
        if self.discovered_servers:
            self.generate_report()
        else:
            print(f"{Fore.YELLOW}No Minecraft servers found in the scanned IP ranges.{Style.RESET_ALL}")
            
        self.scan_count += 1

    def run_continuous(self):
        # keep running scan
        print(f"{Fore.BLUE}Starting Minecraft Server Seeker in continuous mode{Style.RESET_ALL}")
        print(f"{Fore.BLUE}Scans will run every {SCAN_INTERVAL} seconds{Style.RESET_ALL}")
        
        try:
            while True:
                # Check if didnt reach IP Limit
                if MAX_SCAN_COUNT is not None and self.scan_count >= MAX_SCAN_COUNT:
                    print(f"{Fore.YELLOW}Reached maximum scan count ({MAX_SCAN_COUNT}). Exiting.{Style.RESET_ALL}")
                    break
                
                # Run a scan cycle
                self.run_single_scan()
                
                # Wait for the next scan if didnt reach IP Limit
                if MAX_SCAN_COUNT is None or self.scan_count < MAX_SCAN_COUNT:
                    next_scan_time = datetime.datetime.now() + datetime.timedelta(seconds=SCAN_INTERVAL)
                    print(f"{Fore.CYAN}Next scan will start at {next_scan_time.strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}Press Ctrl+C to exit{Style.RESET_ALL}")
                    time.sleep(SCAN_INTERVAL)
        except KeyboardInterrupt:
            print(f"\n{Fore.RED}Continuous scanning interrupted by user{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Total scans performed: {self.scan_count}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Total unique servers found: {len(self.known_servers)}{Style.RESET_ALL}")

    def generate_report(self):
        #Generate a summary report of all discovered servers
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"{OUTPUT_DIR}/scan_report_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump({
                "scan_time": timestamp,
                "scan_number": self.scan_count + 1,
                "total_servers_found": len(self.discovered_servers),
                "total_unique_servers": len(self.known_servers),
                "servers": self.discovered_servers
            }, f, indent=4)
        
        print(f"{Fore.GREEN}Summary report saved to {report_file}{Style.RESET_ALL}")


def main():
    # main function to start  server finder
    try:
        finder = MinecraftServerFinder()
        
        if CONTINUOUS_SCANNING:
            finder.run_continuous()
        else:
            finder.run_single_scan()
            
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Scan interrupted by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")


if __name__ == "__main__":
    main()