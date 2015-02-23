"""
Pyclipper is a wrapper for the C++ translation of Agnus Johnson's Clipper library (http://www.angusj.com/delphi/clipper.php)

Requires cython

This wrapper is written mainly by Maxime Chalton
Adaptions to make it work with version 5 by Lukas Treyer
Adaptions to make it work with version 6.2.1 by Gregor Ratajc

"""

SILENT = True
SCALING_FACTOR = 1

def log_action(description):
    if not SILENT:
        print description

log_action("Python binding clipper library")

import sys as _sys
import struct
import copy as _copy
import unicodedata as _unicodedata
import time as _time

from cython.operator cimport dereference as deref

cdef extern from "Python.h":
    Py_INCREF(object o)
    object Py_BuildValue(char *format, ...)
    object PyBuffer_FromMemory(void *ptr, int size)
    #int PyArg_ParseTuple(object struct,void* ptr)
    char*PyString_AsString(object string)
    int PyArg_VaParse(object args, char *format, ...)
    int PyArg_Parse(object args, char *format, ...)
    int PyObject_AsReadBuffer(object obj, void*buffer, int*buffer_len)
    object PyBuffer_FromObject(object base, int offset, int size)
    object PyBuffer_FromReadWriteObject(object base, int offset, int size)
    PyBuffer_New(object o)


cdef extern from "stdio.h":
    cdef void printf(char*, ...)

cdef extern from "stdlib.h":
    cdef void*malloc(unsigned int size)
    cdef void*free(void*p)
    char *strdup(char *str)
    int strcpy(void*str, void*src)
    int memcpy(void*str, void*src, int size)

from libcpp.vector cimport vector

cdef extern from "extra_defines.hpp":
    cdef int _USE_XYZ

