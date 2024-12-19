# ws-p2p-framework

**A Flexible Open-Source Framework for Peer-to-Peer Communication**

ws-p2p-framework provides a robust and customizable solution for peer-to-peer (P2P) communication with an integrated GUI. This framework allows users to tailor the communication protocols, handshakes, encryption methods, and more to suit their specific needs.

## Usage

To initiate a P2P connection between two peers, Alice and Bob, follow these steps:

```sh
# Alice
python3 main.py --target 192.168.0.1:8000 --host 192.168.0.2:8000

# Bob
python3 main.py --target 192.168.0.2:8000 --host 192.168.0.1:8000
```

## Requirements

- Python: Python 3.x is required.
- GUI Environment: Ensure you have a graphical environment; terminal support is planned for future updates.

## Forks

Here are some notable forks of the ws-p2p-framework that add specific functionalities:

Name | Algorithm | Link
---  | --- | ---
ws-p2p-rsa | RSA | [NotReeceHarris/ws-p2p-rsa](https://github.com/NotReeceHarris/ws-p2p-rsa)
ws-p2p-aes | RSA + AES256 | [NotReeceHarris/ws-p2p-aes](https://github.com/NotReeceHarris/ws-p2p-aes)
ws-p2p-dilithium | RSA + AES256 + DILITHIUM4 | [NotReeceHarris/ws-p2p-dilithium](https://github.com/NotReeceHarris/ws-p2p-dilithium)

## License

```
GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007

Copyright (C) 2007 Free Software Foundation, Inc. <https://fsf.org/> Everyone is permitted to copy and distribute verbatim copies of this license document, but changing it is not allowed.
 ```
