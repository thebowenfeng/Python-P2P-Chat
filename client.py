import socket
import threading

sport = int(input("Enter source port number: "))
ip = input("Enter destination IP address")
dport = int(input("Enter destination port number: "))
listen = input("Listen? (y/n)")

print('punching hole')

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', sport))
sock.sendto(b'0', (ip, dport))
sock.close()

print('ready to exchange messages\n')

# listen for
# equiv: nc -u -l 50001
def listen():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', sport))

    while True:
        data = sock.recv(1024)
        print('\rpeer: {}\n> '.format(data.decode()), end='')


if listen == 'y':
    listener = threading.Thread(target=listen, daemon=True);
    listener.start()
else:
    # send messages
    # equiv: echo 'xxx' | nc -u -p 50002 x.x.x.x 50001
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', dport))
    
    while True:
        msg = input('> ')
        sock.sendto(msg.encode(), (ip, sport))

