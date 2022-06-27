# -*- coding: cp936 -*-
import os
import json
import time
import queue
import threading
import hashlib
from PyQt5.Qt import QApplication
import tools
from base_socket import BaseSocket
import json
import shutil
import psutil
import platform

import tools


class my_FileIO:
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




class my_Handler:
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
                 account,
                 padding_char=b"*",
                 on_error=None
                 ):
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

        self.account=account
        self.response_data = queue.Queue()

    def on_msg(self, b_data):
        protocol=b_data.decode()
        if 'login_accepted' in protocol:
            #登录
            123

        if 'list_accepted' in protocol:
            #列出目录
            self.my_get_dir_list(protocol)

        if 'failed' in protocol:
            #列出目录
            self.my_get_dir_list('')


        elif 'upload_completed' in protocol:
            protocol

        elif 'upload_accepted' in protocol:
            str=protocol.split('\n')
            npos = int()
            if 'resume upload'in protocol:
                npos = int(str[2])
                return npos

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

        elif 'download_accepted' in protocol:
            # 下载
            123

    def send_summary(self):
        pass

    # 发送文件
    def send_files(self, file_list, write_to, set_progress=None):
        for file_path in file_list:
            file_name = os.path.basename(file_path)
            size, unit, bytes_size = tools.file_size(file_path)
            with open(file_path, 'rb') as fp:
                protocol = dict(code=100, msg='', size=os.path.getsize(file_path),
                                write_path=os.path.join(write_to, file_name))
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
                        # 如果设置了回调函数，每秒钟调用并且传递回调函数
                        if int(time.time()) != last_s and set_progress:  # 说明过去了一秒
                            QApplication.processEvents()
                            d = tools.Dict(
                                operation="传送中",
                                name=file_name,
                                progress=int(send_group * self.file_group_len / bytes_size * 100),
                                speed=tools.bytes_to_speed(last_s_send_group * self.file_group_len),
                                detail=tools.bytes_to_speed(send_group * self.file_group_len) + "/" + str(size) + unit,
                                elapsed_time=tools.second_to_time(int(time.time()) - start_time),
                                remaining_time=tools.second_to_time((bytes_size - send_group * self.file_group_len) / (
                                            last_s_send_group * self.file_group_len))
                            )
                            last_s_send_group = int()
                            last_s = int(time.time())
                            set_progress.emit(d)

                    else:
                        print("scoket异常 文件发送停止。")
                        return False
            print("文件发送完毕", file_name)
        return True

    # 下载文件
    def down_load_files(self, file_list, write_path):
        new_file_list = file_list.copy()
        for i in file_list:
            name = os.path.basename(i)
            if os.path.exists(os.path.join(write_path, name)):
                print(f"{os.path.join(write_path, name)} 已存在，跳过...")
                new_file_list.remove(i)
        self.send_data(101, '下载文件', dict(file_list=new_file_list, write_path=write_path))

    # 发送普通对象数据
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
        self.send_data(200, '创建目录', data=dict(dir_path=dir_path))

    def os_remove(self, abs_path):
        self.send_data(204, '删除目录', data=dict(abs_path=abs_path))

    def os_rename(self, old, new):
        self.send_data(202, '重命名', data=dict(old=old, new=new))

    def get_dir_list(self, dir_path):
        # self.send_data(206, '获取目录', data=dict(dir_path=dir_path))
        # self.my_send_data('event=list\npdir=/home')
        res = self.response_data.get()
        print('dirpath', end='')
        print(res)
        res = ['/home']
        return res["list_dir"]

    def get_disk_list(self):
        # disk=[]
        self.send_data(208, '获取磁盘列表')
        # disk.append('event=list\npdir=home/2\n')
        # self.send_data(208,'event=list\npdir=home/2\n')
        # self.response_data.put(disk)
        return self.response_data.get()

    # 在发送数据前通知对方相关信息，做好接受准备
    def before_send(self, protocol):
        self.base_socket.send_all(self.padding(tools.encode_dict(protocol)))

    # 数据解析
    def decode_protocol(self, b_data):
        return json.loads(b_data.decode().replace(self.padding_char.decode(), ''))

    # 数据对齐
    def padding(self, bytes_data):
        bytes_data += self.padding_char * (self.protocol_len - len(bytes_data))
        return bytes_data

    # 服务发生异常，通知客户端
    def error(self, msg):
        self.send_data(500, msg, dict(msg=msg))

    def test_msg(self, msg):
        b_data = msg.dict
        self.base_socket.send_all

