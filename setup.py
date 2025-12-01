from setuptools import setup, find_packages
from setuptools.extension import Extension
from Cython.Distutils import build_ext


sources = ["src/pyclipper/_pyclipper.pyx", "src/clipper.cpp"]


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
    url='https://github.com/fonttools/pyclipper',
    keywords=[
        'polygon clipping, polygon intersection, polygon union, polygon offsetting, polygon boolean, polygon, clipping, clipper, vatti'],
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
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
    cmdclass={'build_ext': build_ext},
)
