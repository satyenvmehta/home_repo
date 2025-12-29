import socket
import market_include
import get_price

import pandas as pd
import pickle

HOST = 'localhost'  # Standard loopback interface address (localhost)
PORT = market_include.HIST_PORT  # Port to listen on (non-privileged ports are > 1023)


data = {
    'Stock': ['AAPL', 'MSFT', 'GOOGL'],
    'Price': [150.0, 250.0, 2800.0]
}
df = pd.DataFrame(data)

def start():
    print("Starting History server")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print("Listening at " + str(PORT) + " " + HOST)

        while True:
            conn, addr = s.accept()
            with conn:
                print('Connected by', addr)
                while True:
                    data = conn.recv(1024)
                    tkr = data.decode("utf-8")

                    print(tkr)
                    if not data:
                        break
                    cp = get_price.getTkrHist(tkr)
                    # cp = df
                    print(cp)
                    # csv_data = df.to_csv(index=False)
                    # encoded_csv_data = csv_data.encode('utf-8')
                    # s.sendall(len(encoded_csv_data).to_bytes(4, 'big'))
                    pickled_data = pickle.dumps(cp)
                    dlen = len(pickled_data)
                    print("Sending length info " + str(dlen) + " bytes")
                    conn.sendall(dlen.to_bytes(4, 'big'))
                    conn.sendall(pickled_data)  # Echo back the received data

if __name__ == '__main__':
    print("Starting History server")
    start()
    print("Done")
