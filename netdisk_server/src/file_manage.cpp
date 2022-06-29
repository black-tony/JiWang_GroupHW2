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
#include <unordered_map>
using namespace std;

int update_link_count(MYSQL *(&mysql), const string &md5, int change) {
    MYSQL_RES *res;
    MYSQL_ROW row;
    string command = "select * from file where md5=\"" + md5 + "\"";
    mysql_query(mysql, command.c_str());
    res = mysql_store_result(mysql);
    row = mysql_fetch_row(res);
    int cnt = stoi(row[2]) + change;
    if (cnt <= 0) {
        command = "delete from file where md5=\"" + md5 + "\"";
        mysql_query(mysql, command.c_str());
        remove(("/usr/netdisk-file/" + md5).c_str());
    }
    else {
        command = "update file set link=" + to_string(cnt) + " where md5=\"" + md5 + "\"";
        if (mysql_query(mysql, command.c_str())) {
            cerr << "mysql_query failed(" << mysql_error(mysql) << ")" << endl;
        }
    }
    return 0;
}

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
            // 为该用户添加链接
            command = "insert into storage(account,type,pdir,name,md5)values(\"" + account + "\",\"f\",\"" + pdir + "\",\"" + filename + "\",\"" + md5 + "\")";
            mysql_query(mysql, command.c_str());
            // 增加计数
            update_link_count(mysql, md5, 1);

            logger("用户:" + account + " 文件" + pdir + filename + "上传完成");
            msg = "upload completed\n";
            return COMPLETE;
        }
        else {
            // 文件不完整,断点续传
            struct stat statbuf;
            if(stat(("/usr/netdisk-file/" + md5).c_str(), &statbuf)==0)
                msg = "resume upload\n" + to_string(statbuf.st_size) + "\n";
                return ACCEPT;
            // 获取文件大小失败,重新传
            fstream fout("/usr/netdisk-file/" + md5, ios::out | ios::trunc | ios::binary);
            fout.write(content, size);
            fout.close();
            msg = "upload begin\n";
            return ACCEPT;
        }
    }

    fstream fout("/usr/netdisk-file/" + md5, ios::out | ios::binary);
    fout.write(content, size);
    fout.close();
    command = "insert into file(md5,status,link)values(\"" + md5 + "\",\"incomplete\", 0)";
    mysql_query(mysql, command.c_str());
    msg = "upload begin\n";
    return ACCEPT;

    //return FAILED;
}

int continue_upload(char *content, int size, const string &md5, string &msg) {
    fstream fout("/usr/netdisk-file/" + md5, ios::out | ios::app | ios::binary);
    if (!fout.is_open()) {
        cerr << "文件打开失败" << endl;
    }
    cout << size << endl;
    fout.write(content, size);
    fout.close();
    msg = "uploading\n";
    return ACCEPT;
}

int finish_upload(MYSQL *(&mysql), const string &account ,const string &pdir, const string &filename, const string &md5, string &msg) {
    MYSQL_RES *res;
    MYSQL_ROW row;
    string command = "select * from file where md5=\"" + md5 + "\"";
    mysql_query(mysql, command.c_str());
    res = mysql_store_result(mysql);
    if ((row = mysql_fetch_row(res)) == NULL) {
        command = "insert into file(md5,status,link)values(\"" + md5 + "\",\"complete\", 1)";
        if (mysql_query(mysql, command.c_str())) {
            cerr << "mysql_query failed(" << mysql_error(mysql) << ")" << endl;
            msg = "upload failed, mysql error\n";
            return FAILED;
        }
    }
    else {
        command = "update file set status=\"complete\" where md5=\"" + md5 + "\" and status=\"incomplete\"";
        if (mysql_query(mysql, command.c_str())) {
            cerr << "mysql_query failed(" << mysql_error(mysql) << ")" << endl;
            msg = "upload failed, mysql error\n";
            return FAILED;
        }
        update_link_count(mysql, md5, 1);
    }

    command = "insert into storage(account,type,pdir,name,md5)values(\"" + account + "\",\"f\",\"" + pdir + "\",\"" + filename + "\",\"" + md5 + "\")";
    if (mysql_query(mysql, command.c_str())) {
        cerr << "mysql_query failed(" << mysql_error(mysql) << ")" << endl;
        msg = "upload failed, mysql error\n";
        return FAILED;
    }

    logger("用户" + account + "文件" + pdir + filename + "上传完成");
    msg = "upload completed\n";
    return COMPLETE;
}

