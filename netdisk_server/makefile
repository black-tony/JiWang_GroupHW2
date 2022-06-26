CC:=g++
INCLUDE:=./include
SRC_DIR:=./src
SRC:=$(SRC_DIR)/main.cpp $(SRC_DIR)/tools.cpp $(SRC_DIR)/login.cpp $(SRC_DIR)/file_manage.cpp $(SRC_DIR)/my_daemon.cpp $(SRC_DIR)/argparse.cpp

.PHONY: all clean

all: netdisk_server

netdisk_server: $(SRC)
	$(CC) $(SRC) -I$(INCLUDE) $$(mysql_config --include) $$(mysql_config --libs) -o netdisk_server

clean:
	rm -rf netdisk_server netdisk.log
