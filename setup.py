from __future__ import print_function
import sys
import os
from setuptools import setup
from setuptools.extension import Extension
from setuptools.command.test import test as TestCommand

version = '1.0.2'

"""
Note on using the setup.py:
setup.py operates in 2 modes that are based on the presence of the 'dev' file in the root of the project.
 - When 'dev' is present, Cython will be used to compile the .pyx sources. This is the development mode
   (as you get it in the git repository).
 - When 'dev' is absent, C/C++ compiler will be used to compile the .cpp sources (that were prepared in
   in the development mode). This is the distribution mode (as you get it on PyPI).

This way the package can be used without or with an incompatible version of Cython.

The idea comes from: https://github.com/MattShannon/bandmat
"""
dev_mode = os.path.exists('dev')

if dev_mode:
    from Cython.Distutils import build_ext

    print('Development mode: Compiling Cython modules from .pyx sources.')
    sources = ["pyclipper/pyclipper.pyx", "pyclipper/clipper.cpp"]

else:
    from distutils.command.build_ext import build_ext

    print('Distribution mode: Compiling Cython generated .cpp sources.')
    sources = ["pyclipper/pyclipper.cpp", "pyclipper/clipper.cpp"]


ext = Extension("pyclipper",
                sources=sources,
                language="c++",
                # define extra macro definitions that are used by clipper
                # Available definitions that can be used with pyclipper:
                # use_lines, use_int32
                # See pyclipper/clipper.hpp
                define_macros=[('use_lines', 1)]
                )


# This command has been borrowed from
# http://pytest.org/latest/goodpractises.html
class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ['tests']

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest

        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


# This command has been borrowed from
# http://www.pydanny.com/python-dot-py-tricks.html
if sys.argv[-1] == 'publish':
    os.system("python setup.py sdist upload")
    os.system("python setup.py bdist_wheel upload")
    sys.exit()

if sys.argv[-1] == 'tag':
    os.system("git tag -a %s -m 'version %s'" % (version, version))
    os.system("git push --tags")
    sys.exit()

setup(
    name='pyclipper',
    version=version,
    description='Cython wrapper for the C++ translation of the Angus Johnson\'s Clipper library (ver. 6.2.1)',
    author='Angus Johnson, Maxime Chalton, Lukas Treyer, Gregor Ratajc',
    author_email='me@gregorratajc.com',
    url='https://github.com/greginvm/pyclipper',
    keywords=[
        'polygon clipping, polygon intersection, polygon union, polygon offsetting, polygon boolean, polygon, clipping, clipper, vatti'],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Cython",
        "Programming Language :: C++",
        "Environment :: Other Environment",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "License :: OSI Approved",
        "License :: OSI Approved :: MIT License",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    ext_modules=[ext],
    tests_require=['unittest2', 'pytest'],
    cmdclass={
        'test': PyTest,
        'build_ext': build_ext},
)
