#include <iostream>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/epoll.h>
#include <vector>
#include <cstring>
#include <unistd.h>
#include <netinet/in.h>
#include <sys/ioctl.h>
#include <net/if.h>
#include "tools.h"
#include "login.h"
#include "file_manage.h"
#include <fstream>
#include <mysql.h>  // mysql特有
using namespace std;

int begin_upload(char *content, int size, MYSQL *(&mysql), const string &md5, const string &account, const string &pdir, const string &filename, string &msg) {
    MYSQL_RES *res;
    MYSQL_ROW row;
    string command = "select * from file where md5=\"" + md5 + "\"";
    mysql_query(mysql, command.c_str());
    res = mysql_store_result(mysql);
    if ((row = mysql_fetch_row(res)) != NULL) {
        if (strcmp(row[1], "complete") == 0) {
            // 存在相同的完整文件,可以秒传
            command = "select * from storage where md5=\"" + md5 + "\" and account=\"" + account + "\"";
            mysql_query(mysql, command.c_str());
            res = mysql_store_result(mysql);
            while ((row = mysql_fetch_row(res)) != NULL) {
                if (row[2] == pdir && row[3] == filename) {
                    msg = "file has existed\n";
                    return COMPLETE;
                }
            }
            command = "insert into storage(account,type,pdir,name,md5)values(\"" + account + "\",\"f\",\"" + pdir + "\",\"" + filename + "\",\"" + md5 + "\")";
            mysql_query(mysql, command.c_str());
            msg = "upload completed\n";
            return COMPLETE;
        }
        else {
            // 文件不完整,断点续传
            struct stat statbuf;
            if(stat(("./file/" + md5).c_str(), &statbuf)==0)
                msg = "resume upload\n" + to_string(statbuf.st_size) + "\n";
                return ACCEPT;
            // 获取文件大小失败,重新传
            fstream fout("./file/" + md5, ios::out | ios::trunc | ios::binary);
            fout.write(content, size);
            fout.close();
            msg = "upload begin\n";
            return ACCEPT;
        }
    }

    // command = "select * from file where md5=\"" + md5 + "\"";
    // if (mysql_query(mysql, command.c_str())) {
    //     cerr << "mysql_query failed(" << mysql_error(mysql) << ")" << endl;
    //     return FAILED;
    // }
    // if ((res = mysql_store_result(mysql))==NULL) {
    //     cout << "mysql_store_result failed" << endl;
    //     return FAILED;
    // }
    // if ((row = mysql_fetch_row(res)) == NULL) {
    //     // 未查找到结果,需完整上传
    //     fstream fout("/file/" + md5, ios::out | ios::binary);
    //     fout.write(content, size);
    //     fout.close();
    //     command = "insert into file(md5,status)values(\"" + md5 + "\",\"incomplete\")";
    //     mysql_query(mysql, command.c_str());
    //     return ACCEPT;
    // }

    fstream fout("./file/" + md5, ios::out | ios::binary);
    fout.write(content, size);
    fout.close();
    command = "insert into file(md5,status)values(\"" + md5 + "\",\"incomplete\")";
    mysql_query(mysql, command.c_str());
    msg = "upload begin\n";
    return ACCEPT;

    //return FAILED;
}

int continue_upload(char *content, int size, const string &md5, string &msg) {
    fstream fout("./file/" + md5, ios::out | ios::app | ios::binary);
    fout.write(content, size);
    fout.close();
    msg = "uploading\n";
    return ACCEPT;
}

int finish_upload(MYSQL *(&mysql), const string &account ,const string &pdir, const string &filename, const string &md5, string &msg) {
    string command = "update file set status=\"complete\" where md5=\"" + md5 + "\" and status=\"incomplete\"";
    if (mysql_query(mysql, command.c_str())) {
        cerr << "mysql_query failed(" << mysql_error(mysql) << ")" << endl;
        msg = "upload failed, mysql error\n";
        return FAILED;
    }

    command = "insert into storage(account,type,pdir,name,md5)values(\"" + account + "\",\"f\",\"" + pdir + "\",\"" + filename + "\",\"" + md5 + "\")";
    if (mysql_query(mysql, command.c_str())) {
        cerr << "mysql_query failed(" << mysql_error(mysql) << ")" << endl;
        msg = "upload failed, mysql error\n";
        return FAILED;
    }
    msg = "upload completed\n";
    return COMPLETE;
}

