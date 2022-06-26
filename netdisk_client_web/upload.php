<meta charset="gbk">
<?php
if($_FILES["file"]["name"] == null || !strcmp($_FILES["file"]["name"], "")) {
    echo "<script>hitory.back();</script>";
}
$md5 = md5_file($_FILES["file"]["tmp_name"]);
if (!file_exists("/usr/netdisk-file/".$md5))
{
    // 如果目录不存在该文件则将文件上传到目录下
    move_uploaded_file($_FILES["file"]["tmp_name"], "/usr/netdisk-file/".$md5);
}

$host="192.168.80.230";
$port=4000;
// create a socket
$socket=socket_create(AF_INET, SOCK_STREAM, 0) or die("Could not create a socket\n");
// connect server(C++ socket)
if (socket_connect($socket, $host, $port) == false) {
    // connect failed
    echo "connect failed";
    socket_close($socket);
}
else {
    session_start();
    $account=$_SESSION['account'];
    $event="event=upload\naccount=".$account."\nstage=finished\nmd5=".$md5."\npdir=".$_SESSION["pdir"]."\nfilename=".$_FILES["file"]["name"]."\n";
    session_write_close();
    $buf;
    socket_send($socket, $event, strlen($event), 0);
    socket_recv($socket, $buf, 4096, 0);
    socket_close($socket);
    echo "<script>alert(\"文件上传成功!\");history.back()</script>";
}

?>