var account;
var sel_name = "";
var sel_pdir = "";
var sel_type = "";
var file_and_dir = {};
function GetAccount() {
    var event = "event=getaccount";
    var xhr = new XMLHttpRequest();
    xhr.open("POST","./server.php", true);
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");  //����Ϊ����ʽ�ύ
    xhr.onreadystatechange = function() {
        // ��������Ƿ�ɹ�
        if(this.readyState === 4 && this.status === 200) {
            // �����Է���������Ӧ���뵱ǰҳ��
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
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");  //����Ϊ����ʽ�ύ
    xhr.onreadystatechange = function() {
        // ��������Ƿ�ɹ�
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
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");  //����Ϊ����ʽ�ύ
    xhr.onreadystatechange = function() {
        // ��������Ƿ�ɹ�
        if(this.readyState === 4 && this.status === 200) {
            //window.location.href=xhr.responseText;
            console.log(xhr.response);
        }
    };
    //xhr.send(null);
    xhr.send(event);
}

function rename_file(name) {
    var newname = prompt("������������");
    if(file_and_dir[newname] == 'f')
    {
        alert("�����ظ��ļ�!��������ϴ�!\n����ظ��ļ��ѱ�ɾ��, ��ˢ��ҳ��!")
        return false
    }
    var pdir = document.getElementById("pdir").innerHTML;
    var event = "event=rename&type=f&account=" + account +"&pdir=" + pdir + "&name=" + name + "&newname=" + newname;
    var xhr = new XMLHttpRequest();
    xhr.open("POST","./server.php", true);
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");  //����Ϊ����ʽ�ύ
    xhr.onreadystatechange = function() {
        // ��������Ƿ�ɹ�
        if(this.readyState === 4 && this.status === 200) {
            console.log(this.responseText);
            GetList();
        }
    };
    xhr.send(encodeURI(event));
}

function rename_dir(name) {
    var newname = prompt("������������");
    if(file_and_dir[newname] == 'd')
    {
        alert("�����ظ��ļ���!��������ϴ�!\n����ظ��ļ��ѱ�ɾ��, ��ˢ��ҳ��!")
        return false
    }
    var pdir = document.getElementById("pdir").innerHTML;
    var event = "event=rename&type=d&account=" + account +"&pdir=" + pdir + "&name=" + name + "&newname=" + newname;
    var xhr = new XMLHttpRequest();
    xhr.open("POST","./server.php", true);
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");  //����Ϊ����ʽ�ύ
    xhr.onreadystatechange = function() {
        // ��������Ƿ�ɹ�
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
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");  //����Ϊ����ʽ�ύ
    xhr.onreadystatechange = function() {
        // ��������Ƿ�ɹ�
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
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");  //����Ϊ����ʽ�ύ
    xhr.onreadystatechange = function() {
        // ��������Ƿ�ɹ�
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
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");  //����Ϊ����ʽ�ύ
    xhr.onreadystatechange = function() {
        // ��������Ƿ�ɹ�
        if(this.readyState === 4 && this.status === 200) {
            // �����Է���������Ӧ���뵱ǰҳ��
            var list = this.responseText.split("\n");
            var div = document.getElementById("file-list");
            div.innerHTML="";   //ɾ����Ԫ��
            for (var i = 0; i < list.length; ++i) {
                if ((list[i][0] != 'f' && list[i][0] != 'd') || list[i][1] != ' ') {
                    continue;
                }
                var subdiv = document.createElement("div");
                var name = list[i].substr(2);
                // ����ͼ��
                var icon = document.createElement("img");
                icon.setAttribute("id", "icon");
                // ������ť
                var but = document.createElement("button");
                but.setAttribute("type", "button");
                var form = document.createElement("form");
                var rename_but = document.createElement("button");
                var remove_but = document.createElement("button");
                var move_but = document.createElement("button");
                var copy_but = document.createElement("button");

                remove_but.innerHTML = "ɾ��";
                move_but.innerHTML = "����";
                copy_but.innerHTML = "����";
                rename_but.innerHTML = "������";
                if (list[i][0] == 'd') {
                    icon.src = "./img/folder.png";
                    but.setAttribute("onclick", "CD(\"" + name + "\")");
                    but.innerHTML = "����";
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
                    input_submit.setAttribute("value","����");
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
    var name = prompt("�������½��ļ�����");
    if(file_and_dir[name] == 'd')
    {
        alert("�����ظ��ļ���!��������ϴ�!\n����ظ��ļ��ѱ�ɾ��, ��ˢ��ҳ��!")
        return false
    }
    var pdir = document.getElementById("pdir").innerHTML;
    var event = "event=mkdir&account=" + account +"&pdir=" + pdir + "&name=" + name;
    var xhr = new XMLHttpRequest();
    console.log(name);
    xhr.open("POST","./server.php", true);
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");  //����Ϊ����ʽ�ύ
    xhr.onreadystatechange = function() {
        // ��������Ƿ�ɹ�
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
    // var file2 = file.cloneNode(false);          //false��ʾֻ������true��ʾ���������ӽڵ�
    // file2.onchange = file.onchange;             //����ʱ��ע��ļ����������������ƣ����Ҫ�˹���ֵ
    // file.parentNode.replaceChild(file2, file);  //�ڸ��ڵ����滻��ԭ�����Ƿ��ͷţ���
}

function Upload()
{
    // var files = document.getElementById('file_form');
    var file_input = document.getElementById('file');
    if(file_input.files.length <= 0 ) 
    {
        alert('��ѡ��Ҫ�ϴ����ļ�!');
        return false;
    }
    if(file_and_dir[file_input.files[0].name] == 'f')
    {
        alert("�����ظ��ļ�!������ļ������ϴ�!\n����ظ��ļ��ѱ�ɾ��, ��ˢ��ҳ��!")
        return false
    }
    console.log('�û�ѡ���˴��ϴ����ļ�');
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
                alert("����봫!")
                
                
            }
            else if(this.responseText == "1")
            {
                Upload_True();
            }
            else 
            {
                document.getElementById("returned_script").innerHTML = this.responseText ;
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
        alert('���뵽��Ӧ�ý����Ƭ��!');
        return false;
    }
    console.log('δ��⵽��Ӧ��MD5�ļ�, ��ʼ��ʽ�ϴ�');
    var fd = new FormData()

    // ���û�ѡ����ļ���ӵ�fd��
    fd.append('file',file_input.files[0])
    fd.append("event", "True_upload")
    // fd.append("test", "TESTIE")
    console.log(fd.get("file"))
    console.log(fd.get("event"))

    var xhr = new XMLHttpRequest()
    

    // �����ļ��ϴ�����
    xhr.upload.onprogress = function(event) {
        // event.lengthComputable��һ������ֵ ��ʾ��ǰ�ϴ��ĳ����Ƿ���пɼ���ĳ���
        if(event.lengthComputable) {
            // event.loaded���Ѵ�����ֽ� 
            // event.total���ܴ�����ֽ�
            // Math.ceil((e.loaded/total) * 100) �Ѵ�����ֽ�/�ܴ�����ֽ�*100��ðٷֱ�����Math.ceil()ȡ��
            var procentComplete = Math.ceil((event.loaded/event.total) * 100)
            console.log(procentComplete);
            // ����������İٷֱ� �޸Ľ�������html
            // $(selector).attr(attribute,value): �������Ժ�ֵ
            var test = document.getElementById('percent');
            test.style = 'width:'+ procentComplete +'%';
            test.innerHTML = procentComplete +'%';
        }
    }
        
        // �����ϴ���ɵ��¼�
    xhr.upload.onload = function(){
        // �޸Ľ�������ɫ���Ƴ���ǰ���������������
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
    // ����open���� ָ��������URL��ַ
    // alert("������������")

    // ��������
    xhr.send(fd)

    // ����onreadystatechange�¼�
}