int handle_upload(char *buf, int rn, const string &account, MYSQL *(&mysql), string &msg) {
    int i = 0;
    string stage, md5, pdir, filename;
    for (; i < rn && buf[i] != '\n'; ++i)
        ;   // event=upload
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        stage += buf[i];
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        md5 += buf[i];
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        pdir += buf[i];
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        filename += buf[i];
    }
    ++i;

    if (stage.substr(0, 6) == "stage=" && md5.substr(0, 4) == "md5=" && pdir.substr(0, 5) == "pdir=" && filename.substr(0, 9) == "filename=") {
        stage = stage.substr(6);
        md5 = md5.substr(4);
        pdir = pdir.substr(5);
        filename = filename.substr(9);
        if (stage == "begin") {
            return begin_upload(buf + i, rn - i, mysql, md5, account, pdir, filename, msg);
        }
        else if (stage == "continue") {
            return continue_upload(buf + i, rn - i, md5, msg);
        }
        else if (stage == "finished") {
            return finish_upload(mysql, account, pdir, filename, md5, msg);
        }
    }
    msg = "format error\n";
    return FAILED;
}

int handle_list(char *buf, int rn, MYSQL *(&mysql), const string &account, string &msg) {
    int i = 0;
    string pdir;
    for (; i < rn && buf[i] != '\n'; ++i)
        ;   // event=upload
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        pdir += buf[i];
    }
    if (pdir.substr(0, 5) != "pdir=")  {
        msg = "format error\n";
        return FAILED;
    }
    pdir = pdir.substr(5);
    string command = "select * from storage where pdir=\"" + pdir + "\" and account=\"" + account + "\"";
    mysql_query(mysql, command.c_str());
    MYSQL_RES *res;
    MYSQL_ROW row;
    res = mysql_store_result(mysql);
    bool pdir_exist = false;
    msg = "";
    while((row = mysql_fetch_row(res)) != NULL) {
        pdir_exist = true;
        // msg += type + " " + name + "\n"
        msg += row[1];
        msg += " ";
        msg += row[3];
        msg += "\n";
    }

    if (pdir_exist) {
        return ACCEPT;
    }
    else  {
        msg = "no such directory\n";
        return FAILED;
    }
}

int handle_move(char *buf, int rn, MYSQL *(&mysql), const string &account, string &msg) {
    int i = 0;
    string pdir, name, dst;
    for (; i < rn && buf[i] != '\n'; ++i)
        ;   // event=move
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        pdir += buf[i];
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        name += buf[i];
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        dst += buf[i];
    }
    if (pdir.substr(0, 5) != "pdir=" && name.substr(0, 5) != "name=" && dst.substr(0, 4) != "dst=")  {
        msg = "format error\n";
        return FAILED;
    }
    pdir = pdir.substr(5);
    name = name.substr(5);
    dst = dst.substr(4);
    string command = "select * from storage where type=\"f\" and pdir=\"" + dst + "\" and account=\"" + account + "\" and name=\"" + name + "\"";
    mysql_query(mysql, command.c_str());
    MYSQL_RES *res;
    MYSQL_ROW row;
    res = mysql_store_result(mysql);
    if ((row = mysql_fetch_row(res)) != NULL) {
        msg = "A file with the same name exists\n";
        return FAILED;
    }
    else {
        command = "select * from storage where type=\"f\" and pdir=\"" + pdir + "\" and account=\"" + account + "\" and name=\"" + name + "\"";
        mysql_query(mysql, command.c_str());
        res = mysql_store_result(mysql);
        if ((row = mysql_fetch_row(res)) != NULL) {
            command = "update storage set pdir=\"" + dst + "\" where type=\"f\" and pdir=\"" + pdir + "\" and account=\"" + account + "\" and name=\"" + name + "\"";
            mysql_query(mysql, command.c_str());
            msg = "move successfully\n";
            return ACCEPT;
        }
    }

    msg = "move failed\n";
    return FAILED;
}

