# CSCA

sources:
https://www.cits.ruhr-uni-bochum.de/imperia/md/content/may/paper/crypto2007.pdf \

__C__ache __S__ide __C__hannel __A__ttack library.

includes:

* Flush+Reload

* Flush+Flush

* Prime+Probe

* ASLR on the Line

* Jump Over ASLR

## Tests

The Flush+Reload and Flush+Flush attacks are
tested by trying to recover a secret RSA key
from GnuPG version 1.4.13.

RSA square: 0xbb9e5 offset (second cache line: 0xbba00)
RSA reduce: 0xbaf9f offset (second cache line: 0xbafc0)
RSA multiplication: 0xbb367 offset (second cache line: 0xbb380)

NOTE: use a gpg secret key with no password, this way the RSA factors
are not encrypted and you can check them with `pgpdump`

### Next Steps

* Comparison between: analysis ignoring repetitive adjacent iterations, analysis computing every non-empty

### Optimization

We can try tweaking:

* probe order

* sequence analysis policy

* first or second cache line ('S', 'M')
