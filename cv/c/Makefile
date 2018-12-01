CXX ?= g++

CXXFLAGS += -c -Wall -O3
LDFLAGS += -lfreenect

all: speed

speed: speed.o; g++ $< -o $@ $(LDFLAGS)

%.o: %.c; g++ $< -o $@ $(CXXFLAGS)

clean: ; rm -f speed.o

