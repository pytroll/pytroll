#g++ -D_UNIX_OS_ -I/local_disk/usr/src/tmp/mccapi/include -L/home/a001673/usr/src/tmp/mccapi/resource/build/lib MessagePublisher.cpp -lpthread -Bstatic -lmccapi
#g++ -D_UNIX_OS_ -I/local_disk/usr/src/tmp/mccapi/include -L/home/a001673/usr/src/tmp/mccapi/resource/build/lib StatusChecker.cpp -lpthread -Bstatic -lmccapi

CC=g++

MCCLIB=/home/a001673/usr/src/mccapi/resource/build/lib
MCCINC=/local_disk/usr/src/mccapi/include
POSTTROLLLIB=/home/a001673/usr/src/posttroll/posttroll++
POSTTROLLINC=/home/a001673/usr/src/posttroll/
SRC=MessagePublisher.cpp
TARGET=mp

all: $(TARGET)

mp: $(SRC)
	$(CC) -D_UNIX_OS_ -I$(MCCINC) -I$(POSTTROLLINC) -L$(MCCLIB) -L$(POSTTROLLLIB) $< -lpthread -lzmq -Bstatic -lmccapi -lposttroll -o $(TARGET)