var account;
var sel_name = "";
var sel_pdir = "";
var sel_type = "";
var file_and_dir = {};
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
    if(file_and_dir[newname] == 'f')
    {
        alert("已有重复文件!请改名后上传!\n如果重复文件已被删除, 请刷新页面!")
        return false
    }
    var pdir = document.getElementById("pdir").innerHTML;
    var event = "event=rename&type=f&account=" + account +"&pdir=" + pdir + "&name=" + name + "&newname=" + newname;
    var xhr = new XMLHttpRequest();
    xhr.open("POST","./server.php", true);
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");  //设置为表单方式提交
    xhr.onreadystatechange = function() {
        // 检查请求是否成功
        if(this.readyState === 4 && this.status === 200) {
            console.log(this.responseText);
            GetList();
        }
    };
    xhr.send(encodeURI(event));
}

function rename_dir(name) {
    var newname = prompt("请输入新名称");
    if(file_and_dir[newname] == 'd')
    {
        alert("已有重复文件夹!请改名后上传!\n如果重复文件已被删除, 请刷新页面!")
        return false
    }
    var pdir = document.getElementById("pdir").innerHTML;
    var event = "event=rename&type=d&account=" + account +"&pdir=" + pdir + "&name=" + name + "&newname=" + newname;
    var xhr = new XMLHttpRequest();
    xhr.open("POST","./server.php", true);
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");  //设置为表单方式提交
    xhr.onreadystatechange = function() {
        // 检查请求是否成功
        if(this.readyState === 4 && this.status === 200) {
            console.log(this.responseText);
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
    file_and_dir = [];
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
                file_and_dir[name] = list[i][0];
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
    document.getElementById("file").onchange = function(e) {
        if(e.target.files.length <= 0)
            return;
        const file = e.target.files[0];
        const sliceLength = 10;
        const chunkSize = Math.ceil(file.size / sliceLength);
        const fileReader = new FileReader();
        const md5 = new SparkMD5();
        let index = 0;
        const loadFile = function(){
            const slice = file.slice(index, index + chunkSize);
            fileReader.readAsBinaryString(slice);
        }
        loadFile();
        fileReader.onload =function(e) {
            md5.appendBinary(e.target.result);
            if (index < file.size) {
                index += chunkSize;
                loadFile();
            } else {
                var md5_ans = md5.end();
                console.log(md5_ans);
                document.getElementById("file_md5").value=md5_ans;
            }
        };
    };
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
    if(file_and_dir[name] == 'd')
    {
        alert("已有重复文件夹!请改名后上传!\n如果重复文件已被删除, 请刷新页面!")
        return false
    }
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

function refreshUploader(file)
{
    file.outerHTML = file.outerHTML;
    // var file2 = file.cloneNode(false);          //false表示只有自身，true表示自身及所有子节点
    // file2.onchange = file.onchange;             //复制时，注册的监听器函数不被复制，因此要人工赋值
    // file.parentNode.replaceChild(file2, file);  //在父节点上替换（原来的是否被释放？）
}

function Upload()
{
    // var files = document.getElementById('file_form');
    var file_input = document.getElementById('file');
    if(file_input.files.length <= 0 ) 
    {
        alert('请选择要上传的文件!');
        return false;
    }
    if(file_and_dir[file_input.files[0].name] == 'f')
    {
        alert("已有重复文件!请更改文件名后上传!\n如果重复文件已被删除, 请刷新页面!")
        return false
    }
    console.log('用户选择了待上传的文件');
    var md5_sum_fd = new FormData();
    md5_sum_fd.append("md5sum", document.getElementById("file_md5").value);
    md5_sum_fd.append("filename", file_input.files[0].name);
    var xhr_md5 = new XMLHttpRequest()
    xhr_md5.onreadystatechange = function() {
        if(xhr_md5.readyState === 4 && xhr_md5.status === 200) {
            // var data = JSON.parse(xhr_md5.responseText)
            console.log(this.responseText)
            if (this.responseText == "0")
            {
                var tmp = document.getElementById('percent');
                tmp.style = 'width:'+ "100" +'%';
                tmp.innerHTML = "100" +'%';
                tmp.className = 'progress-bar progress-bar-success'
                refreshUploader(file_input);
                GetList();
                alert("完成秒传!")
                
                
            }
            else 
            {
                Upload_True();
            }
            
            // console.log(this.responseText);
            // if(data.status === 200) {
            //     document.querySelector('#img').src = 'http://www.liulongbin.top:3006' + data.url
            // } else {
            //     console.log(data.message);
            // }
        }
    }
    xhr_md5.open('POST',"./upload.php", false)
    xhr_md5.send(md5_sum_fd)
}

function Upload_True(){
    var file_input = document.getElementById('file');
    if(file_input.files.length <= 0 ) 
    {
        alert('进入到不应该进入的片段!');
        return false;
    }
    console.log('未检测到对应的MD5文件, 开始正式上传');
    var fd = new FormData()

    // 将用户选择的文件添加到fd中
    fd.append('file',file_input.files[0])
    fd.append("event", "True_upload")
    // fd.append("test", "TESTIE")
    console.log(fd.get("file"))
    console.log(fd.get("event"))

    var xhr = new XMLHttpRequest()
    

    // 监听文件上传进度
    xhr.upload.onprogress = function(event) {
        // event.lengthComputable是一个布尔值 表示当前上传的长度是否具有可计算的长度
        if(event.lengthComputable) {
            // event.loaded：已传输的字节 
            // event.total：总传输的字节
            // Math.ceil((e.loaded/total) * 100) 已传输的字节/总传输的字节*100获得百分比再由Math.ceil()取整
            var procentComplete = Math.ceil((event.loaded/event.total) * 100)
            console.log(procentComplete);
            // 计算进度条的百分比 修改进度条的html
            // $(selector).attr(attribute,value): 设置属性和值
            var test = document.getElementById('percent');
            test.style = 'width:'+ procentComplete +'%';
            test.innerHTML = procentComplete +'%';
        }
    }
        
        // 监听上传完成的事件
    xhr.upload.onload = function(){
        // 修改进度条颜色：移除当前类名，添加新类名
        var tmp = document.getElementById('percent');
        tmp.className = 'progress-bar progress-bar-success'
    }
    xhr.onreadystatechange = function() {
        if(xhr.readyState === 4 && xhr.status === 200) {
            // var data = JSON.parse(xhr.responseText)
            console.log(this.responseText);
            refreshUploader(file_input);
            GetList();
            alert(this.responseText)
            // if(data.status === 200) {
            //     document.querySelector('#img').src = 'http://www.liulongbin.top:3006' + data.url
            // } else {
            //     console.log(data.message);
            // }
        }
    }
    xhr.open('POST',"./upload.php", true)

    // xhr.setRequestHeader("Content-type", "multipart/form-data");
    // 调用open函数 指定类型与URL地址
    // alert("即将发起请求")

    // 发起请求
    xhr.send(fd)

    // 监听onreadystatechange事件
}