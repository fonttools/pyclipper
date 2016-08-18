#!/usr/bin/python
"""
Tests for Pyclipper wrapper library.
"""

from __future__ import print_function
from unittest2 import TestCase, main
import sys

if sys.version_info < (3,):
    integer_types = (int, long)
else:
    integer_types = (int,)

import pyclipper

# Example polygons from http://www.angusj.com/delphi/clipper.php
PATH_SUBJ_1 = [[180, 200], [260, 200], [260, 150], [180, 150]]  # square, orientation is False
PATH_SUBJ_2 = [[215, 160], [230, 190], [200, 190]]  # triangle
PATH_CLIP_1 = [[190, 210], [240, 210], [240, 130], [190, 130]]  # square
PATH_SIGMA = [[300, 400], [100, 400], [200, 300], [100, 200], [300, 200]]  # greek letter sigma
PATTERN = [[4, -6], [6, -6], [-4, 6], [-6, 6]]
INVALID_PATH = [[1, 1], ]  # less than 2 vertices


class TestPyclipperModule(TestCase):
    def test_has_classes(self):
        self.assertTrue(hasattr(pyclipper, 'Pyclipper'))
        self.assertTrue(hasattr(pyclipper, 'PyclipperOffset'))

    def test_has_namespace_methods(self):
        for method in ('Orientation', 'Area', 'PointInPolygon', 'SimplifyPolygon', 'SimplifyPolygons',
                       'CleanPolygon', 'CleanPolygons', 'MinkowskiSum', 'MinkowskiSum2', 'MinkowskiDiff',
                       'PolyTreeToPaths', 'ClosedPathsFromPolyTree', 'OpenPathsFromPolyTree',
                       'ReversePath', 'ReversePaths'):
            self.assertTrue(hasattr(pyclipper, method))


class TestNamespaceMethods(TestCase):
    def setUp(self):
        pyclipper.SCALING_FACTOR = 1

    def test_orientation(self):
        self.assertFalse(pyclipper.Orientation(PATH_SUBJ_1))
        self.assertTrue(pyclipper.Orientation(PATH_SUBJ_1[::-1]))

    def test_area(self):
        # area less than 0 because orientation is False
        area_neg = pyclipper.Area(PATH_SUBJ_1)
        area_pos = pyclipper.Area(PATH_SUBJ_1[::-1])
        self.assertLess(area_neg, 0)
        self.assertGreater(area_pos, 0)
        self.assertEqual(abs(area_neg), area_pos)

    def test_point_in_polygon(self):
        # on polygon
        self.assertEqual(pyclipper.PointInPolygon((180, 200), PATH_SUBJ_1), -1)

        # in polygon
        self.assertEqual(pyclipper.PointInPolygon((200, 180), PATH_SUBJ_1), 1)

        # outside of polygon
        self.assertEqual(pyclipper.PointInPolygon((500, 500), PATH_SUBJ_1), 0)

    def test_minkowski_sum(self):
        solution = pyclipper.MinkowskiSum(PATTERN, PATH_SIGMA, False)
        self.assertGreater(len(solution), 0)

    def test_minkowski_sum2(self):
        solution = pyclipper.MinkowskiSum2(PATTERN, [PATH_SIGMA], False)
        self.assertGreater(len(solution), 0)

    def test_minkowski_diff(self):
        solution = pyclipper.MinkowskiDiff(PATH_SUBJ_1, PATH_SUBJ_2)
        self.assertGreater(len(solution), 0)

    def test_reverse_path(self):
        solution = pyclipper.ReversePath(PATH_SUBJ_1)
        manualy_reversed = PATH_SUBJ_1[::-1]
        self.check_reversed_path(solution, manualy_reversed)

    def test_reverse_paths(self):
        solution = pyclipper.ReversePaths([PATH_SUBJ_1])
        manualy_reversed = [PATH_SUBJ_1[::-1]]
        self.check_reversed_path(solution[0], manualy_reversed[0])

    def check_reversed_path(self, path_1, path_2):
        if len(path_1) is not len(path_2):
            return False

        for i in range(len(path_1)):
            self.assertEqual(path_1[i][0], path_2[i][0])
            self.assertEqual(path_1[i][1], path_2[i][1])

    def test_simplify_polygon(self):
        solution = pyclipper.SimplifyPolygon(PATH_SUBJ_1)
        self.assertEqual(len(solution), 1)

    def test_simplify_polygons(self):
        solution = pyclipper.SimplifyPolygons([PATH_SUBJ_1])
        solution_single = pyclipper.SimplifyPolygon(PATH_SUBJ_1)
        self.assertEqual(len(solution), 1)
        self.assertEqual(len(solution), len(solution_single))
        _do_solutions_match(solution, solution_single)

    def test_clean_polygon(self):
        solution = pyclipper.CleanPolygon(PATH_CLIP_1)
        self.assertEqual(len(solution), len(PATH_CLIP_1))

    def test_clean_polygons(self):
        solution = pyclipper.CleanPolygons([PATH_CLIP_1])
        self.assertEqual(len(solution), 1)
        self.assertEqual(len(solution[0]), len(PATH_CLIP_1))


