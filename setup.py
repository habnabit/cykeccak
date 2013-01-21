from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

setup(
    cmdclass = {'build_ext': build_ext},
    ext_modules = [Extension('keccak', ['keccak.pyx', 'src/KeccakSponge.c', 'src/KeccakF-1600-opt64.c'], include_dirs=['src'])]
)
