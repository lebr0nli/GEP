CC = gcc
CXX = g++
CFLAGS = -g -O0
CXXFLAGS = -g -O0

all: test_program test_program_cpp

test_program: test_program.c
	$(CC) $(CFLAGS) -o $@ $<

test_program_cpp: test_program_cpp.cc
	$(CXX) $(CXXFLAGS) -o $@ $<

clean:
	rm -f test_program test_program_cpp

.PHONY: all clean
