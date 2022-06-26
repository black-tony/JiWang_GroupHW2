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
    std::string account;
};

int setnonblock(int sockfd, bool nonblock = true);
int server_init(Server &s, const std::string &ip, const int port);

void add_event(int epollfd, int fd, int state);
void del_event(int epollfd, int fd, int state);
void mod_event(int epollfd, int fd, int state);

std::string get_time();

#define LOGIN_ACCEPT 0
#define LOGIN_FAILED 1

#define REG_ACCEPT 2
#define REG_FAILED 3

#define UPLOAD_ACCEPT 4
#define UPLOAD_FAILED 5
#define UPLOAD_COMPLETE 6

#define  LIST_ACCEPT 7
#define  LIST_FAILED 8

#define  MOVE_ACCEPT 9
#define  MOVE_FAILED 10

#define  COPY_ACCEPT 11
#define  COPY_FAILED 12

#define  REMOVE_ACCEPT 13
#define  REMOVE_FAILED 14

#define  MKDIR_ACCEPT 15
#define  MKDIR_FAILED 16

#define  RMDIR_ACCEPT 17
#define  RMDIR_FAILED 18

#define  MVDIR_ACCEPT 19
#define  MVDIR_FAILED 20

#define  DOWNLOAD_ACCEPT 21
#define  DOWNLOAD_FAILED 22

#define  ACCEPT 23
#define  FAILED 24