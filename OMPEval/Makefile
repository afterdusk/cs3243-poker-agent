CXX=g++

SRCS := $(wildcard omp/*.cpp)
SRCS += $(wildcard omp/*.c)

all: lib/ompeval.so

lib:
	mkdir lib

lib/ompeval.so: $(SRCS) | lib
	$(CXX) -Wall -shared -o $@ -O3 -std=c++11 -fPIC $^

clean:
	$(RM) lib/ompeval.so
