# Copyright (c) Aaron Gallagher <_@habnab.it>
# See COPYING for details.

from __future__ import print_function, unicode_literals

import os
from setuptools.command.build_ext import build_ext
from setuptools.extension import Extension
from setuptools import setup
import vcversioner

# silence, pyflakes.
build_ext = build_ext


# select keccak implementation from the environment or trying to autodetect a
# 32- vs. 64-bit host.
keccak_implementation = os.environ.get('CYKECCAK_IMPLEMENTATION')
if keccak_implementation is None:
    import struct
    if struct.calcsize(b'P') == 8:
        keccak_implementation = 'opt64'
    else:
        keccak_implementation = 'opt32'

version = vcversioner.find_version()

# set up the extension with the version and keccak sources.
keccak_extension = Extension(
    str('keccak'),
    [str('src/KeccakSponge.c'),
     str('src/KeccakF-1600-%s.c' % (keccak_implementation,))],
    include_dirs=['src'],
    define_macros=[('CYKECCAK_VERSION', str('"%s"' % (version.version,))),
                   ('CYKECCAK_SHA', str('"%s"' % (version.sha.lstrip('g'),)))],
)


# add the cython source in its .pyx or .c form.
try:
    from Cython.Distutils import build_ext
except ImportError:
    if not os.path.exists('keccak.c'):
        print("cython isn't usable and pre-cython'd files aren't present.")
        print("are you installing from a git clone or github tarball?")
        raise
    print("cython not usable; using previously-cython'd .c file.")
    keccak_extension.sources.append('keccak.c')
else:
    keccak_extension.sources.append('keccak.pyx')


with open('README.rst', 'r') as infile:
    long_description = infile.read()

setup(
    name='cykeccak',
    version=version.version,
    description='Cython bindings to the Keccak sponge and SHA-3 functions',
    long_description=long_description,
    author='Aaron Gallagher',
    author_email='_@habnab.it',
    url='https://github.com/habnabit/cykeccak',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Operating System :: POSIX',
        'Programming Language :: Cython',
        'Programming Language :: C',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Security :: Cryptography',
    ],
    license='ISC',
    platforms=['POSIX'],

    cmdclass={'build_ext': build_ext},
    ext_modules=[keccak_extension],
)