int handle_upload(char *buf, int rn, MYSQL *(&mysql), string &msg) {
    int i = 0;
    string account, stage, md5, pdir, filename;
    for (; i < rn && buf[i] != '\n'; ++i)
        ;   // event=upload
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        account += buf[i];
    }
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

    if (stage.substr(0, 6) == "stage=" && md5.substr(0, 4) == "md5=" && pdir.substr(0, 5) == "pdir=" && filename.substr(0, 9) == "filename=" && account.substr(0, 8) == "account=") {
        account = account.substr(8);
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

int handle_list(char *buf, int rn, MYSQL *(&mysql), string &msg) {
    int i = 0;
    string account, pdir;
    for (; i < rn && buf[i] != '\n'; ++i)
        ;   // event=upload
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        account += buf[i];
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        pdir += buf[i];
    }
    if (pdir.substr(0, 5) != "pdir=" || account.substr(0, 8) != "account=")  {
        msg = "format error\n";
        return FAILED;
    }
    account = account.substr(8);
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

    // if (!pdir_exist && pdir != "/") {
    //     msg = "no such directory\n";
    //     return FAILED;
    // }
    // else {
        return ACCEPT;
    //}
}

int move(MYSQL *(&mysql), string &msg, const string &account, const string &pdir, const string &name, const string &dst) {
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
            logger("用户"+account+"将文件"+pdir+name+"移动到"+dst+"目录下");
            msg = "move successfully\n";
            return ACCEPT;
        }
    }

    msg = "move failed\n";
    return FAILED;
}

int copy(MYSQL *(&mysql), string &msg, const string &account, const string &pdir, const string &name, const string &dst) {
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
            string md5 = row[4];
            update_link_count(mysql, md5, 1);
            logger("用户"+account+"将文件"+pdir+name+"复制到"+dst+"目录下");
            msg = "copy successfully\n";
            return ACCEPT;
        }
    }


    msg = "copy failed\n";
    return FAILED;
}

int remove(MYSQL *(&mysql), string &msg, const string &account, const string &pdir, const string &name) {
    string command = "select * from storage where type=\"f\" and pdir=\"" + pdir + "\" and account=\"" + account + "\" and name=\"" + name + "\"";
    mysql_query(mysql, command.c_str());
    MYSQL_RES *res;
    MYSQL_ROW row;
    res = mysql_store_result(mysql);
    if ((row = mysql_fetch_row(res)) != NULL) {
        string md5 = row[4];
        command = "delete from storage where type=\"f\" and pdir=\"" + pdir + "\" and account=\"" + account + "\" and name=\"" + name + "\"";
        mysql_query(mysql, command.c_str());
        // 减小计数
        update_link_count(mysql, md5, -1);
        msg = "remove successfully\n";
        logger("用户"+account+"删除文件"+pdir+name+"成功");
        return ACCEPT;
    }
    else {
        msg = "no such file\n";
        return FAILED;
    }


}

int handle_move(char *buf, int rn, MYSQL *(&mysql), string &msg) {
    int i = 0;
    string account, pdir, name, dst;
    for (; i < rn && buf[i] != '\n'; ++i)
        ;   // event=move
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        account += buf[i];
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        pdir += buf[i];
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        name += buf[i];
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        dst += buf[i];
    }
    if (pdir.substr(0, 5) != "pdir=" || name.substr(0, 5) != "name=" || dst.substr(0, 4) != "dst=" || account.substr(0, 8) != "account=")  {
        msg = "format error\n";
        return FAILED;
    }
    account = account.substr(8);
    pdir = pdir.substr(5);
    name = name.substr(5);
    dst = dst.substr(4);
    return move(mysql, msg, account, pdir, name, dst);
}

