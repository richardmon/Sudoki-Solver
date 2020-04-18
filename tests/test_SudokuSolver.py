from Sudoku.SudokuSolver import SudokuSolver, EMPTY_FIELD
from unittest.mock import MagicMock
from typing import List
import unittest
import copy


class SudokuSolverTest(unittest.TestCase):

    def setUp(self):
        # Sudoku taken from https://en.wikipedia.org/wiki/Sudoku
        self.sudoku = [
                    [5, 3, -1, -1, 7, -1, -1, -1, -1],
                    [6, -1, -1, 1, 9, 5, -1, -1, -1],
                    [-1, 9, 8, -1, -1, -1, -1, 6, -1],
                    [8, -1, -1, -1, 6, -1, -1, -1, 3],
                    [4, -1, -1, 8, -1, 3, -1, -1, 2],
                    [7, -1, -1, -1, 2, -1, -1, -1, 6],
                    [-1, 6, -1, -1, -1, -1, 2, 8, -1],
                    [-1, -1, -1, 4, 1, 9, -1, -1, 5],
                    [-1, -1, -1, -1, 8, -1, -1, 7, 9]
                ]

        self.sudoku_solved = [  # First solution, there are many more
                [5, 3, 2, 6, 7, 8, 9, 4, 1],
                [6, 7, 4, 1, 9, 5, 3, 2, 8],
                [1, 9, 8, 3, 4, 2, 5, 6, 7],
                [8, 2, 9, 7, 6, 1, 4, 5, 3],
                [4, 1, 6, 8, 5, 3, 7, 9, 2],
                [7, 5, 3, 9, 2, 4, 8, 1, 6],
                [9, 6, 1, 5, 3, 7, 2, 8, 4],
                [2, 8, 7, 4, 1, 9, 6, 3, 5],
                [3, 4, 5, 2, 8, 6, 1, 7, 9]
                ]

    def sanity_test(self):
        self.assertEqual(1+1, 2)

    def test_throw_wrong_dimensions(self):
        wrong_sudoku = [
                [1, 2, 3],
                [4, 5, 6],
                [7, 8, 9],
                [10, 11, 12],
                [13, 14, 15],
                [16, 17, 18],
                [19, 20, 21],
                [22, 23, 24],
                [25, 26, 27]
                ]
        self.assertRaises(ValueError, SudokuSolver, wrong_sudoku)

    def test_get_next_empty_field(self):
        sudoku: SudokuSolver = SudokuSolver(self.sudoku)
        expected_i = 0
        expected_j = 2
        i, j = sudoku._get_next_empty_field(self.sudoku)
        self.assertEqual(
                (i, j),
                (expected_i, expected_j)
                )
        self.assertEqual(self.sudoku[i][j], EMPTY_FIELD)

    def test_get_next_empty_field_when_sudoku_is_completed(self):
        sudoku: SudokuSolver = SudokuSolver(self.sudoku)
        expected_i = -1
        expected_j = -1
        i, j = sudoku._get_next_empty_field(self.sudoku_solved)
        self.assertEqual(
                (i, j),
                (expected_i, expected_j)
                )

    def test_is_completed(self):
        sudoku: SudokuSolver = SudokuSolver(self.sudoku)
        completed_solve = sudoku._is_completed(self.sudoku_solved)
        self.assertEqual(completed_solve, True)
        completed_unsolved = sudoku._is_completed(self.sudoku)
        self.assertEqual(completed_unsolved, False)

    def test_check_row(self):
        sudoku: SudokuSolver = SudokuSolver(self.sudoku)
        i = 0
        j = 2
        row = sudoku._check_row(
                sudoku=self.sudoku,
                i=i,
                j=j,
                candidate=self.sudoku[0][0]  # 5
                )
        self.assertFalse(row)
        second_row = sudoku._check_row(
                sudoku=self.sudoku,
                i=i,
                j=j,
                candidate=9
                )
        self.assertTrue(second_row)

    def test_check_column(self):
        sudoku: SudokuSolver = SudokuSolver(self.sudoku)
        i = 1
        j = 1

        column = sudoku._check_column(
                sudoku=self.sudoku,
                i=i,
                j=j,
                candidate=9
                )
        self.assertFalse(column)

        second_col = sudoku._check_column(
                sudoku=self.sudoku,
                i=i,
                j=j,
                candidate=7
                )
        self.assertTrue(second_col)

    def test_check_quadrant(self):
        sudoku: SudokuSolver = SudokuSolver(self.sudoku)
        i = 1
        j = 1
        quadrant = sudoku._check_quadrant(
                sudoku=self.sudoku,
                i=i,
                j=j,
                candidate=8
                )
        self.assertFalse(quadrant)
        i = 4
        j = 4
        quadrant_second = sudoku._check_quadrant(
                sudoku=self.sudoku,
                i=i,
                j=j,
                candidate=9
                )
        self.assertTrue(quadrant_second)

        partialy_solved_sudoku = [
                [5, 3, 4, 6, 7, -1, -1, -1, -1],
                [6, -1, -1, 1, 9, 5, -1, -1, -1],
                [-1, 9, 8, -1, -1, -1, -1, 6, -1],
                [8, -1, -1, -1, 6, -1, -1, -1, 3],
                [4, -1, -1, 8, -1, 3, -1, -1, 2],
                [7, -1, -1, -1, 2, -1, -1, -1, 6],
                [-1, 6, -1, -1, -1, -1, 2, 8, -1],
                [-1, -1, -1, 4, 1, 9, -1, -1, 5],
                [-1, -1, -1, -1, 8, -1, -1, 7, 9]
                ]
        i, j = sudoku._get_next_empty_field(partialy_solved_sudoku)
        quadrant_test_eight = sudoku._check_quadrant(
                sudoku=partialy_solved_sudoku,
                i=i,
                j=j,
                candidate=8
                )
        self.assertTrue(quadrant_test_eight)

    def test_solve_sudoku(self):
        sudoku: SudokuSolver = SudokuSolver(self.sudoku)
        solution: List[List[int]] = sudoku.solve()
        self.assertEqual(solution, self.sudoku_solved)
