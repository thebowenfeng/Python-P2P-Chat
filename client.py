import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import requests
import threading
import socket

cred = credentials.Certificate('silence-79c33-firebase-adminsdk-dljcm-533b274b1c.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

PUBLIC_IP = requests.get('https://api.ipify.org').text


def listen(port, sender_ip):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', port))

    while True:
        data = sock.recv(1024)
        print(f"Received data from {sender_ip}: {data}")


def offer_listen(snapshot, changes, read_time):
    for change in changes:
        if change.type.name == "ADDED" and 'offer' in change.document.to_dict():
            data = change.document.to_dict()['offer']
            if data['receiver_ip'] == PUBLIC_IP:
                print(f"Connection offer received from {data['sender_ip']}. Port to be punched: {data['punch_port']}")
                listening_port = int(input("Enter port to listen to: "))

                print("Initiating port punching...")

                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.bind(('0.0.0.0', listening_port))
                sock.sendto(b'punch', (data['sender_ip'], data['punch_port']))
                sock.close()

                print("Punching complete. Initiating listener...")
                listen_thread = threading.Thread(target=listen, args=(listening_port, data['sender_ip']))
                listen_thread.start()

                print("Sending answer...")
                answer = {
                    'listening_port': listening_port
                }
                db.collection(u'offers').document(change.document.id).update({"answer": answer})


receive_answer = threading.Event()
receiver_listen_port = None


def answer_listen(snapshot, changes, read_time):
    global receiver_listen_port

    for change in changes:
        if change.type.name == "MODIFIED" and 'answer' in change.document.to_dict():
            data = change.document.to_dict["answer"]
            receiver_listen_port = data['listening_port']
            receive_answer.set()


def main_thread():
    db.collection(u'offers').on_snapshot(offer_listen)
    print("Listening to offers...")

    while True:
        receiver_ip = input("Enter IP: ")
        punch_port = int(input("Enter port to be punched: "))
        offer = {
            'sender_ip': PUBLIC_IP,
            'receiver_ip': receiver_ip,
            'punch_port': punch_port
        }

        doc_ref = db.collection(u'offers').add({"offer": offer})
        print(f"Offer sent to {receiver_ip}. Listening for answer...")
        db.collection(u'offers').document(doc_ref[1].id).on_snapshot(answer_listen)
        receive_answer.wait()

        print(f"Answer received. Attempt communication on remote port {receiver_listen_port}")
        receive_answer.clear()

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('0.0.0.0', punch_port))

        while True:
            msg = input(f"Sending message to {receiver_ip}: ")
            sock.sendto(msg.encode(), (receiver_ip, receiver_listen_port))


main_thread()