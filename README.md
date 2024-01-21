# Slyscan

Slyscan is a Python tool for parallelized port scanning using threading, providing information about open ports and banners on specified hosts.

## Features

- Multi-threaded port scanning for multiple hosts simultaneously
- Retrieves banners for open ports (if available)
- Utilizes the `concurrent.futures.ThreadPoolExecutor` for efficient parallelization

## Requirements

- Python 3.x
- Install dependencies using `pip install -r requirements.txt`

## Usage

```bash
python slyscan.py host1 host2 ... hostN