cdef extern from "clipper.hpp" namespace "ClipperLib":

    # enum ClipType { ctIntersection, ctUnion, ctDifference, ctXor };
    cdef enum ClipType:
        ctIntersection = 1,
        ctUnion = 2,
        ctDifference = 3,
        ctXor = 4

    # enum PolyType { ptSubject, ptClip };
    cdef enum PolyType:
        ptSubject = 1,
        ptClip = 2

    # By far the most widely used winding rules for polygon filling are
    # EvenOdd & NonZero (GDI, GDI+, XLib, OpenGL, Cairo, AGG, Quartz, SVG, Gr32)
    # Others rules include Positive, Negative and ABS_GTR_EQ_TWO (only in OpenGL)
    # see http://glprogramming.com/red/chapter11.html
    # enum PolyFillType { pftEvenOdd, pftNonZero, pftPositive, pftNegative };
    cdef enum PolyFillType:
        pftEvenOdd = 1,
        pftNonZero = 2,
        pftPositive = 3,
        pftNegative = 4

    # The correct type definition is taken from cpp source, so
    # the use_int32 is handled correctly.
    # If you need 32 bit ints, just uncomment //#define use_int32 in clipper.hpp
    # and recompile
    ctypedef signed long long cInt
    ctypedef signed long long long64
    ctypedef unsigned long long ulong64

    ctypedef char bool

    # TODO: handle "use_xyz" that adds Z coordinate
    cdef struct IntPoint:
        cInt X
        cInt Y

    #typedef std::vector< IntPoint > Path;
    cdef cppclass Path:
        Path()
        void push_back(IntPoint &)
        IntPoint& operator[](int)
        IntPoint& at(int)
        int size()

    #typedef std::vector< Path > Paths;
    cdef cppclass Paths:
        Paths()
        void push_back(Path &)
        Path& operator[](int)
        Path& at(int)
        int size()

    cdef cppclass PolyNode:
        PolyNode()
        Path Contour
        PolyNodes Childs
        PolyNode*Parent
        PolyNode*GetNext()
        bool IsHole()
        bool IsOpen()
        int ChildCount()

    cdef cppclass PolyNodes:
        PolyNodes()
        void push_back(PolyNode &)
        PolyNode*operator[](int)
        PolyNode*at(int)
        int size()

    cdef cppclass PolyTree(PolyNode):
        PolyTree()
        PolyNode& GetFirst()
        void Clear()
        int Total()

    #enum InitOptions {ioReverseSolution = 1, ioStrictlySimple = 2, ioPreserveCollinear = 4};
    cdef enum InitOptions:
        ioReverseSolution = 1,
        ioStrictlySimple = 2,
        ioPreserveCollinear = 4

    #enum JoinType { jtSquare, jtRound, jtMiter };
    cdef enum JoinType:
        jtSquare = 1,
        jtRound = 2,
        jtMiter = 3

    #enum EndType {etClosedPolygon, etClosedLine, etOpenButt, etOpenSquare, etOpenRound};
    cdef enum EndType:
        etClosedPolygon = 1,
        etClosedLine = 2,
        etOpenButt = 3,
        etOpenSquare = 4,
        etOpenRound = 5

    cdef struct IntRect:
        cInt left
        cInt top
        cInt right
        cInt bottom

    cdef cppclass Clipper:
        Clipper(int initOptions=0)
        #~Clipper()
        void Clear()
        bool Execute(ClipType clipType, Paths & solution, PolyFillType subjFillType, PolyFillType clipFillType)
        bool Execute(ClipType clipType, PolyTree & solution, PolyFillType subjFillType, PolyFillType clipFillType)
        bool ReverseSolution()
        void ReverseSolution(bool value)
        bool StrictlySimple()
        void StrictlySimple(bool value)
        bool PreserveCollinear()
        void PreserveCollinear(bool value)
        bool AddPath(Path & path, PolyType polyType, bool closed)
        bool AddPaths(Paths & paths, PolyType polyType, bool closed)
        IntRect GetBounds()

    cdef cppclass ClipperOffset:
        ClipperOffset(double miterLimit = 2.0, double roundPrecision = 0.25)
        #~ClipperOffset()
        void AddPath(Path & path, JoinType joinType, EndType endType)
        void AddPaths(Paths & paths, JoinType joinType, EndType endType)
        void Execute(Paths & solution, double delta)
        void Execute(PolyTree & solution, double delta)
        void Clear()
        double MiterLimit
        double ArcTolerance

    bool Orientation(const Path & poly)
    double Area(const Path & poly)
    int PointInPolygon(const IntPoint & pt, const Path & path)

    void SimplifyPolygon(const Path & in_poly, Paths & out_polys, PolyFillType fillType = pftEvenOdd)
    void SimplifyPolygons(const Paths & in_polys, Paths & out_polys, PolyFillType fillType = pftEvenOdd)
    void SimplifyPolygons(Paths & polys, PolyFillType fillType = pftEvenOdd)

    void CleanPolygon(const Path& in_poly, Path& out_poly, double distance = 1.415)
    void CleanPolygon(Path& poly, double distance = 1.415)
    void CleanPolygons(const Paths& in_polys, Paths& out_polys, double distance = 1.415)
    void CleanPolygons(Paths& polys, double distance = 1.415)

    void MinkowskiSum(const Path& pattern, const Path& path, Paths& solution, bool pathIsClosed)
    void MinkowskiSum(const Path& pattern, const Paths& paths, Paths& solution, bool pathIsClosed)
    void MinkowskiDiff(const Path& poly1, const Path& poly2, Paths& solution)

    void PolyTreeToPaths(const PolyTree& polytree, Paths& paths)
    void ClosedPathsFromPolyTree(const PolyTree& polytree, Paths& paths)
    void OpenPathsFromPolyTree(PolyTree& polytree, Paths& paths)

    void ReversePath(Path& p)
    void ReversePaths(Paths& p)

#============================= Enum mapping ================

JT_SQUARE = jtSquare
JT_ROUND = jtRound
JT_MITER = jtMiter

ET_CLOSEDPOLYGON = etClosedPolygon
ET_CLOSEDLINE = etClosedLine
ET_OPENBUTT = etOpenButt
ET_OPENSQUARE = etOpenSquare
ET_OPENROUND = etOpenRound

CT_INTERSECTION = ctIntersection
CT_UNION = ctUnion
CT_DIFFERENCE = ctDifference
CT_XOR = ctXor

PT_SUBJECT = ptSubject
PT_CLIP = ptClip

PFT_EVENODD = pftEvenOdd
PFT_NONZERO = pftNonZero
PFT_POSITIVE = pftPositive
PFT_NEGATIVE = pftNegative

#=============================  PyPolyNode =================
class PyPolyNode:
    def __init__(self):
        self.contour = []
        self.childs = []
        self.parent = None
        self.is_hole = False
        self.depth = 0

#=============================  Other objects ==============
from collections import namedtuple
PyIntRect = namedtuple('PyIntRect', ['left', 'top', 'right', 'bottom'])

class ClipperException(Exception):
    pass

#============================= Namespace functions =========
def orientation(py_path):
    return <bint>Orientation(_to_clipper_path(py_path))

def area(py_path):
    return <double>Area(_to_clipper_path(py_path))

def point_in_polygon(py_point, py_path):
    return <int>PointInPolygon(_to_clipper_point(py_point), _to_clipper_path(py_path))

