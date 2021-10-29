import socket as net
import threading as thread
from typing import List
from package import Package, PackageContent, PackageType


class Server:
    def __init__(self, addr=net.gethostname()):
        self._addr = (addr, 6590)
        self._clients: List[net.socket] = []

    def start(self):
        self._running = True
        self._run()

    def stop(self):
        self._running = False

    def wait_for_shutdown(self):
        self._server_thread.join()

    def is_running(self) -> bool:
        return self._running

    def _send_to_all(self, package: Package, excluded: net.socket = ...):
        for client in self._clients:
            if excluded and client == excluded:
                continue
            client.send(package.to_json().encode())

    def _handle_incoming(self):
        try:
            client, client_addr = self._socket.accept()
        except BlockingIOError:
            return
        self._clients.append(client)
        package = Package(PackageType.USER_JOINED, PackageContent(client_addr))
        package.set_sender(client_addr)
        self._send_to_all(package, client)
        print(f"Accepted client {client_addr}")

    def _remove_client(self, client):
        sockname = client.getsockname()
        client.close()
        self._clients.remove(client)
        package = Package(PackageType.USER_LEFT, PackageContent(sockname))
        package.set_sender("SERVER")
        self._send_to_all(package)
        print(f"Removed client {sockname}")

    def _receive(self):
        for client in self._clients:
            try:
                data = client.recv(1024)
            except BlockingIOError:
                continue
            except ConnectionError:
                self._remove_client(client)
                continue

            if data == b'':
                self._remove_client(client)
                continue

            client_addr = client.getsockname()
            package = Package.from_json(data)
            package.set_sender(client_addr)
            self._send_to_all(package, client)
            print(f"Received message from {client_addr}")

    def _serve(self):
        self._handle_incoming()
        self._receive()

    def _run(self):
        def thread_run():
            while self._running:
                self._serve()

        sock = net.socket(
            net.AddressFamily.AF_INET, net.SocketKind.SOCK_STREAM)
        sock.bind(self._addr)
        sock.listen()
        sock.setblocking(False)
        self._socket = sock

        serv = thread.Thread(name="Server-Thread", target=thread_run)
        serv.start()
        self._server_thread = serv
