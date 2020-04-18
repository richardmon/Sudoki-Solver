from typing import List, Tuple
import copy
import math

HEIGHT = 9
WIDTH = 9
EMPTY_FIELD = -1


class SudokuSolver:
    def __init__(self, sudoku: List[List[int]]):
        height = len(sudoku)
        if height != HEIGHT:
            raise ValueError('Wrong dimentions')
        for row in sudoku:
            if len(row) != WIDTH:
                raise ValueError('Wrong dimentions')

        self.sudoku_original: List[List[int]] = sudoku

    def _get_next_empty_field(
            self,
            sudoku: List[List[int]]) -> Tuple[int, int]:
        """
        Return a tuple with the position of the next empty field
        """
        for i in range(HEIGHT):
            for j in range(WIDTH):
                if sudoku[i][j] == EMPTY_FIELD:
                    return (i, j)
        return (-1, -1)

    def _is_completed(self, sudoku: List[List[int]]) -> bool:
        """
        Checks if the sudoku pass as an argument has been completed.
        """
        (i, j) = self._get_next_empty_field(sudoku)
        if i == EMPTY_FIELD and j == EMPTY_FIELD:
            return True
        return False

    def _check_row(
            self,
            sudoku: List[List[int]],
            i: int,
            j: int,
            candidate: int) -> bool:
        """
        Checks for a match of the candidate in the given row,
        if found return False, True otherwise.
        """
        row = sudoku[i]
        for k in range(HEIGHT):
            if candidate == row[k]:
                return False
        return True

    def _check_column(
            self,
            sudoku: List[List[int]],
            i: int,
            j: int,
            candidate: int) -> bool:
        """
        Checks for match of the cantendidate in the given column,
        if found return False, True otherwise.
        """
        for k in range(WIDTH):
            if candidate == sudoku[k][j]:
                return False
        return True

    def _check_quadrant(
            self,
            sudoku: List[List[int]],
            i: int,
            j: int,
            candidate: int) -> bool:
        low_i = math.floor(i/3)*3
        low_j = math.floor(j/3)*3
        top_i = low_i + 3
        top_j = low_j + 3

        for current_i in range(low_i, top_i):
            for current_j in range(low_j, top_j):
                if sudoku[current_i][current_j] == candidate:
                    return False
        return True

    def _valid_candidate(
            self,
            sudoku: List[List[int]],
            i: int,
            j: int,
            candidate: int) -> bool:
        quadrant = self._check_quadrant(sudoku, i, j, candidate)
        column = self._check_column(sudoku, i, j, candidate)
        row = self._check_row(sudoku, i, j, candidate)
        return quadrant and column and row

    def _solve(self, sudoku: List[List[int]]) -> List[List[int]]:
        """
        This method attempts to do a greedy search to solve the sudoku
        """
        sudoku_mod = copy.deepcopy(sudoku)
        i, j = self._get_next_empty_field(sudoku)
        for candidate in range(1, 10):  # Values 1 to 9
            validation = self._valid_candidate(
                    sudoku=sudoku,
                    i=i,
                    j=j,
                    candidate=candidate)
            if validation:
                sudoku_mod[i][j] = candidate
                completed = self._is_completed(sudoku_mod)
                if completed:
                    return sudoku_mod
                else:
                    new_sudoku = self._solve(sudoku_mod)
                    if self._is_completed(new_sudoku):
                        return new_sudoku
        return sudoku

    def solve(self) -> List[List[int]]:
        """
        Returns a matrix with all the fields field if was able to solve
        the sudoku, throws an exception otherwise.
        """
        return self._solve(self.sudoku_original)
