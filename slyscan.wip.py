import argparse
import asyncio
import multiprocessing
import socket
from typing import List, Union

from rich import print
from rich.console import Console

def parse_port_range(port_range: str) -> List[int]:
    """Parse a comma-separated list or range of ports into a sorted list of integers.

    Args:
        port_range (str): Comma-separated list or range of ports.

    Returns:
        List[int]: Sorted list of integers representing the ports.
    """
    ports = set()
    for part in port_range.split(","):
        if "-" in part:
            start, end = map(int, part.split("-"))
            ports.update(range(start, end + 1))
        else:
            ports.add(int(part))
    return sorted(ports)

async def scan_port(host: str, port: int, print_lock: asyncio.Lock) -> None:
    """Try to connect to a host and port and print the result.

    Args:
        host (str): Host to scan.
        port (int): Port to scan.
        print_lock (asyncio.Lock): Lock for synchronized console output.
    """
    try:
        with socket.create_connection((host, port), timeout=1):
            async with print_lock:
                print(
                    f"[bold blue]Port {port}[/bold blue] on [bold cyan]{host}[/bold cyan] is [bold green]open[/bold green]"
                )
    except (socket.error, socket.timeout):
        pass

async def scan_host_async(host: str, ports: List[int], print_lock: asyncio.Lock) -> None:
    """Scan a host for open ports using asynchronous tasks.

    Args:
        host (str): Host to scan.
        ports (List[int]): List of ports to scan.
        print_lock (asyncio.Lock): Lock for synchronized console output.
    """
    tasks = [scan_port(host, port, print_lock) for port in ports]
    await asyncio.gather(*tasks)

def scan_host_multiprocess(host: str, ports: List[int], print_lock: asyncio.Lock) -> None:
    """Scan a host for open ports using a separate process.

    Args:
        host (str): Host to scan.
        ports (List[int]): List of ports to scan.
        print_lock (asyncio.Lock): Lock for synchronized console output.
    """
    loop = asyncio.get_event_loop()
    loop.run_until_complete(scan_host_async(host, ports, print_lock))

def main() -> None:
    """Parse the arguments and scan the hosts for open ports."""
    parser = argparse.ArgumentParser(description="Port scanner")
    parser.add_argument(
        "--hosts", type=str, nargs="+", help="List of hosts to scan", required=True
    )
    parser.add_argument(
        "--ports", type=str, help="Comma-separated list or range of ports to scan", required=True
    )
    args = parser.parse_args()

    hosts = args.hosts
    port_range = args.ports

    ports = parse_port_range(port_range)

    print_lock = asyncio.Lock()

    console = Console()
    with console.status("[bold magenta]Scanning in progress...[/bold magenta]"):
        processes = [
            multiprocessing.Process(
                target=scan_host_multiprocess, args=(host, ports, print_lock)
            )
            for host in hosts
        ]
        for process in processes:
            process.start()
        for process in processes:
            process.join()

if __name__ == "__main__":
    main()
