import os


ROOT_DIR = os.path.dirname(os.path.realpath(__file__))

import sys
sys.path.insert(0, os.path.join(ROOT_DIR, '..'))

import json

from chess import (
    Board,
    Move,
)

from morphy.cn_utils import Puzzle
from morphy.constant import (
    MATERIAL_CAT,
)
from morphy.line import Line as _Line


def too_long_line(p):

    if p['category'] != MATERIAL_CAT:
        return False

    for l in p['lines']:
        line = _Line(Board(p['fen']))
        pm = []

        for m in l['moves']:
            line._make_move(Move.from_uci(m))
            pm.append((line.get_player_material(), line.get_comp_material()))

        if pm[-1] == pm[-2]:
            return True

    return False


def main():
    puzzles_path = sys.argv[1]
    puzzles = []

    with open(puzzles_path, 'r') as puzzles_file:
       for l in puzzles_file:
           l = l.strip()
           if l:
               puzzles.append(json.loads(l))

    for p in puzzles:
        fen = Puzzle.normalize_fen(p['fen'])

        if not p['is_solved']:
            continue
        puzzle = Puzzle.create_puzzle(p)

        if too_long_line(puzzle):
            print(json.dumps(p))

if __name__ == '__main__':
    main()