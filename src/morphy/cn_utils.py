import hashlib

from chess import Board, Move, WHITE as _WHITE
from morphy.constant import (
    MATERIAL_CAT,
    MATE_CAT,
    MATE_MATERIAL_CAT,
    UNKNOWN_CAT,
)
from morphy.utils import white_material, black_material


class Line(dict):
    CATS_MAP = {
        'MATERIAL_CAT': MATERIAL_CAT,
        'MATE_CAT': MATE_CAT,
    }

    @staticmethod
    def calculate_material(fen, line):
        board = Board(fen)

        for m in line['moves']:
            move = Move.from_uci(m)
            board.push(move)

        if Puzzle.player_color(fen) == WHITE:
            return {
                'player_material': white_material(board),
                'comp_material': black_material(board),
            }
        else:
            return {
                'player_material': black_material(board),
                'comp_material': white_material(board),
            }

    @classmethod
    def create_base_line(cls, fen, line):
        base_line = cls({
            'category': cls.CATS_MAP[line['category']],
            'initial_comp_material': line['initial_comp_material'],
            'initial_player_material': line['initial_player_material'],
        })
        base_line.update(cls.calculate_material(fen, line))
        return base_line

    @classmethod
    def create_mate_line(cls, fen, line):
        mate_line = cls.create_base_line(fen, line)
        mate_line['moves'] = line['moves']
        return mate_line

    @classmethod
    def create_material_line(cls, fen, line):
        # The last two moves are after the tactics (p - c - p)
        trimmed_line = dict(line)
        trimmed_line['moves'] = line['moves'][:-2]
        material_line = cls.create_base_line(fen, trimmed_line)
        material_line['moves'] = trimmed_line['moves']
        return material_line

    @classmethod
    def create_line(cls, fen, line):
        if line['category'] == MATERIAL_CAT:
            return cls.create_material_line(fen, line)

        if line['category'] == MATE_CAT:
            return cls.create_mate_line(fen, line)


class Puzzle(dict):
    PUZZLE_ID_LENGTH = 16

    @classmethod
    def create_lines(cls, puzzle):
        lines = []

        for l in [Line.create_line(puzzle['fen'], l) for l in puzzle['lines']]:
            if l not in lines:
                lines.append(l)

        return lines

    @staticmethod
    def normalize_fen(fen):
        return ' '.join(fen.strip().split())

    @staticmethod
    def puzzle_category(lines):
        cats = set([l['category'] for l in lines])

        if MATE_CAT in cats and MATERIAL_CAT in cats and len(cats) == 2:
            return MATE_MATERIAL_CAT

        if MATE_CAT in cats and len(cats) == 1:
            return MATE_CAT

        if MATERIAL_CAT in cats and len(cats) == 1:
            return MATERIAL_CAT

        return UNKNOWN_CAT

    @classmethod
    def hash_from_fen(cls, fen):
        return hashlib.sha256(fen.encode('utf-8')).hexdigest()[:cls.PUZZLE_ID_LENGTH]

    @staticmethod
    def player_color(fen):
        return WHITE if Board(fen).turn is _WHITE else BLACK

    @classmethod
    def create_puzzle(cls, puzzle):
        fen = cls.normalize_fen(puzzle['fen'])
        lines = cls.create_lines(puzzle)
        return cls({
            'id': cls.hash_from_fen(fen),
            'fen': fen,
            'category': cls.puzzle_category(lines),
            'player_color': cls.player_color(fen),
            'lines': lines,
        })


BLACK = 'BLACK'
WHITE = 'WHITE'