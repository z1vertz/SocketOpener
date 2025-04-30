import socket
import psutil
import os
import subprocess

def get_drives():
    partitions = psutil.disk_partitions()
    return [partition.device for partition in partitions]

def handle_client(conn):
    while True:
        path = None
        drives = get_drives()
        while True:
            dct = {}
            response = ""

            for i in range(1, len(drives) + 1):
                dct.setdefault(str(i), drives[i - 1])

            response += '\n'.join([f'{i}: {dct[i]}' for i in dct]) + '\n'

            conn.send(response.encode())

            data = conn.recv(8192)
            if not data:
                break
            changes = data.decode().strip()

            if changes in [z for z in dct]:
                if path is None:
                    path = dct[changes]
                else:
                    path = os.path.join(path, dct[changes])
                if os.path.isdir(path):
                    try:
                        drives = os.listdir(path)
                    except PermissionError:
                        conn.send("Access Denied\n".encode())
                        path = None
                        continue
                else:
                    try:
                        subprocess.Popen([path], shell=True)
                        conn.sendall(f"Running file: {path}\n".encode())
                        path = path.split("\\")[0]+ "\\"
                    except Exception as e:
                        conn.sendall(f"Failed to run file: {e}\n".encode())
                        path = path.split("\\")[0]+ "\\"
                    finally:
                        drives = os.listdir(path)
            elif changes.startswith("!"):
                if changes[1:] == "cancel":
                    conn.send("Operation cancelled.\n".encode())
                    drives = get_drives()
                elif changes[1] == "b":
                    dirs = path.split("\\")
                    steps_back = int(changes[2:])
                    if len(dirs) > 2 and changes[2:].isdigit():
                        if steps_back < len(dirs):
                            path = "\\".join(dirs[:-steps_back])
                            drives = os.listdir(path)
                        else:
                            conn.send("Too many steps back.\n".encode())
                    elif len(dirs) == 2 and steps_back >= 1:
                        break
                    elif len(dirs) < steps_back:
                        break
                    else:
                        conn.send("No more steps back.\n".encode())
                elif changes[1:] == "path":
                    conn.send(f"Current path: {path}\n".encode())
            else:
                conn.send("Invalid input.\n".encode())


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 12345))
    server_socket.listen(1)
    print("Server started and waiting for connection...")

    conn, addr = server_socket.accept()
    print(f"Client connected from {addr}")

    try:
        handle_client(conn)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()
        print(f"Client {addr} disconnected")


if __name__ == "__main__":
    start_server()
