#!/usr/bin/python
"""
Tests for Pyclipper wrapper library.
"""

from __future__ import print_function
import unittest

import pyclipper

# Example polygons from http://www.angusj.com/delphi/clipper.php
PATH_SUBJ_1 = ((180, 200), (260, 200), (260, 150), (180, 150))  # square, orientation is False
PATH_SUBJ_2 = ((215, 160), (230, 190), (200, 190))  # triangle
PATH_CLIP_1 = ((190, 210), (240, 210), (240, 130), (190, 130))  # square
PATH_SIGMA = ((300, 400), (100, 400), (200, 300), (100, 200), (300, 200))  # greek letter sigma
PATTERN = ((4, -6), (6, -6), (-4, 6), (-6, 6))
INVALID_PATH = ((1, 1),)  # less than 2 vertices


class TestPyclipperModule(unittest.TestCase):
    def test_has_classes(self):
        self.assertTrue(hasattr(pyclipper, 'Pyclipper'))
        self.assertTrue(hasattr(pyclipper, 'PyclipperOffset'))

    def test_has_namespace_methods(self):
        for method in ('Orientation', 'Area', 'PointInPolygon', 'SimplifyPolygon', 'SimplifyPolygons',
                       'CleanPolygon', 'CleanPolygons', 'MinkowskiSum', 'MinkowskiSum2', 'MinkowskiDiff',
                       'PolyTreeToPaths', 'ClosedPathsFromPolyTree', 'OpenPathsFromPolyTree',
                       'ReversePath', 'ReversePaths'):
            self.assertTrue(hasattr(pyclipper, method))


class TestNamespaceMethods(unittest.TestCase):
    def test_orientation(self):
        self.assertFalse(pyclipper.Orientation(PATH_SUBJ_1))
        self.assertTrue(pyclipper.Orientation(PATH_SUBJ_1[::-1]))

    def test_area(self):
        # area less than 0 because orientation is False
        self.assertLess(pyclipper.Area(PATH_SUBJ_1), 0)

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
        reversed_path = PATH_SUBJ_1[::-1]
        for i in range(len(PATH_SUBJ_1)):
            self.assertEqual(solution[i][0], reversed_path[i][0])
            self.assertEqual(solution[i][1], reversed_path[i][1])

    def test_reverse_paths(self):
        solution = pyclipper.ReversePaths([PATH_SUBJ_1])
        manualy_reversed = [PATH_SUBJ_1[::-1]]
        self.assertTrue(_do_paths_match(solution, manualy_reversed))

    def test_simplify_polygon(self):
        solution = pyclipper.SimplifyPolygon(PATH_SUBJ_1)
        self.assertEqual(len(solution), 1)

    def test_simplify_polygons(self):
        solution = pyclipper.SimplifyPolygons([PATH_SUBJ_1])
        self.assertEqual(len(solution), 1)

    def test_clean_polygon(self):
        solution = pyclipper.CleanPolygon(PATH_CLIP_1)
        self.assertEqual(len(solution), len(PATH_CLIP_1))

    def test_clean_polygons(self):
        solution = pyclipper.CleanPolygons([PATH_CLIP_1])
        self.assertEqual(len(solution), 1)
        self.assertEqual(len(solution[0]), len(PATH_CLIP_1))


class TestPyPolyNode(unittest.TestCase):
    def setUp(self):
        tree = pyclipper.PyPolyNode()
        tree.Contour.append(PATH_CLIP_1)
        tree.IsOpen = True

        child = pyclipper.PyPolyNode()
        child.IsOpen = False
        child.Parent = tree
        child.Contour.append(PATH_SUBJ_1)
        tree.Childs.append(child)

        child = pyclipper.PyPolyNode()
        child.IsOpen = True
        child.Parent = tree
        child.Contour.append(PATH_SUBJ_2)
        tree.Childs.append(child)

        child2 = pyclipper.PyPolyNode()
        child2.IsOpen = False
        child2.Parent = child
        child2.Contour.append(PATTERN)
        child.Childs.append(child2)

        self.tree = tree

    def test_polytree_to_paths(self):
        paths = pyclipper.PolyTreeToPaths(self.tree)
        self.assertEqual(len(paths), 4)

    def test_closed_paths_from_polytree(self):
        paths = pyclipper.ClosedPathsFromPolyTree(self.tree)
        self.assertEqual(len(paths), 2)

    def test_open_paths_from_polytree(self):
        paths = pyclipper.OpenPathsFromPolyTree(self.tree)
        self.assertEqual(len(paths), 2)