int handle_copy(char *buf, int rn, MYSQL *(&mysql), string &msg) {
    int i = 0;
    string account, pdir, name, dst;
    for (; i < rn && buf[i] != '\n'; ++i)
        ;
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        account += buf[i];
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        pdir += buf[i];
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        name += buf[i];
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        dst += buf[i];
    }
    if (account.substr(0, 8) != "account=" || pdir.substr(0, 5) != "pdir=" || name.substr(0, 5) != "name=" || dst.substr(0, 4) != "dst=")  {
        msg = "format error\n";
        return FAILED;
    }
    account = account.substr(8);
    pdir = pdir.substr(5);
    name = name.substr(5);
    dst = dst.substr(4);
    return copy(mysql, msg, account, pdir, name, dst);
}

int handle_remove(char *buf, int rn, MYSQL *(&mysql), string &msg) {
    int i = 0;
    string account, pdir, name;
    for (; i < rn && buf[i] != '\n'; ++i)
        ;
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        account += buf[i];
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        pdir += buf[i];
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        name += buf[i];
    }
    if (account.substr(0, 8) != "account=" || pdir.substr(0, 5) != "pdir=" || name.substr(0, 5) != "name=")  {
        msg = "format error\n";
        return FAILED;
    }
    account = account.substr(8);
    pdir = pdir.substr(5);
    name = name.substr(5);
    return remove(mysql, msg, account, pdir, name);
}

int handle_mkdir(char *buf, int rn, MYSQL *(&mysql), string &msg) {
    int i = 0;
    string account, name, pdir;
    for (; i < rn && buf[i] != '\n'; ++i) {
        ;
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        account += buf[i];
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        pdir += buf[i];
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        name += buf[i];
    }
    if (name.substr(0, 5) != "name=" && pdir.substr(0, 5) != "pdir=")  {
        msg = "format error\n";
        return FAILED;
    }
    account = account.substr(8);
    name = name.substr(5);
    pdir = pdir.substr(5);
    MYSQL_RES *res;
    MYSQL_ROW row;
    string command = "select * from storage where account=\"" + account + "\" and type=\"d\" and pdir=\"" + pdir + "\" and name=\"" + name + "\")";
    mysql_query(mysql, command.c_str());
    res = mysql_store_result(mysql);
    if ((row = mysql_fetch_row(res)) != NULL) {
        msg = "a dir with same name exists\n";
        return FAILED;
    }

    command = "insert into storage(account,type,pdir,name,md5)values(\"" + account + "\",\"d\",\"" + pdir + "\",\"" + name + "\",\"\")";
    mysql_query(mysql, command.c_str());
    logger("用户"+account+"新建文件夹"+pdir+name);
    msg = "mkdir successfully\n";
    return ACCEPT;
}

int rmdir(MYSQL *(&mysql), string &msg, const string &account, const string &pdir, const string &name) {
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
        // 删除文件夹本身
        command = "delete from storage where type=\"d\" and name=\"" + name + "\" and pdir=\"" + pdir +"\" and account=\"" + account + "\"";
        mysql_query(mysql, command.c_str());
        // 准备删除文件夹下其他文件/文件夹
        unordered_map<string, int> hash;
        string dir = pdir + name + "/";
        command = "select * from storage where account=\"" + account + "\"";
        mysql_query(mysql, command.c_str());
        res = mysql_store_result(mysql);
        while ((row = mysql_fetch_row(res)) != NULL) {
            if (dir == string(row[2]).substr(0, dir.length())) {
                // 检查是否在该目录下
                if (!strcmp(row[1], "d")) {
                    // 删除子文件夹
                    command = "delete from storage where type=\"d\" and pdir=\"" + string(row[2]) + "\" and name=\"" + string(row[3]) + "\" and account=\"" + account + "\"";
                    mysql_query(mysql, command.c_str());
                }
                else if (!strcmp(row[1], "r")) {
                    ++hash[row[4]];
                    command = "delete from storage where type=\"f\" and pdir=\"" + string(row[2]) + "\" and name=\"" + string(row[3]) + "\" and account=\"" + account + "\" and md5=\"" + string(row[4]) + "\"";
                    mysql_query(mysql, command.c_str());
                }
            }
        }
        for (auto i : hash) {
            // 修改计数
            update_link_count(mysql, i.first, -(i.second));
        }
        logger("用户"+account+"文件夹"+pdir+name+"删除成功");
        msg = "rmdir successfully\n";
        return ACCEPT;
    }
}

