import os
import json
import time
import queue
import threading
import hashlib
from PyQt5.Qt import QApplication

from base_socket import BaseSocket

import tools


class FileIO:
    def __init__(self, read_path=None, write_path=None, read_len=None, cover_write=True):
        self.stream_queue = queue.Queue()
        self.read_len = read_len
        if read_path:
            if not os.path.exists(read_path):
                raise (f"文件 {read_path} 不存在",)
            self.abs_path = read_path
            mode = "rb"
        else:
            if not os.path.exists(os.path.dirname(write_path)):
                raise Exception(f"文件夹 {write_path} 不存在")
            if os.path.exists(write_path):
                if cover_write:
                    succ, msg = tools.remove(write_path)
                    if not succ:
                        raise Exception(msg)
                else:
                    raise Exception(f"文件  {write_path} 已存在")
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
                print(f"文件流 {file_stream['write_path']} 写入磁盘成功")
            else:
                # print(f"写入流 {len(file_stream)}")
                self.write_data(file_stream)
        # print("File对象释放了")

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
    可发送文件
    可发送对象
    """
    def __init__(self,
                base_socket,
                 file_io,
                 protocol_len,
                 file_once_recv,
                 once_recv,
                 padding_char=b"*",
                 on_error=None):
        self.file_io = file_io              # 当接受到文件时候
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

        self.show_progress = None   # 信号槽
        self.hide_progress = None
        self.set_status = None

        self.response_data = queue.Queue()

        def on_msg(self, b_data):
            protocol=b_data.decode()
            if 'login_accepted' in protocol:
                #登录
                123



            elif 'register' in protocol:
                #注册
                123

            elif 'upload' in protocol:
                #上传
                123

            elif 'list' in protocol:
                #目录列出
                123

            elif 'move' in protocol:
                #移动
                123

            elif 'copy' in protocol:
                #复制
                123

            elif 'remove' in protocol:
                #删除
                123

            elif 'mkdir' in protocol:
                #创建目录
                123

            elif 'movedir' in protocol:
                # 删除目录
                123

            elif 'download' in protocol:
                # 下载
                123

