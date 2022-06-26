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
#include "argparse.h"
#include <fstream>
#include <mysql.h>  // mysql特有
#include "my_daemon.h"
using namespace std;

#define EPOLL_SIZE 1024
#define MAX_LINK 1000
#define TIMEOUT 600

static Option options[] = {
    {"port", REQUIRED, REQUIRED, "--port [端口号]", "指定服务端端口号"},
    {"ip", OPTIONAL, REQUIRED, "--ip [ip地址]", "指定服务器绑定地址"}
};

struct Arguments {
    int port;
    string ip;
};

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

int event_parse(char *buf, int rn, MYSQL *(&mysql), Client &client, char *rep) {
    string event;
    string msg;
    int ret = FAILED;
    char sd[5000];
    int size;
    for (int i = 0; i < rn && buf[i] != '\n'; ++i) {
        event += buf[i];
    }
    if (event.substr(0, 6) == "event=") {
        event = event.substr(6);
        if (event == "register") {
            ret = handle_register(buf, rn, mysql, msg);
        }
        else if (event == "login") {
            ret = handle_login(buf, rn, mysql, client, msg);
        }
        else if (event == "upload") {
            ret = handle_upload(buf, rn, mysql, msg);
        }
        else if (event == "list") {
            ret = handle_list(buf, rn, mysql, msg);
        }
        else if (event == "move") {
            ret = handle_move(buf, rn, mysql, msg);
        }
        else if (event == "copy") {
            ret = handle_copy(buf, rn, mysql, msg);
        }
        else if (event == "remove") {
            ret = handle_remove(buf, rn, mysql, msg);
        }
        else if (event == "mkdir") {
            ret = handle_mkdir(buf, rn, mysql, msg);
        }
        else if (event == "rmdir") {
            ret = handle_rmdir(buf, rn, mysql, msg);
        }
        else if (event == "mvdir") {
            ret = handle_mvdir(buf, rn, mysql, msg);
        }
        else if (event == "download") {
            ret = handle_download(buf, rn, mysql, msg, sd, size);
        }
        else if (event == "rename") {
            ret = handle_rename(buf, rn, mysql, msg);
        }
        else {
            msg = "event error\n";
            ret = FAILED;
        }
    }
    strcpy(rep, exceptions[ret]);
    strcat(rep, msg.c_str());
    if(event == "download") {
        memcpy(rep + int(msg.size()), sd, size);
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
        char rep[5000];
        memset(rep, 0, sizeof(rep));
        event_parse(buf, rn, mysql, clients[i], rep);
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



int cmdlineParse(Arguments &args, int argc, char * argv[]) {
    ArgParser argp(options, sizeof(options) / sizeof(Option), 0);
    if (argp.parse(argc, argv) != 0) {
        return -1;
    }
    if (argp.getOpt("port", args.port) == -1) {
        return -1;
    }
    if (args.port < 0 || args.port > 65535) {
        cout << "port范围超出限制! 范围为[0..65535]" << endl;
        return -1;
    }
    if (argp.getOpt("ip", args.ip) != 0) {
        args.ip = "";
        return 0;   
    }
    return 0;
}

int main(int argc, char *argv[]) {
    Arguments args = {-1};
    if (cmdlineParse(args, argc, argv) < 0) {
        exit(EXIT_FAILURE);
    }

    my_daemon(1, 1);
    Server server;

    mkdir("/usr/netdisk-file",0777);
    MYSQL *mysql;
    // MYSQL *mysql_user;
    if (connect_mysql(mysql, "netdisk") < 0) {
        return -1;
    }
    if (server_init(server, args.ip, args.port) != 0) {
        return -1;
    }

    handle(server.sfd, mysql);
}