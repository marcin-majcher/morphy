import os
from io import StringIO

import pytest
import chess.pgn
from chess import (
    Board,
    Move,
    WHITE,
    BLACK,
)
from chess.engine import (
    PovScore,
    Cp,
)

from morphy.line import Line


GAMES_PATH = 'test_data/games.pgn'


@pytest.fixture
def games_pgn(request):
    filename = request.module.__file__
    test_dir = os.path.dirname(filename)

    with open(os.path.join(test_dir, GAMES_PATH), 'r') as f:
        return StringIO(f.read())


@pytest.fixture
def game(games_pgn):
    return chess.pgn.read_game(games_pgn)


@pytest.fixture
def line(game):
    board = game.board()
    moves = list(game.mainline_moves())

    for m in moves[:13]:
        board.push(m)
    
    return Line(Board(board.fen()))


@pytest.fixture
def infos():
    return [
        {
            'depth': 24, 
            'seldepth': 39, 
            'multipv': 1, 
            'score': PovScore(Cp(+1370), WHITE),
            'nodes': 26414702,
            'nps': 1656301,
            'tbhits': 0, 
            'time': 15.948,
            'pv': [
                Move.from_uci('d5e7'), Move.from_uci('f8f7'), Move.from_uci('c4e6'), Move.from_uci('d7e6'),
                Move.from_uci('g6e6'), Move.from_uci('f7e7'), Move.from_uci('e6g6'), Move.from_uci('h7f8'),
                Move.from_uci('g6h5'), Move.from_uci('f8h7'), Move.from_uci('c1b1'), Move.from_uci('c6d4'),
                Move.from_uci('f5d4'), Move.from_uci('a7a5'), Move.from_uci('d4f5'), Move.from_uci('b7b5'),
                Move.from_uci('f5e7'), Move.from_uci('d8e7'), Move.from_uci('h5f7'), Move.from_uci('e7f8'),
                Move.from_uci('f7c7'), Move.from_uci('a5a4'), Move.from_uci('c7c6'), Move.from_uci('a8a7'),
                Move.from_uci('c6b5'), Move.from_uci('a4a3'), Move.from_uci('b5h5'), Move.from_uci('a3b2'),
                Move.from_uci('b1b2'), Move.from_uci('a7e7')], 
            'hashfull': 1000,
            'currmove': Move.from_uci('f5d6'),
            'currmovenumber': 50
        },
        {
            'depth': 24, 
            'seldepth': 49,
            'multipv': 2,
            'score': PovScore(Cp(+177), WHITE),
            'nodes': 26414702,
            'nps': 1656301,
            'tbhits': 0, 'time': 15.948,
            'pv': [
                Move.from_uci('f5g7'), Move.from_uci('f8g8'), Move.from_uci('g6e6'), Move.from_uci('g8g7'),
                Move.from_uci('e6h6'), Move.from_uci('c6d4'), Move.from_uci('f4f5'), Move.from_uci('d4f3'),
                Move.from_uci('f5f6'), Move.from_uci('f3g1'), Move.from_uci('f6g7'), Move.from_uci('d7g7'),
                Move.from_uci('h6g7'), Move.from_uci('h8g7'), Move.from_uci('h1g1'), Move.from_uci('g7h8'),
                Move.from_uci('d5b6'), Move.from_uci('d8g5'), Move.from_uci('g1g5'), Move.from_uci('a7b6'),
                Move.from_uci('g5f5'), Move.from_uci('a8a4'), Move.from_uci('b2b3'), Move.from_uci('a4a2'),
                Move.from_uci('f5f7'), Move.from_uci('a2a1'), Move.from_uci('c1d2'), Move.from_uci('a1g1'),
                Move.from_uci('f7c7'), Move.from_uci('h7f6'), Move.from_uci('c7b7'), Move.from_uci('f6e4'),
                Move.from_uci('d2e3'), Move.from_uci('g1g4'), Move.from_uci('b7b6'), Move.from_uci('g4h4'),
                Move.from_uci('c4d3')],
            'hashfull': 1000
        },
        {
            'depth': 24, 
            'seldepth': 43, 
            'multipv': 3, 
            'score': PovScore(Cp(-112), WHITE), 
            'nodes': 26414702, 
            'nps': 1656301,
            'tbhits': 0,
            'time': 15.948,
            'pv': [
                Move.from_uci('g6h5'), Move.from_uci('d7f7'), Move.from_uci('h5f7'), Move.from_uci('f8f7'),
                Move.from_uci('d5c7'), Move.from_uci('d8c7'), Move.from_uci('c4e6'), Move.from_uci('f7f6'),
                Move.from_uci('e6d5'), Move.from_uci('c7b6'), Move.from_uci('g1g2'), Move.from_uci('g7g6'),
                Move.from_uci('d5c6'), Move.from_uci('g6f5'), Move.from_uci('c6b7'), Move.from_uci('a8b8'),
                Move.from_uci('b7d5'), Move.from_uci('f5e4'), Move.from_uci('d5e4'), Move.from_uci('f6f4'),
                Move.from_uci('e4d3'), Move.from_uci('b6e3'), Move.from_uci('c1b1'), Move.from_uci('e3d4'),
                Move.from_uci('b2b3'), Move.from_uci('b8g8'), Move.from_uci('g2g8'), Move.from_uci('h8g8'),
                Move.from_uci('h4h5'), Move.from_uci('h7f6'), Move.from_uci('h5h6'), Move.from_uci('d4e5'),
                Move.from_uci('d3c4'), Move.from_uci('g8h7'), Move.from_uci('c4d3'), Move.from_uci('f6e4'),
                Move.from_uci('h1e1')
            ], 
            'hashfull': 1000
        },
        {
            'depth': 24, 
            'seldepth': 37, 
            'multipv': 4, 
            'score': PovScore(Cp(-223), WHITE),
            'nodes': 26414702, 
            'nps': 1656301,
            'tbhits': 0, 
            'time': 15.948,
            'pv': [
                Move.from_uci('g1g3'), Move.from_uci('d7f7'), Move.from_uci('g6f7'), Move.from_uci('f8f7'),
                Move.from_uci('d5c7'), Move.from_uci('e6c4'), Move.from_uci('c7a8'), Move.from_uci('c4e6'),
                Move.from_uci('f5d6'), Move.from_uci('f7f4'), Move.from_uci('d6b7'), Move.from_uci('d8h4'),
                Move.from_uci('g3g2'), Move.from_uci('h4g5'), Move.from_uci('g2g5'), Move.from_uci('h7g5'),
                Move.from_uci('h1h5'), Move.from_uci('g5h7'), Move.from_uci('h5c5'), Move.from_uci('c6d4'),
                Move.from_uci('a8c7'), Move.from_uci('e6g4'), Move.from_uci('b7d6'), Move.from_uci('h7f6'),
                Move.from_uci('c7d5'), Move.from_uci('f6e4'), Move.from_uci('d5f4'), Move.from_uci('e4c5'),
                Move.from_uci('d6f7'), Move.from_uci('h8g8'), Move.from_uci('f7e5'), Move.from_uci('c5e6')],
            'hashfull': 1000
        },
        { 
            'depth': 24,
            'seldepth': 43,
            'multipv': 5,
            'score': PovScore(Cp(-227), WHITE),
            'nodes': 26414702,
            'nps': 1656301,
            'tbhits': 0, 'time': 15.948,
            'pv': [
                Move.from_uci('h1h2'), Move.from_uci('d7f7'), Move.from_uci('g6f7'), Move.from_uci('f8f7'),
                Move.from_uci('d5c7'), Move.from_uci('d8c7'), Move.from_uci('c4e6'), Move.from_uci('f7f6'),
                Move.from_uci('g1g7'), Move.from_uci('c7b6'), Move.from_uci('e6d5'), Move.from_uci('f6f5'),
                Move.from_uci('g7h7'), Move.from_uci('h8h7'), Move.from_uci('e4f5'), Move.from_uci('b6e3'),
                Move.from_uci('c1d1'), Move.from_uci('a8f8'), Move.from_uci('h2e2'), Move.from_uci('e3f4'),
                Move.from_uci('e2e6'), Move.from_uci('c6d4'), Move.from_uci('e6e7'), Move.from_uci('h7h6'),
                Move.from_uci('f5f6'), Move.from_uci('f8f6'), Move.from_uci('e7b7'), Move.from_uci('a7a5'),
                Move.from_uci('d5e4'), Move.from_uci('d4f5'), Move.from_uci('e4d3'), Move.from_uci('f5h4'),
                Move.from_uci('b7e7')],
            'upperbound': True,
            'hashfull': 1000
        }
    ]


