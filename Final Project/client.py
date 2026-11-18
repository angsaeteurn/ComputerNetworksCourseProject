
import socket
import time
import os



SERVER_IP = "192.168.1.245"
SERVER_PORT = 4450
BUFFER_SIZE = 1024
ENCODING = "utf-8"


client_socket = None


def ConnectServer():
    global client_socket
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(60)
        client_socket.connect((SERVER_IP, SERVER_PORT))
        greeting = receive_message()  # Server sends a welcome as soon as we connect.
        print("Connected:", greeting)
        return True
    except (OSError, ConnectionError) as error:
        print("Connection failed:", error)
        if client_socket is not None:
            client_socket.close()
        client_socket = None
        return False



def receive_message():
    """Read a short text response from the teammate's server."""
    data = client_socket.recv(BUFFER_SIZE)
    if not data:
        raise ConnectionError("Server disconnected.")
    return data.decode(ENCODING)

def send_command(command):
    client_socket.sendall(command.encode(ENCODING))


def upload_file():
    path = input("Enter local file path to upload: ").strip().strip('"')
    if not os.path.isfile(path):
        print("File not found.")
        return

    name = os.path.basename(path)
    if "@" in name:
        print("File names cannot contain '@'.")
        return

    size = os.path.getsize(path)
    send_command(f"UPLOAD@{name}@{size}")
    response = receive_message()

    if response == "EXISTS":
        answer = input("File exists. Overwrite? (yes/no): ").strip().lower()
        send_command("OVERWRITE" if answer == "yes" else "CANCEL")
        response = receive_message()  # READY after overwrite, CANCELLED after cancel.

    if response != "READY":
        print("Upload not started:", response)
        return

    start = time.perf_counter()
    with open(path, "rb") as file:
        while chunk := file.read(65536):
            client_socket.sendall(chunk)

    confirmation = receive_message()
    elapsed = time.perf_counter() - start
    print(confirmation)
    if confirmation.startswith("OK@"):
        print(f"Uploaded {name} ({size:,} bytes) in {elapsed:.2f} sec")
        if elapsed > 0:
            print(f"Average speed: {size / 1_000_000 / elapsed:.2f} MB/s")


#----------------------------DOWNLOAD FILE ---------------------------------
def download_file():
    """Requires the two-line READY handshake patch in FinalServer.py (see instructions)."""
    name = input("Enter server filename to download: ").strip()
    if not name or "@" in name:
        print("Invalid filename.")
        return

    send_command(f"DOWNLOAD@{name}")
    response = receive_message()
    if not response.startswith("OK@"):
        print("Download failed:", response)
        return

    try:
        size = int(response.split("@", 1)[1])
    except ValueError:
        raise ConnectionError("Invalid size response. Check server's download handshake.")
    if size < 0:
        raise ValueError("Invalid negative file size.")

    os.makedirs("downloads", exist_ok=True)
    local_name = os.path.basename(name.replace("\\", "/"))
    destination = os.path.join("downloads", local_name)
    if os.path.exists(destination):
        overwrite = input(f"{destination} exists. Overwrite? (yes/no): ").strip().lower()
     
        if overwrite != "yes":
            send_command("CANCEL")
            print("Download cancelled.")
            return

    send_command("READY")
    received = 0
    start = time.perf_counter()
    temp = destination + ".part"
    try:
        with open(temp, "wb") as output:
            while received < size:
                chunk = client_socket.recv(min(65536, size - received))
                if not chunk:
                    raise ConnectionError("Disconnected during download.")
                output.write(chunk)
                received += len(chunk)
        os.replace(temp, destination)
    except (OSError, ConnectionError) as error:
        print("Download failed:", error)
        return

    elapsed = time.perf_counter() - start
    print(f"Saved {received:,} bytes to {destination} in {elapsed:.2f} sec")
    if elapsed > 0:
        print(f"Average speed: {received / 1_000_000 / elapsed:.2f} MB/s")

        
#--------------------------------DELETE FILE-----------------------------------------
def delete_file():
    name = input("Enter server filename to delete: ").strip()
    if not name or "@" in name:
        print("Invalid filename.")
        return
    if input(f"Delete {name}? (yes/no): ").strip().lower() != "yes":
        print("Cancelled.")
        return
    send_command(f"DELETE@{name}")
    print(receive_message())

#-----------------------DIRECTORY-------------------------------------------
 

def view_directory():
    send_command("DIR")
    print("\nSERVER DIRECTORY\n" + receive_message())


#----------------CREATE SUBFOLDER------------------------------
def create_subfolder():
    folder = input("Folder path to create: ").strip()
    if not folder or "@" in folder:
        print("Invalid folder name.")
        return
    send_command(f"SUBFOLDER@CREATE@{folder}")
    print(receive_message())

#-----------------------------DELETE SUBFOLDER------------------------------------

def delete_subfolder():
    folder = input("Folder path to delete: ").strip()
    if not folder or "@" in folder:
        print("Invalid folder name.")
        return
    if input(f"Delete folder {folder}? (yes/no): ").strip().lower() != "yes":
        print("Cancelled.")
        return
    send_command(f"SUBFOLDER@DELETE@{folder}")
    print(receive_message())


def CommandMenu(): 
    print("\n==========COMMAND MENU=============")
    print("1. Upload File")
    print("2. Download File")
    print("3. Delete File")
    print("4. Directory")
    print("5. Create Subfolder")
    print("6. Delete Subfolder")
    print("7. Exit")
#---------------------------------MAIN------------------------------------------------
def main():
    global client_socket


    if not ConnectServer():
        print("Unable to connect to server.")
        return
    try:
        while True:
            CommandMenu()
        
        
            choice = input("Enter your choice: ")

            if choice == "1":
                upload_file()

            elif choice == "2":
                download_file()

            elif choice == "3":
                delete_file()

            elif choice == "4":
                view_directory()

            elif choice == "5":
                create_subfolder()

            elif choice == "6":
                delete_subfolder()

            elif choice == "7":
                send_command("LOGOUT")
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Try again.")
        
    except (OSError, ConnectionError, ValueError) as error:
        print("Connection or operation error:", error)

    finally:
        if client_socket is not None:
            client_socket.close()
            client_socket = None


if __name__ == "__main__":
    main()



