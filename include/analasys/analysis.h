#ifndef CSCA_ANALYSIS_HPP
#define CSCA_ANALYSIS_HPP

#include <stdio.h>
#include <gmp.h>

typedef struct FLUSH_DATA {

	// point to 'results' field in different FR structs
	unsigned int** attack_results;

	// size of each 'attack_results' array
	unsigned int num_time_slots;

	// size of 'attack_results'
	unsigned int num_attacks;

	// number of elements in 'attack_results' with results ready
	unsigned int num_attacks_completed;
} FLUSH_DATA;

typedef struct FLUSH_RESULT {

	// result of operation to binary conversion
	char* binary;
	unsigned int num_bits;

	unsigned int hamming_distance_dp;
	unsigned int hamming_distance_dp;
	
	unsigned int levensthein_dp;
	unsigned int levensthein_dq;

	unsigned int LCS_begin_dp;
	unsigned int LCS_end_dp;

	unsigned int LCS_begin_dq;
	unsigned int LCS_end_dq;

} FLUSH_RESULT;

typedef struct FLUSH_ANALYSIS {

	FLUSH_RESULT* results;
	unsigned int num_results;

} FLUSH_ANALYSIS;

enum BIT_INTERPRETATION {

	DEFAULT,
	PLUNGER
};

// run attacks and save their data
FLUSH_DATA* fr_attack_and_save(unsigned int num_attacks,
		BIT_INTERPRETATION interpretation);

// generate statistics and bit sequence interpretation using
// data from attacks
FLUSH_ANALYSIS* flush_analysis(FLUSH_DATA* data);

#endif
