#include <iostream>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <string>
#include <cstring>
#include <unistd.h>
#include <netinet/in.h>
#include <sys/ioctl.h>
#include <net/if.h>
#include <fcntl.h>
#include "tools.h"
#include <sys/epoll.h>
using namespace std;

#define ERROR -1

int server_init(Server &s, const string &ip, const int port) {
    // 创建监听描述符
    if (-1 == (s.sfd = socket(AF_INET, SOCK_STREAM, 0))) {
        perror("socket error");
        return ERROR;
    }
    s.addr.sin_family = AF_INET;
    // 绑定ip和端口
    if (ip.size() == 0 || ip == "0.0.0.0") {
        // any ip
        s.addr.sin_addr.s_addr = htonl(INADDR_ANY);
    }
    else {
        s.addr.sin_addr.s_addr = inet_addr(ip.c_str());
    }
    s.addr.sin_port = htons(port);

    // 在绑定前设置REUSEADDR
    int enable = 1;
    if (setsockopt(s.sfd, SOL_SOCKET, SO_REUSEADDR, &enable, sizeof(int)) < 0) {
        perror("setsockopt(SO_REUSEADDR) failed");
        close(s.sfd);
        return ERROR;
    }

    if ((bind(s.sfd, (sockaddr *)&s.addr, sizeof(s.addr))) < 0) {
        perror("bind error!");
        close(s.sfd);
        return ERROR;
    }

    setnonblock(s.sfd);

    if (listen(s.sfd, 128) < 0) {
        perror("listen error");
        close(s.sfd);
        return ERROR;
    }

    return 0;
}

int setnonblock(int sockfd, bool nonblock) {
    int flags = fcntl(sockfd, F_GETFL, 0);
    if (flags < 0) {
        return -1;
    }
    return nonblock == true ? fcntl(sockfd, F_SETFL, flags | O_NONBLOCK) : fcntl(sockfd, F_SETFL, flags & ~O_NONBLOCK);
}

void add_event(int epollfd, int fd, int state){
    struct epoll_event ev;
    ev.events = state;
    ev.data.fd = fd;
    epoll_ctl(epollfd,EPOLL_CTL_ADD,fd,&ev);
}

void del_event(int epollfd, int fd, int state){
    struct epoll_event ev;
    ev.events = state;
    ev.data.fd = fd;
    epoll_ctl(epollfd,EPOLL_CTL_DEL,fd,&ev);
}

void mod_event(int epollfd, int fd, int state){
    struct epoll_event ev;
    ev.events = state;
    ev.data.fd = fd;
    epoll_ctl(epollfd,EPOLL_CTL_MOD,fd,&ev);
}

string get_time() {
    time_t now = time(0);
    string t = ctime(&now);
    const int len = t.size();
    return t.substr(0, len - 1);
}