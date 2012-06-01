CC      = g++
CFLAGS  = -pedantic -Wall -fPIC
LDFLAGS = -lzmq
TARGET  = publisher
SOURCES = publisher.cpp message.cpp
OBJECTS = $(SOURCES:.cpp=.o)
LIB	= libposttroll.so
SLIB    = libposttroll.a

all: $(TARGET) $(LIB) $(SLIB)

$(TARGET): $(OBJECTS)
	$(CC) $(LDFLAGS) $^ -o $@

$(LIB): $(OBJECTS)
	ld -shared -soname $@ $^

$(SLIB): $(OBJECTS)
	ar -ur $@ $^


.cpp.o:
	$(CC) -c $(CFLAGS) $<

.PHONY: clean cleanest

clean:
	rm -f *.o

cleanest: clean
	rm -f $(TARGET) $(LIB) $(SLIB)