class TestFilterPyPolyNode(TestCase):
    def setUp(self):
        tree = pyclipper.PyPolyNode()
        tree.Contour.append(PATH_CLIP_1)
        tree.IsOpen = True

        child = pyclipper.PyPolyNode()
        child.IsOpen = False
        child.Parent = tree
        child.Contour = PATH_SUBJ_1
        tree.Childs.append(child)

        child = pyclipper.PyPolyNode()
        child.IsOpen = True
        child.Parent = tree
        child.Contour = PATH_SUBJ_2
        tree.Childs.append(child)

        child2 = pyclipper.PyPolyNode()
        child2.IsOpen = False
        child2.Parent = child
        child2.Contour = PATTERN
        child.Childs.append(child2)

        # empty contour should not
        # be included in filtered results
        child2 = pyclipper.PyPolyNode()
        child2.IsOpen = False
        child2.Parent = child
        child2.Contour = []
        child.Childs.append(child2)

        self.tree = tree

    def test_polytree_to_paths(self):
        paths = pyclipper.PolyTreeToPaths(self.tree)
        self.check_paths(paths, 4)

    def test_closed_paths_from_polytree(self):
        paths = pyclipper.ClosedPathsFromPolyTree(self.tree)
        self.check_paths(paths, 2)

    def test_open_paths_from_polytree(self):
        paths = pyclipper.OpenPathsFromPolyTree(self.tree)
        self.check_paths(paths, 2)

    def check_paths(self, paths, expected_nr):
        self.assertEqual(len(paths), expected_nr)
        self.assertTrue(all((len(path) > 0 for path in paths)))


class TestPyclipperAddPaths(TestCase):
    def setUp(self):
        pyclipper.SCALING_FACTOR = 1
        self.pc = pyclipper.Pyclipper()

    def test_add_path(self):
        # should not raise an exception
        self.pc.AddPath(PATH_CLIP_1, poly_type=pyclipper.PT_CLIP)

    def test_add_paths(self):
        # should not raise an exception
        self.pc.AddPaths([PATH_SUBJ_1, PATH_SUBJ_2], poly_type=pyclipper.PT_SUBJECT)

    def test_add_path_invalid_path(self):
        self.assertRaises(pyclipper.ClipperException, self.pc.AddPath, INVALID_PATH, pyclipper.PT_CLIP, True)

    def test_add_paths_invalid_path(self):
        self.assertRaises(pyclipper.ClipperException, self.pc.AddPaths, [INVALID_PATH, INVALID_PATH],
                          pyclipper.PT_CLIP, True)
        try:
            self.pc.AddPaths([INVALID_PATH, PATH_CLIP_1], pyclipper.PT_CLIP)
            self.pc.AddPaths([PATH_CLIP_1, INVALID_PATH], pyclipper.PT_CLIP)
        except pyclipper.ClipperException:
            self.fail("add_paths raised ClipperException when not all paths were invalid")


class TestClassProperties(TestCase):
    def check_property_assignment(self, pc, prop_name, values):
        for val in values:
            setattr(pc, prop_name, val)
            self.assertEqual(getattr(pc, prop_name), val)

    def test_pyclipper_properties(self):
        pc = pyclipper.Pyclipper()
        for prop_name in ('ReverseSolution', 'PreserveCollinear', 'StrictlySimple'):
            self.check_property_assignment(pc, prop_name, [True, False])

    def test_pyclipperoffset_properties(self):
        for factor in range(6):
            pyclipper.SCALING_FACTOR = 10 ** factor
            pc = pyclipper.PyclipperOffset()
            for prop_name in ('MiterLimit', 'ArcTolerance'):
                self.check_property_assignment(pc, prop_name, [2.912, 132.12, 12, -123])


