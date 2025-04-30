import socket
import os
import time

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 12345))
    print("Connected to server")

    while True:


        data = client_socket.recv(8192)
        if not data:
            break

        print(data.decode())

        message = input("Enter your choice: ")
        client_socket.send(message.encode())

        os.system("cls")
        time.sleep(1)

    client_socket.close()

if __name__ == "__main__":
    start_client()
