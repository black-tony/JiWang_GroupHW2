#pragma once
#include <mysql.h>
#include <string>
#include "tools.h"

int handle_register(char *buf, int size, MYSQL *(&mysql), std::string &msg);
int handle_login(char *buf, int size, MYSQL *(&mysql), Client &client, std::string &msg);