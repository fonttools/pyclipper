# About

Pyclipper is a Cython wrapper exposing public functions and classes of the C++ translation
of the [Angus Johnson's Clipper library (ver. 6.2.1)](http://www.angusj.com/delphi/clipper.php).

Pyclipper was tested with Python 2.7 and 3.4 on Linux. Compilation of .cpp sourcers generated with Cython (on Linux) succeeded on Windows. See TODOs.

Source code is available on [GitHub](https://github.com/greginvm/pyclipper).

## About Clipper

>> Clipper - an open source freeware library for
>> clipping and offsetting lines and polygons.
>>
>> The Clipper library performs line & polygon clipping - intersection, union, difference & exclusive-or,
>> and line & polygon offsetting. The library is based on Vatti's clipping algorithm.
>> 
>> <cite>[Angus Johnson's Clipper library](http://www.angusj.com/delphi/clipper.php)</cite>

# Install

## Dependencies

Cython dependency is optional. Cpp sources generated with Cython are available in the release branch.

**From PyPI**

        pip install pyclipper
        
**From source**

        python setup.py install
        
**Compile cython source in-place**

        python setup.py build_ext --inplace

# How to use

This wrapper library tries to follow naming convention of the original library 
but in a python way - lowercase and underscores:

- `ClipperLib` namespace is represented by `pyclipper` module,
- classes `Clipper` and `ClipperOffset` -> `Pyclipper` and `Pyclipper` and `PyclipperOffset`,
- `Clipper.Execute` becomes `Pyclipper.execute`,
- `SimplifyPolygons` becomes `simplify_polygons`,
- when Clipper is overloading functions with the same number of parameters but different types (eg. `Clipper.Execute`, one function returns polygon the other polytree) that becomes `Pyclipper.execute` and `Pyclipper.execute2`.

Basic example (based on [Angus Johnson's Clipper library](http://www.angusj.com/delphi/clipper.php)):

```python

import pyclipper

subj = (
    ((180, 200), (260, 200), (260, 150), (180, 150)),
    ((215, 160), (230, 190), (200, 190))
)
clip = ((190, 210), (240, 210), (240, 130), (190, 130))

pc = pyclipper.Pyclipper()
pc.add_path(clip, pyclipper.PT_CLIP, True)
pc.add_paths(subj, pyclipper.PT_SUBJ, True)

solution = pc.execute(pyclipper.CT_INTERSECTION, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD) 
```        

The Clipper library uses integers instead of floating point values to preserve numerical robustness.
You can use `pyclipper.SCALING_FACTOR` to scale your values to preserve the desired presision. 
The default value is 1, which disables scaling. This setting only scales polygon vertices coordinates,
properties like `miterLimit`, `roundPrecision` etc. are not scaled.

For more examples of use see tests.

# Authors

- The Clipper library is written by [Angus Johnson](http://www.angusj.com/delphi/clipper.php),
- This wrapper is written mainly by [Maxime Chalton](https://sites.google.com/site/maxelsbackyard/home/pyclipper>),
- Adaptions to make it work with version 5 written by [Lukas Treyer](http://www.lukastreyer.com),
- Adaptions to make it work with version 6.2.1 and PyPI package written by [Gregor Ratajc](http://www.gregorratajc.com).

# License

- Pyclipper is available under [MIT license](http://opensource.org/licenses/MIT).
- The core Clipper library is available under [Boost Software License](http://www.boost.org/LICENSE_1_0.txt>). Freeware for both open source and commercial applications.

# TODO

- Fix Cython compilation on Windows. Sources created with Cython on Windows could not be compiled, error: "LINK: error LNK2001: unresolved external symbol initpyx". Used MS Visual Studio 9.0 compiler and Cython 0.22 with Python 2.7.6 (x32) on Windows 8.1 x64.
- Cover all the namespace methods
