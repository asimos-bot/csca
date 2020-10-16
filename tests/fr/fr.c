#include <ctdd/ctdd.h>
#include "fr/fr.h"

int fr_test_calibrate() {

	FR fr = fr_init( 100000, (void*)0xa3e0 );

	fr_calibrate(&fr, 1, 1000000, "scripts/calibration.csv");

	//fr_monitor_elf(&fr, "/usr/bin/gnome-calculator");

	return 0;
}

int fr_test_init() {

	FR fr2 = fr_init( 10, (void*)0x1, (void*)0x1000000, (void*) 0x0a );

	ctdd_assert(fr2.len == 3);
	ctdd_assert(fr2.addrs[0] == (void*)0x1);
	ctdd_assert(fr2.addrs[1] == (void*)0x1000000);
	ctdd_assert(fr2.addrs[2] == (void*)0x0a);

	return 0;
}

int run_tests() {

	ctdd_verify(fr_test_init);
	ctdd_verify(fr_test_calibrate);

	return 0;
}

int main() {

	ctdd_setup_signal_handler();

	return ctdd_test(run_tests);
}
