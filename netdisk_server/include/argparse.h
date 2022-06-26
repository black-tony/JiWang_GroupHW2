#pragma once
#include <vector>
#include <string>
#define ERROR   -1

enum Type { OPTIONAL, REQUIRED, NOARG };

struct Option{
    const char *name;
    Type opttype;
    Type argtype;
    const char *usage;
    const char *doc;
};

class ArgParser {
protected:
    struct Option *options;
    int optnum;
    int paramnum;
    std::vector<std::string> results;
    std::vector<bool> flag;
    std::vector<std::string> params;
    int searchOption(const char *target);
public:
    ArgParser(Option *ops = nullptr, const int n = 0, const int m = 0);
    void usage();
    int parse(int argc, char *argv[]);
    int getOpt(const char *name, int &value);
    int getOpt(const char *name, std::string &value);
    int getOpt(const char *name);
};
