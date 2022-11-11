import random 

import pytest
from chess import (
    WHITE,
    BLACK,
    STARTING_FEN,
    Board,
    Move,
)
from chess.engine import (
    PovScore,
    Cp,
    Mate,
)

from morphy.line import Line
from morphy.utils import (
    move,
    CannotSolve,
    black_material,
    white_material,
)
from morphy.constant import (
    MATE_CAT,
    MATERIAL_CAT,
    UNKNOWN_CAT,
)

@pytest.fixture
def fen():
    return 'r7/3kn1p1/p2pq2p/2p1p3/Pp2P3/1Q2B2P/1PP2PP1/R5K1 w - - 0 1'


def test_get_player_color(game):
    board = game.board()
    moves = list(game.mainline_moves())
    move_number = random.randrange(len(moves) - 2)
    
    for m in moves[:move_number + 1]:
        board.push(m)
    
    assert board.fen() != STARTING_FEN
    
    fen = board.fen()
    player_color = WHITE if fen.split()[1] == 'w' else BLACK
    line = Line(Board(fen))
    assert line.get_player_color() == player_color

    line.board.push(moves[move_number + 1])
    line.board.push(moves[move_number + 2])
    assert line.get_player_color() == player_color
    
    
def test_copy(fen):
    line = Line(Board(fen))
    line._closed = True
    line._initial_comp_material = 222
    line._initial_player_material = 522
    line._analysis_result.append(42)
    line._repeated_position = True
    c_line = line.copy()
    assert isinstance(c_line, Line)
    assert id(c_line) != id(line)
    assert c_line.board == line.board
    assert c_line.board._stack == line.board._stack
    assert c_line.board.move_stack == line.board.move_stack
    assert id(c_line.board) != id(line.board)
    assert c_line._closed == line._closed
    assert c_line._player_color == line._player_color
    assert c_line._analysis_result == line._analysis_result
    assert c_line._initial_player_material == line._initial_player_material
    assert c_line._initial_comp_material == line._initial_comp_material
    assert id(c_line._parent) == id(line)
    assert [id(c) for c in line._children] == [id(c_line)]
    assert c_line._repeated_position == line._repeated_position
    
    
def test_make_move(game):
    board = game.board()
    moves = list(game.mainline_moves())
    
    for m in moves[:13]:
        board.push(m)
    
    next_move = moves[13]
    line = Line(board)
    fen = line.board.fen()
    line._make_move(next_move)
    
    assert fen != line.board.fen()
    assert next_move == line.board.move_stack[-1]
    
    next_move = moves[14]
    new_line = line.make_move(next_move, 42)
    
    assert id(new_line) != id(line)
    assert next_move == new_line.board.move_stack[-1]
    assert next_move != line.board.move_stack[-1]
    assert new_line._analysis_result[-1] == 42
    assert line._analysis_result == []


def test_close(fen):
    line = Line(Board(fen))
    line.close()
    assert line._closed == True
    
    
def test_is_closed(fen):
    line = Line(Board(fen))
    assert line.is_closed() is False
    line.close()
    assert line.is_closed() is True


def test_is_open(fen):
    line = Line(Board(fen))
    assert line.is_open() is True
    line.close()
    assert line.is_open() is False
    
    
def test_is_player_move(game):
    board = game.board()
    moves = list(game.mainline_moves())
    board.push(moves[0]) #black turn
    board.push(moves[1]) #white turn
    board.push(moves[2]) #black turn
    line = Line(Board(board.fen()))
    assert line.get_player_color() == BLACK
    assert line.is_player_move() is True
    line._make_move(moves[3]) # Comp
    line._make_move(moves[4]) # Player
    assert line.is_player_move() is True
    line._make_move(moves[5]) # Player
    assert line.is_player_move() is False


def test_get_player_material():
    fen = "2r3k1/pp4pp/8/3p4/1n1PRq2/1Q3N1b/PP3P1P/RB4K1 w - - 0 1"
    line = Line(Board(fen))
    assert line.get_player_material() == 30.5
    assert line._initial_player_material == line.get_player_material()
    line._player_color = not line._player_color
    assert line.get_player_material() == 25.5


def test_get_comp_material():
    fen = "2r3k1/pp4pp/8/3p4/1n1PRq2/1Q3N1b/PP3P1P/RB4K1 w - - 0 1"
    line = Line(Board(fen))
    assert line.get_comp_material() == 25.5
    assert line._initial_comp_material == line.get_comp_material()
    line._player_color = not line._player_color
    assert line.get_comp_material() == 30.5


def test_player_gained_material(analysis_result):
    board = Board('4r1k1/8/3R1Qpp/2p5/2P1p1q1/P3P3/1P2PK2/8 b - - 0 1')
    line = Line(board)
    
    for i in analysis_result:
        line = line.make_move(move(i), i)
        
    assert line._initial_comp_material > line.get_comp_material()
    assert line.player_gained_material()


