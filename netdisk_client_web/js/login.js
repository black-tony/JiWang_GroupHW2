function checkValid()
{
    var username = document.forms['login']['ID'].value;
    var password = document.forms['login']['passwd'].value;
    if(username == null || username == "")
    {
        alert("未输入用户名!");
        return false;
    }
    if(password == null || password == "")
    {
        alert("请输入密码!");
        return false;
    }
    return true;
}