######################## my  ##############################

    def my_send_files(self, file_name,file_path, write_to):

        file=file_path+'/'+file_name
        print(file)
        with open(file, 'rb') as fp:
            # self.before_send(protocol)
            flag = 0
            md5 = hashlib.md5()

            while chunk := fp.read(10240):  #大文件md5
                md5.update(chunk)

            print(md5.hexdigest())
            # 回到开头
            fp.seek(0, 0)

            while True:
                filedata = fp.read(10240)

                if not filedata:
                    stage = 'finished'
                    str = 'event=upload\naccount='+self.account+'\nstage=' + stage + '\nmd5=' + md5.hexdigest() + '\npdir=' + write_to + '\nfilename=' + file_name + '\n'

                    # print(str)
                    self.my_send_data(str.encode('gbk'))
                    break
                if flag == 0:
                    stage='begin'
                    str = 'event=upload\naccount='+self.account+'\nstage=' + stage + '\nmd5=' + md5.hexdigest() + '\npdir=' + write_to + '\nfilename=' + file_name + '\n'
                    # print(str)
                    self.my_send_data(str.encode('gbk')+filedata)

                    flag += 1
                    continue
                else:
                    stage = 'continue'
                    str = 'event=upload\naccount='+self.account+'\nstage=' + stage + '\nmd5=' + md5.hexdigest() + '\npdir=' + write_to + '\nfilename=' + file_name + '\n'
                    #str += filestr + '\n'

                    # print(str)

                    self.my_send_data(str.encode('gbk')+filedata)
                time.sleep(0.2)
        print("文件发送完毕", file_name)
        return True


    def my_down_load_files(self, file_path, file_name,file_npos):
        #'event=download\naccount='+ [用户名]+'\npdir=' +[文件所在位置, "/"结尾]+'\nname=' +[文件名]'\npos=' [文件开始下载位置]+'\n''
        download_msg = 'event=download\naccount='+ self.account+'\npdir=' +file_path+'/'+'\nname=' +file_name+'\npos=' +file_npos+'\n'
        self.my_send_data(download_msg.encode('gbk'))


    #byte型传输
    def my_send_data(self, msg_data):
        # print(msg)
        # b_data = msg.encode()
        # print(b_data)
        if msg_data:
            self.base_socket.send_all(msg_data)

    def my_send_dir_list(self, account,dir_path):

        list_msg='event=list\naccount='+self.account+'\n' + 'pdir=' + dir_path + '\n'
        self.my_send_data(list_msg.encode('gbk'))
        time.sleep(1)


    def my_get_dir_list(self, protocol):
        file_list_tmp=protocol.split('\n')
        file_list=list()
        #item_file.type=''
        for file in file_list_tmp:
            if file:
                item_file = tools.Dict()
                if file[0] == 'f':
                    item_file.name=file[2:]
                    item_file.type='file'
                    file_list.append(item_file)
                elif file[0] == 'd':
                    item_file.name = file[2:]
                    item_file.type = 'Folder'
                    file_list.append(item_file)


            #print(file)
        Sort_Dict = {1: "type", 2: "name"}
        self.response_data.put(file_list)
        #return file_list

    def get_dir_list2(self):
        time.sleep(1)
        res= self.response_data.get()    #通过队列取目录

        return res





    def my_get_disk_list(self):
        # disk=[]
        # self.send_data(208, '获取磁盘列表')
        # disk.append('event=list\npdir=home/2\n')
        # self.send_data(208,'event=list\npdir=home/2\n')
        # self.response_data.put(disk)
        #self.my_get_dir_list('/home')   #最初的网盘目录
        #self.my_send_dir_list('/home')
        return '/'


