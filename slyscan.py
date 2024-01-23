import os
import socket
import argparse
import logging
from rich.console import Console
from concurrent.futures import ThreadPoolExecutor

# Set a timeout for socket operations
TIMEOUT = 1
COMMON_PORTS = [80, 22, 135, 139, 445, 3389, 25, 3306, 5432, 5900, 6379, 27017, 1433]

# Create a single ThreadPoolExecutor instance
executor = ThreadPoolExecutor(max_workers=os.cpu_count())

# Initialize a rich console for colorful output
console = Console()

def is_valid_host(host):
    try:
        # Attempt DNS resolution
        addrinfo = socket.getaddrinfo(host, None)

        # Check if the host is reachable on at least one resolved address and port
        reachable = any(
            socket.create_connection((addr[0], port), timeout=TIMEOUT) for addr in addrinfo for port in COMMON_PORTS
        )

        return reachable
    except (socket.gaierror, socket.timeout, ConnectionRefusedError):
        return False

def scan_ports_for_host(host):
    """
    Scan all ports on a specified host using parallel execution.

    Args:
    - host (str): The target host to scan.

    Returns:
    None
    """
    open_ports = []

    # Check if the host is valid and reachable on common ports
    if not is_valid_host(host):
        console.print(f"{host} is not a valid host or not reachable on common ports.")
        return

    # Scan all ports in parallel using the shared ThreadPoolExecutor instance
    futures = [executor.submit(scan_port, host, port) for port in range(1, 65536)]

    try:
        # Collect results from parallel scans
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                open_ports.append(result)
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Scan interrupted by user.[/bold yellow]")
        executor.shutdown(wait=False)

    # Print results for the host
    if open_ports:
        console.print(f"\n[bold]Results for {host}:[/bold]\n")
        for result in open_ports:
            console.print(result)

def scan_port(host, port):
    """
    Scan a single port on a specified host.

    Args:
    - host (str): The target host to scan.
    - port (int): The port to scan on the host.

    Returns:
    - str or None: A message indicating an open port with a banner or None if the port is closed.
    """
    # Create a TCP socket for scanning a single port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(TIMEOUT)
        result = s.connect_ex((host, port))

        # Check if the port is open
        if result == 0:
            try:
                # Attempt to receive a banner from the open port
                banner = s.recv(1024).decode('utf-8').strip()
                if banner:
                    return f"Port [bold cyan]{port}[/bold cyan] open on {host}: {banner}"
            except (socket.timeout, UnicodeDecodeError) as e:
                # Log the exception for debugging
                logging.error(f"Exception in scan_port for {host}:{port}: {e}")
                return f"Port [bold cyan]{port}[/bold cyan] open on {host}: Unable to retrieve banner"
    return None

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Port scanner")
    parser.add_argument("hosts", nargs="+", help="Hosts to scan")
    args = parser.parse_args()

    hosts = args.hosts

    try:
        # Scan hosts in parallel using the shared ThreadPoolExecutor instance
        executor.map(scan_ports_for_host, hosts)
    except Exception as e:
        # Log the exception for debugging
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    # Entry point of the script
    main()
