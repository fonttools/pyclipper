# About

Pyclipper is a wrapper for the C++ translation of [Clipper library by Agnus Johnson](http://angusj.com/delphi/clipper.php "Clipper library by Agnus Johnson").

# Install

Installers are available at PyPI: link

Install with `pip` or `easy_install`:

        pip install pyclipper
        # or
        easy_install pyclipper
        
Install from source:

        git clone git@github.com:greginvm/pyclipper.git
        python setup.py install
        
Build in place:

        python setup.py build_ext --inplace
        

# Dependencies

- [Cython](http://www.cython.org/#download)

# Examples

This wrapper library tries to follows naming convention of the original library 
but in a python way - lowercase and underscores:

- `Clipper.Execute` becomes `Pyclipper.execute`,
- `SimplifyPolygons` becomes `simplify_polygons`,
- when Clipper is overloading functions with the same number of parameters but different types (eg. `Clipper.Execute`) 
that becomes `Pyclipper.execute` and `Pyclipper.execute2`.

Basic example (based on examples on http://www.angusj.com/delphi/clipper.php):

```python

import pyclipper

subj = (
    ((180, 200), (260, 200), (260, 150), (180, 150)),
    ((215, 160), (230, 190), (200, 190))
)
clip = ((190, 210), (240, 210), (240, 130), (190, 130))

pc = pyclipper.Pyclipper()
pc.add_path(clip, PT_CLIP, True)
pc.add_paths(subj, PT_SUBJ, True)

solution = pc.execute(CT_INTERSECTION, PFT_EVENODD, PFT_EVENODD) 
```        

For more examples of use see the [tests file](../pyclipper/test_pyclipper.py)

# Authors

 - This wrapper is written mainly by Maxime Chalton
https://sites.google.com/site/maxelsbackyard/home/pyclipper
 - Adaptions to make it work with version 5 of Angus Johnson's Library written by Lukas Treyer
http://www.lukastreyer.com
 - Adaptions to make it work with version 6.2.1 of Angus Johnson's Library written by Gregor Ratajc
 http://www.gregorratajc.com


# License
MIT