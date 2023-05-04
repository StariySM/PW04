from threading import Thread
from time import sleep
from http import client
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import mimetypes
import pathlib
import socket
import json
from datetime import datetime


class HttpHandler(BaseHTTPRequestHandler):

    def run_client(self, data, ip='127.0.0.1', port=5000):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server = ip, port

        byte_data = json.dumps(data).encode()
        print(byte_data, type(byte_data))
        sock.sendto(byte_data, server)
        print(f'Send {data}')
        sock.close()

    def do_GET(self):

        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('index.html')
        elif pr_url.path == '/message':
            self.send_html_file('message.html')
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file('error.html', 404)

    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        print(data)
        data_parse = urllib.parse.unquote_plus(data.decode())
        print(data_parse)
        data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
        print(data_dict)
        self.run_client(data_dict)
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())


def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('', 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


def run_server(ip='127.0.0.1', port=5000):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = ip, port
    sock.bind(server)
    try:
        while True:
            data = sock.recvfrom(1024)
            time_of_data = str(datetime.now())
            print(f"в {time_of_data} прилетела {data}")
            data_for_file = {time_of_data: data[0].decode()}
            print(f"!!!!!{data_for_file}")
            with open("storage/data.json", "a") as fh:
                json.dump(data_for_file, fh)

    except KeyboardInterrupt:
        print(f'Destroy server')
    finally:
        sock.close()


if __name__ == '__main__':
    httpserver = Thread(target=run)
    httpserver.start()
    soccetserver = Thread(target=run_server)
    soccetserver.start()
