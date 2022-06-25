# 最终界面
需要修改Main_nd.py 156行ip和port

需要库
pip install PyQt5
pip install PyQt5-tools


运行Main_nd.py即可
（bug 可能注册完需要重新运行程序才不会导致切换主界面时卡死 所以一次最好登录一个正确的）

因为没有修改c/s交互代码所以moudle.py 119行初始化网盘界面是注释的
#self.init_remote_table()  # 初始化本地文件表格

效果图见上一级README.md

