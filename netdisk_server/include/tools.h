#pragma once
#include <string>


void logger(const std::string &msg);

struct Server {
    int sfd;
    std::string ip;
    int port;
    sockaddr_in addr;
};

struct Client {
    int sfd;
    sockaddr_in addr;
    std::string ip;
};

int setnonblock(int sockfd, bool nonblock = true);
int server_init(Server &s, const std::string &ip, const int port);

void add_event(int epollfd, int fd, int state);
void del_event(int epollfd, int fd, int state);
void mod_event(int epollfd, int fd, int state);

std::string get_time();

#define ACCEPT 0
#define FAILED 1
#define COMPLETE 2