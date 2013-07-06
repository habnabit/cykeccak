# Copyright (c) Aaron Gallagher <_@habnab.it>
# See COPYING for details.

from __future__ import unicode_literals

import keccak

from binascii import unhexlify
from random import RECIP_BPF
from unittest import TestCase, main


class SHA3TestCaseMixin(object):
    "Mixin class for tests of the Keccak-derived SHA-3 types."

    hash_factory = None
    hash_empty = hash_without_period = hash_with_period = None

    def assertHashesEqual(self, hash_obj, hex_hash):
        "Assert that the hex and non-hex digests match an expected value."
        self.assertEqual(hash_obj.digest(), unhexlify(hex_hash.encode()))
        self.assertEqual(hash_obj.hexdigest(), hex_hash)

    def test_empty_hash(self):
        "Providing no input should reliably give an expected output value."
        self.assertHashesEqual(self.hash_factory(), self.hash_empty)
        self.assertHashesEqual(self.hash_factory(b''), self.hash_empty)

        h = self.hash_factory()
        h.update(b'')
        self.assertHashesEqual(h, self.hash_empty)

    def test_hash_without_period(self):
        """
        Various ways of providing the same hash value of "The quick brown fox
        jumps over the lazy dog" should reliably give an expected output value.
        """
        self.assertHashesEqual(self.hash_factory(b'The quick brown fox jumps over the lazy dog'),
                               self.hash_without_period)

        h = self.hash_factory()
        h.update(b'The quick brown fox jumps over the lazy dog')
        self.assertHashesEqual(h, self.hash_without_period)

        h = self.hash_factory()
        h.update(b'The quick brown fox jumps over the lazy dog')
        h.update(b'')
        self.assertHashesEqual(h, self.hash_without_period)

        h = self.hash_factory()
        h.update(b'The quick brown fox ')
        h.update(b'jumps over the lazy dog')
        self.assertHashesEqual(h, self.hash_without_period)

        h = self.hash_factory()
        h.update(b'The quick brown ')
        h.update(b'fox')
        h.update(b' jumps over the lazy dog')
        self.assertHashesEqual(h, self.hash_without_period)

    def test_hash_with_period(self):
        """
        Various ways of providing the same hash value of "The quick brown fox
        jumps over the lazy dog." should reliably give an expected output
        value.
        """
        self.assertHashesEqual(self.hash_factory(b'The quick brown fox jumps over the lazy dog.'),
                               self.hash_with_period)

        h = self.hash_factory()
        h.update(b'The quick brown fox jumps over the lazy dog.')
        self.assertHashesEqual(h, self.hash_with_period)

        h = self.hash_factory()
        h.update(b'The quick brown fox jumps over the lazy dog.')
        h.update(b'')
        self.assertHashesEqual(h, self.hash_with_period)

        h = self.hash_factory()
        h.update(b'The quick brown fox ')
        h.update(b'jumps over the lazy dog.')
        self.assertHashesEqual(h, self.hash_with_period)

        h = self.hash_factory()
        h.update(b'The quick brown fox ')
        h.update(b'jumps over the lazy dog')
        h.update(b'.')
        self.assertHashesEqual(h, self.hash_with_period)

        h = self.hash_factory()
        h.update(b'The quick brown ')
        h.update(b'fox')
        h.update(b' jumps over the lazy dog.')
        self.assertHashesEqual(h, self.hash_with_period)

    def test_repeatable_digest(self):
        "Calling digest multiple times should repeatably give the same output."
        h = self.hash_factory()
        self.assertHashesEqual(h, self.hash_empty)
        self.assertHashesEqual(h, self.hash_empty)

    def test_no_update_after_digest(self):
        "Calling update after digest should raise a KeccakError."
        h = self.hash_factory()
        h.digest()
        self.assertRaises(keccak.KeccakError, h.update, b'spam')

        h = self.hash_factory()
        h.update(b'spam eggs')
        h.digest()
        self.assertRaises(keccak.KeccakError, h.update, b'spam')

        h = self.hash_factory(b'spam')
        h.digest()
        self.assertRaises(keccak.KeccakError, h.update, b'eggs')


