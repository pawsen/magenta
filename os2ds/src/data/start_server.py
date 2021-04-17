#!/usr/bin/env python

import os
import os.path
import http.server
import contextlib
from multiprocessing import Manager, Process
import socket


here_path = os.path.dirname(__file__)
test_data_path = os.path.join(here_path, "data", "web")


__PORT = 64346

def check_socket(host='', port=__PORT):
    "retuns 0 for open port, != 0 for not open"
    # make sure the connection is closed
    with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        return sock.connect_ex((host, port)) == 0

def run_web_server(started):
    cwd = os.getcwd()
    try:
        os.chdir(test_data_path)
        server = http.server.HTTPServer(
                ('', __PORT),
                http.server.SimpleHTTPRequestHandler)

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


def start_server():
    with Manager() as manager:

        started = manager.Condition()
        started.acquire()
        try:
            ws = Process(target=run_web_server, args=(started,))
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


def start_server_if_not_running():
    if not check_socket():
        ws = start_server()
        print(f"http server started on http://127.0.0.1:{__PORT}")
        return ws

if __name__ == '__main__':
    start_server_if_not_running()
