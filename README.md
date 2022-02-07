# Python-P2P-Chat

A proof of concept decentralized peer-to-peer messaging app utilizing [UDP hole punching](https://en.wikipedia.org/wiki/UDP_hole_punching) and firebase as signalling server.
This app works on most NAT configuration except symmetric, typically found in corporate networks.

### Workflow

Scenario: client A wants to send client B a message

- Client A and client B both runs and listens to firebase for new offers. 
- Client A make an offer and upload to firebase, with sender IP, receiver IP and destination port (port to be punched)
- Client B receives offer, responds to offer by specifying the port it is listening on (source port) and performs UDP hole punching by sending a UDP packet to the destination port
- Client A receives answer from Client B, and starts communication by sending from destination port (port that has been punched by B) to the source port (port B is listening on).

