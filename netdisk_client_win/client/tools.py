import os
import time
import json
import shutil
import psutil
import platform

from PyQt5.QtCore import QFileInfo
from PyQt5.QtWidgets import QFileIconProvider


class Dict(dict):
    def __init__(self, *args, **kwargs):
        super(Dict, self).__init__(*args, **kwargs)

    def __getattr__(self, item):
        return self.get(item)

    def __setattr__(self, key, value):
        self[key] = value


class ICO:
    FILE_TYPE_ICO = dict()
    FILE_TYPE_ICO["File Folder"] = "static/ico/Folder"
    FILE_TYPE_ICO["Folder"] = "static/ico/Folder"
    FILE_TYPE_ICO["Alias"] = "static/ico/Folder-"
    FILE_TYPE_ICO["jpg File"] = "static/ico/jpg.png"
    FILE_TYPE_ICO["png File"] = "static/ico/png.png"
    FILE_TYPE_ICO["sys File"] = "static/ico/img.png"
    FILE_TYPE_ICO["text File"] = "static/ico/txt.txt"
    FILE_TYPE_ICO["File"] = "static/ico/txt.txt"
    FILE_TYPE_ICO["zip File"] = "static/ico/zip.zip"
    FILE_TYPE_ICO["7z File"] = "static/ico/7z.7z"
    FILE_TYPE_ICO["rar File"] = "static/ico/rar.rar"
    FILE_TYPE_ICO["gz File"] = "static/ico/gz.gz"


def os_exists(abs_path):
    return os.path.exists(abs_path)


def file_size(abs_path):
    bytes_size = os.path.getsize(abs_path)
    k_size = bytes_size / 1024
    if k_size >= 1024:
        k_size /= 1024
        unit = " MB"
        if k_size >= 1024:
            k_size /= 1024
            unit = "GB"
    else:
        unit = " KB"
    return round(k_size, 2), unit, bytes_size


def bytes_to_speed(bytes_num):
    k_size = bytes_num / 1024
    if k_size >= 1024:
        k_size /= 1024
        unit = " MB"
        if k_size >= 1024:
            k_size /= 1024
            unit = "GB"
    else:
        unit = " KB"
    return str(round(k_size, 2)) + unit


def second_to_time(second):
    m, s = divmod(second, 60)
    h, m = divmod(m, 60)
    return "%02d:%02d:%02d" % (h, m, s)


def get_disk():
    sys_name = platform.system()
    disk = []
    if sys_name == "Windows":
        for i in psutil.disk_partitions():
            disk.append(i.device.replace("\\", "/"))
    else:
        disk.append("/home")
    return disk


def listdir(abs_path, include_conceal=True):
    #abs_path='D:/computer_network/grouphw/ndisk/NetWrokDisk-master/client/static/ico'
    provider = QFileIconProvider()
    try:
        list_dir = os.listdir(abs_path)
    except Exception as e:
        return []
    list_dir.sort()
    file_list = list()

    for file in list_dir:
        item_file = Dict()
        if file.startswith(".") and not include_conceal:
            continue
        abs_file_path = os.path.join(abs_path, file)
        item_file.name = file
        item_file.type = provider.type(QFileInfo(abs_file_path))
        try:
            mtime = os.path.getmtime(abs_file_path)
            item_file.last_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(mtime)))
        except Exception:
            item_file.last_time = ""
        try:
            if item_file.type in ["File Folder", "Folder"]:
                item_file.size = ""
                item_file.raw_size = 0
            else:
                size, unit, bytes_size = file_size(abs_file_path)
                item_file.size = str(size) + " " + unit
        except Exception:
            item_file.raw_size = 0
            item_file.size = ""
        file_list.append(item_file)
    Sort_Dict = {1: "type", 2: "name", 3: "last_time", 4: "raw_size"}
    file_list = sorted(file_list, key=lambda x: x[Sort_Dict[1]], reverse=False)
    return file_list


def mkdir(dir_path):
    if not dir_path:
        return False, "不能为空"
    if os.path.exists(dir_path):
        return False, f"{dir_path} 已存在！"
    try:
        os.mkdir(dir_path)
        return True, ""
    except Exception as e:
        return False, f"异常 {str(e)}"


def rename(old, new):
    if not old or not new:
        return False, "不能为空"
    if os.path.exists(new):
        return False, f"{new} 已存在！"
    else:
        try:
            os.renames(old, new)
            return True, ""
        except Exception as e:
            return False, f"异常 {str(e)}"


def remove(abs_path):
    # 删除目录
    if os.path.isdir(abs_path):
        try:
            shutil.rmtree(path=abs_path)
            return True, ""
        except Exception as e:
            return False, f"删除失败 {str(e)}"
    # 删除文件
    else:
        try:
            os.remove(abs_path)
            return True, ""
        except Exception as e:
            return False, f"删除失败{str(e)}"

def padding_data(data, need_len):
    data += b"*" * need_len
    return data

def jsondumps(data):
    return json.dumps(data).encode()

def decode_dict(bytes_data):
    try:
        return json.loads(bytes_data.decode())
    except Exception as e:
        print("decode_dict error", e, bytes_data)

# 编码数据
def encode_dict(dict_data):
    return json.dumps(dict_data).encode()

def list_dir_all(path, name):
    create_root = False
    abs_path = os.path.join(path, name)
    if os.path.isdir(abs_path):    # 发送的是目录
        for home, dirs, files in os.walk(abs_path):
            if not create_root:
                create_root = True
                yield 0, name
            new_home = home.replace(path, '')
            # 获得所有文件夹
            for dirname in dirs:
                yield 0, os.path.join(new_home, dirname)

            # 获得所有文件
            for filename in files:
               yield 1, os.path.join(new_home, filename)
    else:
        yield 1, name

