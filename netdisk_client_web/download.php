<?php
header("content-type:text/html; charset=gbk");
session_start();
$host="localhost";
$port=4000;
$account=$_SESSION['account'];
if (strcmp($_POST['pdir'], $_SESSION['pdir'])) {
    $_SESSION['pdir'] = $_POST['pdir'];
}
session_write_close();

// header('Content-type:text/html;charset=gb18030');
//�����ݿ�
$mysqli=new mysqli('localhost','root','root123','netdisk');
if (mysqli_connect_errno()){
    echo "����ʧ�ܣ�ԭ��Ϊ��".mysqli_connect_error();
    exit();
}
//���������ַ���
$result = $mysqli->query("set names gbk");
$query = "select * from storage where pdir=\"".$_POST["pdir"]."\" and account = \"".$account."\" and name = \"".$_POST['name']."\"";
$result = $mysqli->query($query);
$row=$result->fetch_assoc();
$file_dir = "/usr/netdisk-file/";     // �����ļ����Ŀ¼
$file_name = $row['md5'];        // �����ļ���
//echo $file_dir.$file_name;
$result->close();
//�ر����ݿ�
$mysqli->close();
// ����ļ��Ƿ����
if (!file_exists($file_dir.$file_name)) {
    header('HTTP/1.1 404 NOT FOUND');
} else {
    // ��ֻ���Ͷ�����ģʽ���ļ�
    $file = fopen($file_dir.$file_name, "rb");

    // �������������һ���ļ�����ʽ���ļ�
    Header("Content-type: application/octet-stream");
    // ����Χ�Ķ�����λ
    Header("Accept-Ranges: bytes");
    // Content-Length��ָ���������������Ӧ�����ݵ��ֽڳ���
    Header("Accept-Length: ".filesize($file_dir.$file_name));
    // ����������������ļ��ǿ��Ե������������أ����غ���ļ�����Ϊ$file_name�ñ�����ֵ��
    Header("Content-Disposition: attachment; filename=".$_POST["name"]);

    // ��ȡ�ļ����ݲ�ֱ������������
    echo fread($file, filesize($file_dir.$file_name));
    fclose($file);

    exit ();
}
?>