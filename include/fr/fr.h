#ifndef CSCA_FR_HPP
#define CSCA_FR_HPP

#include <stdio.h>
#include <string.h>
#include <sys/mman.h>

#define ARRAY_SIZE(arr) sizeof(arr)/sizeof(arr[0])

typedef struct FR {

	int (*cbk)(void* addr);
	unsigned int hit_begin;
	unsigned int hit_end;

	unsigned int len;
	void** addrs;
} FR;

#define fr_init(...)\
	(FR){\
		.cbk = NULL,\
		.hit_begin = 0,\
		.hit_end = 225,\
		.len = ARRAY_SIZE( ( (void*[]){__VA_ARGS__} ) ),\
		.addrs = (void*[]){__VA_ARGS__}\
	}

// set callback function, which will be called when a hit is detected
// in a address (the one given as argument)
// if callback returns a non-zero value, the monitoring stops
void fr_set_callback(FR*, int (*cbk)(void* addr));

// monitor addresses, callback is called when a hit is detected
// functions ends when a callback returns a non-zero value
void fr_monitor(FR*);

// mmap an binary to memory, you can also just
// use "fr_monitor()" and "fr_set_callback()"
// without this
void fr_load_bin(FR*, const char*);

#endif
