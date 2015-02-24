from __future__ import print_function
import sys
import os
from setuptools import setup
from setuptools.extension import Extension
from setuptools.command.test import test as TestCommand

version = '0.7'

try:
    from Cython.Distutils import build_ext
    from Cython.Build import cythonize

    print("using cython")
    ext = cythonize(Extension("pyclipper/pyclipper.pyx", sources=["pyclipper/clipper.cpp"], language="c++"))

except ImportError:
    from distutils.command.build_ext import build_ext

    print("not using cython")

    ext = [Extension("pyclipper",
                     sources=["pyclipper/pyclipper.cpp", "pyclipper/clipper.cpp"],
                     language="c++",
                     # define_macros=[('use_int32', 1)]
    )]


# This command has been borrowed from
# http://pytest.org/latest/goodpractises.html
class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

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
    description='Cython wrapper for the C++ translation of the Angus Johnson\'s Clipper library',
    long_description="""

Pyclipper is a Cython wrapper exposing public functions and classes of the C++ translation
of the `Angus Johnson\'s Clipper library (ver. 6.2.1)
<http://www.angusj.com/delphi/clipper.php>`_.

Pyclipper was tested with Python 2.7 and 3.4.

Source code is available at `GitHub <https://github.com/greginvm/pyclipper>`_.

**About Clipper**

::

  Clipper - an open source freeware library for
  clipping and offsetting lines and polygons.

  The Clipper library performs line & polygon clipping - intersection, union, difference & exclusive-or,
  and line & polygon offsetting. The library is based on Vatti's clipping algorithm.

Source: `Angus Johnson\'s Clipper library
<http://www.angusj.com/delphi/clipper.php>`_.

**Authors**

- The Clipper library is written by `Angus Johnson <http://www.angusj.com/delphi/clipper.php>`_,
- This wrapper is written mainly by `Maxime Chalton <https://sites.google.com/site/maxelsbackyard/home/pyclipper>`_,
- Adaptions to make it work with version 5 written by `Lukas Treyer <http://www.lukastreyer.com>`_,
- Adaptions to make it work with version 6.2.1 and PyPI package written by `Gregor Ratajc <http://www.gregorratajc.com>`_.

**License**

- Pyclipper is available under `MIT license <http://opensource.org/licenses/MIT>`_.
- The core Clipper library is available under `Boost Software License <http://www.boost.org/LICENSE_1_0.txt>`_. Freeware for both open source and commercial applications.

    """,
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
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    ext_modules=ext,
    tests_require=['pytest'],
    cmdclass={
        'test': PyTest,
        'build_ext': build_ext},
)