class TestPyclipperExecute(TestCase):
    def setUp(self):
        pyclipper.SCALING_FACTOR = 1
        self.pc = pyclipper.Pyclipper()
        self.add_default_paths(self.pc)
        self.default_args = [pyclipper.CT_INTERSECTION, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD]

    @staticmethod
    def add_default_paths(pc):
        pc.AddPath(PATH_CLIP_1, pyclipper.PT_CLIP)
        pc.AddPaths([PATH_SUBJ_1, PATH_SUBJ_2], pyclipper.PT_SUBJECT)

    @staticmethod
    def add_paths(pc, clip_path, subj_paths, addend=None, multiplier=None):
        pc.AddPath(_modify_vertices(clip_path, addend=addend, multiplier=multiplier), pyclipper.PT_CLIP)
        for subj_path in subj_paths:
            pc.AddPath(_modify_vertices(subj_path, addend=addend, multiplier=multiplier), pyclipper.PT_SUBJECT)

    def test_get_bounds(self):
        bounds = self.pc.GetBounds()
        self.assertIsInstance(bounds, pyclipper.PyIntRect)
        self.assertEqual(bounds.left, 180)
        self.assertEqual(bounds.right, 260)
        self.assertEqual(bounds.top, 130)
        self.assertEqual(bounds.bottom, 210)

    def test_execute(self):
        solution = self.pc.Execute(*self.default_args)
        self.assertEqual(len(solution), 2)

    def test_execute2(self):
        solution = self.pc.Execute2(*self.default_args)
        self.assertIsInstance(solution, pyclipper.PyPolyNode)
        self.check_pypolynode(solution)

    def test_clear(self):
        self.pc.Clear()
        solution = self.pc.Execute(*self.default_args)
        self.assertEqual(len(solution), 0)

    def test_exact_results(self):
        """
        Test whether coordinates passed into the library are returned exactly, if they are not affected by the
        operation.
        """

        pc = pyclipper.Pyclipper()

        # Some large triangle.
        path = [[[0, 1], [0, 0], [15 ** 15, 0]]]

        pc.AddPaths(path, pyclipper.PT_SUBJECT, True)
        result = pc.Execute(pyclipper.PT_CLIP, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)

        assert result == path

    def check_pypolynode(self, node):
        self.assertTrue(len(node.Contour) is 0 or len(node.Contour) > 2)

        # check vertex coordinate, should not be an iterable (in that case
        # that means that node.Contour is a list of paths, should be path
        if node.Contour:
            self.assertFalse(hasattr(node.Contour[0][0], '__iter__'))

        for child in node.Childs:
            self.check_pypolynode(child)


class TestPyclipperOffset(TestCase):
    def setUp(self):
        pyclipper.SCALING_FACTOR = 1

    @staticmethod
    def add_path(pc, path):
        pc.AddPath(path, pyclipper.JT_ROUND, pyclipper.ET_CLOSEDPOLYGON)

    def test_execute(self):
        pc = pyclipper.PyclipperOffset()
        self.add_path(pc, PATH_CLIP_1)
        solution = pc.Execute(2.0)
        self.assertIsInstance(solution, list)
        self.assertEqual(len(solution), 1)

    def test_execute2(self):
        pc = pyclipper.PyclipperOffset()
        self.add_path(pc, PATH_CLIP_1)
        solution = pc.Execute2(2.0)
        self.assertIsInstance(solution, pyclipper.PyPolyNode)
        self.assertEqual(len(pyclipper.OpenPathsFromPolyTree(solution)), 0)
        self.assertEqual(len(pyclipper.ClosedPathsFromPolyTree(solution)), 1)

    def test_clear(self):
        pc = pyclipper.PyclipperOffset()
        self.add_path(pc, PATH_CLIP_1)
        pc.Clear()
        solution = pc.Execute(2.0)
        self.assertIsInstance(solution, list)
        self.assertEqual(len(solution), 0)


