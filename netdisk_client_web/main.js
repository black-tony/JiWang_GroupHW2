var account;
var sel_name = "";
var sel_pdir = "";
var sel_type = "";

function GetAccount() {
    var event = "event = getaccount";
    var xhr = new XMLHttpRequest();
    xhr.open("POST","./server.php", true);
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");  //设置为表单方式提交
    xhr.onreadystatechange = function() {
        // 检查请求是否成功
        if(this.readyState === 4 && this.status === 200) {
            // 将来自服务器的响应插入当前页面
            account = this.responseText;
            var acc = document.getElementById("account");
            acc.innerHTML = account;
        }
    };
    xhr.send(event);
}

function Paste() {
    if (sel_name == "" || sel_pdir == "" || sel_type=="") {
        return;
    }
    var pdir = document.getElementById("pdir").innerHTML;
    var event = "event=" + sel_type + "&pdir=" + sel_pdir + "&name=" + sel_name + "&dst=" + pdir;
    var xhr = new XMLHttpRequest();
    xhr.open("POST","./server.php", true);
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");  //设置为表单方式提交
    xhr.onreadystatechange = function() {
        // 检查请求是否成功
        if(this.readyState === 4 && this.status === 200) {
            console.log(event);
            console.log(xhr.responseText);
            GetList();
        }
    };
    xhr.send(encodeURI(event));
    sel_name = sel_pdir = sel_type = "";
}

function BackUp() {
    var pdir = document.getElementById("pdir"); 
    for (var i = pdir.innerHTML.length - 2; i >= 0; --i) {
        if (pdir.innerHTML[i] == '/') {
            pdir.innerHTML = pdir.innerHTML.substring(0, i + 1);
            break;
        }
    }

    GetList();
}

function CD(dst) {
    var pdir = document.getElementById("pdir");
    pdir.innerHTML += dst + '/';

    GetList();
}

function download(name) {
    var pdir = document.getElementById("pdir").innerText;
    var event = "event=download&account=" + account + "&pdir=" + pdir + "&name=" + name;
    var xhr = new XMLHttpRequest();
    //xhr.open("POST","./server.php?event=download&account=" + account + "&pdir=" + pdir + "&name=" + name, true);
    xhr.open("POST","./server.php", true);
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");  //设置为表单方式提交
    xhr.onreadystatechange = function() {
        // 检查请求是否成功
        if(this.readyState === 4 && this.status === 200) {
            //window.location.href=xhr.responseText;
            console.log(xhr.response);
        }
    };
    //xhr.send(null);
    xhr.send(event);
}

function rename_file(name) {
    var newname = prompt("请输入新名称");
    var pdir = document.getElementById("pdir").innerHTML;
    var event = "event=rename&type=f&account=" + account +"&pdir=" + pdir + "&name=" + name + "&newname=" + newname;
    var xhr = new XMLHttpRequest();
    xhr.open("POST","./server.php", true);
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");  //设置为表单方式提交
    xhr.onreadystatechange = function() {
        // 检查请求是否成功
        if(this.readyState === 4 && this.status === 200) {
            //console.log(this.responseText);
            GetList();
        }
    };
    xhr.send(encodeURI(event));
}

function rename_dir(name) {
    var newname = prompt("请输入新名称");
    var pdir = document.getElementById("pdir").innerHTML;
    var event = "event=rename&type=d&account=" + account +"&pdir=" + pdir + "&name=" + name + "&newname=" + newname;
    var xhr = new XMLHttpRequest();
    xhr.open("POST","./server.php", true);
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");  //设置为表单方式提交
    xhr.onreadystatechange = function() {
        // 检查请求是否成功
        if(this.readyState === 4 && this.status === 200) {
            GetList();
        }
    };
    xhr.send(encodeURI(event));
}

function remove_dir(name) {
    var pdir = document.getElementById("pdir").innerHTML;
    var event = "event=rmdir&account=" + account +"&pdir=" + pdir + "&name=" + name;
    var xhr = new XMLHttpRequest();
    xhr.open("POST","./server.php", true);
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");  //设置为表单方式提交
    xhr.onreadystatechange = function() {
        // 检查请求是否成功
        if(this.readyState === 4 && this.status === 200) {
            console.log(xhr.responseText);
            GetList();
        }
    };
    xhr.send(encodeURI(event));
}

function remove_file(name) {
    var pdir = document.getElementById("pdir").innerHTML;
    var event = "event=remove&account=" + account +"&pdir=" + pdir + "&name=" + name;
    var xhr = new XMLHttpRequest();
    xhr.open("POST","./server.php", true);
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");  //设置为表单方式提交
    xhr.onreadystatechange = function() {
        // 检查请求是否成功
        if(this.readyState === 4 && this.status === 200) {
            console.log(xhr.responseText);
            GetList();
        }
    };
    xhr.send(encodeURI(event));
}


