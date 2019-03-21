CXX=g++

ifdef SYSTEMROOT
    CXXFLAGS += -lpthread
else
    CXXFLAGS += -pthread
endif

ifeq ($(SSE4),1)
	CXXFLAGS += -msse4.2
endif

SRCS := $(wildcard omp/*.cpp)
SRCS += $(wildcard omp/*.c)

all: lib/ompeval.so

lib:
	mkdir lib

lib/ompeval.so: $(SRCS) | lib
	$(CXX) -Wall -shared -o $@ -O3 -fPIC $^

clean:
	$(RM) lib/ompeval.so
