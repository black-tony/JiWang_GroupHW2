#include <cstring>
#include <string>
#include <iostream>
#include <vector>
#include "argparse.h"
using namespace std;

int ArgParser::searchOption(const char *target) {
    for (int i = 0; i < optnum; ++i) {
        if (strcmp(options[i].name, target) == 0) {
            return i;
        }
    }
    return -1;
}
    
ArgParser::ArgParser(Option *ops, const int n, const int m) {
    options = ops;
    optnum = n;
    results.resize(n);
    flag.resize(n, false);
    paramnum = m;
}

void ArgParser::usage() {
    if (options == nullptr) {
        return;
    }
    for (int i = 0; i < optnum; ++i) {
        cout << options[i].name << ": ";
        if (options[i].usage != nullptr) {
            cout << options[i].usage << " ";
        }
        if (options[i].doc != nullptr) {
            cout << options[i].doc;
        }
        cout << endl;
    }
}

int ArgParser::parse(int argc, char *argv[]) {
    if (options == nullptr) {
        return -1;
    }
    int cnt = 0;
    for (int i = 1; i < argc; ) {
        if (argv[i][0] == '-' && argv[i][1] == '-') {
            int pos = searchOption(argv[i] + 2);
            if (pos == -1) {
                cerr << "未知的选项" << argv[i] << endl;
                return -1;
            }
            flag[pos] = true;
            if (options[pos].argtype == NOARG) {
                ++i;
                continue;
            }
            if ((i + 1 >= argc) || (argv[i + 1][0] == '-' && argv[i + 1][1] == '-')) {
                if (options[pos].argtype == REQUIRED) {
                    cerr << "选项" << argv[i] << "缺少参数" << endl;
                    return -1;
                }
                ++i;
            }
            else {
                results[pos] = argv[i + 1]; 
                i += 2;
            }
        }
        else {
            ++cnt;
            if (cnt > paramnum) {
                cout << "未知的参数" << argv[i] << endl;
                return -1;
            }
            params.emplace_back(argv[i]);
            ++i;
        }
    }
    
    for (int i = 0; i < optnum; ++i) {
        if (options[i].opttype == REQUIRED && flag[i] == false) {
            cout << "缺少选项--" << options[i].name << endl;
            return -1;
        }
    }
    return 0;
}

int ArgParser::getOpt(const char *name, int &value) {
    int pos = searchOption(name);
    if (pos == -1 || flag[pos] == false) {
        return 1;
    }
    else {
        if (results[pos].size() == 0) {
            return 0;
        }
        try {
            value = stoi(results[pos]);
        }
        catch (const invalid_argument &) {
            cerr << "选项" << name << "参数不是合法值" << endl;
            return -1;
        }
        catch (const out_of_range &) {
            cerr << "选项" << name << "参数超范围" << endl;
            return -1;
        }
        catch (...) {
            cerr << "选项" << name << "参数解析失败" << endl;
            return -1;
        }
    }
    return 0;
}

int ArgParser::getOpt(const char *name, string &value) {
    int pos = searchOption(name);
    if (pos == -1 || flag[pos] == false) {
        return 1;
    }
    else {
        value = results[pos];
        return 0;
    }
}

int ArgParser::getOpt(const char *name) {
    int pos = searchOption(name);
    if (pos == -1 || flag[pos] == false) {
        return 1;
    }
    else {
        return 0;
    }
}
