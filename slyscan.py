import socket
import argparse
from multiprocessing import Process
from concurrent.futures import ThreadPoolExecutor

def parse_ports(ports_arg):
    ports = []
    for part in ports_arg:
        if '-' in part:
            start, end = map(int, part.split('-'))
            ports.extend(range(start, end + 1))
        else:
            ports.append(int(part))
    return ports

def scan_ports(host, ports):
    with ThreadPoolExecutor(max_workers=100) as executor:
        for port in ports:
            executor.submit(scan_port, host, port)

def scan_port(host, port):
    try:
        with socket.create_connection((host, port), timeout=1) as sock:
            print(f"Port {port} is open on {host}")
    except (socket.timeout, ConnectionRefusedError):
        pass
    except Exception as e:
        print(f"Error scanning port {port} on {host}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Multi-threaded Port Scanner")
    parser.add_argument("--hosts", nargs="+", required=True, help="Hosts to scan")
    parser.add_argument("--ports", nargs="+", required=True, help="Ports to scan (supports single ports, multiple ports, and port ranges)")
    args = parser.parse_args()

    hosts = args.hosts
    ports = parse_ports(args.ports)

    processes = []
    for host in hosts:
        p = Process(target=scan_ports, args=(host, ports))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

if __name__ == "__main__":
    main()