class TestScalingFactorWarning(TestCase):
    def setUp(self):
        pyclipper.SCALING_FACTOR = 2.
        self.pc = pyclipper.Pyclipper()

    def test_orientation(self):
        with self.assertWarns(DeprecationWarning):
            pyclipper.Orientation(PATH_SUBJ_1)

    def test_area(self):
        with self.assertWarns(DeprecationWarning):
            pyclipper.Area(PATH_SUBJ_1)

    def test_point_in_polygon(self):
        with self.assertWarns(DeprecationWarning):
            self.assertEqual(pyclipper.PointInPolygon((180, 200), PATH_SUBJ_1), -1)

    def test_minkowski_sum(self):
        with self.assertWarns(DeprecationWarning):
            pyclipper.MinkowskiSum(PATTERN, PATH_SIGMA, False)

    def test_minkowski_sum2(self):
        with self.assertWarns(DeprecationWarning):
            pyclipper.MinkowskiSum2(PATTERN, [PATH_SIGMA], False)

    def test_minkowski_diff(self):
        with self.assertWarns(DeprecationWarning):
            pyclipper.MinkowskiDiff(PATH_SUBJ_1, PATH_SUBJ_2)

    def test_add_path(self):
        with self.assertWarns(DeprecationWarning):
            self.pc.AddPath(PATH_CLIP_1, poly_type=pyclipper.PT_CLIP)

    def test_add_paths(self):
        with self.assertWarns(DeprecationWarning):
            self.pc.AddPaths([PATH_SUBJ_1, PATH_SUBJ_2], poly_type=pyclipper.PT_SUBJECT)


class TestScalingFunctions(TestCase):
    scale = 2 ** 31
    path = [(0, 0), (1, 1)]
    paths = [path] * 3

    def test_value_scale_to(self):
        value = 0.5
        res = pyclipper.scale_to_clipper(value, self.scale)

        assert isinstance(res, integer_types)
        assert res == int(value * self.scale)

    def test_value_scale_from(self):
        value = 1000000000000
        res = pyclipper.scale_from_clipper(value, self.scale)

        assert isinstance(res, float)
        # Convert to float to get "normal" division in Python < 3.
        assert res == float(value) / self.scale

    def test_path_scale_to(self):
        res = pyclipper.scale_to_clipper(self.path)

        assert len(res) == len(self.path)
        assert all(isinstance(i, list) for i in res)
        assert all(isinstance(j, integer_types) for i in res for j in i)

    def test_path_scale_from(self):
        res = pyclipper.scale_from_clipper(self.path)

        assert len(res) == len(self.path)
        assert all(isinstance(i, list) for i in res)
        assert all(isinstance(j, float) for i in res for j in i)

    def test_paths_scale_to(self):
        res = pyclipper.scale_to_clipper(self.paths)

        assert len(res) == len(self.paths)
        assert all(isinstance(i, list) for i in res)
        assert all(isinstance(j, list) for i in res for j in i)
        assert all(isinstance(k, integer_types) for i in res for j in i for k in j)

    def test_paths_scale_from(self):
        res = pyclipper.scale_from_clipper(self.paths)

        assert len(res) == len(self.paths)
        assert all(isinstance(i, list) for i in res)
        assert all(isinstance(j, list) for i in res for j in i)
        assert all(isinstance(k, float) for i in res for j in i for k in j)


class TestNonStandardNumbers(TestCase):

    def test_sympyzero(self):
        try:
            from sympy import Point2D
            from sympy.core.numbers import Zero
        except ImportError:
            self.skipTest("Skipping, sympy not available")

        path = [(0,0), (0,1)]
        path = [Point2D(v) for v in [(0,0), (0,1)]]
        assert type(path[0].x) == Zero
        path = pyclipper.scale_to_clipper(path)
        assert path == [[0, 0], [0, 2147483648]]


def _do_solutions_match(paths_1, paths_2, factor=None):
    if len(paths_1) != len(paths_2):
        return False

    paths_1 = [_modify_vertices(p, multiplier=factor, converter=round if factor else None) for p in paths_1]
    paths_2 = [_modify_vertices(p, multiplier=factor, converter=round if factor else None) for p in paths_2]

    return all(((p_1 in paths_2) for p_1 in paths_1))


def _modify_vertices(path, addend=0.0, multiplier=1.0, converter=None):
    path = path[:]

    def convert_coordinate(c):
        if multiplier is not None:
            c *= multiplier
        if addend is not None:
            c += addend
        if converter:
            c = converter(c)
        return c

    return [[convert_coordinate(c) for c in v] for v in path]


def run_tests():
    main()


if __name__ == '__main__':
    run_tests()
