import os
import socket
import argparse
import logging
import concurrent.futures
from rich.progress import Progress
from rich import print as rprint
import queue

# Set up logging to handle errors
logging.basicConfig(level=logging.ERROR)

# Constants
TIMEOUT = 1
COMMON_PORTS = [80, 22, 135, 139, 445, 3389, 25, 3306, 5432, 5900, 6379, 27017, 1433]

# Create a ThreadPoolExecutor with maximum workers based on CPU count
executor = concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count())
open_ports_queue = queue.Queue()

# Function to check if a given host is valid and reachable on common ports
def is_valid_host(host):
    try:
        addrinfo = socket.getaddrinfo(host, None)
        reachable = any(
            socket.create_connection((addr[0], port), timeout=TIMEOUT) for addr in addrinfo for port in COMMON_PORTS
        )
        return reachable
    except (socket.gaierror, socket.timeout, ConnectionRefusedError):
        return False

# Function to scan a specific port on a given host
def scan_port(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(TIMEOUT)
        result = s.connect_ex((host, port))

        if result == 0:
            try:
                banner = s.recv(1024).decode('utf-8').strip()
                if banner:
                    open_ports_queue.put((host, port, banner))
            except (socket.timeout, UnicodeDecodeError) as e:
                logging.error(f"Exception in scan_port for {host}:{port}: {e}")
                rprint(f"[bold cyan]Port {port} open on {host}[/bold cyan]: Unable to retrieve banner")

# Function to scan ports for a given host
def scan_ports_for_host(host):
    open_ports = []

    if not is_valid_host(host):
        rprint(f"[bold red]{host} is not a valid host or not reachable on common ports.[/bold red]")
        return

    # Use ThreadPoolExecutor to asynchronously scan ports for the current host
    futures = [executor.submit(scan_port, host, port) for port in range(1, 65536)]

    try:
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result is not None:  # Corrected line
                open_ports.append(result)
    except KeyboardInterrupt:
        rprint("\n[bold yellow]Scan interrupted by user.[/bold yellow]")
        executor.shutdown(wait=False)

    if open_ports:
        rprint(f"\n[bold]Results for {host}:[/bold]\n")
        for result in open_ports:
            rprint(result[2])  # Corrected line

# Main function
def main():
    parser = argparse.ArgumentParser(description="Port scanner")
    parser.add_argument("hosts", nargs="+", help="Hosts to scan")
    args = parser.parse_args()

    hosts = args.hosts

    with Progress() as progress:
        # Use ThreadPoolExecutor to concurrently scan multiple hosts
        try:
            executor.map(scan_ports_for_host, hosts)
        except Exception as e:
            logging.error(f"An error occurred: {e}")

    # Process results by grouping them by host
    results_by_host = {}
    while not open_ports_queue.empty():
        result = open_ports_queue.get()
        host = result[0]
        if host not in results_by_host:
            results_by_host[host] = []
        results_by_host[host].append(result)

    # Display results for open ports grouped by host
    for host, results in results_by_host.items():
        rprint(f"\n[bold]Results for {host}:[/bold]\n")
        for result in results:
            rprint(f"[bold cyan]Port {result[1]} open on {result[0]}[/bold cyan]: {result[2]}")

# Entry point
if __name__ == "__main__":
    main()
