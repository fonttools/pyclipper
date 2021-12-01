from __future__ import print_function
import sys
import os
from setuptools import setup, find_packages
from setuptools.extension import Extension
from io import open

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
    sources = ["src/pyclipper/_pyclipper.pyx", "src/clipper.cpp"]

    from setuptools.command.sdist import sdist as _sdist

    class sdist(_sdist):
        """ Run 'cythonize' on *.pyx sources to ensure the .cpp files included
        in the source distribution are up-to-date.
        """
        def run(self):
            from Cython.Build import cythonize
            cythonize(sources, language_level="2")
            _sdist.run(self)

    cmdclass = {'sdist': sdist, 'build_ext': build_ext}

else:
    print('Distribution mode: Compiling Cython generated .cpp sources.')
    sources = ["src/pyclipper/_pyclipper.cpp", "src/clipper.cpp"]
    cmdclass = {}


needs_pytest = {'pytest', 'test'}.intersection(sys.argv)
pytest_runner = ['pytest_runner'] if needs_pytest else []


ext = Extension("pyclipper._pyclipper",
                sources=sources,
                language="c++",
                include_dirs=["src"],
                # define extra macro definitions that are used by clipper
                # Available definitions that can be used with pyclipper:
                # use_lines, use_int32
                # See src/clipper.hpp
                # define_macros=[('use_lines', 1)]
                )

with open("README.rst", "r", encoding='utf-8') as readme:
    long_description = readme.read()

setup(
    name='pyclipper',
    use_scm_version={"write_to": "src/pyclipper/_version.py"},
    description='Cython wrapper for the C++ translation of the Angus Johnson\'s Clipper library (ver. 6.4.2)',
    long_description=long_description,
    long_description_content_type="text/x-rst",
    author='Angus Johnson, Maxime Chalton, Lukas Treyer, Gregor Ratajc',
    author_email='me@gregorratajc.com',
    maintainer="Cosimo Lupo",
    maintainer_email="cosimo@anthrotype.com",
    license='MIT',
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
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    ext_modules=[ext],
    setup_requires=[
       'cython>=0.28',
       'setuptools_scm>=1.11.1',
    ] + pytest_runner,
    tests_require=['pytest'],
    cmdclass=cmdclass,
)
