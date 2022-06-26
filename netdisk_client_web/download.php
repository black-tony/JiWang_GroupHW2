<?php
session_start();
$host="192.168.80.230";
$port=4000;
$account=$_SESSION['account'];
if (strcmp($_POST['pdir'], $_SESSION['pdir'])) {
    $_SESSION['pdir'] = $_POST['pdir'];
}
session_write_close();

header('Content-type:text/html;charset=gb18030');
//打开数据库
$mysqli=new mysqli('localhost','root','root123','netdisk');
if (mysqli_connect_errno()){
    echo "连接失败，原因为：".mysqli_connect_error();
    exit();
}
//设置中文字符集
$result = $mysqli->query("set names gbk");
$query = "select * from storage where pdir=\"".$_POST["pdir"]."\" and account = \"".$account."\" and name = \"".$_POST['name']."\"";
$result = $mysqli->query($query);
$row=$result->fetch_assoc();
$file_dir = "/usr/netdisk-file/";     // 下载文件存放目录
$file_name = $row['md5'];        // 下载文件名
//echo $file_dir.$file_name;
$result->close();
//关闭数据库
$mysqli->close();
// 检查文件是否存在
if (!file_exists($file_dir.$file_name)) {
    header('HTTP/1.1 404 NOT FOUND');
} else {
    // 以只读和二进制模式打开文件
    $file = fopen($file_dir.$file_name, "rb");

    // 告诉浏览器这是一个文件流格式的文件
    Header("Content-type: application/octet-stream");
    // 请求范围的度量单位
    Header("Accept-Ranges: bytes");
    // Content-Length是指定包含于请求或响应中数据的字节长度
    Header("Accept-Length: ".filesize($file_dir.$file_name));
    // 用来告诉浏览器，文件是可以当做附件被下载，下载后的文件名称为$file_name该变量的值。
    Header("Content-Disposition: attachment; filename=".$_POST["name"]);

    // 读取文件内容并直接输出到浏览器
    echo fread($file, filesize($file_dir.$file_name));
    fclose($file);

    exit ();
}
?>