# TODO: In the following commented functions Cython generates invalid cpp code
# that throws the "aggregate has incomplete type and cannot be defined" when
# compiling.
def simplify_polygon(py_path, PolyFillType fill_type=pftEvenOdd):
    raise NotImplementedError()
    """cdef Paths solution
    SimplifyPolygon(_to_clipper_path(py_path), solution, fill_type)
    return _from_clipper_paths(solution)"""

def simplify_polygons(py_paths, PolyFillType fill_type=pftEvenOdd):
    raise NotImplementedError()
    """cdef Paths solution
    SimplifyPolygons(_to_clipper_paths(py_paths), solution, fill_type)
    return _from_clipper_paths(solution)"""

def clean_polygon(py_path, double distance):
    raise NotImplementedError()
    """cdef Path solution
    cdef Path path = _to_clipper_path(py_path)
    CleanPolygon(path, solution, distance)
    return _from_clipper_path(solution)"""

def clean_polygons(py_paths, double distance=1.415):
    raise NotImplementedError()
    """cdef Paths solution
    CleanPolygons(_to_clipper_paths(py_paths), solution, distance)
    return _from_clipper_paths(solution)"""


def minkowski_sum(py_path_pattern, py_path, bint path_is_closed):
    cdef Paths solution
    MinkowskiSum(_to_clipper_path(py_path_pattern),
                 _to_clipper_path(py_path),
                 solution,
                 path_is_closed
    )
    return _from_clipper_paths(solution)

def minkowski_sum2(py_path_pattern, py_paths, bint path_is_closed):
    cdef Paths solution
    MinkowskiSum(
        _to_clipper_path(py_path_pattern),
        _to_clipper_paths(py_paths),
        solution,
        path_is_closed
    )
    return _from_clipper_paths(solution)

def minkowski_diff(py_path_1, py_path_2):
    cdef Paths solution
    MinkowskiDiff(_to_clipper_path(py_path_1), _to_clipper_path(py_path_2), solution)
    return _from_clipper_paths(solution)

# TODO: Add _to_clipper_polytree for the following 3 functions
def polytree_to_paths(py_poly_node):
    raise NotImplementedError()

def closed_paths_from_polytree(py_poly_node):
    raise NotImplementedError()

def open_paths_from_polytree(py_poly_node):
    raise NotImplementedError()

# TODO: This 2 functions are probably not useful - besides reversing it has to
# convert paths twice, it might be better if developer does this
# without this package. Adds unneeded complexity.
def reverse_path(py_path):
    cdef Path path = _to_clipper_path(py_path)
    ReversePath(path)
    return _from_clipper_path(path)

def reverse_paths(py_paths):
    cdef Paths paths = _to_clipper_paths(py_paths)
    ReversePaths(paths)
    return _from_clipper_paths(paths)

cdef class Pyclipper:
    cdef Clipper *thisptr  # hold a C++ instance which we're wrapping
    def __cinit__(self):
        log_action("Creating a Clipper")
        self.thisptr = new Clipper()

    def __dealloc__(self):
        log_action("Deleting a Clipper")
        del self.thisptr

    def add_path(self, py_path, PolyType poly_type, closed=True):
        cdef Path path = _to_clipper_path(py_path)
        cdef bint result = <bint> self.thisptr.AddPath(path, poly_type, <bint> closed)
        if not result:
            raise ClipperException('The path is invalid for clipping')
        return result

    def add_paths(self, py_paths, PolyType poly_type, closed=True):
        cdef Paths paths = _to_clipper_paths(py_paths)
        cdef bint result = <bint> self.thisptr.AddPaths(paths, poly_type, <bint> closed)
        if not result:
            raise ClipperException('All paths are invalid for clipping')
        return result

    def clear(self):
        self.thisptr.Clear()

    def get_bounds(self):
        cdef IntRect rr = <IntRect> self.thisptr.GetBounds()
        return PyIntRect(left=rr.left, top=rr.top, right=rr.right, bottom=rr.bottom)

    def execute(self, ClipType clip_type=ctDifference, PolyFillType subj_fill_type=pftEvenOdd,
                PolyFillType clip_fill_type=pftEvenOdd):
        cdef Paths solution
        cdef object success = <bint> self.thisptr.Execute(clip_type, solution, subj_fill_type, clip_fill_type)
        if not success:
            raise ClipperException('Execution of clipper did not succeed!')
        return _from_clipper_paths(solution)

    def execute2(self, ClipType clip_type=ctDifference, PolyFillType subj_fill_type=pftEvenOdd,
                 PolyFillType clip_fill_type=pftEvenOdd):
        cdef PolyTree solution
        cdef object success = <bint> self.thisptr.Execute(clip_type, solution, subj_fill_type, clip_fill_type)
        if not success:
            raise ClipperException('Execution of clipper did not succeed!')
        return _from_poly_tree(solution)

    property reverse_solution:
        def __get__(self):
            return <bint> self.thisptr.ReverseSolution()

        def __set__(self, value):
            self.thisptr.ReverseSolution(<bint> value)

    property preserve_collinear:
        def __get__(self):
            return <bint> self.thisptr.PreserveCollinear()

        def __set__(self, value):
            self.thisptr.PreserveCollinear(<bint> value)

    property strictly_simple:
        def __get__(self):
            return <bint> self.thisptr.StrictlySimple()

        def __set__(self, value):
            self.thisptr.StrictlySimple(<bint> value)


