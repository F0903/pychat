import server


def main():
    msg_server = server.Server()
    msg_server.start()
    print("Server running...")
    while msg_server.is_running():
        if input() == "stop":
            msg_server.stop()
            msg_server.wait_for_shutdown()
            continue


if __name__ == "__main__":
    main()
