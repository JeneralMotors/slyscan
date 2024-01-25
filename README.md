```
#          🐍 SlyScan 🐍  

Multi-threaded   |
Multi-processed  |  Port Scanner
Multi-host       |
```

This Python script provides a multi-threaded port scanning tool designed to scan multiple hosts for open ports within a specified range. It utilizes concurrent programming with multiprocessing and threading to efficiently scan ports for multiple hosts.

## Dependencies

- `socket`
- `argparse`
- `multiprocessing`
- `concurrent.futures.ThreadPoolExecutor`
- `tqdm`
- `rich`

## Features

- **Multi-threaded Scanning:** Utilizes threading to concurrently scan open ports, optimizing speed for each host.

- **Multi-processed Architecture:** Harnesses the power of multiprocessing to perform simultaneous port scans across multiple hosts, enhancing overall scanning efficiency.

- **Port Range Support:** Supports a flexible port specification, allowing scanning of single ports, multiple ports, and port ranges.

- **Dynamic Progress Tracking:** Employs a dynamic progress bar using `tqdm` for real-time visualization of scanning progress.

- **Colorful Console Output:** Utilizes the `rich` library to provide visually appealing and informative console output.

- **User-friendly Command-line Interface:** Accepts command-line arguments for specifying hosts and ports, making it easy to customize scanning parameters.

- **Robust Port Parsing:** Parses a variety of port specifications, including single ports and port ranges, ensuring flexibility in configuration.

- **Efficient Thread Pooling:** Employs a ThreadPoolExecutor for efficient distribution of port scanning tasks among threads.

- **Comprehensive Result Printing:** Displays detailed results, including open ports for each scanned host, in a clear and organized format.

- **Cross-platform Compatibility:** Designed to work seamlessly across different platforms, providing a consistent experience.

- **Manager for Shared Data:** Utilizes the `Manager` class to share data (progress and open ports) among processes, ensuring synchronized and accurate results.

## Example Usage

```bash
$ python port_scanner.py --hosts 192.168.1.1 192.168.1.2 --ports 80 443 8080-8090
