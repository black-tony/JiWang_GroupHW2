# ʹ��˵��(�ݶ�)
����makefile�����ļ���make���ɱ���,��������һ��netdisk_serverֱ������(�����ػ�����)  
```
make
./netdisk_server
```

## ip�Ͷ˿�
��main.cpp��main���������ʼ��������ip��port�޸�

## ���ݿ�
���ݿ�����netdisk,�����û���������ı�����user,��ʱд���ڳ�������  
�����Ĺ�������(��Ҫ�ֶ�����)
```
#Ĭ�ϵ����Լ�����������ʼ�Ǹ���ҵ������
mysql -u root -proot123
create database netdisk;
create table user (account varchar(255), passwd varchar(255));
```

## ������ʽ(�ݶ�,���ܻ���)
C/S����,ֱ�ӷ���������

��¼: "event=login\naccount=\[�û���]\npasswd=[����]\n"  
ע��: "event=register\naccount=\[�û���]\npasswd=[����]\n"  

��"\[\]"���������ݰ����滻(�滻����\[\])  
��û��̫����������ʾ,�õ�'\n'�ָ�,��ر�֤3��'\n',�ɹ���ط�"accepted",ʧ�ܻط�"failed"(�ظ�ע��Ҳ��failed)

## ��־
��־����netdisk.log,�����½��ļ��е�ˮƽ(ɶ������¼)