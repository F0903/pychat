import socket as net
import threading as thread
from typing import Any, Callable
from package import Package, PackageType


class ClientException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class ClientNotRunningException(ClientException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class Client:
    def __init__(self, server_addr=net.gethostname()):
        self._server_addr = (server_addr, 6590)
        self._on_receive: Callable[[str, str], Any] = []
        self._on_user_joined: Callable[[str, str], Any] = []
        self._on_user_left: Callable[[str, str], Any] = []

    def start(self):
        self._running = True
        self._run()

    def stop(self):
        self._running = False

    def wait_for_shutdown(self):
        self._receive_thread.join()

    def is_running(self):
        return self._running

    def on_receive(self, callback: Callable[[str, str], Any]):
        self._on_receive.append(callback)

    def on_user_joined(self, callback: Callable[[str, str], Any]):
        self._on_user_joined.append(callback)

    def on_user_left(self, callback: Callable[[str, str], Any]):
        self._on_user_left.append(callback)

    def send(self, package: Package):
        if not self.is_running():
            raise ClientNotRunningException()
        self._sock.send(package.to_json().encode())

    def _handle_package(self, package: Package):
        p_type = package.get_type()
        match p_type:
            case PackageType.USER_MSG:
                for f in self._on_receive:
                    f(package.get_sender(), package.get_content().get_msg())
            case PackageType.USER_JOINED:
                for f in self._on_user_joined:
                    f(package.get_sender(), package.get_content().get_msg())
            case PackageType.USER_LEFT:
                for f in self._on_user_left:
                    f(package.get_sender(), package.get_content().get_msg())

    def _receive(self):
        while self._running:
            try:
                data = self._sock.recv(1024)
            except BlockingIOError:
                continue
            except ConnectionError:
                print("Connection error with the server occurred. Shutting down...")
                self.stop()
                return

            if data == b'':
                print("ERR: server sent empty data")
                continue

            package = Package.from_json(data)
            self._handle_package(package)

    def _run(self):
        sock = net.socket(net.AddressFamily.AF_INET,
                          net.SocketKind.SOCK_STREAM)
        sock.connect(self._server_addr)
        sock.setblocking(False)
        self._sock = sock

        self._running = True
        rec_thread = thread.Thread(name="Receive-Thread", target=self._receive)
        rec_thread.start()
        self._receive_thread = rec_thread
