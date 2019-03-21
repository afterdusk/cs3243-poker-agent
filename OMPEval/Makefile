CXXFLAGS += -O3 -std=c++11 -Wall -Wpedantic

ifdef SYSTEMROOT
    CXXFLAGS += -lpthread
else
    CXXFLAGS += -pthread
endif

ifeq ($(SSE4),1)
	CXXFLAGS += -msse4.2
endif

SRCS := $(wildcard omp/*.cpp)
OBJS := ${SRCS:.cpp=.o}

all: lib/ompeval.a

lib:
	mkdir lib

lib/ompeval.a: $(OBJS) | lib
	ar rcs $@ $^

clean:
	$(RM) lib/ompeval.a $(OBJS)