int handle_copy(char *buf, int rn, MYSQL *(&mysql), const string &account, string &msg) {
    int i = 0;
    string pdir, name, dst;
    for (; i < rn && buf[i] != '\n'; ++i)
        ;
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        pdir += buf[i];
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        name += buf[i];
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        dst += buf[i];
    }
    if (pdir.substr(0, 5) != "pdir=" && name.substr(0, 5) != "name=" && dst.substr(0, 4) != "dst=")  {
        msg = "format error\n";
        return FAILED;
    }
    pdir = pdir.substr(5);
    name = name.substr(5);
    dst = dst.substr(4);
    string command = "select * from storage where type=\"f\" and pdir=\"" + dst + "\" and account=\"" + account + "\" and name=\"" + name + "\"";
    mysql_query(mysql, command.c_str());
    MYSQL_RES *res;
    MYSQL_ROW row;
    res = mysql_store_result(mysql);
    if ((row = mysql_fetch_row(res)) != NULL) {
        msg = "A file with the same name exists\n";
        return FAILED;
    }
    else {
        command = "select * from storage where type=\"f\" and pdir=\"" + pdir + "\" and account=\"" + account + "\" and name=\"" + name + "\"";
        mysql_query(mysql, command.c_str());
        res = mysql_store_result(mysql);
        if ((row = mysql_fetch_row(res)) != NULL) {
            command = "insert into storage(account,type,pdir,name,md5)values(\"" + account + "\",\"" + string(row[1]) + "\",\"" + dst + "\",\"" + name + "\",\"" + string(row[4]) + "\")";
            mysql_query(mysql, command.c_str());
            msg = "copy successfully\n";
            return ACCEPT;
        }
    }


    msg = "copy failed\n";
    return FAILED;
}

int handle_remove(char *buf, int rn, MYSQL *(&mysql), const string &account, string &msg) {
    int i = 0;
    string pdir, name;
    for (; i < rn && buf[i] != '\n'; ++i)
        ;
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        pdir += buf[i];
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        name += buf[i];
    }
    if (pdir.substr(0, 5) != "pdir=" && name.substr(0, 5) != "name=")  {
        msg = "format error\n";
        return FAILED;
    }
    pdir = pdir.substr(5);
    name = name.substr(5);
    string command = "select * from storage where pdir=\"" + pdir + "\" and account=\"" + account + "\" and name=\"" + name + "\"";
    mysql_query(mysql, command.c_str());
    MYSQL_RES *res;
    MYSQL_ROW row;
    res = mysql_store_result(mysql);
    if ((row = mysql_fetch_row(res)) != NULL) {
        string md5 = row[4];
        command = "delete from storage where pdir=\"" + pdir + "\" and account=\"" + account + "\" and name=\"" + name + "\"";
        mysql_query(mysql, command.c_str());
        command = "select * from storage where md5=\"" + md5 + "\"";
        mysql_query(mysql, command.c_str());
        res = mysql_store_result(mysql);
        if ((row = mysql_fetch_row(res)) == NULL) {
            command = "delete from file where md5=\"" + md5 + "\"";
            mysql_query(mysql, command.c_str());
        }
    }

    msg = "remove successfully\n";
    return ACCEPT;
}

int handle_mkdir(char *buf, int rn, MYSQL *(&mysql), const string &account, string &msg) {
    int i = 0;
    string name, dst;
    for (; i < rn && buf[i] != '\n'; ++i) {
        ;
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        name += buf[i];
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        dst += buf[i];
    }
    if (name.substr(0, 5) != "name=" && dst.substr(0, 4) != "dst=")  {
        msg = "format error\n";
        return FAILED;
    }
    name = name.substr(5);
    dst = dst.substr(4);
    MYSQL_RES *res;
    MYSQL_ROW row;
    string command = "select * from storage where account=\"" + account + "\" and type=\"d\" and dst=\"" + dst + "\" and name=\"" + name + "\")";
    mysql_query(mysql, command.c_str());
    res = mysql_store_result(mysql);
    if ((row = mysql_fetch_row(res)) != NULL) {
        msg = "a dir with same name exists\n";
        return FAILED;
    }

    command = "insert into storage(account,type,pdir,name,md5)values(\"" + account + "\",\"d\",\"" + dst + "\",\"" + name + "\",\"\")";
    mysql_query(mysql, command.c_str());

    msg = "mkdir successfully\n";
    return ACCEPT;
}