def test_can_close_material_line(analysis_result):
    board = Board('4r1k1/8/3R1Qpp/2p5/2P1p1q1/P3P3/1P2PK2/8 b - - 0 1')
    line = Line(board)

    for i in analysis_result:
        line = line.make_move(move(i), i)
    
    parent = line._parent
    parent.player_gained_material = lambda: True
    parent._children = [1, 2]
    assert line.can_close_material_line()
    parent.player_gained_material = lambda: False
    assert line.can_close_material_line() is False
    parent.player_gained_material = lambda: True
    parent._children = [1]
    assert line.can_close_material_line() is False
    line._parent = None
    assert line.can_close_material_line() is False


def test_get_line_category(analysis_result):
    board = Board('4r1k1/8/3R1Qpp/2p5/2P1p1q1/P3P3/1P2PK2/8 b - - 0 1')
    line = Line(board)
    assert line.get_line_category() == UNKNOWN_CAT

    for i in analysis_result:
        line = line.make_move(move(i), i)
        
    assert line.get_line_category() == MATERIAL_CAT
    line._analysis_result.append({
        'score': PovScore(Mate(11), BLACK)
    })
    assert line.get_line_category() == MATE_CAT


def test_moves(analysis_result):
    board = Board('4r1k1/8/3R1Qpp/2p5/2P1p1q1/P3P3/1P2PK2/8 b - - 0 1')
    line = Line(board)

    for i in analysis_result:
        line = line.make_move(move(i), i)
    
    assert len(line.moves()) > 0
    assert line.moves() == line.board.move_stack


def test_length(analysis_result):
    board = Board('4r1k1/8/3R1Qpp/2p5/2P1p1q1/P3P3/1P2PK2/8 b - - 0 1')
    line = Line(board)

    for i in analysis_result:
        line = line.make_move(move(i), i)

    assert len(line.moves()) > 0
    assert line.length() == len(line.board.move_stack)


def test_player_won_game():
    board = Board("8/2p3Q1/p1RNKP2/n2p1p2/1P1k1p1R/1p1N1P1b/3PPPrb/8 w - - 0 1")
    line = Line(board)
    line = line.make_move(Move.from_uci('d3c1'))
    line = line.make_move(Move.from_uci('b3b2'))
    line = line.make_move(Move.from_uci('e2e3'))
    assert line.player_won_game()
    

def test_is_repetition():
    board = Board("8/7p/5pk1/8/2b1p3/4PqPQ/PB5P/6K1 b - -")
    line = Line(board)
    line = line.make_move(Move.from_uci('f3d1'))
    line = line.make_move(Move.from_uci('g1f2'))
    line = line.make_move(Move.from_uci('d1c2'))
    line = line.make_move(Move.from_uci('f2g1'))
    line = line.make_move(Move.from_uci('c2d1'))
    assert line.is_repetition()


def test_evaluate():
    # check repetition
    board = Board("8/7p/5pk1/8/2b1p3/4PqPQ/PB5P/6K1 b - -")
    line = Line(board)
    line.evaluate()
    assert line._repeated_position is False
    line = line.make_move(Move.from_uci('f3d1'))
    line = line.make_move(Move.from_uci('g1f2'))
    line = line.make_move(Move.from_uci('d1c2'))
    line = line.make_move(Move.from_uci('f2g1'))
    line = line.make_move(Move.from_uci('c2d1'))
    line.evaluate()
    assert line._repeated_position is True
    
    # close line
    line = Line(board)
    line.evaluate()
    assert not line.is_closed()
    line.player_won_game = lambda: True
    line.evaluate()
    assert line.is_closed()
    line.player_won_game = lambda: False
    line._closed = False
    line.evaluate()
    assert not line.is_closed()
    line.can_close_material_line = lambda: True
    line.evaluate()
    assert line.is_closed()
    
    # raise CannotSolve
    line = Line(board)
    line.board.is_game_over = lambda claim_draw: True
    
    with pytest.raises(CannotSolve):
        line.evaluate()


def test_has_repetition():
    board = Board("8/7p/5pk1/8/2b1p3/4PqPQ/PB5P/6K1 b - -")
    line = Line(board)
    line.evaluate()
    assert line.has_repetition() is False
    line = line.make_move(Move.from_uci('f3d1'))
    line = line.make_move(Move.from_uci('g1f2'))
    line = line.make_move(Move.from_uci('d1c2'))
    line = line.make_move(Move.from_uci('f2g1'))
    line = line.make_move(Move.from_uci('c2d1'))
    line.evaluate()
    assert line.has_repetition() is True


def test_to_dict():
    board = Board("8/7p/5pk1/8/2b1p3/4PqPQ/PB5P/6K1 b - -")
    line = Line(board)
    line = line.make_move(Move.from_uci('f3d1'))
    line = line.make_move(Move.from_uci('g1f2'))
    line = line.make_move(Move.from_uci('d1c2'))
    line = line.make_move(Move.from_uci('f2g1'))
    line = line.make_move(Move.from_uci('c2d1'))
    line.get_line_category = lambda: MATERIAL_CAT
    line.close()
    expected = {
        'category': MATERIAL_CAT,
        'is_closed': line.is_closed(),
        'player_color': False,
        'moves': [
            'f3d1',
            'g1f2',
            'd1c2',
            'f2g1',
            'c2d1',
        ],
        'initial_player_material': black_material(board),
        'initial_comp_material': white_material(board),
        'player_material': black_material(line.board),
        'comp_material': white_material(line.board),
    }
    assert expected == line.to_dict()
