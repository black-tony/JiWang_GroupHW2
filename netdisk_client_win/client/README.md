# 最终界面
需要修改Main_nd.py 156行ip和port

需要库
pip install PyQt5
pip install PyQt5-tools


运行Main_nd.py即可
（bug 可能注册完需要重新运行程序才不会导致切换主界面时卡死 所以一次最好登录一个正确的）



效果图见上一级README.md

生成exe:
pip install pyinstaller

示例1，动态库形式打包exe程序：
pyinstaller -D -w  Main_nd.py

示例2，静态形式打包成一个单独的exe程序：
pyinstaller -F -w  Main_nd.py
