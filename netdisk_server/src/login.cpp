#include <iostream>
#include <arpa/inet.h>
#include <sys/epoll.h>
#include <vector>
#include <cstring>
#include <unistd.h>
#include <netinet/in.h>
#include <sys/ioctl.h>
#include <net/if.h>
#include "tools.h"
#include <fstream>
#include "login.h"
using namespace std;

int query(MYSQL *(&mysql), MYSQL_RES *(&res), const string &command) {
    if (mysql_query(mysql, command.c_str())) {
        cerr << "mysql_query failed(" << mysql_error(mysql) << ")" << endl;
        return -1;
    }

    /* 将查询结果存储起来，出现错误则返回NULL
       注意：查询结果为NULL，不会返回NULL */
    if ((res = mysql_store_result(mysql))==NULL) {
        cout << "mysql_store_result failed" << endl;
        return -1;
    }
    return 0;
}

int register_user(MYSQL *(&mysql), const string &account, const string &passwd, string &msg) {
    MYSQL_RES *res;
    MYSQL_ROW row;
    string command = "select account from user where (account=\"" + account + "\")";
    query(mysql, res, command);
    if ((row = mysql_fetch_row(res)) == NULL) {
        // 未查找到结果,即不存在重复用户,可以注册
        command = "insert into user(account,passwd)values(\"" + account + "\",\"" + passwd + "\")";
        if (mysql_query(mysql, command.c_str())) {
            cerr << "mysql_query failed(" << mysql_error(mysql) << ")" << endl;
            msg = "register failed, database error\n";
            return FAILED;
        }
    }
    else {
        msg = "duplicate account\n";
        return FAILED;
    }
    logger("用户" + account + "注册");
    msg = "register success\n";
    return ACCEPT;
}

int handle_register(char *buf, int rn, MYSQL *(&mysql), string &msg) {
    string account;
    string passwd;
    int i = 0;
    for (; i < rn && buf[i] != '\n'; ++i)
        ;   // event=register
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        account += buf[i];
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        passwd += buf[i];
    }
    if (account.substr(0, 8) == "account=" && passwd.substr(0, 7) == "passwd=") {
        account = account.substr(8);
        passwd = passwd.substr(7);
        if (account.size() > 0 && passwd.size() > 0) {
            return register_user(mysql, account, passwd, msg);
        }
    }
    msg = "format error\n";
    return FAILED;
}

int user_login(MYSQL *(&mysql), const string &account, const string &passwd, string &msg) {
    MYSQL_RES *res;
    MYSQL_ROW row;
    string command = "select * from user where (account=\"" + account + "\")";
    query(mysql, res, command);
    if ((row = mysql_fetch_row(res)) != NULL) {
        if (row[1] != passwd) {
            msg = "incorrect account or password\n";
            return FAILED;
        }
        else {
            logger("用户" + account + "登陆");
            msg = "login success\n";
            return ACCEPT;
        }
    }
    else {
        // 未查找到结果,用户名不存在
        msg = "account does not exist\n";
        return FAILED;
    }

}

int handle_login(char *buf, int rn, MYSQL *(&mysql), Client &client, string &msg) {
    string account;
    string passwd;
    int i = 0;
    for (; i < rn && buf[i] != '\n'; ++i)
        ;   // event=login
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        account += buf[i];
    }
    for (++i; i < rn && buf[i] != '\n'; ++i) {
        passwd += buf[i];
    }
    if (account.substr(0, 8) == "account=" && passwd.substr(0, 7) == "passwd=") {
        account = account.substr(8);
        passwd = passwd.substr(7);
        if (account.size() > 0 && passwd.size() > 0) {
            if (user_login(mysql, account, passwd, msg) == FAILED) {
                return FAILED;
            }
            else {
                client.account = account;
                return ACCEPT;
            }
        }
    }
    msg = "format error\n";
    return FAILED;
}