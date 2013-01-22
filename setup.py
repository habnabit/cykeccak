from distutils.command.build_ext import build_ext
from distutils.core import setup
from distutils.extension import Extension
import os

# silence, pyflakes.
build_ext = build_ext

keccak_implementation = os.environ.get('CYKECCAK_IMPLEMENTATION')
if keccak_implementation is None:
    import struct
    if struct.calcsize('P') == 8:
        keccak_implementation = 'opt64'
    else:
        keccak_implementation = 'opt32'

keccak_extension = Extension(
    'keccak',
    ['src/KeccakSponge.c', 'src/KeccakF-1600-%s.c' % (keccak_implementation,)],
    include_dirs=['src'],
)

try:
    from Cython.Distutils import build_ext
except ImportError:
    print "cython not found; using previously-cython'd .c file."
    keccak_extension.sources.append('keccak.c')
else:
    keccak_extension.sources.append('keccak.pyx')

setup(
    name='cykeccak',
    cmdclass={'build_ext': build_ext},
    ext_modules=[keccak_extension],
)
