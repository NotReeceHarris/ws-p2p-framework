
def disconnected():
    pass

def connected(client):
    print("Connected")

def send(data):
    print(f"Sending: {data}")

    return data

def recv(data, client):
    print(f"Received: {data}")
    
    return data, 'Friend'
