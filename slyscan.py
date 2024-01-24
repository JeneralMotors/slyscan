import asyncio
import argparse
from aiomultiprocess import Pool
from rich.console import Console
from rich import print

async def scan_port(args):
    host, port = args
    try:
        reader, writer = await asyncio.open_connection(host, port)
        print(f"[bold blue]Port {port}[/bold blue] on [bold cyan]{host}[/bold cyan] is [bold green]open[/bold green]")
        writer.close()
    except (OSError, asyncio.TimeoutError):
        pass

async def scan_ports(hosts, ports):
    async with Pool() as pool:
        host_port_combinations = [(host, port) for host in hosts for port in ports]
        await pool.map(scan_port, host_port_combinations)

def parse_port_range(port_range):
    start, end = map(int, port_range.split('-'))
    return range(start, end + 1)

def parse_args():
    parser = argparse.ArgumentParser(description='Asynchronous Port Scanner')
    parser.add_argument('hosts', nargs='+', help='Target hosts (space-separated)')
    parser.add_argument('--ports', type=parse_port_range, default='1-1024', help='Target ports (e.g., 80, 8080, 8000-8100)')
    return parser.parse_args()

async def main():
    args = parse_args()

    console = Console()
    with console.status("[bold magenta]Scanning in progress...[/bold magenta]"):
        await scan_ports(args.hosts, args.ports)

if __name__ == "__main__":
    asyncio.run(main())