int mvdir(MYSQL *(&mysql), string &msg, const string &account, const string &pdir, const string &name, const string &dst) {
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
        // 移动文件夹本身
        command = "update storage set pdir=\"" + dst + "\" where type=\"d\" and pdir=\"" + pdir + "\" and account=\"" + account + "\" and name=\"" + name + "\"";
        mysql_query(mysql, command.c_str());
        // 准备移动文件夹下其他文件/文件夹
        string dir = pdir + name + "/";
        command = "select * from storage where account=\"" + account + "\"";
        mysql_query(mysql, command.c_str());
        res = mysql_store_result(mysql);
        while ((row = mysql_fetch_row(res)) != NULL) {
            if (dir == string(row[2]).substr(0, dir.length())) {
                // 检查是否在该目录下
                if (!strcmp(row[1], "d")) {
                    // 移动子文件夹
                    command = "update storage set pdir=\"" + dst+string(row[2]).substr(pdir.length()) + "\" where type=\"d\" and pdir=\"" + dir + "\" and account=\"" + account + "\" and name=\"" + string(row[3]) + "\"";
                    mysql_query(mysql, command.c_str());
                }
                else if (!strcmp(row[1], "r")) {
                    command = "update storage set pdir=\"" + dst+string(row[2]).substr(pdir.length()) + "\" where type=\"f\" and pdir=\"" + dir + "\" and account=\"" + account + "\" and name=\"" + string(row[3]) + "\" and md5=\"" + string(row[4]) + "\"";
                    mysql_query(mysql, command.c_str());
                }
            }
        }
        logger("用户"+account+"移动文件夹"+pdir+name+"至"+dst);
        msg = "mvdir successfully\n";
        return ACCEPT;
    }
}

int cpdir(MYSQL *(&mysql), string &msg, const string &account, const string &pdir, const string &name, const string &dst) {
    MYSQL_RES *res;
    MYSQL_ROW row;
    string command = "select * from storage where type=\"d\" and name=\"" + name + "\" and pdir=\"" + dst +"\" and account=\"" + account + "\"";
    mysql_query(mysql, command.c_str());
    res = mysql_store_result(mysql);
    if ((row = mysql_fetch_row(res)) != NULL) {
        msg = "A dir with same name exists\n";
        return FAILED;
    }
    else {
        // 准备复制文件夹下其他文件/文件夹
        unordered_map<string, int> hash;
        string dir = pdir + name + "/";
        command = "select * from storage where account=\"" + account + "\"";
        if(mysql_query(mysql, command.c_str())) {
            cerr << "mysql_query failed(" << mysql_error(mysql) << ")" << endl;
        }
        res = mysql_store_result(mysql);
        while ((row = mysql_fetch_row(res)) != NULL) {
            if (dir == string(row[2]).substr(0, dir.length())) {
                // 检查是否在该目录下
                if (!strcmp(row[1], "d")) {
                    // 复制子文件夹
                    command = "insert into storage(account,type,pdir,name,md5)values(\"" + account + "\",\"d\",\"" + dst+string(row[2]).substr(pdir.length()) + "\",\"" + string(row[3]) + "\",\"\")";
                    mysql_query(mysql, command.c_str());
                }
                else if (!strcmp(row[1], "r")) {
                    ++hash[row[4]];
                    command = "insert into storage(account,type,pdir,name,md5)values(\"" + account + "\",\"f\",\"" + dst+string(row[2]).substr(pdir.length()) + "\",\"" + string(row[3]) + "\",\"" + string(row[4]) + "\")";
                    mysql_query(mysql, command.c_str());
                }
            }
        }
        for (auto i : hash) {
            // 修改计数
            update_link_count(mysql, i.first, -(i.second));
        }
        // 复制文件夹本身
        command = "insert into storage(account,type,pdir,name,md5)values(\"" + account + "\",\"d\",\"" + dst + "\",\"" + name + "\",\"\")";
        mysql_query(mysql, command.c_str());
        logger("用户"+account+"复制文件夹"+pdir+name+"至"+dst);
        msg = "cpdir successfully\n";
        return ACCEPT;
    }
}

