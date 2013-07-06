# Copyright (c) Aaron Gallagher <_@habnab.it>
# See COPYING for details.

import binascii
import random

from cpython.bytes cimport (PyBytes_FromStringAndSize,
                            PyBytes_AsStringAndSize,
                            PyBytes_AS_STRING)
from cpython.version cimport PY_MAJOR_VERSION

# these get defined in setup.py.
cdef extern from *:
    char *CYKECCAK_VERSION
    char *CYKECCAK_SHA

__version__ = CYKECCAK_VERSION
__author__ = "Aaron Gallagher <_@habnab.it>"
__sha__ = CYKECCAK_SHA

cdef extern from "KeccakSponge.h":
    ctypedef struct spongeState:
        bint squeezing
        unsigned int rate
        unsigned int capacity

    int InitSponge(spongeState *, unsigned int rate, unsigned int capacity) nogil
    int Absorb(spongeState *, unsigned char *, unsigned long long) nogil
    int Squeeze(spongeState *, unsigned char *, unsigned long long) nogil

class KeccakError(Exception):
    pass

cdef class Sponge:
    "A class representing the current state of the Keccak sponge function."
    cdef spongeState state

    property squeezing:
        "True if this Sponge has been squeezed at least once."
        def __get__(self):
            return self.state.squeezing

    property rate:
        "The value of the rate r."
        def __get__(self):
            return self.state.rate

    property capacity:
        "The value of the capacity c."
        def __get__(self):
            return self.state.capacity

    def __cinit__(self, unsigned int rate, unsigned int capacity):
        if rate > 1600:
            raise ValueError('rate must be <= 1600')
        if capacity > 1600:
            raise ValueError('capacity must be <= 1600')
        if rate + capacity != 1600:
            raise ValueError('rate + capacity must equal 1600')
        if rate % 64 != 0:
            raise ValueError('rate must be divisible by 64')
        if InitSponge(&self.state, rate, capacity):
            raise KeccakError()

    def absorb(self, data):
        "Absorb some input data into the sponge."
        cdef char *buffer
        cdef Py_ssize_t length
        if self.state.squeezing:
            raise KeccakError("can't absorb after starting to squeeze")
        PyBytes_AsStringAndSize(data, &buffer, &length)
        with nogil:
            res = Absorb(&self.state, <unsigned char *>buffer, length * 8)
        if res:
            raise KeccakError()

    def squeeze(self, n_bytes):
        "Squeeze some output data from the sponge."
        cdef unsigned char *buffer
        cdef unsigned long long ull_n_bytes = n_bytes
        output = PyBytes_FromStringAndSize(NULL, ull_n_bytes)
        buffer = <unsigned char *>PyBytes_AS_STRING(output)
        with nogil:
            res = Squeeze(&self.state, buffer, ull_n_bytes * 8)
        if res:
            raise KeccakError()
        return output


def _int_of_bytes(bytes s):
    "Convert a string of bytes to its integer representation."
    cdef unsigned char *buffer
    cdef char *tmp
    cdef Py_ssize_t length, pos
    PyBytes_AsStringAndSize(s, &tmp, &length)
    buffer = <unsigned char *>tmp
    ret = 0
    for pos in range(length):
        ret = (ret << 8) | buffer[0]
        buffer += 1
    return ret


class SpongeRandom(random.SystemRandom):
    "A ``random.Random`` subclass which derives its entropy from a sponge."

    def __init__(self, sponge):
        self.sponge = sponge

    def random(self):
        "Get the next sponge-derived number on the range [0.0, 1.0)."
        return self.getrandbits(random.BPF) * random.RECIP_BPF

    def getrandbits(self, n_bits):
        "Generate an integer of ``n_bits`` sponge-squeezed bits."
        if n_bits <= 0:
            raise ValueError('number of bits must be greater than zero')
        n_bytes = (n_bits + 7) // 8
        squeezed = self.sponge.squeeze(n_bytes)
        val = _int_of_bytes(squeezed)
        return val >> (n_bytes * 8 - n_bits)


class _SHA3Base:
    "A class implementing the primary functionality of the SHA-3 functions."
    n_bits = None
    sponge_factory = Sponge

    def __init__(self, string=None):
        capacity = self.n_bits * 2
        rate = 1600 - capacity
        self.sponge = self.sponge_factory(rate, capacity)
        if string is not None:
            self.update(string)
        self._digest = None

    def update(self, string):
        """Absorb some input data into the underlying sponge.

        Unlike hash implementations in the standard library ``hashlib``,
        ``update`` can't be called again after calling ``digest`` once.
        """

        self.sponge.absorb(string)

    def digest(self):
        """Squeeze a fixed amount of data from the underlying sponge.

        Unlike hash implementations in the standard library ``hashlib``,
        ``update`` can't be called again after calling ``digest`` once. As a
        result, and unlike ``Sponge.squeeze``, successive calls to ``digest``
        will always return the same value.
        """

        # this value has to be saved because squeezing a sponge multiple times
        # will give different output every time.
        ret = self._digest
        if ret is None:
            ret = self._digest = self.sponge.squeeze(self.n_bits // 8)
        return ret

    def hexdigest(self):
        "Like ``digest``, but the output is encoded with hexadecimal digits."
        if PY_MAJOR_VERSION > 2:
            return binascii.hexlify(self.digest()).decode()
        else:
            return self.digest().encode('hex')


class sha3_224(_SHA3Base):
    "224-bit SHA-3."
    n_bits = 224

class sha3_256(_SHA3Base):
    "256-bit SHA-3."
    n_bits = 256

class sha3_384(_SHA3Base):
    "384-bit SHA-3."
    n_bits = 384

class sha3_512(_SHA3Base):
    "512-bit SHA-3."
    n_bits = 512
