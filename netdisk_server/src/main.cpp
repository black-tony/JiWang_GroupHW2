#include <iostream>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/epoll.h>
#include <arpa/inet.h>
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

#define EPOLL_SIZE 1024
#define MAX_LINK 1000
#define TIMEOUT 600

const char* exceptions[] = {
    "accepted\n",
    "failed\n",
    "completed\n",    // file transport complete
};

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

int event_parse(char *buf, int rn, MYSQL *(&mysql), Client &client, string &msg) {
    string event;
    for (int i = 0; i < rn && buf[i] != '\n'; ++i) {
        event += buf[i];
    }
    if (event.substr(0, 6) == "event=") {
        event = event.substr(6);
        if (event == "register") {
            return handle_register(buf, rn, mysql, msg);
        }
        else if (event == "login") {
            return handle_login(buf, rn, mysql, client, msg);
        }
        else if (event == "upload") {
            return handle_upload(buf, rn, client.account ,mysql, msg);
        }
        else if (event == "list") {
            return handle_list(buf, rn, mysql, client.account, msg);
        }
    }
    msg = "format error\n";
    return FAILED;
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
    constexpr int size = 20480;
    char buf[size];
    memset(buf, 0, sizeof(buf));

    const int len = clients.size();
    int i = 0;
    for(; i < len; ++i) {
        if (clients[i].sfd == client_fd) {
            break;
        }
    }
    int rn = recv(client_fd, buf, sizeof(buf), 0);
    if (rn <= 0) {
        // 断开连接
        close(client_fd);
        del_event(epoll_fd, client_fd, EPOLLIN);
        clients.erase(clients.begin() + i);
    }
    else {
        char rep[100];
        memset(rep, 0, sizeof(rep));
        string msg;
        int excep = event_parse(buf, rn, mysql, clients[i], msg);
        strcpy(rep, exceptions[excep]);
        strcat(rep, msg.c_str());
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
    mkdir("./file",0755);
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