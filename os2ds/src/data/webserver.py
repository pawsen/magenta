#!/usr/bin/env python

import http.server
import contextlib
from multiprocessing import Manager, Process
from pathlib import Path
import os
import socket
import argparse
import sys

address = "localhost"
port = 64346
fwd = (Path(__file__).parent / "web").absolute()


def check_socket(host: str = address, port: int = port):
    "retuns 0 for open port, != 0 for not open"
    # make sure the connection is closed
    with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        return sock.connect_ex((host, port)) == 0


def run_web_server(started, host: str = address, port: int = port, path: Path = fwd):
    cwd = os.getcwd()
    try:
        os.chdir(path)
        server = http.server.HTTPServer(
            (host, port), http.server.SimpleHTTPRequestHandler
        )

        # The web server is started and listening; let the test runner know
        started.acquire()
        try:
            started.notify()
        finally:
            started.release()

        while True:
            server.handle_request()
    finally:
        os.chdir(cwd)


def start_server(host: str = address, port: int = port, path: Path = fwd):
    with Manager() as manager:

        started = manager.Condition()
        started.acquire()
        try:
            ws = Process(target=run_web_server, args=(started, host, port, path))
            ws.start()

            # Wait for the web server to check in and notify us that it's
            # ready to be used
            started.wait()

            print("ws ready")

        finally:
            started.release()
            print("ws released")
    return ws


def stop_server(ws):
    ws.terminate()
    ws.join()


help_str = "Listening on {0}:{1}, serving files from {2}"


def start_server_if_not_running(
    host: str = address, port: int = port, path: Path = fwd
):
    if not check_socket(host, port):
        ws = start_server(host, port, path)
        print(help_str.format(host, port, path))
        return ws


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        add_help=True,
        description=(
            f"This script will launch a webserver, by default "
            + help_str.format(address, port, fwd)
        ),
    )

    parser.add_argument(
        "-host",
        action="store",
        default=address,
        help=f"ip address of listening interface (default {address})",
    )
    parser.add_argument(
        "-port",
        action="store",
        default=port,
        help=f"TCP port for listening incoming connections (default {port})",
    )
    parser.add_argument(
        "-path",
        action="store",
        #default=fwd,
        help=f"path of the folder to serve files from (default {fwd})",
    )

    try:
        options = parser.parse_args()
    except Exception as e:
        print(f"Houston we have an Error, {e}")
        print(options)
        sys.exit(1)

    if options.path:
        options.path = Path(options.path).absolute()
    else:
        options.path = fwd

    start_server_if_not_running(
        host=options.host, port=int(options.port), path=options.path
    )
