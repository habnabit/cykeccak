from cpython.bytes cimport (PyBytes_FromStringAndSize,
                            PyBytes_AsStringAndSize,
                            PyBytes_AS_STRING)

cdef extern from "KeccakSponge.h":
    ctypedef struct spongeState:
        bint squeezing
        unsigned int rate
        unsigned int capacity

    int InitSponge(spongeState *, unsigned int rate, unsigned int capacity)
    int Absorb(spongeState *, unsigned char *, unsigned long long)
    int Squeeze(spongeState *, unsigned char *, unsigned long long)

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
        if Absorb(&self.state, <unsigned char *>buffer, length * 8):
            raise KeccakError()

    update = absorb

    def squeeze(self, n_bytes):
        "Squeeze some output data from the sponge."
        output = PyBytes_FromStringAndSize(NULL, n_bytes)
        if Squeeze(&self.state, <unsigned char *>PyBytes_AS_STRING(output), n_bytes * 8):
            raise KeccakError()
        return output

    digest = squeeze

    def hexdigest(self, n_bytes):
        "Squeeze some output data from the sponge encoded with hexadecimal digits."
        return self.squeeze(n_bytes).encode('hex')
