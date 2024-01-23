import asyncio
import concurrent.futures
import logging
import socket
import argparse
import os
from rich.progress import Progress, BarColumn
from rich import print as rprint

# Configure logging to show only errors
logging.basicConfig(level=logging.ERROR)

# Constants
TIMEOUT = 1
COMMON_PORTS = [80, 22, 135, 139, 445, 3389, 25, 3306, 5432, 5900, 6379, 27017, 1433]

# Use asyncio.Queue for thread-safe result collection
open_ports_queue = asyncio.Queue()

# Function to check if a host is valid and reachable on common ports
async def is_valid_host(host):
    try:
        addrinfo = await asyncio.to_thread(socket.getaddrinfo, host, None)
        futures = [asyncio.to_thread(socket.create_connection, (addr[0], port), timeout=TIMEOUT)
                   for addr in addrinfo for port in COMMON_PORTS]
        
        done, _ = await asyncio.wait(futures, timeout=TIMEOUT)

        reachable = any(task.result() for task in done)
        return reachable
    except (socket.gaierror, socket.timeout, ConnectionRefusedError):
        return False

# Function to scan a specific port on a host
async def scan_port(host, port):
    try:
        async with asyncio.open_connection(host, port, timeout=TIMEOUT) as connection:
            banner = await asyncio.to_thread(connection[0].recv, 1024).decode('utf-8').strip()
            if banner:
                await open_ports_queue.put((host, port, banner))
    except (socket.timeout, UnicodeDecodeError) as e:
        logging.error(f"Exception in scan_port for {host}:{port}: {e}")
    except Exception as e:
        logging.error(f"Exception in scan_port for {host}:{port}: {e}")

# Function to scan open ports for a host
async def scan_ports_for_host(host):
    if not await is_valid_host(host):
        rprint(f"[bold red]{host} is not a valid host or not reachable on common ports.[/bold red]")
        return

    try:
        total_ports = 65535
        max_workers = os.cpu_count()

        progress = Progress(
            "[progress.description]{task.description}",
            BarColumn(complete_style="cyan", finished_style="cyan"),
            "[progress.percentage]{task.percentage:>3.0f}%",
            "[progress.remaining]{task.completed}/{task.total} ports",
        )

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            loop = asyncio.get_event_loop()
            task_set = [loop.run_in_executor(executor, scan_port, host, port) for port in range(1, total_ports + 1, 100)]

            with progress:
                await asyncio.gather(*task_set)

    except KeyboardInterrupt:
        rprint("\n[bold yellow]Scan interrupted by user.[/bold yellow]")

# Main function to handle command-line arguments and initiate scanning
async def main():
    parser = argparse.ArgumentParser(description="Port scanner")
    parser.add_argument("hosts", nargs="+", help="Hosts to scan")
    args = parser.parse_args()

    hosts = args.hosts
    open_ports_results = []

    await asyncio.gather(*[scan_ports_for_host(host) for host in hosts])

    # Collect results from the queue
    while not open_ports_queue.empty():
        open_ports_results.append(open_ports_queue.get_nowait())

    # Display results for open ports grouped by host
    results_by_host = {host: results for host, results in zip(hosts, open_ports_results) if results}

    for host, results in results_by_host.items():
        rprint(f"\n[bold]Results for {host}:[/bold]\n")
        for result in results:
            rprint(f"[bold cyan]Port {result[1]} open on {result[0]}[/bold cyan]: {result[2]}")

if __name__ == "__main__":
    asyncio.run(main())
