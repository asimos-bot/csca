#ifndef CSCA_RSACRT_H
#define CSCA_RSACRT_H

#include "fr/fr.h"

#define RSACRT_S_IDX 0
#define RSACRT_R_IDX 1
#define RSACRT_M_IDX 2

#define N_BITS 2048

typedef struct rsacrt_data {

	char bits[N_BITS];
	unsigned int n_bits;
	unsigned int n_bits_last_seq;
} rsacrt_data;

// write the sequence of square, reduce and multiply 
// deteced in a file to form a .
// The order of addresses in the FR struct is:
// Square, Reduce, Multiply
void rsacrt_monitor(FR*, const char* elf);

#endif
