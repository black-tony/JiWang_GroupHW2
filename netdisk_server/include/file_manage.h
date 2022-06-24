#pragma once
#include <string>
#include <mysql.h>

int handle_upload(char *buf, int size, const std::string &account, MYSQL *(&mysql), std::string &msg);
int handle_list(char *buf, int rn, MYSQL *(&mysql), const std::string &account, std::string &msg);
int handle_move(char *buf, int rn, MYSQL *(&mysql), const std::string &account, std::string &msg);
int handle_copy(char *buf, int rn, MYSQL *(&mysql), const std::string &account, std::string &msg);
int handle_remove(char *buf, int rn, MYSQL *(&mysql), const std::string &account, std::string &msg);
int handle_mkdir(char *buf, int rn, MYSQL *(&mysql), const std::string &account, std::string &msg);
int handle_rmdir(char *buf, int rn, MYSQL *(&mysql), const std::string &account, std::string &msg);
int handle_mvdir(char *buf, int rn, MYSQL *(&mysql), const std::string &account, std::string &msg);
int handle_download(char *buf, int rn, MYSQL *(&mysql), const std::string &account, std::string &msg, char *sd, int& size);