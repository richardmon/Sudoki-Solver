from typing import List, Optional
from Sudoku.SudokuSolver import SudokuSolver

Sudoku = List[List[int]]

def solve(sudoku_to_solve: Sudoku) -> Optional[Sudoku] :
    """
    Solves a sudoku given or returns None  if no solution is found 
    """
    sudoku = SudokuSolver(sudoku_to_solve)
    solution = sudoku.solve()
    if solution != sudoku_to_solve:
        return solution
    return None