int handle_rmdir(char *buf, int rn, MYSQL *(&mysql), string &msg) {
    int i = 0;
    string account, pdir, name;
    for (; i < rn && buf[i] != '\n'; ++i) {
        ;
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        account += buf[i];
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        pdir += buf[i];
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        name += buf[i];
    }
    if (account.substr(0, 8) != "account=" || pdir.substr(0, 5) != "pdir=" || name.substr(0, 5) != "name=")  {
        msg = "format error\n";
        return FAILED;
    }
    account = account.substr(8);
    pdir = pdir.substr(5);
    name = name.substr(5);
    return rmdir(mysql, msg, account, pdir, name);
}

int handle_cpdir(char *buf, int rn, MYSQL *(&mysql), string &msg) {
    int i = 0;
    string account, pdir, name, dst;
    for (; i < rn && buf[i] != '\n'; ++i) {
        ;
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        account += buf[i];
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        pdir += buf[i];
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        name += buf[i];
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        dst += buf[i];
    }
    if (account.substr(0, 8) != "account=" || pdir.substr(0, 5) != "pdir=" || name.substr(0, 5) != "name=" || dst.substr(0, 4) != "dst=")  {
        msg = "format error\n";
        return FAILED;
    }
    account = account.substr(8);
    pdir = pdir.substr(5);
    name = name.substr(5);
    dst = dst.substr(4);
    return cpdir(mysql, msg, account, pdir, name, dst);
}

int handle_mvdir(char *buf, int rn, MYSQL *(&mysql), string &msg) {
    int i = 0;
    string account, pdir, name, dst;
    for (; i < rn && buf[i] != '\n'; ++i)
        ;   // event=move
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        account += buf[i];
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        pdir += buf[i];
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        name += buf[i];
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        dst += buf[i];
    }
    if (account.substr(0, 8) != "account=" || pdir.substr(0, 5) != "pdir=" || name.substr(0, 5) != "name=" || dst.substr(0, 4) != "dst=")  {
        msg = "format error\n";
        return FAILED;
    }
    account = account.substr(8);
    pdir = pdir.substr(5);
    name = name.substr(5);
    dst = dst.substr(4);
    return mvdir(mysql, msg, account, pdir, name, dst);
}

int handle_download(char *buf, int rn, MYSQL *(&mysql), string &msg, char *sd, int &size) {
    int i = 0;
    string account, pdir, name, pos;
    for (; i < rn && buf[i] != '\n'; ++i) {
        ;
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        account += buf[i];
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
    account = account.substr(8);
    pdir = pdir.substr(5);
    name = name.substr(5);
    pos = pos.substr(4);
    MYSQL_RES *res;
    MYSQL_ROW row;
    string command = "select * from storage where type=\"f\" and pdir=\"" + pdir + "\" and account=\"" + account + "\" and name=\"" + name + "\"";
    if (mysql_query(mysql, command.c_str())) {
        cerr << "mysql_query failed(" << mysql_error(mysql) << ")" << endl;
    }
    res = mysql_store_result(mysql);
    if ((row = mysql_fetch_row(res)) != NULL) {
        string md5 = row[4];
        fstream fin("/usr/netdisk-file/" + md5, ios::in | ios::binary);
        fin.seekg(stoll(pos), ios::beg);
        fin.read(sd, 4096);
        size = fin.gcount();
        //cout << size << endl;
        if (size < 4096) {
            logger("用户" + account + "文件" + pdir + name + "下载完成");
            msg = "download completed\n";
            return COMPLETE;
        }
        else {
            msg = "downloading\n";
            return ACCEPT;
        }
    }
    msg = "download error\n";
    return FAILED;
}

int handle_rename(char *buf, int rn, MYSQL *(&mysql), string &msg) {
    int i = 0;
    string account, type, pdir, name, newname;
    for (; i < rn && buf[i] != '\n'; ++i) {
        ;
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        account += buf[i];
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        type += buf[i];
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        pdir += buf[i];
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        name += buf[i];
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        newname += buf[i];
    }
    if (account.substr(0, 8) != "account=" || type.substr(0,5) != "type=" || pdir.substr(0, 5) != "pdir=" || name.substr(0, 5) != "name="  || newname.substr(0, 8) != "newname=")  {
        msg = "format error\n";
        return FAILED;
    }
    account = account.substr(8);
    type = type.substr(5);
    pdir = pdir.substr(5);
    name = name.substr(5);
    newname = newname.substr(8);
    MYSQL_RES *res;
    MYSQL_ROW row;
    string command = "select * from storage where account=\"" + account + "\" and pdir=\"" + pdir + "\" and name=\"" + newname + "\" and type=\"" + type + "\"";
    mysql_query(mysql, command.c_str());
    res = mysql_store_result(mysql);
    if ((row = mysql_fetch_row(res)) != NULL) {
        // 存在同名
        msg = "same name exists";
        return FAILED;
    }
    else {
        command = "update storage set name=\"" + newname + "\" where account=\"" + account + "\" and pdir=\"" + pdir + "\" and name=\"" + name + "\" and type=\"" + type + "\"";
        mysql_query(mysql, command.c_str());
        msg = "rename successfully";
        logger("用户" + account + "的" + pdir + name + "改名为" + pdir + newname);
        return ACCEPT;
    }
}

int handle_copyensure(char *buf, int rn, MYSQL *(&mysql), string &msg) {
    int i = 0;
    string account, pdir, name, dst;
    for (; i < rn && buf[i] != '\n'; ++i)
        ;
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        account += buf[i];
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        pdir += buf[i];
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        name += buf[i];
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        dst += buf[i];
    }
    if (account.substr(0, 8) != "account=" || pdir.substr(0, 5) != "pdir=" || name.substr(0, 5) != "name=" || dst.substr(0, 4) != "dst=")  {
        msg = "format error\n";
        return FAILED;
    }
    account = account.substr(8);
    pdir = pdir.substr(5);
    name = name.substr(5);
    dst = dst.substr(4);
    remove(mysql, msg, account, dst, name);
    return copy(mysql, msg, account, pdir, name, dst);
}