@pytest.fixture
def analysis_result():
    return [
        {'depth': 24, 'seldepth': 41, 'multipv': 1, 'score': PovScore(Cp(+815), BLACK), 'nodes': 25396167, 'nps': 2256835,
         'tbhits': 0, 'time': 11.253,
         'pv': [Move.from_uci('e8f8'), Move.from_uci('f6f8'), Move.from_uci('g8f8'), Move.from_uci('d6d1'),
                Move.from_uci('g4h4'), Move.from_uci('f2g2'), Move.from_uci('h4g5'), Move.from_uci('g2f2'),
                Move.from_uci('g5f6'), Move.from_uci('f2g3'), Move.from_uci('f6b2'), Move.from_uci('g3f2'),
                Move.from_uci('b2a3'), Move.from_uci('d1h1'), Move.from_uci('f8g7'), Move.from_uci('h1h4'),
                Move.from_uci('a3a6'), Move.from_uci('h4e4'), Move.from_uci('a6f6'), Move.from_uci('e4f4'),
                Move.from_uci('f6e6'), Move.from_uci('f4f3'), Move.from_uci('g6g5'), Move.from_uci('f3g3'),
                Move.from_uci('g7f6'), Move.from_uci('g3g2'), Move.from_uci('h6h5'), Move.from_uci('f2f3'),
                Move.from_uci('h5h4'), Move.from_uci('e3e4'), Move.from_uci('e6c4'), Move.from_uci('e4e5'),
                Move.from_uci('f6f5'), Move.from_uci('f3f2'), Move.from_uci('g5g4')], 'hashfull': 1000,
         'currmove': Move.from_uci('g4e2'), 'currmovenumber': 25},
        {'depth': 24, 'seldepth': 50, 'multipv': 1, 'score': PovScore(Cp(-822), WHITE), 'nodes': 3034982, 'nps': 2707388,
         'tbhits': 0, 'time': 1.121,
         'pv': [Move.from_uci('f6f8'), Move.from_uci('g8f8'), Move.from_uci('d6d1'), Move.from_uci('g4h4'),
                Move.from_uci('f2g2'), Move.from_uci('h4g5'), Move.from_uci('g2f2'), Move.from_uci('g5f6'),
                Move.from_uci('f2g3'), Move.from_uci('f6b2'), Move.from_uci('g3f2'), Move.from_uci('b2a3'),
                Move.from_uci('d1h1'), Move.from_uci('f8g7'), Move.from_uci('h1h4'), Move.from_uci('a3a6'),
                Move.from_uci('h4e4'), Move.from_uci('a6f6'), Move.from_uci('e4f4'), Move.from_uci('f6e6'),
                Move.from_uci('f4f3'), Move.from_uci('g6g5'), Move.from_uci('f3g3'), Move.from_uci('e6c4'),
                Move.from_uci('g3g1'), Move.from_uci('c4f7'), Move.from_uci('f2e1'), Move.from_uci('f7d5'),
                Move.from_uci('g1g3'), Move.from_uci('g7g6'), Move.from_uci('e1f2'), Move.from_uci('h6h5'),
                Move.from_uci('g3g2'), Move.from_uci('d5e5'), Move.from_uci('g2g1')], 'hashfull': 765},
        {'depth': 24, 'seldepth': 43, 'multipv': 1, 'score': PovScore(Cp(+859), BLACK), 'nodes': 1822361, 'nps': 2618334,
         'tbhits': 0, 'time': 0.696,
         'pv': [Move.from_uci('g8f8'), Move.from_uci('d6d1'), Move.from_uci('g4h4'), Move.from_uci('f2g2'),
                Move.from_uci('h4g5'), Move.from_uci('g2f2'), Move.from_uci('g5f6'), Move.from_uci('f2g3'),
                Move.from_uci('f6b2'), Move.from_uci('g3f2'), Move.from_uci('b2a3'), Move.from_uci('d1h1'),
                Move.from_uci('f8g7'), Move.from_uci('h1h4'), Move.from_uci('a3a6'), Move.from_uci('h4e4'),
                Move.from_uci('a6f6'), Move.from_uci('f2e1'), Move.from_uci('g6g5'), Move.from_uci('e4g4'),
                Move.from_uci('f6e6'), Move.from_uci('g4g3'), Move.from_uci('g7g6'), Move.from_uci('e1f2'),
                Move.from_uci('h6h5'), Move.from_uci('g3g1'), Move.from_uci('e6f5'), Move.from_uci('f2e1'),
                Move.from_uci('f5e4'), Move.from_uci('g1g3'), Move.from_uci('h5h4'), Move.from_uci('g3h3'),
                Move.from_uci('e4g4'), Move.from_uci('h3f3')]},
        {'depth': 24, 'seldepth': 46, 'multipv': 1, 'score': PovScore(Cp(-863), WHITE), 'nodes': 2312377, 'nps': 2739783,
         'tbhits': 0, 'time': 0.844,
         'pv': [Move.from_uci('d6d8'), Move.from_uci('f8g7'), Move.from_uci('d8d1'), Move.from_uci('g4h4'),
                Move.from_uci('f2g2'), Move.from_uci('h4g5'), Move.from_uci('g2f2'), Move.from_uci('g5f6'),
                Move.from_uci('f2g3'), Move.from_uci('f6b2'), Move.from_uci('g3f2'), Move.from_uci('b2a3'),
                Move.from_uci('d1d7'), Move.from_uci('g7f8'), Move.from_uci('d7c7'), Move.from_uci('a3b4'),
                Move.from_uci('f2f1'), Move.from_uci('b4c4'), Move.from_uci('c7c8'), Move.from_uci('f8f7'),
                Move.from_uci('c8c7'), Move.from_uci('f7e6'), Move.from_uci('c7h7'), Move.from_uci('h6h5'),
                Move.from_uci('f1f2'), Move.from_uci('e6f6'), Move.from_uci('f2e1'), Move.from_uci('f6f5'),
                Move.from_uci('e1d2'), Move.from_uci('c4d5'), Move.from_uci('d2c2'), Move.from_uci('d5a2'),
                Move.from_uci('c2d1'), Move.from_uci('a2b3'), Move.from_uci('d1d2'), Move.from_uci('f5e6')]}]
