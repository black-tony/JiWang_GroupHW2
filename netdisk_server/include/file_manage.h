#pragma once
#include <string>
#include <mysql.h>

int handle_upload(char *buf, int size, const std::string &account, MYSQL *(&mysql), std::string &msg);
int handle_list(char *buf, int rn, MYSQL *(&mysql), const std::string &account, std::string &msg);