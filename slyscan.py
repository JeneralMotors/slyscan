import socket
import argparse
from multiprocessing import Process, Manager
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from rich.console import Console

console = Console()

def parse_ports(ports_arg):
    ports = []
    for part in ports_arg:
        if '-' in part:
            start, end = map(int, part.split('-'))
            ports.extend(range(start, end + 1))
        else:
            ports.append(int(part))
    return ports

def scan_ports(host, ports, progress_dict, open_ports_dict, host_count, update_interval=1700):
    open_ports = []

    with ThreadPoolExecutor(max_workers=100) as executor:
        progress_bar = tqdm(total=len(ports), position=progress_dict[host], desc=f"Scanning {host} ({progress_dict[host]+1}/{host_count})", leave=False)

        futures = [executor.submit(scan_port, host, port) for port in ports]

        for i, future in enumerate(futures):
            result = future.result()
            if result:  
                open_ports.append(result)
            if i % update_interval == 0:
                progress_bar.update(update_interval)

        remaining = len(ports) % update_interval
        if remaining:   
            progress_bar.update(remaining)

        progress_bar.close()

    open_ports_dict[host] = open_ports

def scan_port(host, port):
    try:
        with socket.create_connection((host, port), timeout=1):
            return port
    except (socket.timeout, ConnectionRefusedError):
        return None
    except Exception as e:
        return str(e)

def print_open_ports(host, open_ports):
    if open_ports:
        console.print(f"\n[bold green]Open ports[/bold green] on [bold magenta]{host}[/bold magenta]: [bold green]{', '.join(map(str, open_ports))}[/bold green]")
    else:
        console.print(f"[bold red]No open ports found[/bold red] on [bold magenta]{host}[/bold magenta]")

def main():
    parser = argparse.ArgumentParser(description="Multi-threaded Port Scanner")
    parser.add_argument("--hosts", nargs="+", required=True, help="Hosts to scan")
    parser.add_argument("--ports", nargs="+", required=True, help="Ports to scan (supports single ports, multiple ports, and port ranges)")
    args = parser.parse_args()

    hosts = args.hosts
    ports = parse_ports(args.ports)

    # Use Manager to share progress_dict and open_ports_dict among processes
    with Manager() as manager:
        progress_dict = manager.dict({host: i for i, host in enumerate(hosts)})
        open_ports_dict = manager.dict()

        processes = []
        for host in hosts:
            p = Process(target=scan_ports, args=(host, ports, progress_dict, open_ports_dict, len(hosts)))
            p.start()
            processes.append(p)

        for p in processes:
            p.join()

        # Print results once all hosts have finished scanning
        for host in hosts:
            open_ports = open_ports_dict[host]
            print_open_ports(host, open_ports)

if __name__ == "__main__":
    main()
