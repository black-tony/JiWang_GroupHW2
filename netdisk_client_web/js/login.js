function checkValid()
{
    var username = document.forms['login']['ID'].value;
    var password = document.forms['login']['passwd'].value;
    if(username == null || username == "")
    {
        alert("δ�����û���!");
        return false;
    }
    if(password == null || password == "")
    {
        alert("����������!");
        return false;
    }
    return true;
}