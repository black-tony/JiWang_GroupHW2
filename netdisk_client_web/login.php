<?php 
header("content-type:text/html; charset=gbk");
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
    $event="event=login\naccount=".$_POST["account"]."\npasswd=".$_POST["passwd"]."\n";
    $buf;
    socket_send($socket, $event, strlen($event), 0);
    socket_recv($socket, $buf, 4096, 0);
    socket_close($socket);
    $array = explode("\n", $buf);
    if (!strcmp($array[0], "accepted")) {
        session_start();
        $_SESSION['account']=$_POST['account'];
        $_SESSION['pdir']="/";
        session_write_close();
        header("location:./main.html");
    }
    else {
        // �û������������!
        // echo "<script>alert('�˳��ɹ�!');location.href='".$_SERVER["HTTP_REFERER"]."';</script>"; 
        echo "<script>alert(\"".$array[1]."\");location.href='".$_SERVER["HTTP_REFERER"]."';</script>";
        exit;
    }
}
?>