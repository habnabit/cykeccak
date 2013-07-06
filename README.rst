.. image:: https://travis-ci.org/habnabit/cykeccak.png

========
cykeccek
========

From the `Keccak website <http://keccak.noekeon.org/index.html>`_:

    Keccak is a family of sponge functions. The sponge function is a
    generalization of the concept of cryptographic hash function with infinite
    output and can perform quasi all symmetric cryptographic functions, from
    hashing to pseudo-random number generation to authenticated encryption.

``cykeccak`` is a thin Cython_ wrapper around `the reference implementation of
Keccak <http://keccak.noekeon.org/files.html>`_ and an implementation of SHA-3
on top of that wrapper.

Installation
============

Cython is not required to build ``cykeccak`` as long as the source distribution
contains a ``keccak.c`` file, such as `the tarballs available from pypi
<http://pypi.python.org/pypi/cykeccak/>`_. Installing from a github tarball is
not recommended, as they ship without ``keccak.c``, ``version.txt``, or a
``.git`` directory. With neither ``version.txt`` nor a git repository present,
``setup.py`` will be unable to determine the version of ``cykeccak``.

The underlying C code is architechture-dependent, and ``setup.py`` will attempt
to guess whether to build from the 32-bit or 64-bit sources based on whether
the python executing ``setup.py`` is a 32- or 64-bit binary. To avoid guessing,
the ``CYKECCAK_IMPLEMENTATION`` environment variable can also be set to either
``opt32`` or ``opt64``.


.. _Cython: http://cython.org/
