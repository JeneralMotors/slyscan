import socket
import sys
from rich.console import Console
from concurrent.futures import ThreadPoolExecutor

# Set a timeout for socket operations
TIMEOUT = 1

def scan_port(host, port):
    """
    Scan a single port on a specified host.

    Args:
    - host (str): The target host to scan.
    - port (int): The port to scan on the host.

    Returns:
    - str or None: A message indicating an open port with a banner or None if the port is closed.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(TIMEOUT)
        result = s.connect_ex((host, port))

        if result == 0:
            try:
                banner = s.recv(1024).decode('utf-8').strip()
                if banner:
                    return f"Port [bold cyan]{port}[/bold cyan] open on {host}: {banner}"
            except (socket.timeout, UnicodeDecodeError):
                return f"Port [bold cyan]{port}[/bold cyan] open on {host}: Unable to retrieve banner"
    return None

def scan_ports(host, port_range):
    """
    Scan multiple ports on a specified host using parallel execution.

    Args:
    - host (str): The target host to scan.
    - port_range (range): The range of ports to scan on the host.

    Returns:
    None
    """
    console = Console()
    open_ports = []

    with ThreadPoolExecutor() as executor:
        # Scan ports in parallel using ThreadPoolExecutor
        futures = [executor.submit(scan_port, host, port) for port in port_range]

        # Collect results from parallel scans
        for future in futures:
            result = future.result()
            if result:
                open_ports.append(result)

    # Print results for the host
    if open_ports:
        console.print(f"\n[bold]Results for {host}:[/bold]\n")
        for result in open_ports:
            console.print(result)

if __name__ == "__main__":
    # Get hosts from command line arguments
    hosts = sys.argv[1:]
    # Define the range of ports to scan
    port_range = range(1, 65536)

    with ThreadPoolExecutor() as executor:
        # Scan hosts in parallel using ThreadPoolExecutor
        executor.map(scan_ports, hosts, [port_range] * len(hosts))
