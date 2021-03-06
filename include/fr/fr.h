#ifndef CSCA_FR_HPP
#define CSCA_FR_HPP

#include <stdio.h>
#include <stdint.h>
#include <unistd.h>
#include <sys/mman.h>
#include <fcntl.h>
#include <sys/types.h>
#include <stdlib.h>
#include <sched.h>

#define HIST_SIZE 700

#define ARRAY_SIZE(arr) sizeof(arr)/sizeof(arr[0])

typedef struct FR {

	unsigned int* results;
	unsigned int num_time_slots;

	// timestamp to detect hit range
	unsigned int hit_begin;
	unsigned int hit_end;

	// array of addresses
	unsigned int len;
	void** addrs;
} FR;

#define fr_init(num_slots, ...)\
	(FR){\
		.results = (unsigned int[ num_slots * ARRAY_SIZE( ( (void*[]){__VA_ARGS__} ) ) ]){0},\
		.num_time_slots = num_slots,\
		.hit_begin = 0,\
		.hit_end = 180,\
		.len = ARRAY_SIZE( ( (void*[]){__VA_ARGS__} ) ),\
		.addrs = (void*[]){__VA_ARGS__}\
	};\

// monitor addresses, return which address was detected in the "results" matrix
void fr_monitor_raw(FR*);

// mmap an elf binary to memory and call "fr_monitor". It detects if the
// binary was compiled to be position independent, if it was, it interprets
// the given addresses as offsets
void fr_monitor_elf(FR*, const char* filename);

// find the best hit_begin and hit_end.
// "sensibility" determines how much false positives are tolerated.
// high "sensibility" trades less false positives for less true positives,
// since it decreases the hit range.
// "num_samples" is the number of samples used for calibration.
// "filename" is a file in which a histogram (produced during calibration)
// can be saved, you  can just give it NULL if you don't want to write it.
void fr_calibrate(FR*, double sensibility, unsigned int num_samples, const char* filename);

#endif
