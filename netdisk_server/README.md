# ʹ��˵��(�ݶ�)
����makefile�����ļ���make���ɱ���,��������һ��netdisk_serverֱ������(�����ػ�����)  
```
make
./netdisk_server
```

## ip�Ͷ˿�
��main.cpp��main���������ʼ��������ip��port�޸�

## ���ݿ�
���ݿ�����netdisk,�����û���������ı�����user,�����ļ���Ϣ�ı���file,��ʱд���ڳ�������  
�����Ĺ�������(��Ҫ�ֶ�����)
```
#Ĭ�ϵ����Լ�����������ʼ�Ǹ���ҵ������
mysql -u root -proot123
create database netdisk;
use netdisk;
create table user (account varchar(255), passwd varchar(255));
create table file (md5 varchar(255), status varchar(255), link int);
create table storage (account varchar(255), type varchar (1), pdir varchar(255), name varchar(255), md5 varchar(255));
```

## ������ʽ(�ݶ�,���ܻ���)
C/S����,ֱ�ӷ���������,�ط�����һ��Ϊ2~3���ַ�����\n,��һ���ַ���accepted/completed/failed��ű�ʾ�������,�ڶ����ַ������м�����,�����¼ʧ��/�ɹ�,�������ַ���(Ŀǰֻ�жϵ�������,��ʾ�ӵ�x�ֽڿ�ʼ�ϵ�����)��ʾһЩ�����Ϣ
���η��Ͳ�Ҫ����20480�ֽ�

<strong>��¼</strong>: "event=login\naccount=[�û���]\npasswd=[����]\n"  
<strong>ע��</strong>: "event=register\naccount=[�û���]\npasswd=[����]\n"  

login�����û���account��socket fd  
��"\[\]"���������ݰ����滻(�滻����\[\])  
��û��̫����������ʾ,�õ�'\n'�ָ�,��ر�֤3��'\n',�ɹ���ط�"accepted",ʧ�ܻط�"failed"(�ظ�ע��Ҳ��failed)  

<strong>�ļ��ϴ�</strong>: "event=upload\naccount=[�û���]\nstage=[����ֵ,����˵]\nmd5=[�ļ���md5��]\npdir=[�ϴ����ļ�����Ŀ¼]\nfilename=[�ϴ�����ļ���]\n[�ļ�����(stage=finishʱ��Ҫ�ⲿ��),�����βû��\n]"  
����stageȡbegin��continue��finished,����Ҫmd5 pdir filename������ȷ(���ǵ���Ҫ�첽�������û�)  
beginʱ�������ݿ���ļ����,�������ͬ�������ļ���ֱ��"�봫",�ط�"completed\n",�������ͬ�����������ļ���ϵ�����,�ط�"accepted\nresume upload\n[��x�ֽڿ�ʼ,�����Ǹ�ʮ��������]\n",�����ȫ�µ��ļ�,������ʼ�ϴ���д�����ݿ��¼,�ط�"accepted\n"  
continueʱ���ļ�ĩ����д��,�ط�"accepted\n"  
finishʱ����ļ�����,�ط�"completed\n"  
begin������Ҳ��û������,finishû������

�ļ����������ִ���ļ�ͬĿ¼�µ�fileĿ¼��,�ļ���ͳһ��Ϊ��md5(�÷���md5,������1400+KB��С���ļ��ϴ���֤,������̲���Ӧ��û����)

���ǵ�pythonʵ��md5����Ƚϼ�,php(��ҳ�������������php?)���ֳ�ʵ��,linux md5Ҳ�ȽϺò���,������md5����Ϊ�ļ��ı��

<strong>�г��ļ�</strong>: "event=list\naccount=[�û���]\npdir=[·��,��"/"��ʼд(Ĭ��ÿ����Ŀ¼��/)]\n"  
ͬ��,account��socket��fd��(��Ҫ��login)  
��ѯʧ�ܻط�"failed\n"��һ������,�ɹ��ط�"accepted\n",����ÿ��Ϊ"[f��d,�����ַ�,��ʾ�ļ���Ŀ¼] [����]\n"  
����,Ҫ�г�"/"Ŀ¼�������ļ�,(����ֻ��test.txtһ���ļ�)  
����"event=list\npdir=/"  
�ط�"accepted\nf test.txt\n",f/d�����ּ��пո�

<strong>�ļ��ƶ�</strong>: "event=move\naccount=[�û���]\npdir=[�ļ�����λ��,"/"��β]\nname=[�ļ���]\ndst=[�ƶ�Ŀ��λ��,"/"��β]\n"  
<strong>�ļ�����</strong>: "event=copy\naccount=[�û���]\npdir=[�ļ�����λ��,"/"��β]\nname=[�ļ���]\ndst=[ճ��Ŀ��λ��,"/"��β]\n"  
<strong>�ļ�ɾ��</strong>: "event=remove\naccount=[�û���]\npdir=[�ļ�����λ��,"/"��β]\nname=[�ļ���]\n"  
<strong>�ļ��д���</strong>: "event=mkdir\naccount=[�û���]\npdir=[�ļ�������λ��,"/"��β]\nname=[�ļ�����]\n"  

����û��ô���

<strong>�ļ��и���</strong>: "event=cpdir\naccount=[�û���]\npdir=[�ļ�������λ��,"/"��β]\nname=[�ļ�����]\ndst=[ճ��Ŀ��λ��,"/"��β]\n"  
<strong>�ļ���ɾ��(����������)</strong>: "event=rmdir\naccount=[�û���]\npdir=[�ļ�������λ��,"/"��β]\nname=[�ļ�����]\n"  
<strong>�ļ����ƶ�(����������)</strong>: "event=move\naccount=[�û���]\npdir=[�ļ�������λ��,"/"��β]\nname=[�ļ�����]\ndst=[�ƶ�Ŀ��λ��,"/"��β]\n"  

<strong>�ļ�����</strong>: "event=download\naccount=[�û���]\npdir=[�ļ�����λ��,"/"��β]\nname=[�ļ���]\npos=[�ļ���ʼ����λ��,���Ѿ�����4096�ֽ�,�Ǿͷ�4096,�Ѿ�����8192,�ͷ�8192]\n"  
�ɹ�ʱ�ط�"accepted\n[������]\n[�ļ�����,�����ƴ�]"  

## ��־
��־����netdisk.log,�����½��ļ��е�ˮƽ(ɶ������¼)