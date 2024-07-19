import zmq

class ReceiverClient:
    
    def __init__(self, port=5555):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(f"tcp://localhost:{port}")

    def _send_message(self, message):
        self.socket.send_string(message)
        response = self.socket.recv_string()
        print(response)
        return response
    
    def collect_pedestal(self):
        return self._send_message("collect_pedestal")
    
    def ping(self):
        return self._send_message("ping")
    
if __name__ == "__main__":
    client = ReceiverClient()
    client._send_message("Hello")
    client.collect_pedestal()