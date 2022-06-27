# -*- coding: cp936 -*-
from PyQt5.QtCore import Qt, pyqtSignal, QFileInfo
from PyQt5.QtWidgets import (QWidget, QTableWidgetItem, QAbstractItemView, QFileIconProvider, QMenu, QMessageBox,
                             QApplication)


from main_window import Ui_Form
from sub_windoow import Ui_widget
from progress import Ui_transfer
from tools import Dict, ICO, os
import tools

DEBUG =1

class Base:
    @classmethod
    def fmt_pack(cls, widget=None, **kwargs):
        """
        ��ʽ������֮ǰ���ݲ����ĸ�ʽ
        """
        if kwargs is None:
            data = Dict()
        else:
            data = Dict(kwargs)
        return Dict(widget=widget, data=data)

    @staticmethod
    def question(package):
        res = QMessageBox.question(package.widget, "ɾ��", "ȷ��ɾ����", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if res == QMessageBox.Yes:
            return True
        return False


class ProgressWindow(Ui_transfer, QWidget):
    def __init__(self):
        super(Ui_transfer, self).__init__()
        self.setupUi(self)
        self.setWindowModality(Qt.ApplicationModal)

    def set_status(self, data):
        self.operation.setText(data.operation)
        self.name.setText(data.name)
        # ����
        self.progress.setValue(int(data.progress) or 1)
        # ����
        self.detail.setText(data.detail)
        # �����ٶ�
        self.speed.setText(data.speed)
        # ����ʱ��
        self.elapsed_time.setText(data.elapsed_time)
        # Ԥ�ƻ���ʱ��
        self.remaining_time.setText(data.remaining_time)

    def show_window(self):
        self.show()

    def hide_window(self):
        self.hide()

    def closeEvent(self, event) -> None:
        reply = QMessageBox.question(self, "�ļ�����", "�Ƿ�ȡ�����ͣ�", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.on_close:
                self.on_close()
        else:
            event.ignore()


class InputWindow(Base, Ui_widget, QWidget):
    def __init__(self, accept=None):
        super(Ui_widget, self).__init__()
        self.setupUi(self)
        self.accept = accept
        self.package = None
        self.buttonBox.accepted.connect(self.ok)
        self.buttonBox.rejected.connect(self.hide_window)
        self.setWindowModality(Qt.ApplicationModal)

    def register(self, package):
        self.package = package

    def ok(self):
        self.package.data.text = self.dir_name.text()
        self.package.data.ok(self.package)

    def show_window(self):
        self.show()

    def set_title(self, package):
        self.setWindowTitle(package.data.title)

    def set_text(self, package):
        self.dir_name.setText(package.data.text)

    def hide_window(self):
        self.hide()
        self.package = None
        self.accept = None
        self.set_text(self.fmt_pack(text=str()))


class MainWindow(Base, Ui_Form, QWidget):
    set_progress = pyqtSignal(Dict)
    show_progress = pyqtSignal()
    hide_progress = pyqtSignal()

    def __init__(self, local_c, remote_c, module_c,account,password):
        super().__init__()
        self.account=account
        self.table_headers = ['�ļ�����', '�ļ���С', '�ļ�����', '�޸�ʱ��']
        self.setupUi(self)  # �̳�������

        self.local_table_func = tools  # ������һЩ���Բ��������ļ�io�ĺ���
        self.remote_table_func = remote_c  # �����˿�����Զ�̷�������һЩ����
        self.modules = module_c  # ���������������
        self.remote_table_func.on_error = self.on_error

        self.set_progress.connect(self.modules.progress_window.set_status)
        self.show_progress.connect(self.modules.progress_window.show_window)
        self.hide_progress.connect(self.modules.progress_window.hide_window)
        self.init_local_table()  # ��ʼ�������ļ����
        self.init_remote_table()  # ��ʼ�������ļ����


    def get_local_selected(self):
        selected_list = list()
        # self.LocalFiles.selectionModel().selectedColumns()
        select_rows = self.LocalFiles.selectionModel().selectedRows()
        if len(select_rows):
            for i in select_rows:
                select_name = self.LocalFiles.item(i.row(), 0).text()
                base_path = self.get_comboBox_first_item(self.fmt_pack(self.LocalComboBox))
                selected_list.append((base_path, select_name))
        return selected_list

    def get_remote_selected(self):
        selected_list = list()
        select_rows = self.RemoteFiles.selectionModel().selectedRows()
        if len(select_rows):
            for i in select_rows:
                select_name = self.RemoteFiles.item(i.row(), 0).text()
                base_path = self.get_comboBox_first_item(self.fmt_pack(self.RemoteComboBox))
                selected_list.append((base_path, select_name))
        return selected_list

    def selecte_send(self):
        select_rows = self.get_local_selected()
        if len(select_rows):
            for path, name in select_rows:
                self.local_upload(self.fmt_pack(local_path=path, name=name))

        else:
            selected_list = list()
            select_rows = self.get_remote_selected()
            if len(select_rows):
                for path, name in select_rows:
                    selected_list.append(os.path.join(path, name))
            if selected_list:
                self.remote_downloads(selected_list)

    def select_del(self):
        select_rows = self.get_local_selected()
        if select_rows:
            removes_list = list()
            for path, name in select_rows:
                removes_list.append(os.path.join(path, name))
            self.remove_dirs(self.fmt_pack(removes_list=removes_list))
        else:
            select_rows = self.get_remote_selected()

    def remove_dirs(self, package):
        del_count = len(package.data.removes_list)
        package.data.title = "�����������"
        package.data.text = f"����ɾ�� {del_count}������ɾ���󲻿ɳ��أ�"
        if self.aer_you_sure(package):
            self.show_progress.emit()
            for i in package.data.removes_list:
                if self.set_progress:
                    progress_data = tools.Dict(
                        operation="����ɾ��",
                        name=os.path.basename(i),
                        progress=100,
                        speed="---",
                        detail="",
                        elapsed_time="00:00:00",
                        remaining_time="00:00:00"
                    )
                    self.set_progress.emit(progress_data)
                QApplication.processEvents()
                self.local_table_func.remove(i)
            self.hide_progress.emit()
            self.local_reload_table()


    def keyPressEvent(self, evt):
        # control + s
        if evt.key() == Qt.Key_S and evt.modifiers() == Qt.ControlModifier:
            self.selecte_send()
        # ˢ��
        if evt.modifiers() == Qt.ControlModifier and evt.key() == Qt.Key_R:
            self.local_reload_table()
            self.remote_reload()
        # ɾ��
        if evt.modifiers() == Qt.ControlModifier and evt.key() == Qt.Key_D:
            self.select_del()
        # print(evt.key())
        # if evt.key() == Qt.Key_Control:

        # if evt.modifiers() == Qt.ControlModifier:
        #     print("you want del ?")
        # if evt.modifiers() == Qt.AltModifier:
        #     print("you want send ?")
        # if evt.modifiers() == Qt.ShiftModifier:
        #     print("you press shift")

    def init_local_table(self):
        # �����̷��б�
        #self.set_disk(self.fmt_pack(widget=self.LocalComboBox, disk_list=self.local_table_func.get_disk()))
        print("�����û�",end='')
        print(self.account)
        disk=self.local_table_func.get_disk()
        disk.append('D:/��������')
        disk.append('D:/computer_network')
        self.set_disk(self.fmt_pack(widget=self.LocalComboBox, disk_list=disk))
        # �󶨴����л��ص�����
        self.bind_comboBox_change_event(self.fmt_pack(self.LocalComboBox, callbak=self.on_local_change_disk))

        # ��ӱ�ͷ
        self.add_table_header(self.fmt_pack(self.LocalFiles, headers=self.table_headers))

        # ��ȡ��Ŀ¼�ļ�������ӵ��ļ������
        list_dir = lambda: self.local_table_func.listdir(
            self.get_comboBox_first_item(self.fmt_pack(self.LocalComboBox)))
        self.add_item_on_file_table(self.fmt_pack(self.LocalFiles, listdir=list_dir()))

        # ��ӱ��˫���¼�(��һ��)
        self.bind_doubleClicked(self.fmt_pack(self.LocalFiles,
                                              get_listdir=list_dir,
                                              curpath=self.get_local_path,
                                              comboBox=self.LocalComboBox
                                              ) ,ctype=0)
        # ����һ����
        self.LocalLastDir.clicked.connect(lambda: self.go_back(self.fmt_pack(self.LocalComboBox,
                                                                             listdir=list_dir,
                                                                             file_widget=self.LocalFiles
                                                                             )))

        # �����Ҽ��˵�
        button_func = Dict(�ϴ�=self.my_local_upload,
                           ˢ��=self.local_reload_table,
                           ɾ��=self.local_remove_and_reload,
                           �½��ļ���=self.local_ready_mkdir,
                           ������=self.local_ready_rename,
                           �����ļ�=self.copy,
                           �����ļ���=self.copydir)
        get_local_path = lambda: self.get_comboBox_first_item(self.fmt_pack(self.LocalComboBox))
        get_remote_path = lambda: self.get_comboBox_first_item(self.fmt_pack(self.RemoteComboBox))
        data = self.fmt_pack(self.LocalFiles, menu=button_func, get_local_path=get_local_path,
                             get_remote_path=get_remote_path)
        # ���˵��󶨵�ָ��������
        self.table_add_right_key_menu(data)

    def init_remote_table(self):
        # �����̷��б�
        disk_list_tmp=[]
        disk_list_tmp.append(self.remote_table_func.my_get_disk_list())
        print('init_remote_table ����' ,end='')
        print(disk_list_tmp)
        self.set_disk(
            self.fmt_pack(widget=self.RemoteComboBox, disk_list=disk_list_tmp))

        # �󶨴����л��ص�����
        self.bind_comboBox_change_event(self.fmt_pack(self.RemoteComboBox, callbak=self.on_remote_change_disk))

        # ��ӱ�ͷ
        self.add_table_header(self.fmt_pack(self.RemoteFiles, headers=self.table_headers))

        # ��ȡ��Ŀ¼�ļ�������ӵ��ļ������
        dir_path=self.get_comboBox_first_item(self.fmt_pack(self.RemoteComboBox))

        list_msg='event=list\naccount='+self.account + '\npdir=' + dir_path + '\n' #��ʼ����ȡ��Ŀ¼

        self.remote_table_func.my_send_data(list_msg.encode('gbk'))

        #self.my_send_data('event=list\n' + 'pdir=' + dir_path + '\n')

        list_dir = lambda: self.remote_table_func.get_dir_list2()
        #print(list_dir)
        '''list_dir = lambda: self.remote_table_func.my_send_dir_list(
            self.get_comboBox_first_item(self.fmt_pack(self.RemoteComboBox)))'''

        self.add_item_on_file_table(self.fmt_pack(self.RemoteFiles, listdir=list_dir()))

        # ��ӱ��˫���¼�(��һ��)
        self.bind_doubleClicked(self.fmt_pack(self.RemoteFiles,
                                              get_listdir=list_dir,
                                              curpath=self.get_remote_path,
                                              comboBox=self.RemoteComboBox
                                              ),ctype=1)
        # (��һ��)
        self.RemoteLastDir.clicked.connect(lambda: self.go_back(self.fmt_pack(self.RemoteComboBox,
                                                                              listdir=list_dir,
                                                                              file_widget=self.RemoteFiles
                                                                              )))
        # �����Ҽ��˵�
        button_func = Dict(����=self.remote_download,
                           ˢ��=self.remote_reload,
                           ɾ��=self.remote_remove,
                           �½��ļ���=self.remote_mkdir,
                           ������=self.remote_rename)

        get_local_path = lambda: self.get_comboBox_first_item(self.fmt_pack(self.LocalComboBox))
        get_remote_path = lambda: self.get_comboBox_first_item(self.fmt_pack(self.RemoteComboBox))
        data = self.fmt_pack(self.RemoteFiles, menu=button_func, get_local_path=get_local_path,
                             get_remote_path=get_remote_path)
        # ���˵��󶨵�ָ��������
        self.table_add_right_key_menu(data)

    def bind_doubleClicked(self, package,ctype):
        package.widget.doubleClicked.connect(lambda x: self._to_next_node(x, package,ctype))

    @classmethod
    def bind_comboBox_change_event(cls, package):
        """
        ������������¼�
        """
        package.widget.currentIndexChanged.connect(package.data.callbak)

    def on_error(self, data):
        print("modele_on_error: ", data)

    def on_local_change_disk(self):
        """
        �����л����̷�
        """
        next_dir_list = self.local_table_func.listdir(Dict(path=self.LocalComboBox.currentText()))
        print("�����л��̷�", self.LocalComboBox.currentText())
        #self.BaseSocket.send_all('event=list\npdir=/home'.encode())

        if next_dir_list:
            self.clear_table_files(self.fmt_pack(self.LocalFiles))
            self.add_item_on_file_table(self.fmt_pack(self.LocalFiles, listdir=next_dir_list))

    def on_remote_change_disk(self):
        """
        �����л����̷�
        """
        print("Զ���л��̷�", self.RemoteComboBox.currentText())
        next_dir_list = self.remote_table_func.get_dir_list(self.RemoteComboBox.currentText())
        if next_dir_list:
            self.clear_table_files(self.fmt_pack(self.RemoteFiles))
            self.add_item_on_file_table(self.fmt_pack(self.RemoteFiles, listdir=next_dir_list))
            # self.remote_reload(self.fmt_pack())

    def on_progress_window_close(self):
        print("on_progress_window_close")

    def local_upload(self, package):
        print('package',end='')
        print(package)
        # abs_path = os.path.join(package.data.local_path, package.data.name)
        for flag, item in tools.list_dir_all(package.data.local_path, package.data.name):
            self.show_progress.emit()
            if flag == 0:  # ��Ҫ����Ŀ¼
                write_to = self.get_comboBox_first_item(self.fmt_pack(self.RemoteComboBox))
                self.set_progress.emit(Dict(
                    operation="����Ŀ¼",
                    name=item,
                    progress=100,
                    detail="�������",
                    speed="---",
                    elapsed_time="00:00:00",
                    remaining_time="00:00:00"
                ))
                QApplication.processEvents()
                self.remote_table_func.os_mkdir(os.path.join(write_to, item))
                print(f"����Ŀ¼:{item}")
            else:  # �����ļ�
                abs_path = os.path.join(package.data.local_path, item)
                base_write_to = self.get_comboBox_first_item(self.fmt_pack(self.RemoteComboBox))
                #base_write_to='/home'
                write_to = os.path.dirname(os.path.join(base_write_to, item))
                print(abs_path)
                print(base_write_to)
                print(write_to)
                try:
                    #self.remote_table_func.send_files([abs_path], write_to, self.set_progress)
                    self.remote_table_func.my_send_files([abs_path], write_to)
                    if DEBUG:
                        print(abs_path)
                        print(base_write_to)
                        print(write_to)
                except Exception as e:
                    print("12344")

        self.hide_progress.emit()
        self.remote_reload(package)

    def local_ready_mkdir(self, package):
        """
        ���ش����ļ�
        """
        package.data.local = True
        package.data.mkdir = True
        package.data.path = package.data.local_path
        package.data.ok = self.input_ok
        self.modules.input_window.register(package)
        self.modules.input_window.show_window()
        self.modules.input_window.set_title(self.fmt_pack(title="����Ŀ¼"))

    def local_ready_rename(self, package):
        """
        �����������ļ�
        """
        package.data.local = True
        package.data.rename = True
        package.data.path = package.data.local_path
        package.data.ok = self.input_ok
        self.modules.input_window.register(package)
        self.modules.input_window.show_window()
        self.modules.input_window.set_title(self.fmt_pack(title="������"))
        self.modules.input_window.set_text(self.fmt_pack(text=package.data.name))

    def local_ready_del(self, package):
        """
        ɾ������ָ����
        """
        abs_path = os.path.join(package.data.local_path, package.data.name)
        self.local_table_func.remove(abs_path)

    def local_reload_table(self, package=None):
        """���¼��ر����ļ��б�"""
        package = self.fmt_pack(self.LocalFiles)
        self.clear_table_files(package)
        package.data.listdir = self.local_table_func.listdir(
            self.get_comboBox_first_item(self.fmt_pack(self.LocalComboBox)))
        self.add_item_on_file_table(package)

    def local_remove_and_reload(self, package):
        """
        ɾ��Ŀ¼���ļ� �������¼����б�
        """
        package.data.title = "�����������"
        package.data.text = "ɾ���󲻿ɳ��أ�"
        if self.aer_you_sure(package):
            self.local_ready_del(package)
            self.local_reload_table(package)

    def remote_download(self, package):
        # for flag, item in tools.list_dir_all(package.data.remote_path, package.data.name):
        #     if flag == 0:   # ��Ҫ����Ŀ¼
        #         write_to = self.get_comboBox_first_item(self.fmt_pack(self.RemoteComboBox))
        #         self.remote_table_func.os_mkdir(os.path.join(write_to, item))
        #     else:   # �����ļ�
        #         abs_path = os.path.join(package.data.local_path, item)
        #         base_write_to = self.get_comboBox_first_item(self.fmt_pack(self.RemoteComboBox))
        #         write_to = os.path.dirname(os.path.join(base_write_to, item))
        #         self.remote_table_func.send_files([abs_path], write_to)
        # tools.list_dir_all()
        self.remote_table_func.down_load_files([os.path.join(package.data.remote_path, package.data.name)],
                                               package.data.local_path)

    def remote_downloads(self, files):
        local_path = self.get_comboBox_first_item(self.fmt_pack(self.LocalComboBox))
        self.remote_table_func.down_load_files(files, local_path)

    def remote_reload(self, package=None):
        # ��ȡ��Ŀ¼�ļ�������ӵ��ļ������
        '''list_dir = self.remote_table_func.get_dir_list(self.get_comboBox_first_item(self.fmt_pack(self.RemoteComboBox)))
        self.clear_table_files(self.fmt_pack(self.RemoteFiles))
        self.add_item_on_file_table(self.fmt_pack(self.RemoteFiles, listdir=list_dir))
        self.add_table_header(self.fmt_pack(self.RemoteFiles, headers=self.table_headers))'''
        self.clear_table_files(self.fmt_pack(self.RemoteFiles))
        # ��ȡ��Ŀ¼�ļ�������ӵ��ļ������
        dir_path=self.get_comboBox_first_item(self.fmt_pack(self.RemoteComboBox))
        #print(dir_path)
        list_msg='event=list\naccount='+self.account + '\npdir=' + dir_path + '\n'
        self.remote_table_func.my_send_data(list_msg.encode('gbk'))

        list_dir = lambda: self.remote_table_func.get_dir_list2()
        print(list_dir)

        self.add_item_on_file_table(self.fmt_pack(self.RemoteFiles, listdir=list_dir()))


    def remote_mkdir(self, package):
        package.data.remote = True
        package.data.mkdir = True
        package.data.path = package.data.remote_path
        package.data.ok = self.input_ok
        self.modules.input_window.register(package)
        self.modules.input_window.show_window()
        self.modules.input_window.set_title(self.fmt_pack(title="����Ŀ¼"))
        #print('mkdir@@@@@')
        #print(package.data.path)
        #print(package.data.title)
        #mkdir_msg = 'event=mkdir\naccount='+self.account+'\npdir='+'\nname='+'\n'
        #self.remote_table_func.my_send_data(mkdir_msg.encode('gbk'))

    def remote_remove(self, package):
        if self.aer_you_sure(self.fmt_pack(self, title="�����������", text="ɾ�����ɳ���!")):
            self.remote_table_func.os_remove(os.path.join(package.data.remote_path, package.data.name))
            self.remote_reload(package)

    def remote_rename(self, package):
        package.data.remote = True
        package.data.rename = True
        package.data.path = package.data.remote_path
        package.data.ok = self.input_ok
        self.modules.input_window.register(package)
        self.modules.input_window.show_window()
        self.modules.input_window.set_title(self.fmt_pack(title="������"))
        self.modules.input_window.set_text(self.fmt_pack(text=package.data.name))

    def copy(self):
        print('copy')

    def copydir(self):
        print('copydir')


    def get_local_path(self):
        return self.LocalComboBox.currentText()

    def get_remote_path(self):
        return self.RemoteComboBox.currentText()


    def my_local_upload(self, package):
        #print(package)
        abs_path = os.path.join(package.data.local_path)
        base_write_to = self.get_comboBox_first_item(self.fmt_pack(self.RemoteComboBox))
        #base_write_to='/home'
        write_to = os.path.dirname(os.path.join(base_write_to))
        file_name=package.data.name
        #print(file_name)
        #print(abs_path)
        #print(base_write_to)
        #print(write_to)
        self.remote_table_func.my_send_files(str(file_name), str(abs_path), str(base_write_to))
        try:
            #self.remote_table_func.send_files([abs_path], write_to, self.set_progress)
            #self.remote_table_func.my_send_files(file_name,str(abs_path), str(base_write_to))
            if DEBUG:
                print(abs_path)
                print(base_write_to)
                print(write_to)
        except Exception as e:
            print("12344")


        self.remote_reload(package)









    # ==========================Զ���뱾�ص��ļ�����÷���=======================================+#

    def _to_next_node(self, evt, package,ctype):
        f_widget = package.widget
        file_type = f_widget.item(f_widget.currentRow(), 2).text()
        click_name = f_widget.item(f_widget.currentRow(), 0).text()
        cur_path = package.data.curpath()
        next_path = os.path.join(cur_path, click_name)
        if file_type == "File Folder" or file_type == "Folder":
            if not ctype:
                next_path = os.path.join(cur_path, click_name + "/")
                self.set_comboBox_text(self.fmt_pack(package.data.comboBox, text=next_path))
                package.data.listdir = package.data.get_listdir()
                self.clear_table_files(package)
                self.add_item_on_file_table(package)
            else:
                self.remote_table_func.my_send_dir_list(next_path)
                self.set_comboBox_text(self.fmt_pack(package.data.comboBox, text=next_path))

        else:
            if "Local" in f_widget.objectName():
                print("��%s" % next_path)
                os.system(next_path)
            else:
                QMessageBox.warning(self.RemoteFiles, '��ʾ', '���ܴ�Զ���ļ�')

    def go_back(self, package):
        cur_path = self.get_comboBox_first_item(package)[:-1]  # dirname�����Է�б��������Ŀ¼����Ҫ�����һ����б��ȥ��
        last_path = os.path.dirname(cur_path) + "/"  # �ڼ���ȥ
        self.set_comboBox_text(self.fmt_pack(package.widget, text=last_path))
        package.data.listdir = package.data.listdir()
        package.widget = package.data.file_widget
        self.clear_table_files(package)
        self.add_item_on_file_table(package)

    @staticmethod
    def set_comboBox_text(package):
        package.widget.setCurrentText(package.data.text)

    def msg_box(self, package):
        QMessageBox.warning(self, package.title, package.text)

    @staticmethod
    def aer_you_sure(package):
        if QMessageBox.question(package.widget, package.data.title, package.data.text) == QMessageBox.Yes:
            return True
        return False

    def input_ok(self, package):
        """
        ��������Ŀ¼���߸�����Ŀ¼�����ļ����ֺ����ת������ж����ַ�
        """
        if package.data.local:
            abs_path = os.path.join(package.data.local_path, package.data.text)
            if package.data.mkdir:
                status, msg = self.local_table_func.mkdir(abs_path)

                if status is not True:
                    print(msg)
                else:
                    self.modules.input_window.hide_window()
                    self.local_reload_table(self.fmt_pack())
            else:
                old_path = os.path.join(package.data.local_path, package.data.name)
                status, msg = self.local_table_func.rename(old_path, abs_path)
                if status is not True:
                    print(msg)
                else:
                    self.modules.input_window.hide_window()
                    self.local_reload_table(self.fmt_pack())
        else:
            abs_path = os.path.join(package.data.remote_path, package.data.text)
            if package.data.mkdir:
                #self.remote_table_func.os_mkdir(abs_path)
                #@@@@@
                dir_path=self.get_comboBox_first_item(self.fmt_pack(self.RemoteComboBox))
                mkdir_msg = 'event=mkdir\naccount=' + self.account + '\npdir=' +dir_path+ '\nname='+package.data.text + '\n'
                self.remote_table_func.my_send_data(mkdir_msg.encode('gbk'))

                #self.remote_table_func.my_send_data()
                self.modules.input_window.hide_window()
            else:
                old_path = os.path.join(package.data.remote_path, package.data.name)
                self.remote_table_func.os_rename(old_path, abs_path)
                self.modules.input_window.hide_window()
                self.local_reload_table(self.fmt_pack())
            self.remote_reload(package)

    @classmethod
    def add_table_header(cls, package):
        """�����ļ���ͷ"""
        # ���ñ�ͷ���ɼ�������������һ��
        package.widget.verticalHeader().setVisible(False)
        # SelectionBehavior�������ڿ���ѡ����Ϊ���������ݵ�λ����ָѡ��ʱѡ�������ǰ��С����л��ǰ�����ѡ������ѡ����
        package.widget.setSelectionBehavior(QAbstractItemView.SelectRows)
        # �����Ͳ���QTreeWidget�У������ַ����������������ݵı༭��editTriggers�����༭��editItem�����༭��openPersistentEditor�򿪳־ñ༭����
        package.widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # Ӧ�������õ����ʱ��ѡ�ж�����
        package.widget.setColumnCount(4)
        # �������Ҽ�
        package.widget.setContextMenuPolicy(Qt.CustomContextMenu)
        for index, item_name in enumerate(package.data.headers):
            item = QTableWidgetItem()
            item.setText(item_name)
            package.widget.setHorizontalHeaderItem(index, item)
        package.widget.setRowCount(0)

    @classmethod
    def add_item_on_file_table(cls, package):
        """
        ��ָ�����������ָ�����ض���ʽ��������
        """

        for index, file_obj in enumerate(package.data.listdir):
            file_obj = Dict(file_obj)
            # �������
            package.widget.insertRow(index)

            # =============�ļ�ͼ��
            item0 = QTableWidgetItem()
            item0.setText(file_obj.name)
            provider = QFileIconProvider()
            item0.setIcon(provider.icon(QFileInfo(ICO.FILE_TYPE_ICO.get(file_obj.type, "ico/txt.txt"))))
            # f_t_widget.setRowHeight(index, 20)
            package.widget.setItem(index, 0, item0)

            # =============�ļ���С
            item3 = QTableWidgetItem()
            # item3.setFont(self.fileInfoWidget.global_row_font)
            item3.setText(file_obj.size)
            package.widget.setItem(index, 1, item3)

            # =============�ļ�����
            item2 = QTableWidgetItem()
            # item2.setFont(self.fileInfoWidget.global_row_font)
            # fileType = provider.type(QFileInfo(abs_file_path))
            item2.setText(file_obj.type)
            package.widget.setItem(index, 2, item2)

            # ============����޸�ʱ��
            item1 = QTableWidgetItem()
            # item1.setFont(self.fileInfoWidget.global_row_font)
            # mtime = os.path.getmtime(abs_file_path)
            item1.setText(file_obj.last_time)
            package.widget.setItem(index, 3, item1)
        return True

    def table_add_right_key_menu(self, package):
        """
        �󶨱��Ҽ�����
        pos�Ҽ�ʱ������ݽ�ȥ
        """
        package.widget.customContextMenuRequested.connect(lambda pos: self.on_right_click(pos, package))

    @classmethod
    def on_right_click(cls, pos, package):
        row_num = -1
        select_name = str()
        try:
            row_num = package.widget.selectionModel().selection().indexes()[0].row()
            select_name = package.widget.item(row_num, 0).text()
        except IndexError:
            pass

        menu = QMenu()
        for value, func in package.data.menu.items():
            menu.addAction(value)
            # item_menu = menu.addAction(value)
            # menu_map[item_menu] = func

        # ��ʾ�˵���������һ����ѡ������߿�
        action = menu.exec_(package.widget.mapToGlobal(pos))
        if not action:
            print("δѡ���κ�ѡ��")
            return

        # ѡ�еĲ���
        select_action = action.text()
        # û��ѡ���ļ�ʱ����ʹ����Щ����
        if row_num == -1 and select_action in ["�ϴ�", "����", "������", "ɾ��"]:
            QMessageBox.warning(package.widget, "����", "��ѡ��Ҫ�༭���ļ�")
            return

        # ��ȡ������Ӧ�ĺ���
        button_func = package.data.menu[select_action]
        standard_data = cls.fmt_pack(name=select_name,
                                     local_path=package.data.get_local_path(),
                                     remote_path=package.data.get_remote_path())
        button_func(standard_data)

    @classmethod
    def set_disk(cls, package):
        for i in package.data.disk_list:
            package.widget.addItem(i)

    @classmethod
    def clear_table_files(cls, package):
        if package.widget.rowCount() > 0:
            for row in range(package.widget.rowCount()):
                package.widget.removeRow(0)

    @classmethod
    def get_comboBox_first_item(cls, package):
        return package.widget.currentText()