int handle_rmdir(char *buf, int rn, MYSQL *(&mysql), const string &account, string &msg) {
    int i = 0;
    string pdir, name;
    for (; i < rn && buf[i] != '\n'; ++i) {
        ;
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        pdir += buf[i];
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        name += buf[i];
    }
    if (pdir.substr(0, 5) != "pdir=" || name.substr(0, 5) != "name=")  {
        msg = "format error\n";
        return FAILED;
    }
    pdir = pdir.substr(5);
    name = name.substr(5);
    MYSQL_RES *res;
    MYSQL_ROW row;
    string command = "select * from storage where type=\"d\" and name=\"" + name + "\" and pdir=\"" + pdir +"\" and account=\"" + account + "\"";
    mysql_query(mysql, command.c_str());
    res = mysql_store_result(mysql);
    if ((row = mysql_fetch_row(res)) == NULL) {
        msg = "no such dir\n";
        return FAILED;
    }
    else {
        command = "delete from storage where type=\"d\" and name=\"" + name + "\" and pdir=\"" + pdir +"\" and account=\"" + account + "\"";
        mysql_query(mysql, command.c_str());
        command = "delete from storage where pdir=\"" + pdir + name + "/\" and account=\"" + account + "\"";
        mysql_query(mysql, command.c_str());
        msg = "rmdir successfully\n";
        return ACCEPT;
    }
}

int handle_mvdir(char *buf, int rn, MYSQL *(&mysql), const string &account, string &msg) {
    int i = 0;
    string pdir, name, dst;
    for (; i < rn && buf[i] != '\n'; ++i)
        ;   // event=move
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        pdir += buf[i];
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        name += buf[i];
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        dst += buf[i];
    }
    if (pdir.substr(0, 5) != "pdir=" && name.substr(0, 5) != "name=" && dst.substr(0, 4) != "dst=")  {
        msg = "format error\n";
        return FAILED;
    }
    pdir = pdir.substr(5);
    name = name.substr(5);
    dst = dst.substr(4);
    string command = "select * from storage where type=\"d\" and pdir=\"" + dst + "\" and account=\"" + account + "\" and name=\"" + name + "\"";
    mysql_query(mysql, command.c_str());
    MYSQL_RES *res;
    MYSQL_ROW row;
    res = mysql_store_result(mysql);
    if ((row = mysql_fetch_row(res)) != NULL) {
        msg = "A dir with the same name exists\n";
        return FAILED;
    }
    else {
        command = "select * from storage where type=\"d\" and pdir=\"" + pdir + "\" and account=\"" + account + "\" and name=\"" + name + "\"";
        mysql_query(mysql, command.c_str());
        res = mysql_store_result(mysql);
        if ((row = mysql_fetch_row(res)) != NULL) {
            command = "update storage set pdir=\"" + dst + "\" where type=\"d\" and pdir=\"" + pdir + "\" and account=\"" + account + "\" and name=\"" + name + "\"";
            mysql_query(mysql, command.c_str());
            command = "update storage set pdir=\"" + dst + name + "/\" where type=\"f\" and pdir=\"" + pdir + name + "/\" and account=\"" + account + "\"";
            mysql_query(mysql, command.c_str());
            msg = "mvdir successfully\n";
            return ACCEPT;
        }
    }

    msg = "mvdir failed\n";
    return FAILED;
}

int handle_download(char *buf, int rn, MYSQL *(&mysql), const string &account, string &msg, char *sd, int &size) {
    int i = 0;
    string pdir, name, pos;
    for (; i < rn && buf[i] != '\n'; ++i) {
        ;
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        pdir += buf[i];
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        name += buf[i];
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        pos += buf[i];
    }
    if (pdir.substr(0, 5) != "pdir=" && name.substr(0, 5) != "name=" && pos.substr(0, 4) != "pos=")  {
        msg = "format error\n";
        return FAILED;
    }
    pdir = pdir.substr(0, 5);
    name = name.substr(0, 5);
    pos = pos.substr(0, 4);
    MYSQL_RES *res;
    MYSQL_ROW row;
    string command = "select * from storage where type=\"f\" and pdir=\"" + pdir + "\" and account=\"" + account + "\" and name=\"" + name + "\"";
    mysql_query(mysql, command.c_str());
    res = mysql_store_result(mysql);
    if ((row = mysql_fetch_row(res)) != NULL) {
        string md5 = row[4];
        fstream fin("file/" + md5, ios::in | ios::binary);
        fin.seekg(stoll(pos), ios::beg);
        fin.read(sd, 4096);
        size = fin.gcount();
        if (size < 4096) {
            msg = "download completed\n";
        }
        else {
            msg = "downloading\n";
        }
        return ACCEPT;
    }
    msg = "download error\n";
    return FAILED;
}