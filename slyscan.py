import asyncio
import argparse
from rich.console import Console

console = Console()

def parse_ports(ports_arg):
    """
    Parse the input ports argument to extract individual ports and port ranges.

    Args:
        ports_arg (list): List of strings representing ports, port ranges, or a combination.

    Returns:
        list: List of individual ports.
    """
    ports = []
    for part in ports_arg:
        if '-' in part:
            start, end = map(int, part.split('-'))
            ports.extend(range(start, end + 1))
        else:
            ports.append(int(part))
    return ports

async def scan_port(host, port):
    """
    Scan an individual port on the given host.

    Args:
        host (str): The target host.
        port (int): The port to scan.
    """
    try:
        _, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=1)
        console.print(f"Port [green]{port}[/green] is open on {host}")
        writer.close()
        await writer.wait_closed()
    except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
        console.print(f"Port [red]{port}[/red] is closed on {host}")
    except Exception as e:
        console.print(f"Error scanning port [yellow]{port}[/yellow] on {host}: {e}")

async def scan_ports(host, ports):
    """
    Scan the specified ports on the given host using asyncio.

    Args:
        host (str): The target host to scan.
        ports (list): List of ports to scan.
    """
    tasks = [asyncio.create_task(scan_port(host, port)) for port in ports]
    await asyncio.gather(*tasks)

def main():
    """
    Main function to parse command line arguments and initiate the port scanning process.
    """
    parser = argparse.ArgumentParser(description="Asyncio Port Scanner")
    parser.add_argument("--hosts", nargs="+", required=True, help="Hosts to scan")
    parser.add_argument("--ports", nargs="+", required=True, help="Ports to scan (supports single ports, multiple ports, and port ranges)")
    args = parser.parse_args()

    hosts = args.hosts
    ports = parse_ports(args.ports)

    for host in hosts:
        asyncio.run(scan_ports(host, ports))

if __name__ == "__main__":
    main()
