# 使用说明(暂定)
进入makefile所在文件夹make即可编译,编译后产生一个netdisk_server直接运行(不是守护进程)  
```
make
./netdisk_server
```

## ip和端口
在main.cpp的main函数里面最开始两个变量ip和port修改

## 数据库
数据库名是netdisk,保存用户名和密码的表单名是user,暂时写死在程序里了  
创建的过程如下(需要手动创建)
```
#默认的在自己虚拟机做的最开始那个作业的设置
mysql -u root -proot123
create database netdisk;
create table user (account varchar(255), passwd varchar(255));
```

## 交互格式(暂定,可能会大改)
C/S交互,直接发的裸数据

登录: "event=login\naccount=\[用户名]\npasswd=[密码]\n"  
注册: "event=register\naccount=\[用户名]\npasswd=[密码]\n"  

用"\[\]"包裹的内容按需替换(替换后无\[\])  
还没做太多错误处理和提示,用的'\n'分隔,务必保证3个'\n',成功会回发"accepted",失败回发"failed"(重复注册也是failed)

## 日志
日志名是netdisk.log,属于新建文件夹的水平(啥都不记录)