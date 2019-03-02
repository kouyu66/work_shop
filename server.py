import socket
import threading
import time
import json


# ------ 创建socket服务器 ------#
#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s.bind(('', 1025))
#s.listen(5)
#s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#sock, addr = s.accept()
#t1 = threading.Thread(target=dataRecv, args=(sock, addr))
#t1.start()

class Inbox():
    '''模拟一个支持多线程的socket服务端'''

    def __init__(self, port_number):
        '''设置socket基础信息'''
        self.__record = []
        self.__led = False
        self.__s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__s.bind(('', port_number))
        self.__s.listen(5)
        self.__s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def on(self):
        '''将serverDameon函数设置为守护线程，放置在后台运行'''
        def serverDaemon(self):
            '''无限循环接受远程联入信息，转交dataRecv函数处理，并为每一次联入单开一个线程，支持多线程'''
            def dataRecv(self, sock, addr, lock):
                '''获取锁以后，每1024个字节收一次数据包，解析并添加到类属性列表中，同时设置led状态为True，通讯完毕后端口关闭，释放锁'''
                lock.acquire()
                while True:    
                    data = sock.recv(1024)
                    if not data:
                        break
                    decode_data = json.loads(data.decode('utf-8'))
                    self.__record.append(decode_data)
                    self.__led = True
                lock.release()
                sock.close()
                return
            lock = threading.Lock()
            while True:
                sock, addr = self.__s.accept()
                t1 = threading.Thread(target=dataRecv, args=(self, sock, addr, lock))
                t1.start()
            return
        t1 = threading.Thread(target=serverDaemon, args=(self,), daemon=True)
        t1.start()    
  

    def led(self):
        '''判断led灯当前状态'''
        return self.__led

    def vomit(self):
        '''返回属性类堆栈中的第一条信息'''
        if not self.__record:
            self.__led = False
            return None
        else:
            return self.__record.pop(0)

# ----------------Unit Test--------------- #
test_server = Inbox(1025)
test_server.on()

while True:
    if test_server.led():
        print(test_server.vomit())
    else:
        time.sleep(1)
        print(time.time())

# ------------ Unit Test ------------ #
