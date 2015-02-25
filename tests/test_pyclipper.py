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
        for method in ('orientation', 'area', 'point_in_polygon', 'minkowski_sum', 'minkowski_diff',
                       'polytree_to_paths', 'closed_paths_from_polytree', 'open_paths_from_polytree'):
            self.assertTrue(hasattr(pyclipper, method))


class TestNamespaceMethods(unittest.TestCase):
    def test_orientation(self):
        self.assertFalse(pyclipper.orientation(PATH_SUBJ_1))
        self.assertTrue(pyclipper.orientation(PATH_SUBJ_1[::-1]))

    def test_area(self):
        # area less than 0 because orientation is False
        self.assertLess(pyclipper.area(PATH_SUBJ_1), 0)

    def test_point_in_polygon(self):
        # on polygon
        self.assertEqual(pyclipper.point_in_polygon((180, 200), PATH_SUBJ_1), -1)

        # in polygon
        self.assertEqual(pyclipper.point_in_polygon((200, 180), PATH_SUBJ_1), 1)

        # outside of polygon
        self.assertEqual(pyclipper.point_in_polygon((500, 500), PATH_SUBJ_1), 0)

    def test_minkowski_sum(self):
        solution = pyclipper.minkowski_sum(PATTERN, PATH_SIGMA, False)
        self.assertGreater(len(solution), 0)

    def test_minkowski_sum2(self):
        solution = pyclipper.minkowski_sum2(PATTERN, [PATH_SIGMA], False)
        self.assertGreater(len(solution), 0)

    def test_minkowski_diff(self):
        solution = pyclipper.minkowski_diff(PATH_SUBJ_1, PATH_SUBJ_2)
        self.assertGreater(len(solution), 0)

    def test_polytree_to_paths(self):
        pass

    def test_closed_paths_from_polytree(self):
        pass

    def test_open_paths_from_polytree(self):
        pass

    def test_reverse_path(self):
        solution = pyclipper.reverse_path(PATH_SUBJ_1)
        reversed_path = PATH_SUBJ_1[::-1]
        for i in range(len(PATH_SUBJ_1)):
            self.assertEqual(solution[i][0], reversed_path[i][0])
            self.assertEqual(solution[i][1], reversed_path[i][1])

    def test_reverse_paths(self):
        solution = pyclipper.reverse_paths([PATH_SUBJ_1])
        manualy_reversed = [PATH_SUBJ_1[::-1]]
        self.assertTrue(_do_paths_match(solution, manualy_reversed))


class TestPyclipperAddPaths(unittest.TestCase):
    def setUp(self):
        self.pc = pyclipper.Pyclipper()

    def test_add_path(self):
        self.pc.add_path(PATH_CLIP_1, poly_type=pyclipper.PT_CLIP)

    def test_add_paths(self):
        self.pc.add_paths([PATH_SUBJ_1, PATH_SUBJ_2], poly_type=pyclipper.PT_SUBJECT)

    def test_add_path_invalid_path(self):
        self.assertRaises(pyclipper.ClipperException, self.pc.add_path, INVALID_PATH, pyclipper.PT_CLIP, True)

    def test_add_paths_invalid_path(self):
        self.assertRaises(pyclipper.ClipperException, self.pc.add_paths, [INVALID_PATH, INVALID_PATH],
                          pyclipper.PT_CLIP, True)
        try:
            self.pc.add_paths([INVALID_PATH, PATH_CLIP_1], pyclipper.PT_CLIP)
        except pyclipper.ClipperException:
            self.fail("add_paths raised ClipperException when not all paths were invalid")


class TestPyclipperExecute(unittest.TestCase):
    def setUp(self):
        self.pc = pyclipper.Pyclipper()
        _add_test_paths_to_pyclipper(self.pc)

    def test_properties(self):
        for prop in ('reverse_solution', 'preserve_collinear', 'strictly_simple'):
            setattr(self.pc, prop, True)
            self.assertTrue(getattr(self.pc, prop))
            setattr(self.pc, prop, False)
            self.assertFalse(getattr(self.pc, prop))

    def test_get_bounds(self):
        bounds = self.pc.get_bounds()
        self.assertIsInstance(bounds, pyclipper.PyIntRect)

    def test_clear(self):
        self.pc.clear()
        solution = self.pc.execute()
        self.assertIsInstance(solution, list)
        self.assertEqual(len(solution), 0)

    def test_execute(self):
        solution1 = self.pc.execute(pyclipper.CT_INTERSECTION, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)
        self.assertIsInstance(solution1, list)
        self.assertGreater(len(solution1), 0)

    def test_scaling(self):
        solution1 = self.pc.execute(pyclipper.CT_INTERSECTION, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)

        pyclipper.SCALING_FACTOR = 1000
        pc2 = pyclipper.Pyclipper()
        _add_test_paths_to_pyclipper(pc2)
        solution2 = pc2.execute(pyclipper.CT_INTERSECTION, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)

        self.assertTrue(_do_paths_match(solution1, solution2))

    def test_execute2(self):
        solution = self.pc.execute2(pyclipper.CT_INTERSECTION, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)
        self.assertIsInstance(solution, pyclipper.PyPolyNode)


class TestPyclipperOffsetAddPaths(unittest.TestCase):
    def setUp(self):
        self.pc = pyclipper.PyclipperOffset()
        _add_test_paths_to_pyclipperoffset(self.pc)

    def test_properties(self):
        for prop in ('miter_limit', 'arc_tolerance'):
            val = 2.0
            setattr(self.pc, prop, val)
            self.assertEqual(getattr(self.pc, prop), val)
            val = 1.0
            setattr(self.pc, prop, val)
            self.assertEqual(getattr(self.pc, prop), val)

    def test_execute(self):
        solution = self.pc.execute(2.0)
        self.assertIsInstance(solution, list)

    def test_execute2(self):
        solution = self.pc.execute2(2.0)
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
    pc.add_path(PATH_CLIP_1, pyclipper.PT_CLIP)
    pc.add_paths([PATH_SUBJ_1, PATH_SUBJ_2], pyclipper.PT_SUBJECT)


def _add_test_paths_to_pyclipperoffset(pc):
    pc.add_path(PATH_CLIP_1, pyclipper.JT_ROUND, pyclipper.ET_CLOSEDPOLYGON)


def run_tests():
    unittest.main()


if __name__ == '__main__':
    run_tests()