cdef class PyclipperOffset:
    cdef ClipperOffset *thisptr

    def __cinit__(self):
        log_action("Creating a ClipperOffset")
        self.thisptr = new ClipperOffset()

    def __dealloc__(self):
        log_action("Deleting a ClipperOffset")
        del self.thisptr

    def add_path(self, py_path, JoinType join_type, EndType end_type):
        cdef Path path = _to_clipper_path(py_path)
        self.thisptr.AddPath(path, join_type, end_type)

    def add_paths(self, py_paths, JoinType join_type, EndType end_type):
        cdef Paths paths = _to_clipper_paths(py_paths)
        self.thisptr.AddPaths(paths, join_type, end_type)

    def execute(self, double delta):
        cdef Paths solution
        self.thisptr.Execute(solution, delta)
        return _from_clipper_paths(solution)

    def execute2(self, double delta):
        cdef PolyTree solution
        self.thisptr.Execute(solution, delta)
        return _from_poly_tree(solution)

    def clear(self):
        self.thisptr.Clear()

    property miter_limit:
        def __get__(self):
            return <double> self.thisptr.MiterLimit

        def __set__(self, value):
            self.thisptr.MiterLimit = <double> value

    property arc_tolerance:
        def __get__(self):
            return <double> self.thisptr.ArcTolerance

        def __set__(self, value):
            self.thisptr.ArcTolerance = <double> value


#=============================== Utility functions =========
cdef _from_poly_tree(PolyTree & cPolyTree):
    poly_tree = PyPolyNode()
    depths = [0]
    for i in xrange(cPolyTree.ChildCount()):
        cChild = cPolyTree.Childs[i]
        pychild = __node_walk(cChild, poly_tree)
        poly_tree.childs.append(pychild)
        depths.append(pychild.depth + 1)
    poly_tree.depth = max(depths)
    return poly_tree

cdef __node_walk(PolyNode *cPolyNode, object parent):
    pynode = PyPolyNode()

    # parent
    pynode.parent = parent

    # is hole?
    cdef object ishole = <bint> cPolyNode.IsHole()
    pynode.is_hole = ishole

    # contour
    pynode.contour.append(_from_clipper_path(cPolyNode.Contour))

    # kids
    cdef PolyNode *cNode
    depths = [0]
    for i in xrange(cPolyNode.ChildCount()):
        cNode = cPolyNode.Childs[i]
        pychild = __node_walk(cNode, pynode)
        depths.append(pychild.depth + 1)
        pynode.childs.append(pychild)

    pynode.depth = max(depths)

    return pynode

cdef Paths _to_clipper_paths(object polygons):
    cdef Paths paths = Paths()
    for poly in polygons:
        paths.push_back(_to_clipper_path(poly))
    return paths

cdef Path _to_clipper_path(object polygon):
    cdef Path path = Path()
    cdef IntPoint p
    for v in polygon:
        path.push_back(_to_clipper_point(v))
    return path

cdef IntPoint _to_clipper_point(object py_point):
    return IntPoint(__to_clipper_value(py_point[0]), __to_clipper_value(py_point[1]))

cdef object _from_clipper_paths(Paths paths):
    polys = []

    cdef Path path
    for i in xrange(paths.size()):
        path = paths[i]
        polys.append(_from_clipper_path(path))

    return polys

cdef object _from_clipper_path(Path path):
    poly = []
    cdef IntPoint point
    for i in xrange(path.size()):
        point = path[i]
        poly.append([
            __from_clipper_value(point.X),
            __from_clipper_value(point.Y)
        ])
    return poly

cdef cInt __to_clipper_value(val):
    return val * SCALING_FACTOR

cdef double __from_clipper_value(cInt val):
    return val / SCALING_FACTOR
