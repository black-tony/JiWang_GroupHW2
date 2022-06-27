# -*- coding: cp936 -*-
import threading
import time
import socket
import tools
"""
ʵ��һ���ɿ���socketͨ��������������һ�¹���
    ��ͨ���߱��Լ�ά��ͨ��������
    ��ͨ���߱������ֽ������ܣ��������ܱ�֤���ݵ�������
    ��ͨ���߱������ֽ������ܣ��������ܱ�֤���ݵ�������
"""
DEBUG = 1

class BaseSocket:
    """
    ����һ��socket�Ự�����յ�һ�������İ�����ûص�����
    """
    def __init__(self, conn, address, protocol_len, enable_ping=False, retry_interval=1, ping_interval=3):

        self.conn = conn
        self.conn_online = True
        self.retry_interval = retry_interval
        self.ping_interval = ping_interval
        self.address = address
        self.enable_ping = enable_ping
        self.protocol_len = protocol_len
        self.on_msg = None
        if enable_ping:
            threading.Thread(target=self.check_conn).start()
            threading.Thread(target=self.ping).start()

    def set_onmsg(self, f):
        self.on_msg = f

    def recv_data_for_every(self):
        """
        ��ͨ���߱������ֽ������ܣ��������ܱ�֤���ݵ�������
        """
        def innter(self_):
            print("�ȴ��ص�����...")
            while True:
                if self.on_msg:
                    print("�׽��ּ���������...")
                    break
            while self.conn:
                try:
                    if not self.protocol_len:
                        raise ("����ָ���������ݵĳ���",)
                    received_data = self.conn.recv(self.protocol_len)

                    # print("innter  1111", received_data)

                    data_len = len(received_data)
                except ConnectionResetError:
                    print(f"error �� {self.address} �Ͽ�����")
                    self.conn.close()
                    return
                if data_len == 0:
                    print(f"�� {self.address} �Ͽ�����")
                    self.conn.close()
                    return
                '''if self.protocol_len:
                    while data_len < self.protocol_len:
                        received_data += self.conn.recv(self.protocol_len - data_len)
                        data_len = len(received_data)'''

                print('base����',end='')
                print(received_data)
                self.on_msg(received_data)

        threading.Thread(target=innter, args=(self,)).start()

    def recv_once(self, size):
        recv_size = int()
        recv_data = b''
        while size != recv_size:
            recv_data += self.conn.recv(size - recv_size)
            recv_size = len(recv_data)
        return recv_data

    def recv_agroup(self, size):
        receive_size = 0
        receive_data = b''
        while not size == receive_size:  # ����Э����˵�����ļ���С��ѭ�����գ�ֱ���������
            try:
                receive_data += self.conn.recv(size - receive_size)

            except ValueError as e:
                print(e)
            receive_size = len(receive_data)
        return receive_data

    def get_conn(self):
        while True:
            try:
                self.conn = None
                self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.conn.connect(self.address)
                self.conn_online = True
                print(f"Socket���ӳɹ�")
                if self.enable_ping:
                    threading.Thread(target=self.ping).start()
                    threading.Thread(target=self.recv_data_for_every).start()
                    print("Ping������")
                return self.conn
            except Exception as e:
                print(f"����socketʧ�� {str(e)}")
                #time.sleep(self.retry_interval)

    def send_all(self, data):
        while True:
            if self.conn_online:
                try:
                    '''test=data.encode()'''
                    print(data)
                    self.conn.sendall(data)
                    return True
                except Exception as e:
                    print(f"sendall error {str(e)}")
                    #time.sleep(1)

        threading.Thread(target=send_all, args=(self,)).start()


    def ping(self):
        """
        ����  self.conn_online ��״̬
        """
        while True:
            if self.conn_online:
                ping_data = tools.jsondumps(dict(code=0, msg='', data=None))
                if len(ping_data) < self.protocol_len:
                    ping_data = tools.padding_data(ping_data, self.protocol_len - len(ping_data))
                try:
                    self.conn.sendall(ping_data)
                except Exception as e:
                    print("��鵽����" ,e)
                    self.conn.close()
                    self.conn_online = False
                    return True
                #time.sleep(self.ping_interval)

    def check_conn(self):
        """
        ����  self.conn_online ��״̬�ж��Ƿ�����
        """
        while True:
            #time.sleep(0.1)
            if self.conn_online:    # �ȴ�����
                while True: # �ȴ�����
                    if not self.conn_online:
                        print("׼������")
                        self.get_conn()
                        break
                    #time.sleep(0.1)