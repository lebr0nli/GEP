CC = gcc
CFLAGS = -g -O0

all: test_program

test_program: test_program.c
	$(CC) $(CFLAGS) -o $@ $<

clean:
	rm -f test_program

.PHONY: all clean
