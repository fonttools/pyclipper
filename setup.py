from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext


ext = Extension("pyclipper.pyclipper",
                sources=["pyclipper/pyclipper.pyx", "pyclipper/clipper.cpp"],
                libraries=["stdc++"],  # "ln", "util" ,"pthread" ,"rt"
                language="c++",  # this causes Pyrex/Cython to create C++ source
                library_dirs=["/Library/Python/2.7/site-packages"],
                include_dirs=["./"]
)

setup(
    ext_modules=[ext],
    cmdclass={'build_ext': build_ext},
)