class TestPyclipperAddPaths(unittest.TestCase):
    def setUp(self):
        self.pc = pyclipper.Pyclipper()

    def test_add_path(self):
        self.pc.AddPath(PATH_CLIP_1, poly_type=pyclipper.PT_CLIP)

    def test_add_paths(self):
        self.pc.AddPaths([PATH_SUBJ_1, PATH_SUBJ_2], poly_type=pyclipper.PT_SUBJECT)

    def test_add_path_invalid_path(self):
        self.assertRaises(pyclipper.ClipperException, self.pc.AddPath, INVALID_PATH, pyclipper.PT_CLIP, True)

    def test_add_paths_invalid_path(self):
        self.assertRaises(pyclipper.ClipperException, self.pc.AddPaths, [INVALID_PATH, INVALID_PATH],
                          pyclipper.PT_CLIP, True)
        try:
            self.pc.AddPaths([INVALID_PATH, PATH_CLIP_1], pyclipper.PT_CLIP)
        except pyclipper.ClipperException:
            self.fail("add_paths raised ClipperException when not all paths were invalid")


class TestPyclipperExecute(unittest.TestCase):
    def setUp(self):
        self.pc = pyclipper.Pyclipper()
        _add_test_paths_to_pyclipper(self.pc)

    def test_properties(self):
        for prop in ('ReverseSolution', 'PreserveCollinear', 'StrictlySimple'):
            setattr(self.pc, prop, True)
            self.assertTrue(getattr(self.pc, prop))
            setattr(self.pc, prop, False)
            self.assertFalse(getattr(self.pc, prop))

    def test_get_bounds(self):
        bounds = self.pc.GetBounds()
        self.assertIsInstance(bounds, pyclipper.PyIntRect)

    def test_clear(self):
        self.pc.Clear()
        solution = self.pc.Execute(2)
        self.assertIsInstance(solution, list)
        self.assertEqual(len(solution), 0)

    def test_execute(self):
        solution1 = self.pc.Execute(pyclipper.CT_INTERSECTION,
                                    pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)
        self.assertIsInstance(solution1, list)
        self.assertGreater(len(solution1), 0)

    def test_scaling(self):
        solution1 = self.pc.Execute(pyclipper.CT_INTERSECTION,
                                    pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)

        pyclipper.SCALING_FACTOR = 1000
        pc2 = pyclipper.Pyclipper()
        _add_test_paths_to_pyclipper(pc2)
        solution2 = pc2.Execute(pyclipper.CT_INTERSECTION,
                                pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)

        self.assertTrue(_do_paths_match(solution1, solution2))

    def test_execute2(self):
        solution = self.pc.Execute2(pyclipper.CT_INTERSECTION,
                                    pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)
        self.assertIsInstance(solution, pyclipper.PyPolyNode)


class TestPyclipperOffsetAddPaths(unittest.TestCase):
    def setUp(self):
        self.pc = pyclipper.PyclipperOffset()
        _add_test_paths_to_pyclipperoffset(self.pc)

    def test_properties(self):
        for prop in ('MiterLimit', 'ArcTolerance'):
            val = 2.0
            setattr(self.pc, prop, val)
            self.assertEqual(getattr(self.pc, prop), val)
            val = 1.0
            setattr(self.pc, prop, val)
            self.assertEqual(getattr(self.pc, prop), val)

    def test_execute(self):
        solution = self.pc.Execute(2.0)
        self.assertIsInstance(solution, list)

    def test_execute2(self):
        solution = self.pc.Execute2(2.0)
        self.assertIsInstance(solution, pyclipper.PyPolyNode)


def _do_paths_match(paths_1, paths_2):
    if len(paths_1) != len(paths_2):
        return False

    paths_2_lists = [list(_convert_elements_to_list(path)) for path in paths_2]
    for i in range(len(paths_1)):
        if list(_convert_elements_to_list(paths_1[i])) not in paths_2_lists:
            return False
    return True


def _convert_elements_to_list(collection_of_vertices):
    return [list(v) for v in collection_of_vertices]


def _add_test_paths_to_pyclipper(pc):
    pc.AddPath(PATH_CLIP_1, pyclipper.PT_CLIP)
    pc.AddPaths([PATH_SUBJ_1, PATH_SUBJ_2], pyclipper.PT_SUBJECT)


def _add_test_paths_to_pyclipperoffset(pc):
    pc.AddPath(PATH_CLIP_1, pyclipper.JT_ROUND, pyclipper.ET_CLOSEDPOLYGON)


def run_tests():
    unittest.main()


if __name__ == '__main__':
    run_tests()