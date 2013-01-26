from distutils.command.build_ext import build_ext
from distutils.core import setup
from distutils.extension import Extension
import os
import subprocess

# silence, pyflakes.
build_ext = build_ext


# select keccak implementation from the environment or trying to autodetect a
# 32- vs. 64-bit host.
keccak_implementation = os.environ.get('CYKECCAK_IMPLEMENTATION')
if keccak_implementation is None:
    import struct
    if struct.calcsize('P') == 8:
        keccak_implementation = 'opt64'
    else:
        keccak_implementation = 'opt32'


# try to pull the version from git, or fall back on a previously-saved version.
try:
    proc = subprocess.Popen(['git', 'describe', '--tags', '--long'],
                            stdout=subprocess.PIPE)
except OSError:
    print "couldn't determine version from git; using version.txt"
    with open('version.txt', 'rb') as infile:
        raw_version = infile.read()
else:
    raw_version = proc.communicate()[0].strip()
    with open('version.txt', 'wb') as outfile:
        outfile.write(raw_version)


# parse the git-described verion into something usable.
tag_version, commits, sha = raw_version.rsplit('-', 2)
if commits == '0':
    version = tag_version
else:
    version = '%s.dev%s' % (tag_version, commits)


# set up the extension with the version and keccak sources.
keccak_extension = Extension(
    'keccak',
    ['src/KeccakSponge.c', 'src/KeccakF-1600-%s.c' % (keccak_implementation,)],
    include_dirs=['src'],
    define_macros=[('CYKECCAK_VERSION', '"%s"' % (version,)),
                   ('CYKECCAK_SHA', '"%s"' % (sha.lstrip('g'),))],
)


# add the cython source in its .pyx or .c form.
try:
    from Cython.Distutils import build_ext
except ImportError:
    if not os.path.exists('keccak.c'):
        print "cython not usable and no cython'd files present."
        print "are you installing from a git clone or github tarball?"
        raise
    print "cython not usable; using previously-cython'd .c file."
    keccak_extension.sources.append('keccak.c')
else:
    keccak_extension.sources.append('keccak.pyx')


setup(
    name='cykeccak',
    version=version,
    description='Cython bindings to the Keccak sponge function',
    author='Aaron Gallagher',
    author_email='_@habnab.it',
    url='https://github.com/habnabit/cykeccak',

    cmdclass={'build_ext': build_ext},
    ext_modules=[keccak_extension],
)
