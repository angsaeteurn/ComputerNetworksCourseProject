
import os
import socket
import threading
import time

IP = "192.168.1.245"
PORT = 4450
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
SERVER_PATH = "server"

os.makedirs(SERVER_PATH, exist_ok=True)


def get_path(filename):
    path = os.path.abspath(os.path.join(SERVER_PATH, filename))
    root = os.path.abspath(SERVER_PATH)

    if os.path.commonpath([root, path]) != root:
        return None

    return path


def receive_file(conn, filename, file_size):

    path = get_path(filename)

    if path is None:
        conn.sendall("ERROR@Invalid filename".encode(FORMAT))
        return

    received = 0
    start = time.perf_counter()

    try:
        with open(path, "wb") as file:

            while received < file_size:

                chunk = conn.recv(min(SIZE, file_size - received))

                if not chunk:
                    raise ConnectionError("Upload interrupted")

                file.write(chunk)
                received += len(chunk)

    except Exception:
        if os.path.exists(path):
            os.remove(path)
        raise

    end = time.perf_counter()

    transfer_time = end - start
    speed = (file_size / (1024 * 1024)) / transfer_time if transfer_time > 0 else 0

    print(f"Uploaded: {filename}")
    print(f"Time: {transfer_time:.2f} seconds")
    print(f"Speed: {speed:.2f} MB/s")

    conn.sendall("OK@Upload complete".encode(FORMAT))


def send_file(conn, filename):

    path = get_path(filename)

    if path is None or not os.path.isfile(path):
        conn.sendall("ERROR@File does not exist".encode(FORMAT))
        return

    file_size = os.path.getsize(path)

    conn.sendall(f"OK@{file_size}".encode(FORMAT))

    start = time.perf_counter()

    with open(path, "rb") as file:

        while True:

            chunk = file.read(SIZE)

            if not chunk:
                break

            conn.sendall(chunk)

    end = time.perf_counter()

    transfer_time = end - start
    speed = (file_size / (1024 * 1024)) / transfer_time if transfer_time > 0 else 0

    print(f"Downloaded: {filename}")
    print(f"Time: {transfer_time:.2f} seconds")
    print(f"Speed: {speed:.2f} MB/s")


### to handle the clients
def handle_client(conn, addr):

    print(f"[NEW CONNECTION] {addr} connected.")
    conn.sendall("OK@Welcome to the server".encode(FORMAT))

    while True:
        try:
            received_data = conn.recv(SIZE)

            if not received_data:
                break

            data = received_data.decode(FORMAT).split("@")
            cmd = data[0]

            send_data = "OK@"

            if cmd == "LOGOUT":
                break

            elif cmd == "TASK":
                send_data += "LOGOUT from the server.\n"
                conn.sendall(send_data.encode(FORMAT))

            elif cmd == "UPLOAD":

                filename = data[1]
                file_size = int(data[2])
                path = get_path(filename)

                if path is None:
                    conn.sendall("ERROR@Invalid filename".encode(FORMAT))
                    continue

                if os.path.exists(path):

                    conn.sendall("EXISTS".encode(FORMAT))

                    answer = conn.recv(SIZE).decode(FORMAT)

                    if answer != "OVERWRITE":
                        conn.sendall("CANCELLED".encode(FORMAT))
                        continue

                conn.sendall("READY".encode(FORMAT))
                receive_file(conn, filename, file_size)

            elif cmd == "DOWNLOAD":

                filename = data[1]
                send_file(conn, filename)

            elif cmd == "DELETE":

                filename = data[1]
                path = get_path(filename)

                if path and os.path.isfile(path):
                    os.remove(path)
                    send_data += "File deleted successfully"
                else:
                    send_data = "ERROR@File does not exist"

                conn.sendall(send_data.encode(FORMAT))

            elif cmd == "DIR":

                files = os.listdir(SERVER_PATH)
                send_data += "\n".join(files)
                conn.sendall(send_data.encode(FORMAT))

            elif cmd == "SUBFOLDER":

                action = data[1]
                folder = data[2]
                path = get_path(folder)

                if path is None:
                    conn.sendall("ERROR@Invalid folder path".encode(FORMAT))
                    continue

                if action == "CREATE":
                    os.makedirs(path, exist_ok=True)
                    send_data += "Folder created"

                elif action == "DELETE":

                    if os.path.isdir(path):
                        os.rmdir(path)
                        send_data += "Folder deleted"
                    else:
                        send_data = "ERROR@Folder does not exist"

                else:
                    send_data = "ERROR@Invalid folder action"

                conn.sendall(send_data.encode(FORMAT))

        except Exception as e:
            print(f"[ERROR] {addr}: {e}")
            break

    print(f"{addr} disconnected")
    conn.close()


def main():
    print("Starting the server")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()

    print(f"Server is listening on {IP}: {PORT}")

    while True:
        conn, addr = server.accept()

        thread = threading.Thread(
            target=handle_client,
            args=(conn, addr)
        )

        thread.start()


if __name__ == "__main__":
    main()
