from __future__ import print_function
import sys
import os
from setuptools import setup
from setuptools.extension import Extension

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

    from setuptools.command.sdist import sdist as _sdist

    class sdist(_sdist):
        """ Run 'cythonize' on *.pyx sources to ensure the .cpp files included
        in the source distribution are up-to-date.
        """
        def run(self):
            from Cython.Build import cythonize
            cythonize(sources, language='c++')
            _sdist.run(self)

    cmdclass = {'sdist': sdist, 'build_ext': build_ext}

else:
    print('Distribution mode: Compiling Cython generated .cpp sources.')
    sources = ["pyclipper/pyclipper.cpp", "pyclipper/clipper.cpp"]
    cmdclass = {}


needs_pytest = {'pytest', 'test'}.intersection(sys.argv)
pytest_runner = ['pytest_runner'] if needs_pytest else []


ext = Extension("pyclipper",
                sources=sources,
                language="c++",
                # define extra macro definitions that are used by clipper
                # Available definitions that can be used with pyclipper:
                # use_lines, use_int32
                # See pyclipper/clipper.hpp
                define_macros=[('use_lines', 1)]
                )


setup(
    name='pyclipper',
    use_scm_version=True,
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
    setup_requires=[
       'setuptools_scm>=1.11.1',
       'setuptools_scm_git_archive>=1.0',
    ] + pytest_runner,
    tests_require=['unittest2', 'pytest'],
    cmdclass=cmdclass,
)
