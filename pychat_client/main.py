import client
from package import Package, PackageContent, PackageType


def main():
    msg_client = client.Client()
    msg_client.start()

    msg_client.on_receive(lambda sender, msg: print(f"{sender}: {msg}"))
    msg_client.on_user_joined(lambda sender, user: print(
        f"{user} has joined the server."))
    msg_client.on_user_left(lambda sender, user: print(
        f"{user} has left the server."))

    print("Started client.")
    while msg_client.is_running():
        inp = input()
        if inp == "stop":
            msg_client.stop()
            msg_client.wait_for_shutdown()
            continue
        msg_client.send(Package(PackageType.USER_MSG, PackageContent(inp)))


if __name__ == "__main__":
    main()
