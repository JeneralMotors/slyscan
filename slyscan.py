import os
import socket
import argparse
import logging
import concurrent.futures
from rich import print as rprint

# Set the logging level to ERROR
logging.basicConfig(level=logging.ERROR)

# Set a timeout for socket operations
TIMEOUT = 1
COMMON_PORTS = [80, 22, 135, 139, 445, 3389, 25, 3306, 5432, 5900, 6379, 27017, 1433]

# Create a single ThreadPoolExecutor instance
executor = concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count())

def is_valid_host(host):
    try:
        addrinfo = socket.getaddrinfo(host, None)
        reachable = any(
            socket.create_connection((addr[0], port), timeout=TIMEOUT) for addr in addrinfo for port in COMMON_PORTS
        )
        return reachable
    except (socket.gaierror, socket.timeout, ConnectionRefusedError):
        return False

def scan_port(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(TIMEOUT)
        result = s.connect_ex((host, port))

        if result == 0:
            try:
                banner = s.recv(1024).decode('utf-8').strip()
                if banner:
                    rprint(f"[bold cyan]Port {port} open on {host}[/bold cyan]: {banner}")
            except (socket.timeout, UnicodeDecodeError) as e:
                logging.error(f"Exception in scan_port for {host}:{port}: {e}")
                rprint(f"[bold cyan]Port {port} open on {host}[/bold cyan]: Unable to retrieve banner")

def scan_ports_for_host(host):
    open_ports = []

    if not is_valid_host(host):
        rprint(f"[bold red]{host} is not a valid host or not reachable on common ports.[/bold red]")
        return

    futures = [executor.submit(scan_port, host, port) for port in range(1, 65536)]

    try:
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                open_ports.append(result)
    except KeyboardInterrupt:
        rprint("\n[bold yellow]Scan interrupted by user.[/bold yellow]")
        executor.shutdown(wait=False)

    if open_ports:
        rprint(f"\n[bold]Results for {host}:[/bold]\n")
        for result in open_ports:
            rprint(result)

def main():
    parser = argparse.ArgumentParser(description="Port scanner")
    parser.add_argument("hosts", nargs="+", help="Hosts to scan")
    args = parser.parse_args()

    hosts = args.hosts

    try:
        executor.map(scan_ports_for_host, hosts)
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
