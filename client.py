import socket
import threading

sport = int(input("Enter source port number: "))
ip = input("Enter destination IP address")
dport = int(input("Enter destination port number: "))

print("Punching hole")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('0.0.0.0', sport))
sock.sendto(b'0', (ip, dport))

print("Hole punched")


def listen():
    sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock2.bind(('0.0.0.0', sport))

    while True:
        data, addr = sock2.recvfrom(1024)
        print(data.decode())


listener = threading.Thread(target=listen, daemon=True)
listener.start()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', dport))

while True:
    msg = input("> ")
    sock.sendto(msg.encode(), ("194.193.55.245", sport))

