import socket
import threading
import json
from colorama import Fore, Style

class PythonBridgeServer:
   
    def __init__(self, host="127.0.0.1", port=50505):
        self.host = host
        self.port = port
        self.server = None
        self.running = False

    def start(self):
        
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen(1)
        self.running = True
        print(Fore.CYAN + f"Starting the Pon RPC server:{self.host}:{self.port}" + Style.RESET_ALL)

        thread = threading.Thread(target=self.accept_loop, daemon=True)
        thread.start()

    def accept_loop(self):
        while self.running:
            conn, addr = self.server.accept()
            data = conn.recv(4096)
            if not data:
                continue
            try:
                req = json.loads(data.decode())
                cmd = req.get("command", "")
                print(Fore.YELLOW + f"[Ruby→Python]Invoke command:{cmd}" + Style.RESET_ALL)
                
                if cmd == "about":
                    response = "Command Line OS 3.0 - Ruby Bridge OK "
                else:
                    response = f"Unknown command: {cmd}"
                conn.send(json.dumps({"result": response}).encode())
            except Exception as e:
                conn.send(json.dumps({"error": str(e)}).encode())
            finally:
                conn.close()

    def stop(self):
        self.running = False
        if self.server:
            self.server.close()
