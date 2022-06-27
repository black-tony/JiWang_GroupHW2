<?php 
header("content-type:text/html; charset=gbk");
session_start();
$host="localhost";
$port=4000;
$account=$_SESSION['account'];
if (isset($_POST['pdir']) && strcmp($_POST['pdir'], $_SESSION['pdir'])) {
    $_SESSION['pdir'] = iconv("UTF-8", "gbk", $_POST['pdir']);
}
session_write_close();
// create a socket
$socket=socket_create(AF_INET, SOCK_STREAM, 0) or die("Could not create a socket\n");
// connect server(C++ socket)
if (socket_connect($socket, $host, $port) == false) {
    // connect failed
    echo "connect failed";
    socket_close($socket);
}
else if (isset($_POST['event'])) {
    if (!strcmp($_POST["event"], "getaccount")) {
        socket_close($socket);
        echo $account;
        exit;
    }
    else if (!strcmp($_POST["event"], "list")) {
        $event="event=".$_POST["event"]."\naccount=".$account."\npdir=".$_POST["pdir"]."\n";
        $event= iconv("UTF-8","gbk",$event);
    }
    else if (!strcmp($_POST['event'], 'mkdir')) {
        //echo "before:".$_POST["name"];
        $event="event=".$_POST["event"]."\naccount=".$account."\npdir=".$_POST["pdir"]."\nname=".$_POST["name"]."\n";
        //echo "after:".mb_convert_encoding($_POST["name"];
        $event= iconv("UTF-8","gbk",$event);
    }
    else if (!strcmp($_POST['event'], "rename")) {
        $event="event=".$_POST["event"]."\naccount=".$account."\ntype=".$_POST['type']."\npdir=".$_POST["pdir"]."\nname=".$_POST["name"]."\nnewname=".$_POST["newname"]."\n";
        $event= iconv("UTF-8","gbk",$event);
    }
    else if (!strcmp($_POST["event"], "move")) {
        $event="event=".$_POST["event"]."\naccount=".$account."\npdir=".$_POST["pdir"]."\nname=".$_POST["name"]."\ndst=".$_POST["dst"]."\n";
        $event= iconv("UTF-8","gbk",$event);
    }
    else if (!strcmp($_POST["event"], "copy")) {
        $event="event=".$_POST["event"]."\naccount=".$account."\npdir=".$_POST["pdir"]."\nname=".$_POST["name"]."\ndst=".$_POST["dst"]."\n";
        $event= iconv("UTF-8","gbk",$event);
    }
    else if (!strcmp($_POST["event"], "remove")) {
        $event="event=".$_POST["event"]."\naccount=".$account."\npdir=".$_POST["pdir"]."\nname=".$_POST["name"]."\n";
        $event= iconv("UTF-8","gbk",$event);
    }
    else if (!strcmp($_POST["event"], "rmdir")) {
        $event="event=".$_POST["event"]."\naccount=".$account."\npdir=".$_POST["pdir"]."\nname=".$_POST["name"]."\n";
        $event= iconv("UTF-8","gbk",$event);
    }
    else {
        socket_close($socket);
        exit();
    }
    $buf;
    socket_send($socket, $event, strlen($event), 0);
    socket_recv($socket, $buf, 4096, 0);
    socket_close($socket);
    echo $buf;
}
else {
    socket_close($socket);
}
?>