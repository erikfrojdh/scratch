import zmq
import time
class ReceiverServer:
    _commands = ['collect_pedestal',]

    def __init__(self, port=5555):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(f"tcp://*:{port}")

    def _decode(self, message):
        if ':' in message:
            cmd, args = message.split(':')
            if ',' in args:
                args = args.split(',')
            else:
                args = [args]
        else:
            cmd = message
            args = []
        
        return cmd, args
    
    def _has_function(self, cmd):
        return cmd in self._commands
    
    def collect_pedestal(self):
        time.sleep(1)
        return "OK:Pedestal collected"

    def run(self):
        while True:
            #  Wait for next request from client
            message = self.socket.recv_string()
            print(f"Received request: {message}")

            cmd, args = self._decode(message)
            print(cmd, args)

            #Command was not found
            if not self._has_function(cmd):
                self.socket.send_string("ERROR:Invalid command")
                continue
 
            res = getattr(self, cmd)(*args)
            self.socket.send_string(res)

if __name__ == "__main__":
    server = ReceiverServer()
    server.run()