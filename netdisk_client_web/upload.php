<?php
header("content-type:text/html; charset=gbk");
$buf;
function update_info($md5_sum, $filename)
{
    $host="localhost";
    $port=4000;
    // create a socket
    $socket=socket_create(AF_INET, SOCK_STREAM, 0) or die("Could not create a socket\n");
    // connect server(C++ socket)
    if (socket_connect($socket, $host, $port) == false) {
        // connect failed
        echo "connect failed";
        socket_close($socket);
        return -1;
    }
    else {
        session_start();
        $account=$_SESSION['account'];
        $event="event=upload\naccount=".$account."\nstage=finished\nmd5=".$md5_sum."\npdir=".$_SESSION["pdir"]."\nfilename=".$filename."\n";
        session_write_close();
        socket_send($socket, $event, strlen($event), 0);
        socket_recv($socket, $buf, 4096, 0);
        socket_close($socket);
        // echo "<script>alert(\"�ļ��ϴ��ɹ�!\");history.back()</script>";
        return 0;
    }
}
 
if(isset($_POST['md5sum']))
{
    $md5 = $_POST['md5sum'];
    if (file_exists("/usr/netdisk-file/".$md5))
    {
        if(update_info($md5, $_POST['filename']) == 0)
        {
            echo "0";
        }
    }
    else 
    {
        echo "1";
    }

}
else if(isset($_POST['event']))
{
    if(!strcmp($_POST["event"], "True_upload"))
    {
        if($_FILES["file"]["name"] == null || !strcmp($_FILES["file"]["name"], "")) {
            echo "û��ѡ���ϴ��ļ�!";
        }
        else 
        {
            if(!is_uploaded_file($_FILES["file"]["tmp_name"]))
            {
                echo "�����ϴ����ļ�!";
            }

            $md5 = md5_file($_FILES["file"]["tmp_name"]);
            // echo $md5;
            if (!file_exists("/usr/netdisk-file/".$md5))
            {
                if(!move_uploaded_file($_FILES["file"]["tmp_name"], "/usr/netdisk-file/".$md5))
                {
                    echo "�޷���".$_FILES["file"]["tmp_name"]."�ƶ���"."/usr/netdisk-file/".$md5;
                }
                else
                {
                    if(update_info($md5, $_FILES["file"]["name"]) == 0)
                    {
                        echo "�ϴ��ɹ�!";
                    }
                }
                
            }
            else 
            {
                echo "�㲻Ӧ�õ�������!_TrueUpload_FAIL";
            }
        }
        // if($_FILES["filename"]["name"] == null || !strcmp($_FILES["filename"]["name"], "")) {
        //     echo "NOT FILE_NAME";
        // }
        
        // echo "OKKK";
        // if($_POST['filename'] == null){
        //     echo "NULL";
        // }
        
    }
    
    
}
else 
{
    print_r($_FILES);
    print_r($_POST);
    echo "������ô����������?_UPLOAD_FAIL";
}
//print_r($_FILES);
//print_r($_POST);

?>