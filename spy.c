#include "rsacrt/rsacrt.h"

int main() {

	FR fr = fr_init( (void*)0x999b0, (void*)0x98f5b, (void*)0x99420 );

	fr_calibrate(&fr, 1, 100000, "scripts/histogram.csv");

	rsacrt_monitor(&fr, "gnupg-1.4.13/g10/gpg");

	return 0;
}
