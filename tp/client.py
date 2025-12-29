import socket

HOST = 'localhost'  # The server's hostname or IP address
PORT = 65432        # The port used by the server

def open_socket():
    return socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#connect socket def
def connect_socket(s, host, port):
    s.connect((host, port))
    return s
#send data def
def send_data(s, data):
    s.sendall(data.encode())
    return s
#receive data def
def receive_data(s):
    data = s.recv(1024)
    return data
#close socket def
def close_socket(s):
    s.close()
    return s

def main(s, tkr):
    send_data(s, tkr)
    data = receive_data(s)
    print(data.decode())
    # close_socket(s)
    return data.decode()

if __name__ == '__main__':
    s = open_socket()
    s = connect_socket(s, HOST, PORT)
    main(s, 'AAPL')
    main(s, 'GOOG')
    main(s, 'MSFT')
    main(s, 'AMZN')
    close_socket(s)

# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#     s.connect((HOST, PORT))
#
#     message = 'AAPL'  #Hello, world!'
#     s.sendall(message.encode())
#     data = s.recv(1024)
#     text_data = data.decode("utf-8")
#
# print('Received from server:', text_data)