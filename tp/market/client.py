import socket

from base_lib.core.base_classes import BasePrice
from base_lib.core.base_container_classes import BaseList, BaseDict
# from tp.lib.ticker import Ticker
from tp.market.market_include import CURR_PORT, HIST_PORT
# from tp.market.ticker import Ticker

import pickle

# from tp.ticker import Ticker

HOST = 'localhost'  # The server's hostname or IP address
# CURRPORT = 65432        # The port used by the server

def open_socket():
    return socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#connect socket def
def connect_socket(s, host, port):
    s.connect((host, port))
    return s

def getActiveSocket(port):
    s = open_socket()
    s = connect_socket(s, HOST, port)
    return s

#send data def
def send_data(s, data):
    s.sendall(data.encode())
    return s

def sock_recv(s, n):
    try:
        data = s.recv(n)
    except:
        raise ValueError("Failed to receive data from server")
    return data

#receive all data
def recvall(sock, n):
    if n <= 1024:
        return sock_recv(sock, n)  #.recv(n)
    """Helper function to receive exactly n bytes from the socket."""
    data = b''
    while len(data) < n:
        packet = sock_recv(sock, n - len(data))
        if not packet:
            return None
        data += packet
    return data

#receive data def
def receive_data(sock, dlen=1024):
    # data_length = int.from_bytes(s.recv(4), 'big')
    # data = sock.recv(dlen)
    data = recvall(sock, dlen)
    if not data:
        raise ValueError("Failed to receive data from server")
    return data
#close socket def
def close_socket(s):
    s.close()
    return s

def validate_tkr(tkr):
    if tkr.startswith(tuple("0123456789")):
        return False
    return True

def _getTickerInfo(sock, tkr):
    if  not validate_tkr(tkr):
        return None
    send_data(sock, tkr)
    data_length_bytes = receive_data(sock, 4)
    data_length = int.from_bytes(data_length_bytes, 'big')
    print("data length: ", data_length)
    if not data_length_bytes:
        raise ValueError("Failed to receive data length from server " + str(data_length_bytes) + " " + str(data_length) + " " + str(tkr))
    data = receive_data(sock, data_length)
    results = pickle.loads(data)

    return results

def getTkrPrice(sock, tkr):
    if not validate_tkr(tkr):
        price = None
    else:
        send_data(sock, tkr)
        data = receive_data(sock)
        price = BasePrice(float(data.decode()))
    tkr = Ticker(tkr, price)
    return tkr

import common_include as C
# from base_lib.core.common_include import MFList
def getPricesFor(param):
    s = getActiveSocket(CURR_PORT)
    if (not s):
        print("Error getting connection")
        return False
    if isinstance(param, str):
        tkr = getTkrPrice(s, param)
        print("only price ", tkr.price)
        return tkr
    if isinstance(param, list):
        results = BaseDict()
        for tkr in param:
            if len(tkr) > 6:
                results.append(tkr, None)
                continue
            if tkr in C.MFList:
                print("MF LIST " + tkr)
                results.append(tkr, None)
                continue
            print("getting price for ", tkr)
            tkrDet = getTkrPrice(s, tkr)
            if tkrDet.price is None:
                print("Error getting price for ", tkr)
            elif tkrDet.isZeroPrice():
                print("Zero price for ", tkr)
            results.append(tkr, tkrDet)
        return results

def getHistoricalDataFor(lst):
    if not isinstance(lst, list):
        return False
    s = getActiveSocket(HIST_PORT)
    if (not s):
        print("Error getting connection")
        return False
    if isinstance(lst, list):
        results = BaseDict()
        for tkr in lst:
            print("getting historical data for ", tkr)
            tkr_hist = _getTickerInfo(s, tkr)
            results.append(tkr, tkr_hist)
    return results

#unit test
def unit_test():
    # print(getPricesFor('AAPL'))
    # return
    lst = ['DUFRY', 'AAPL', 'MSFT', '12345', 'G637AM102', 'TSLA']
    # res = getHistoricalDataFor(lst)
    res = getPricesFor(lst)
    if isinstance(res, BaseDict):
        res.print()
    if isinstance(res, Ticker):
        print(res.price)
    if isinstance(res, BaseList):
        res.print()
        # print(res)

if __name__ == '__main__':
    unit_test()

