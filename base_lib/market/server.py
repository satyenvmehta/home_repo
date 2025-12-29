import market_include
import socket
import get_price

HOST = 'localhost'  # Standard loopback interface address (localhost)
PORT = market_include.CURR_PORT  # Port to listen on (non-privileged ports are > 1023)

def start():
    print("Starting Current Price server...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        while True:
            conn, addr = s.accept()
            with conn:
                print('Connected by', addr)
                while True:
                    data = conn.recv(1024)
                    text_data = data.decode("utf-8")

                    # print(text_data)
                    if not data:
                        break
                    cp = get_price.get_market_price(text_data)
                    # print(cp)
                    conn.sendall(cp.encode())  # Echo back the received data

if __name__ == '__main__':
    print("Starting Current Price server")
    start()
    print("Done")