# -*- coding: cp936 -*-
import os
import json
import time
import queue
import threading
import hashlib
#from PyQt5.Qt import QApplication
from PyQt5.QtWidgets import QApplication

from base_socket import BaseSocket

import tools


class FileIO:
    def __init__(self, read_path=None, write_path=None, read_len=None, cover_write=True):
        self.stream_queue = queue.Queue()
        self.read_len = read_len
        if read_path:
            if not os.path.exists(read_path):
                raise (f"�ļ� {read_path} ������",)
            self.abs_path = read_path
            mode = "rb"
        else:
            if not os.path.exists(os.path.dirname(write_path)):
                raise Exception(f"�ļ��� {write_path} ������")
            if os.path.exists(write_path):
                if cover_write:
                    succ, msg = tools.remove(write_path)
                    if not succ:
                        raise Exception(msg)
                else:
                    raise Exception(f"�ļ�  {write_path} �Ѵ���")
            self.abs_path = write_path
            mode = "wb"
        self.FP = open(self.abs_path, mode)
        if write_path:
            threading.Thread(target=self.clear_stream).start()

    def clear_stream(self):
        while not self.FP.closed:
            file_stream = self.stream_queue.get()
            if isinstance(file_stream, dict):
                self.close_file()
                print(f"�ļ��� {file_stream['write_path']} д����̳ɹ�")
            else:
                # print(f"д���� {len(file_stream)}")
                self.write_data(file_stream)
        # print("File�����ͷ���")

    def write_data(self, data):
        self.FP.write(data)
        return True

    def read_data(self):
        one_group = self.FP.read(self.read_len)
        while one_group:
            yield one_group
            one_group = self.FP.read(self.read_len)

    def close_file(self):
        self.FP.close()


