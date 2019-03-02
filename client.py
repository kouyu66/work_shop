import socket
import json
import time

class Client():

    def __init__(self, ip, port_number):
        self.__ip = ip
        self.__port_number = port_number
        self.__s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__s.connect((self.__ip, self.__port_number))

    def send(self, data):
        encode_data = (json.dumps(data)).encode('utf-8')
        self.__s.send(encode_data)
        self.__s.send(('').encode('utf-8')) # 发送约定的空字符作为结束标志

    def close(self):
        self.__s.close()

test_client = Client('192.168.31.33', 1025)
info_list = ['hello', 'this is test message', 'multi-test message', 'try if this can work or not']
# info_list = 'this is test message'
for info in info_list:
    time.sleep(1)
    test_client.send(info)
