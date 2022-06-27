<?php
header("content-type:text/html; charset=gbk");
$passwd=$_POST["passwd"];
$len = strlen($passwd);
$upper = false;
$lower = false;
$other = false;
$digit = false;
for ($i = 1; $i < $len; ++$i) {
    if ('0' <= $passwd[$i] && $passwd[$i] <= '9') {
        $digit = true;
    }
    else if ('a' <= $passwd[$i] && $passwd[$i] <= 'z') {
        $lower = true;
    } 
    else if ('A' <= $passwd[$i] && $passwd[$i] <= 'Z') {
        $upper = true;
    }
    else {
        $other = true;
    }
}
$cnt = $upper + $lower + $other + $digit;
if ($cnt >= 3 && $len >= 12) {
    echo "<script>alert(\"密码设置不合要求!\");histroy.back()</script>";
    exit;
}

$host="localhost";
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
    $event="event=register\naccount=".$_POST["account"]."\npasswd=".$_POST["passwd"]."\n";
    $buf;
    socket_send($socket, $event, strlen($event), 0);
    socket_recv($socket, $buf, 4096, 0);
    socket_close($socket);
    $array = explode("\n", $buf);
    if (!strcmp($array[0], "accepted")) {
        header("location:./login.html");
    }
    else {
        echo "<script>alert(\"注册失败!用户名或重复\");</script>";
        
        exit;
    }
}
?>