class Handler:
    """
    �ɷ����ļ�
    �ɷ��Ͷ���
    """
    def __init__(self,
                base_socket,
                 file_io,
                 protocol_len,
                 file_once_recv,
                 once_recv,
                 padding_char=b"*",
                 on_error=None):
        self.file_io = file_io              # �����ܵ��ļ�ʱ��
        self.once_recv = once_recv
        self.base_socket = base_socket
        self.padding_char = padding_char
        self.protocol_len = protocol_len
        self.file_group_len = file_once_recv
        self.on_error = on_error
        self.file_fp = None
        self.allow_send = False
        self.recv_allow_send_response = False
        self.local_reload = None

        self.show_progress = None   # �źŲ�
        self.hide_progress = None
        self.set_status = None

        self.response_data = queue.Queue()
    # ���в����ĳ�ʼ��

    # ������Ϣ���̳�RecvStream�ࣩ
    def on_msg(self, b_data):
        try:
            protocol = self.decode_protocol(b_data)
           # print('����:')

        except Exception as e:
            print("����Э�����", e, b_data, len(b_data))
            return
        try:
            print('����',end='')
            print(protocol)
            code = protocol["code"]
            next_size = protocol.get("size")
            msg = protocol["msg"]
            #print(protocol)
        except Exception as e:
            print("����Э�����", e)
            return


        if code == 100:    # �յ����ļ���
            print(f"�յ��ļ��� {protocol['write_path']}")
            all_size = next_size
            last_d = b''                        # ���յ���һ�������
            last_second_recv_bytes = int()      # ��һ����յ����ֽ��������ڼ������ؽ�����
            last_second = int(time.time())      # �������Ƽ��һ�����һ�����ؽ��ȵı���
            start_time = int(time.time())       # �������ݿ�ʼ��ʱ��
            once_recv = self.once_recv          # �涨��һ�������ն�������
            receive_size = 0                    # һ�������˶�������
            detail_size = tools.bytes_to_speed(all_size)   # ��Ҫ���ص����ݴ�С�����Ի���ʽչʾ

            # �״ν��յ��ļ�����Ҫʵ����һ���ļ���
            if not self.file_fp:
                try:
                    self.file_fp = self.file_io(write_path=protocol["write_path"])
                except Exception as e:
                    print("��ʼ���ļ��������", str(e))
                    return
            # ����Ҫ���յ����ݴ��ڵ�����������ʱ����Ҫ����whileѭ����ֱ���������
            if all_size > once_recv:
                while receive_size !=  all_size:
                    receive_data = self.base_socket.recv_once(once_recv)
                    last_d = receive_data
                    last_second_recv_bytes += len(receive_data)
                    receive_size += len(receive_data)

                    # Ϊ�˲���IO����ʱ�䣬����ʹ�ù���ģʽ�����ļ���д��
                    self.file_fp.stream_queue.put(receive_data)

                    # ��ʣ�������С��һ��Ĵ�С����Ҫ������һ�ν����ֽڵ�������������������
                    if (all_size - receive_size) < once_recv:
                        once_recv = all_size - receive_size

                    # ÿ���Ӹ������ؽ�����
                    if int(time.time()) != last_second and self.set_status:
                        progress = tools.Dict(
                            operation="������",
                            name=os.path.basename(protocol["write_path"]),
                            progress=int(receive_size / all_size * 100),
                            speed=tools.bytes_to_speed(last_second_recv_bytes),
                            detail=tools.bytes_to_speed(receive_size) + "/" + detail_size,
                            elapsed_time=tools.second_to_time(int(time.time()) - start_time),
                            remaining_time=tools.second_to_time((all_size - receive_size) / last_second_recv_bytes))
                        self.set_status.emit(tools.Dict(progress))
                        last_second = int(time.time())
                        last_second_recv_bytes = int()

            else:
                receive_data = self.base_socket.recv_once(all_size)
                last_d = receive_data
                self.file_fp.stream_queue.put(receive_data)
            # ����һ���ֵ���󣬱�ʾд�����
            self.file_fp.stream_queue.put(protocol)
            self.file_fp = None
            print(f"�ļ�д�뻺��ɹ� {os.path.basename(protocol['write_path'])} \n"
                  f"�ļ�һ��{all_size} ������ {receive_size}  ���һ�����ݳ��� {len(last_d)} \n {last_d}")

        elif code == 101:   # �ͻ�����Ҫ�����ļ�
            receive_data = self.base_socket.recv_agroup(next_size)
            data = tools.decode_dict(receive_data)
            file_list = data["file_list"]
            write_to = data["write_path"]
            print("�ͻ������ļ�", file_list)
            self.send_files(file_list, write_to)

        elif code == 200: # ������Ŀ¼
            # ֻ�з������Ż�ʹ�ô˷���
            receive_data = self.base_socket.recv_agroup(next_size)
            data = tools.decode_dict(receive_data)
            # if data.get("dir_path") == "C:/test/Keil/C51/Examples/ST uPSD/upsd3300/DK3300-ELCD/I2C/I2C_Master":
            #     print("11111")
            dir_path = data["dir_path"]
            succ, msg = tools.mkdir(dir_path)
            if not succ:
                # return self.send_data(201, '������Ŀ¼�ɹ�')
                return self.error(msg)

        elif code == 202:   # ��������
            # ֻ�з������Ż�ʹ�ô˷���
            receive_data = self.base_socket.recv_agroup(next_size)
            data = tools.decode_dict(receive_data)
            succ, msg = tools.rename(data["old"], data["new"])
            if succ:
                return self.send_data(203, '�������ɹ�')
            return self.error(msg)

        elif code == 204:   #ɾ��������Ŀ¼�����ļ�
            # ֻ�з������Ż�ʹ�ô˷���
            receive_data = self.base_socket.recv_agroup(next_size)
            data = tools.decode_dict(receive_data)
            succ, msg = tools.remove(data["abs_path"])
            if succ:
                return self.send_data(205, 'ɾ���ɹ�')
            return self.error(msg)

        elif code == 206:   # �ͻ��˻�ȡ������Ŀ¼
            receive_data = self.base_socket.recv_agroup(next_size)
            data = tools.decode_dict(receive_data)
            list_dir = tools.listdir(data["dir_path"])
            self.send_data(207, data=dict(list_dir=list_dir))

        elif code == 207: # ����������Ŀ¼
            receive_data = self.base_socket.recv_agroup(next_size)
            data = tools.decode_dict(receive_data)
            self.response_data.put(data)

        elif code == 208:  # �ͻ��˻�ȡ����������
            disk_list = tools.get_disk()
            self.send_data(207, data=dict(disk_list=disk_list))

        elif code == 209:
            receive_data = self.base_socket.recv_agroup(next_size)
            data = tools.decode_dict(receive_data)
            self.response_data.put(data["disk_list"])
            disk_list = data["disk_list"]
            print("�յ������������б�", disk_list)

        elif code == 210:
            if self.local_reload:
                print("ˢ�±����ļ�")
                self.local_reload()

        elif code == 500:   # �յ��쳣
            receive_data = self.base_socket.recv_agroup(next_size)
            data = tools.decode_dict(receive_data)
            if self.on_error:
                self.on_error(data)
            print(f"�յ��쳣�� {data}")

        elif code == 501:   # �յ�֪ͨ
            print(f"�յ���Ϣ�� {protocol['msg']}")

        elif code == 600:
            if self.show_progress:
                self.show_progress.emit()

        elif code == 601:
            if self.hide_progress:
                self.hide_progress.emit()

        elif code == 602:
            receive_data = self.base_socket.recv_agroup(next_size)
            data = tools.decode_dict(receive_data)
            if self.set_status:
                self.set_status.emit(tools.Dict(data))

    def send_summary(self):
        pass

    # �����ļ�
    def send_files(self, file_list, write_to, set_progress=None):
        for file_path in file_list:
            file_name = os.path.basename(file_path)
            size, unit, bytes_size = tools.file_size(file_path)
            with open(file_path, 'rb') as fp:
                protocol = dict(code=100, msg='', size=os.path.getsize(file_path), write_path=os.path.join(write_to, file_name))
                self.before_send(protocol)
                b_data = fp.read(self.file_group_len)
                last_s = int(time.time())
                last_s_send_group = int()
                send_group = int()
                start_time = int(time.time())
                while b_data:
                    if self.base_socket.send_all(b_data):
                        send_group += 1
                        last_s_send_group += 1
                        b_data = fp.read(self.file_group_len)
                        # ��������˻ص�������ÿ���ӵ��ò��Ҵ��ݻص�����
                        if int(time.time()) != last_s and set_progress:  # ˵����ȥ��һ��
                            QApplication.processEvents()
                            d = tools.Dict(
                                operation="������",
                                name=file_name,
                                progress=int(send_group * self.file_group_len / bytes_size* 100),
                                speed=tools.bytes_to_speed(last_s_send_group * self.file_group_len),
                                detail=tools.bytes_to_speed(send_group * self.file_group_len) + "/" + str(size) + unit,
                                elapsed_time=tools.second_to_time(int(time.time()) - start_time),
                                remaining_time=tools.second_to_time((bytes_size - send_group * self.file_group_len) / (last_s_send_group * self.file_group_len))
                            )
                            last_s_send_group = int()
                            last_s = int(time.time())
                            set_progress.emit(d)

                    else:
                        print("scoket�쳣 �ļ�����ֹͣ��")
                        return False
            print("�ļ��������", file_name)
        return True

    # �����ļ�
    def down_load_files(self, file_list, write_path):
        new_file_list = file_list.copy()
        for i in file_list:
            name = os.path.basename(i)
            if os.path.exists(os.path.join(write_path, name)):
                print(f"{os.path.join(write_path, name)} �Ѵ��ڣ�����...")
                new_file_list.remove(i)
        self.send_data(101, '�����ļ�', dict(file_list=new_file_list, write_path=write_path))

    # ������ͨ��������
    def send_data(self, code, msg='', data=None):
        b_data = tools.encode_dict(data)
        size = len(b_data) if data else int()
        protocol = dict(code=code, msg=msg, size=size)

        print(protocol)
        print('\n')
        print(data)
        print('\n')
        print(b_data)
        print('\n')

        self.before_send(protocol)
        if data:
            self.base_socket.send_all(b_data)
        return

    def os_mkdir(self, dir_path):
        self.send_data(200, '����Ŀ¼', data=dict(dir_path=dir_path))

    def os_remove(self, abs_path):
        self.send_data(204, 'ɾ��Ŀ¼', data=dict(abs_path=abs_path))

    def os_rename(self, old, new):
        self.send_data(202, '������', data=dict(old=old, new=new))

    def get_dir_list(self, dir_path):
        #self.send_data(206, '��ȡĿ¼', data=dict(dir_path=dir_path))
        #self.my_send_data('event=list\npdir=/home')
        res = self.response_data.get()
        print('dirpath',end='')
        print(res)
        res=['/home']
        return res["list_dir"]
    
    def get_disk_list(self):
        #disk=[]
        self.send_data(208, '��ȡ�����б�')
        #disk.append('event=list\npdir=home/2\n')
        #self.send_data(208,'event=list\npdir=home/2\n')
        #self.response_data.put(disk)
        return self.response_data.get()
    
    # �ڷ�������ǰ֪ͨ�Է������Ϣ�����ý���׼��
    def before_send(self, protocol):
        self.base_socket.send_all(self.padding(tools.encode_dict(protocol)))

    # ���ݽ���
    def decode_protocol(self, b_data):
        return json.loads(b_data.decode().replace(self.padding_char.decode(), ''))

    # ���ݶ���
    def padding(self, bytes_data):
        bytes_data += self.padding_char * (self.protocol_len - len(bytes_data))
        return bytes_data

    # �������쳣��֪ͨ�ͻ���
    def error(self, msg):
        self.send_data(500, msg, dict(msg=msg))


    def test_msg(self,msg):
        b_data=msg.dict
        self.base_socket.send_all






    def my_send_data(self, msg):
        #print(msg)
        #b_data = msg.encode()
        #print(b_data)
        if msg:
            self.base_socket.send_all(msg)

    def my_get_dir_list(self, dir_path):

        self.my_send_data('event=list\n'+'pdir='+dir_path+'\n')

        res = self.response_data.get()
        #print(res)
        return res["list_dir"]

    '''def my_get_disk_list(self):
        # disk=[]
        #self.send_data(208, '��ȡ�����б�')
        # disk.append('event=list\npdir=home/2\n')
        # self.send_data(208,'event=list\npdir=home/2\n')
        # self.response_data.put(disk)
        self.my_get_dir_list('/home')
        return self.response_data.get()'''
