#include <ctdd/ctdd.h>
#include "fr/fr.h"

int fr_test_init() {

	FR fr2 = fr_init( (void*)0x1, (void*)0x1000000, (void*) 0x0a );

	printf("arr: size:%d [0]:%p [1]:%p\n", fr2.len, fr2.addrs[0], fr2.addrs[1]);

	return 0;
}

int run_tests() {

	ctdd_verify(fr_test_init);

	return 0;
}

int main() {

	ctdd_setup_signal_handler();

	return ctdd_test(run_tests);
}