class SHA3_224TestCase(TestCase, SHA3TestCaseMixin):
    hash_factory = keccak.sha3_224
    hash_empty = 'f71837502ba8e10837bdd8d365adb85591895602fc552b48b7390abd'
    hash_without_period = '310aee6b30c47350576ac2873fa89fd190cdc488442f3ef654cf23fe'
    hash_with_period = 'c59d4eaeac728671c635ff645014e2afa935bebffdb5fbd207ffdeab'


class SHA3_256TestCase(TestCase, SHA3TestCaseMixin):
    hash_factory = keccak.sha3_256
    hash_empty = 'c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470'
    hash_without_period = '4d741b6f1eb29cb2a9b9911c82f56fa8d73b04959d3d9d222895df6c0b28aa15'
    hash_with_period = '578951e24efd62a3d63a86f7cd19aaa53c898fe287d2552133220370240b572d'


class SHA3_384TestCase(TestCase, SHA3TestCaseMixin):
    hash_factory = keccak.sha3_384
    hash_empty = '2c23146a63a29acf99e73b88f8c24eaa7dc60aa771780ccc006afbfa8fe2479b2dd2b21362337441ac12b515911957ff'
    hash_without_period = (
        '283990fa9d5fb731d786c5bbee94ea4db4910f18c62c03d173fc0a5e494422e8a0b3da7574dae7fa0baf005e504063b3')
    hash_with_period = (
        '9ad8e17325408eddb6edee6147f13856ad819bb7532668b605a24a2d958f88bd5c169e56dc4b2f89ffd325f6006d820b')


class SHA3_512TestCase(TestCase, SHA3TestCaseMixin):
    hash_factory = keccak.sha3_512
    hash_empty = (
        '0eab42de4c3ceb9235fc91acffe746b29c29a8c366b7c60e4e67c466f36a4304'
        'c00fa9caf9d87976ba469bcbe06713b435f091ef2769fb160cdab33d3670680e')
    hash_without_period = (
        'd135bb84d0439dbac432247ee573a23ea7d3c9deb2a968eb31d47c4fb45f1ef4'
        '422d6c531b5b9bd6f449ebcc449ea94d0a8f05f62130fda612da53c79659f609')
    hash_with_period = (
        'ab7192d2b11f51c7dd744e7b3441febf397ca07bf812cceae122ca4ded638788'
        '9064f8db9230f173f6d1ab6e24b6e50f065b039f799f5592360a6558eb52d760')


class FakeSponge(object):
    byte = b'\xff'

    def squeeze(self, n_bytes):
        return self.byte * n_bytes

class SpongeRandomTestCase(TestCase):
    def setUp(self):
        self.rng = keccak.SpongeRandom(FakeSponge())

    def test_getrandbits(self):
        for x in range(1, 129):
            self.assertEqual(self.rng.getrandbits(x), (2 ** x) - 1)
        self.rng.sponge.byte = b'\x00'
        for x in range(1, 129):
            self.assertEqual(self.rng.getrandbits(x), 0)

    def test_random(self):
        self.assert_(self.rng.random() < 1)
        self.assertAlmostEqual(self.rng.random(), 1)
        self.assertEqual(self.rng.random() + RECIP_BPF, 1)
        self.rng.sponge.byte = b'\x00'
        self.assertEqual(self.rng.random(), 0)

    def test_real_sponge(self):
        self.rng.sponge = sponge = keccak.Sponge(576, 1024)
        sponge.absorb(b'hello test data')
        assert self.rng.getrandbits(8) == 234
        assert self.rng.getrandbits(7) == 29
        assert self.rng.getrandbits(6) == 19
        assert self.rng.getrandbits(1) == 1


if __name__ == '__main__':
    main()