function GetList() {
    var pdir = document.getElementById("pdir").innerHTML;
    var event = "event=list&account=" + account + "&pdir=" + pdir;
    var xhr = new XMLHttpRequest();
    xhr.open("POST","./server.php", true);
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");  //设置为表单方式提交
    xhr.onreadystatechange = function() {
        // 检查请求是否成功
        if(this.readyState === 4 && this.status === 200) {
            // 将来自服务器的响应插入当前页面
            var list = this.responseText.split("\n");
            var div = document.getElementById("file-list");
            div.innerHTML="";   //删除子元素
            for (var i = 0; i < list.length; ++i) {
                if ((list[i][0] != 'f' && list[i][0] != 'd') || list[i][1] != ' ') {
                    continue;
                }
                var subdiv = document.createElement("div");
                var name = list[i].substr(2);
                // 创建图标
                var icon = document.createElement("img");
                icon.setAttribute("id", "icon");
                // 创建按钮
                var but = document.createElement("button");
                but.setAttribute("type", "button");
                var form = document.createElement("form");
                var rename_but = document.createElement("button");
                var remove_but = document.createElement("button");
                var move_but = document.createElement("button");
                var copy_but = document.createElement("button");

                remove_but.innerHTML = "删除";
                move_but.innerHTML = "剪切";
                copy_but.innerHTML = "复制";
                rename_but.innerHTML = "重命名";
                if (list[i][0] == 'd') {
                    icon.src = "./img/folder.png";
                    but.setAttribute("onclick", "CD(\"" + name + "\")");
                    but.innerHTML = "进入";
                    rename_but.setAttribute("onclick", "rename_dir(\"" + name + "\")");
                    remove_but.setAttribute("onclick", "remove_dir(\"" + name + "\")");
                }
                else {
                    move_but.setAttribute("onclick", "Move(\"" + name + "\")");
                    copy_but.setAttribute("onclick", "Copy(\"" + name + "\")");
                    rename_but.setAttribute("onclick", "rename_file(\"" + name + "\")");
                    remove_but.setAttribute("onclick", "remove_file(\"" + name + "\")");
                    icon.src = "./img/file.png";
                    form.setAttribute("method","post");
                    form.setAttribute("style","display:inline");
                    form.setAttribute("action","./download.php");
                    form.setAttribute("enctype","multipart/form-data");
                    var input_pdir = document.createElement("input");
                    input_pdir.setAttribute("type","hidden");
                    input_pdir.setAttribute("name","pdir");
                    input_pdir.setAttribute("value",pdir);
                    var input_name = document.createElement("input");
                    input_name.setAttribute("type","hidden");
                    input_name.setAttribute("name","name");
                    input_name.setAttribute("value",name);
                    var input_account = document.createElement("input");
                    input_account.setAttribute("type","hidden");
                    input_account.setAttribute("name","account");
                    input_account.setAttribute("value",account);
                    var input_submit = document.createElement("input");
                    input_submit.setAttribute("type", "submit");
                    input_submit.setAttribute("name","submit");
                    input_submit.setAttribute("value","下载");
                    form.appendChild(input_pdir);
                    form.appendChild(input_name);
                    form.appendChild(input_account);
                    form.appendChild(input_submit);
                }

                subdiv.appendChild(icon);
                div.appendChild(subdiv);
                subdiv.innerHTML += name;
                if (list[i][0] == 'd') {
                    subdiv.appendChild(but);
                    subdiv.appendChild(rename_but);
                    subdiv.appendChild(remove_but);
                }
                else {
                    subdiv.appendChild(form); 
                    subdiv.appendChild(rename_but);
                    subdiv.appendChild(remove_but);
                    subdiv.appendChild(move_but);
                    subdiv.appendChild(copy_but);
                }
            }
        }
    };
    xhr.send(encodeURI(event));
}

function init(){
    GetAccount();
    GetList();
}

function Copy(name) {
    var pdir = document.getElementById("pdir").innerHTML;
    sel_pdir = pdir;
    sel_name = name;
    sel_type = "copy";
}

function Move(name) {
    var pdir = document.getElementById("pdir").innerHTML;
    sel_pdir = pdir;
    sel_name = name;
    sel_type = "move";
}

function mkdir() {
    var name = prompt("请输入新建文件夹名");
    var pdir = document.getElementById("pdir").innerHTML;
    var event = "event=mkdir&account=" + account +"&pdir=" + pdir + "&name=" + name;
    var xhr = new XMLHttpRequest();
    console.log(name);
    xhr.open("POST","./server.php", true);
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");  //设置为表单方式提交
    xhr.onreadystatechange = function() {
        // 检查请求是否成功
        if(this.readyState === 4 && this.status === 200) {
            console.log(xhr.responseText);
            GetList();
        }
    };
    
    xhr.send(encodeURI(event));
}