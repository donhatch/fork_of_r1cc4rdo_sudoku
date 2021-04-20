# A self-contained sudoku solver. Find me here: https://github.com/r1cc4rdo/sudoku

from itertools import *
import re
import sys

sudoku = """

 8 . . | . . . | . . . 
 . . 3 | 6 . . | . . . 
 . 7 . | . 9 . | 2 . . 
-------+-------+-------
 . 5 . | . . 7 | . . . 
 . . . | . 4 5 | 7 . . 
 . . . | 1 . . | . 3 . 
-------+-------+-------
 . . 1 | . . . | . 6 8 
 . . 8 | 5 . . | . 1 . 
 . 9 . | . . . | 4 . . 

"""
groups = ([set(range(row * 9, row * 9 + 9)) for row in range(9)] +
          [set(range(col, 81, 9)) for col in range(9)] +
          [set(((block/3*3 + i/3)*3 + block%3)*3 + i%3 for i in range(9)) for block in range(9)])
rows_and_columns = groups[0:18]


def dumpboard(board):
    maxwidth = max(map(len, board))
    print "maxwidth = %r"%maxwidth
    line, div = '|'.join([' %-9s %-9s %-9s ']*3)+'\n', '+'.join(['-'*(maxwidth*3+4)]*3)+"\n"
    line = re.sub(r'9', str(maxwidth), line)
    print (line * 3 + div + line * 3 + div + line * 3) % tuple(board)

def eliminate_candidates(board, groups=groups):
    for subset_size, group in product(range(1, 9), groups):
        for subset in combinations(group, subset_size):
            candidates_in_subset = set(''.join(board[index] for index in subset))
            if len(candidates_in_subset) == len(subset):  # we found a constraint
                original_board = board
                subset_set = set(subset)
                all_supersets = [g for g in groups if subset_set <= g]
                for index in set(index for g in all_supersets for index in g if index not in subset_set):
                    board[index] = ''.join(c for c in board[index] if c not in candidates_in_subset)
                    assert board[index]  # if triggered, inconsistent assignment detected


def transpose_digits_with_cols(board):
    # for each row and digit, answer[row * 9 + digit] will be a string
    # representing the col positions of digit in the row
    return [''.join('123456789'[col] for col in range(9) if digit in board[row * 9 + col])
            for row in range(9) for digit in '123456789']


def eliminate_rowcolumn_fish(board):
    board[:] = transpose_digits_with_cols(board)
    eliminate_candidates(board, rows_and_columns)
    board[:] = transpose_digits_with_cols(board)


num_solves = 0
def solve(board):
    print "in solve:";
    dumpboard(board)

    global num_solves; num_solves += 1
    candidates, prev = 1 + 9**3, 2 + 9**3
    while 81 < candidates < prev:  # keep eliminating
        eliminate_candidates(board)
        #eliminate_rowcolumn_fish(board)
        prev, candidates = candidates, sum(map(len, board))
    if candidates == 81:  # we're done!
        return board
    print "got stuck at:"
    dumpboard(board)

    lengths = map(len, board)  # otherwise, we need to search
    pivot = lengths.index(sorted(set(lengths))[1])
    for board[pivot] in board[pivot]:
        try:
            return solve(board[:])
        except AssertionError as e:
            pass  # try next element
    raise AssertionError('No solutions found')  # keep searching in caller


if __name__ == '__main__':
    if len(sys.argv) > 1:
        sudoku = ' '.join(sys.argv[1:])
    board = list(islice((c if c in '123456789' else '123456789' for c in sudoku if c in '0123456789.'), 81))
    line, div = ' {} {} {} | {} {} {} | {} {} {} \n', '-------+-------+-------\n'
    print (line * 3 + div + line * 3 + div + line * 3).format(*solve(board))
    print "num_solves = %r" % (num_solves,)
