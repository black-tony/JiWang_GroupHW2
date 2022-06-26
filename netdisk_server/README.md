# 使用说明(暂定)
进入makefile所在文件夹make即可编译,编译后产生一个netdisk_server直接运行(不是守护进程)  
```
make
./netdisk_server
```

## ip和端口
在main.cpp的main函数里面最开始两个变量ip和port修改

## 数据库
数据库名是netdisk,保存用户名和密码的表单名是user,保存文件信息的表单是file,暂时写死在程序里了  
创建的过程如下(需要手动创建)
```
#默认的在自己虚拟机做的最开始那个作业的设置
mysql -u root -proot123
create database netdisk;
use netdisk;
create table user (account varchar(255), passwd varchar(255));
create table file (md5 varchar(255), status varchar(255), link int);
create table storage (account varchar(255), type varchar (1), pdir varchar(255), name varchar(255), md5 varchar(255));
```

## 交互格式(暂定,可能会大改)
C/S交互,直接发的裸数据,回发数据一般为2~3个字符串接\n,第一个字符串accepted/completed/failed大概表示操作结果,第二个字符串进行简单描述,例如登录失败/成功,第三个字符串(目前只有断点续传有,表示从第x字节开始断点续传)表示一些相关信息
单次发送不要超过20480字节

<strong>登录</strong>: "event=login\naccount=[用户名]\npasswd=[密码]\n"  
<strong>注册</strong>: "event=register\naccount=[用户名]\npasswd=[密码]\n"  

login后会绑定用户的account和socket fd  
用"\[\]"包裹的内容按需替换(替换后无\[\])  
还没做太多错误处理和提示,用的'\n'分隔,务必保证3个'\n',成功会回发"accepted",失败回发"failed"(重复注册也是failed)  

<strong>文件上传</strong>: "event=upload\naccount=[用户名]\nstage=[三个值,下面说]\nmd5=[文件的md5码]\npdir=[上传后文件所在目录]\nfilename=[上传后的文件名]\n[文件内容(stage=finish时不要这部分),这里结尾没有\n]"  
其中stage取begin、continue、finished,均需要md5 pdir filename几项正确(考虑到需要异步处理多个用户)  
begin时进行数据库的文件检查,如果有相同的完整文件会直接"秒传",回发"completed\n",如果有相同但不完整的文件会断点续传,回发"accepted\nresume upload\n[第x字节开始,这里是个十进制整数]\n",如果是全新的文件,正常开始上传并写入数据库记录,回发"accepted\n"  
continue时在文件末继续写入,回发"accepted\n"  
finish时标记文件完整,回发"completed\n"  
begin可以有也可没有内容,finish没有内容

文件保存在与可执行文件同目录下的file目录里,文件名统一改为其md5(用发的md5,进行了1400+KB大小的文件上传验证,传输过程不错应该没问题)

考虑到python实现md5计算比较简单,php(网页版好像间接限制了php?)有现成实现,linux md5也比较好操作,所以用md5码作为文件的标记

<strong>列出文件</strong>: "event=list\naccount=[用户名]\npdir=[路径,从"/"开始写(默认每个根目录是/)]\n"  
同样,account和socket的fd绑定(即要先login)  
查询失败回发"failed\n"和一句描述,成功回发"accepted\n",后面每句为"[f或d,单个字符,表示文件或目录] [名称]\n"  
例如,要列出"/"目录下所有文件,(假设只有test.txt一个文件)  
发送"event=list\npdir=/"  
回发"accepted\nf test.txt\n",f/d和名字间有空格

<strong>文件移动</strong>: "event=move\naccount=[用户名]\npdir=[文件所在位置,"/"结尾]\nname=[文件名]\ndst=[移动目标位置,"/"结尾]\n"  
<strong>文件复制</strong>: "event=copy\naccount=[用户名]\npdir=[文件所在位置,"/"结尾]\nname=[文件名]\ndst=[粘贴目标位置,"/"结尾]\n"  
<strong>文件删除</strong>: "event=remove\naccount=[用户名]\npdir=[文件所在位置,"/"结尾]\nname=[文件名]\n"  
<strong>文件夹创建</strong>: "event=mkdir\naccount=[用户名]\npdir=[文件夹所在位置,"/"结尾]\nname=[文件夹名]\n"  
<strong>文件删除</strong>: "event=remove\naccount=[用户名]\npdir=[文件所在位置,"/"结尾]\nname=[文件名]\n"  

以下没怎么测过

<strong>文件移动(强制覆盖)</strong>: "event=moveensure\naccount=[用户名]\npdir=[文件所在位置,"/"结尾]\nname=[文件名]\ndst=[移动目标位置,"/"结尾]\n"  
<strong>文件复制(强制覆盖)</strong>: "event=copyensure\naccount=[用户名]\npdir=[文件所在位置,"/"结尾]\nname=[文件名]\ndst=[粘贴目标位置,"/"结尾]\n"  
<strong>文件夹复制</strong>: "event=cpdir\naccount=[用户名]\npdir=[文件夹所在位置,"/"结尾]\nname=[文件夹名]\ndst=[粘贴目标位置,"/"结尾]\n"  
<strong>文件夹移动(含内面内容)</strong>: "event=mvdir\naccount=[用户名]\npdir=[文件夹所在位置,"/"结尾]\nname=[文件夹名]\ndst=[移动目标位置,"/"结尾]\n"  
<strong>文件夹复制</strong>: "event=cpdirensure\naccount=[用户名]\npdir=[文件夹所在位置,"/"结尾]\nname=[文件夹名]\ndst=[粘贴目标位置,"/"结尾]\n"  
<strong>文件夹移动(含内面内容)</strong>: "event=mvdirensure\naccount=[用户名]\npdir=[文件夹所在位置,"/"结尾]\nname=[文件夹名]\ndst=[移动目标位置,"/"结尾]\n"  
<strong>文件夹删除(含里面内容)</strong>: "event=rmdir\naccount=[用户名]\npdir=[文件夹所在位置,"/"结尾]\nname=[文件夹名]\n"  

<strong>文件下载</strong>: "event=download\naccount=[用户名]\npdir=[文件所在位置,"/"结尾]\nname=[文件名]\npos=[文件开始下载位置,即已经下了4096字节,那就发4096,已经下了8192,就发8192]\n"  
成功时回发"accepted\n[简单描述]\n[文件内容,二进制打开]"  

## 日志
日志名是netdisk.log,属于新建文件夹的水平(啥都不记录)