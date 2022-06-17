#include <iostream>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <sys/epoll.h>
#include <string>
#include <vector>
#include <cstring>
#include <unistd.h>
#include <netinet/in.h>
#include <sys/ioctl.h>
#include <net/if.h>
#include "tools.h"
#include <fstream>
#include <mysql.h>  // mysql特有
using namespace std;

#define EPOLL_SIZE 1024
#define MAX_LINK 1000
#define TIMEOUT 600

void logger(const string &msg) {
    fstream log("netdisk.log", ios::out | ios::app);
    log << "[" << get_time() << "]: " << msg << endl;
}

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

int connect_mysql(MYSQL*(&mysql), const string &db_name) {
    // initial
    if (NULL == (mysql = mysql_init(NULL))) {
        cerr << "mysql_init failed" << endl;
        return -1;
    }
    // connect
    if (NULL == mysql_real_connect(mysql,"localhost", "root", "root123",db_name.c_str(), 0, NULL, 0)) {
        cout << "mysql_real_connect failed(" << mysql_error(mysql) << ")" << endl;
        return -1;
    }
    // 设置字符集,不然读出来乱码
    mysql_set_character_set(mysql, "gbk");
    return 0;
}

int register_user(MYSQL *(&mysql), const string &account, const string &passwd) {
    MYSQL_RES *res;
    MYSQL_ROW row;
    string command = "select account from user where (account=" + account + ")";
    query(mysql, res, command);
    if ((row = mysql_fetch_row(res)) == NULL) {
        // 未查找到结果,即不存在重复用户,可以注册
        command = "insert into user(account,passwd)values(\"" + account + "\",\"" + passwd + "\")";
        if (mysql_query(mysql, command.c_str())) {
            cerr << "mysql_query failed(" << mysql_error(mysql) << ")" << endl;
            return -1;
        }
    }
    else {
        return -1;
    }
    logger("用户" + account + "注册");
    return 0;
}

int handle_register(char *buf, int size, MYSQL *(&mysql)) {
    string account;
    string passwd;
    int i = 0;
    for (; i < size && buf[i] != '\n'; ++i)
        ;   // event=register
    for (++i; i < size && buf[i] != '\n'; ++i) {
        account += buf[i];
    }
    for (++i; i < size && buf[i] != '\n'; ++i) {
        passwd += buf[i];
    }
    if (account.substr(0, 8) == "account=" && passwd.substr(0, 7) == "passwd=") {
        account = account.substr(8);
        passwd = passwd.substr(7);
        if (account.size() > 0 && passwd.size() > 0) {
            if (register_user(mysql, account, passwd) < 0) {
                return -1;
            }
            else {
                return 0;
            }
        }
    }

    return -1;
}

int user_login(MYSQL *(&mysql), const string &account, const string &passwd) {
    MYSQL_RES *res;
    MYSQL_ROW row;
    string command = "select * from user where (account=" + account + ")";
    query(mysql, res, command);
    if ((row = mysql_fetch_row(res)) != NULL) {
        if (row[1] != passwd) {
            return -1;
        }
        else {
            logger("用户" + account + "登陆");
            return 0;
        }
    }
    else {
        // 未查找到结果,用户名不存在
        return -1;
    }

}

int handle_login(char *buf, int size, MYSQL *(&mysql)) {
    string account;
    string passwd;
    int i = 0;
    for (; i < size && buf[i] != '\n'; ++i)
        ;   // event=login
    for (++i; i < size && buf[i] != '\n'; ++i) {
        account += buf[i];
    }
    for (++i; i < size && buf[i] != '\n'; ++i) {
        passwd += buf[i];
    }
    if (account.substr(0, 8) == "account=" && passwd.substr(0, 7) == "passwd=") {
        account = account.substr(8);
        passwd = passwd.substr(7);
        if (account.size() > 0 && passwd.size() > 0) {
            if (user_login(mysql, account, passwd) < 0) {
                return -1;
            }
            else {
                return 0;
            }
        }
    }

    return -1;
}

int event_parse(char *buf, int size, MYSQL *(&mysql)) {
    string str;
    for (int i = 0; i < size && buf[i] != '\n'; ++i) {
        str += buf[i];
    }
    if (str.substr(0, 6) == "event=") {
        string event = str.substr(6);
        if (event == "register") {
            if (handle_register(buf, size, mysql) < 0) {
                return -1;
            }
        }
        else if (event == "login") {
            if (handle_login(buf, size, mysql) < 0) {
                return -1;
            }
        }
    }
    return 0;
}

int handle_accept(int server_fd, int epoll_fd, vector<Client> &clients) {
    Client cli;
    socklen_t addr_len = sizeof(sockaddr_in);
    cli.sfd = accept(server_fd, (sockaddr*)(&cli.addr), &addr_len);
    setnonblock(cli.sfd);
    add_event(epoll_fd, cli.sfd, EPOLLIN);
    clients.emplace_back(cli);

    return 0;
}

int handle_recv(int client_fd, int epoll_fd, vector<Client> &clients, MYSQL *(&mysql)) {
    constexpr int size = 1024;
    char buf[size];
    memset(buf, 0, sizeof(buf));
    int rn = recv(client_fd, buf, sizeof(buf), 0);
    if (rn <= 0) {
        // 断开连接
        close(client_fd);
        del_event(epoll_fd, client_fd, EPOLLIN);
        const int len = clients.size();
        for(int i = 0; i < len; ++i) {
            if (clients[i].sfd == client_fd) {
                clients.erase(i + clients.begin());
            }
        }
    }
    else {
        char rep[100];
        memset(rep, 0, sizeof(rep));
        if (event_parse(buf, size, mysql) < 0) {
            strcpy(rep, "failed\n");
        }
        else {
            strcpy(rep, "accepted\n");
        }
        send(client_fd, rep, strlen(rep), 0);
    }
    return 0;
}

void handle(int server_fd, MYSQL *(&mysql)) {
    vector<Client> clients;
    int epoll_fd = epoll_create(EPOLL_SIZE);
    add_event(epoll_fd, server_fd, EPOLLIN);
    epoll_event events[MAX_LINK];
    int conn_cnt = 0;

    while (1) {
        if (conn_cnt >= MAX_LINK) {
            logger("连接数达到上限");
        }
        int ev_cnt = epoll_wait(epoll_fd, events, MAX_LINK, TIMEOUT);
        for (int i = 0; i < ev_cnt; ++i) {
            int fd = events[i].data.fd;
            if (fd == server_fd && (events[i].events & EPOLLIN != 0)) {
                handle_accept(server_fd, epoll_fd, clients);
            }
            else if (fd != server_fd) {
                if (events[i].events & EPOLLIN != 0) {
                    handle_recv(fd, epoll_fd, clients, mysql);
                }
            }
        }
    }
}

int main() {
    Server server;
    string ip = "192.168.80.230";
    int port = 4000;

    MYSQL *mysql;
    // MYSQL *mysql_user;
    if (connect_mysql(mysql, "netdisk") < 0) {
        return -1;
    }
    if (server_init(server, ip, port) != 0) {
        return -1;
    }

    handle(server.sfd, mysql);
}