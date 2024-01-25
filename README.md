#         🐍 SlyScan 🐍  

Multi-threaded   |
Multi-processed  |  Port Scanner
Multi-host       |

This Python script provides a multi-threaded port scanning tool designed to scan multiple hosts for open ports within a specified range. It utilizes concurrent programming with multiprocessing and threading to efficiently scan ports for multiple hosts.

## Dependencies

- `socket`
- `argparse`
- `multiprocessing`
- `concurrent.futures.ThreadPoolExecutor`
- `tqdm`
- `rich`

## Example Usage

```bash
$ python port_scanner.py --hosts 192.168.1.1 192.168.1.2 --ports 80 443 8080-8090
