CC = zig cc
CXX = zig cc
TARGET = x86_64-linux-musl
CFLAGS = -target $(TARGET) -static -g -O0
# Workaround for: https://codeberg.org/ziglang/zig/issues/32132
CXXFLAGS = -x c++ -target $(TARGET) -static -g -O0

all: test_program test_program_cpp

test_program: test_program.c
	$(CC) $(CFLAGS) -o $@ $<

test_program_cpp: test_program_cpp.cc
	$(CXX) $(CXXFLAGS) -o $@ $<

clean:
	rm -f test_program test_program_cpp

.PHONY: all clean
