CC:=g++
INCLUDE:=./include
SRC_DIR:=./src
SRC:=$(SRC_DIR)/main.cpp $(SRC_DIR)/tools.cpp

.PHONY: all clean

all: netdisk_server

netdisk_server: $(SRC)
	$(CC) $(SRC) -I$(INCLUDE) $$(mysql_config --include) $$(mysql_config --libs) -o netdisk_server

clean:
	rm -rf netdisk_server