int handle_moveensure(char *buf, int rn, MYSQL *(&mysql), string &msg) { 
    int i = 0;
    string account, pdir, name, dst;
    for (; i < rn && buf[i] != '\n'; ++i)
        ;   // event=move
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        account += buf[i];
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        pdir += buf[i];
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        name += buf[i];
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        dst += buf[i];
    }
    if (pdir.substr(0, 5) != "pdir=" || name.substr(0, 5) != "name=" || dst.substr(0, 4) != "dst=" || account.substr(0, 8) != "account=")  {
        msg = "format error\n";
        return FAILED;
    }
    account = account.substr(8);
    pdir = pdir.substr(5);
    name = name.substr(5);
    dst = dst.substr(4);
    remove(mysql, msg, account, dst, name);
    return move(mysql, msg, account, pdir, name, dst);
}

int handle_cpdirensure(char *buf, int rn, MYSQL *(&mysql), string &msg) {
    int i = 0;
    string account, pdir, name, dst;
    for (; i < rn && buf[i] != '\n'; ++i) {
        ;
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        account += buf[i];
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        pdir += buf[i];
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        name += buf[i];
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        dst += buf[i];
    }
    if (account.substr(0, 8) != "account=" || pdir.substr(0, 5) != "pdir=" || name.substr(0, 5) != "name=" || dst.substr(0, 4) != "dst=")  {
        msg = "format error\n";
        return FAILED;
    }
    account = account.substr(8);
    pdir = pdir.substr(5);
    name = name.substr(5);
    dst = dst.substr(4);
    rmdir(mysql, msg, account, dst, name);
    return cpdir(mysql, msg, account, pdir, name, dst);
}

int handle_mvdirensure(char *buf, int rn, MYSQL *(&mysql), string &msg) {
    int i = 0;
    string account, pdir, name, dst;
    for (; i < rn && buf[i] != '\n'; ++i)
        ;   // event=move
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        account += buf[i];
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        pdir += buf[i];
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        name += buf[i];
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        dst += buf[i];
    }
    if (account.substr(0, 8) != "account=" || pdir.substr(0, 5) != "pdir=" || name.substr(0, 5) != "name=" || dst.substr(0, 4) != "dst=")  {
        msg = "format error\n";
        return FAILED;
    }
    account = account.substr(8);
    pdir = pdir.substr(5);
    name = name.substr(5);
    dst = dst.substr(4);
    rmdir(mysql, msg, account, dst, name);
    return mvdir(mysql, msg, account, pdir, name, dst);
}