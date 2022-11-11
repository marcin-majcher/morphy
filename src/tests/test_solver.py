import copy
from unittest import mock

import pytest
from chess import (
    Board,
    BLACK,
    WHITE,
)
from chess.engine import (
    PovScore,
    Cp,
    Mate,
)
from morphy.engine import (
    Limit,
)
from morphy.line import Line

from morphy.solver import (
    Solver,
)
from morphy.settings.default_settings import (
    BEST_MOVE_SEARCH_CONF,
    BEST_MOVES_SEARCH_CONF,
    CP_CLOSE_SCORE,
    MATE_CLOSE_SCORE,
)
from morphy.utils import (
    close_score_threshold,
    CannotSolve,
    flatten,
)


def test_reset():
    solver = Solver('engine')
    solver._open_lines = [1, 2, 3]
    solver._closed_lines = [4, 5, 6]
    solver._fen = 'aneczka'
    solver._depth = 42
    solver.reset()
    assert solver._closed_lines == []
    assert solver._open_lines == []
    assert solver._fen is None
    assert solver._depth == 0


def test_best_move_search_conf_should_be_copied():
    solver = Solver('engine')
    limit = Limit(depth=1)
    solver.best_move_search_conf['limit'] = limit
    assert BEST_MOVE_SEARCH_CONF['limit'] != limit
    
    best_move_search_conf = copy.deepcopy(BEST_MOVE_SEARCH_CONF)
    best_move_search_conf['options'] = [1]
    solver = Solver('engine', best_move_search_conf=best_move_search_conf)
    assert solver.best_move_search_conf['options'] == best_move_search_conf['options']
    solver.best_move_search_conf['options'].append(2)
    assert solver.best_move_search_conf['options'] != best_move_search_conf['options']


def test_best_moves_search_conf_should_be_copied():
    solver = Solver('engine')
    limit = Limit(depth=1)
    solver.best_moves_search_conf['limit'] = limit
    assert BEST_MOVES_SEARCH_CONF['limit'] != limit
    
    best_moves_search_conf = copy.deepcopy(BEST_MOVES_SEARCH_CONF)
    best_moves_search_conf['options'] = [1]
    solver = Solver('engine', best_moves_search_conf=best_moves_search_conf)
    assert solver.best_moves_search_conf['options'] == best_moves_search_conf['options']
    solver.best_moves_search_conf['options'].append(2)
    assert solver.best_moves_search_conf['options'] != best_moves_search_conf['options']
    
    
def test_search_best_move(line):
    engine = mock.Mock()
    limit = Limit(nodes=10**7)
    solver = Solver(engine)
    info = solver.search_best_move(line, limit=limit)
    assert solver.best_move_search_conf['limit'] != limit
    
    with pytest.raises(AssertionError):
        solver.search_best_move(line, multipv=2)
    
    solver.best_move_search_conf['limit'] = limit
    engine.analyse.assert_called_once_with(line.board, **solver.best_move_search_conf)
    assert info == engine.analyse.return_value
    
    
def test_search_best_moves(line):
    engine = mock.Mock()
    solver = Solver(engine)
    multipv = 2
    info = solver.search_best_moves(line, multipv=multipv)
    assert solver.best_moves_search_conf['multipv'] != multipv
    
    with pytest.raises(AssertionError):
        solver.search_best_moves(line, multipv=1)
        
    solver.best_moves_search_conf['multipv'] = multipv
    engine.analyse.assert_called_once_with(line.board, **solver.best_moves_search_conf)
    assert info == engine.analyse.return_value
    
    
def test_move_to_closed_lines():
    solver = Solver('engine')
    solver._closed_lines.append(Line(Board()))
    solver._closed_lines[0].close()
    lines = [
        Line(Board()),
        Line(Board()),
        Line(Board()),
        Line(Board()),
    ]
    lines[0].close()
    lines[3].close()
    solver._move_to_closed_lines(lines)
    assert solver._closed_lines == [solver._closed_lines[0], lines[0], lines[3]]
    
    
def test_replace_open_lines():
    solver = Solver('engine')
    solver._open_lines = [1, 2]
    lines = [
        Line(Board()),
        Line(Board()),
        Line(Board()),
        Line(Board()),
    ]
    lines[0].close()
    lines[3].close()
    solver._replace_open_lines(lines)
    assert solver._open_lines == [lines[1], lines[2]]
    
    
def test_extract_best_winning_moves(infos):
    line = Line(Board('r2b1r1k/pppq2pn/2npb1Q1/3N1N1p/2B1PP1P/8/PPP5/2K3RR w - - 0 1'))
    solver = Solver('engine')
    winning_moves = solver.extract_best_winning_moves(infos, line)
    assert [infos[0]] == winning_moves
    info = copy.deepcopy(winning_moves[0])
    infos.append(info)
    info['score'] = PovScore(
        Cp(info['score'].relative.score() - solver.calc_cp_threshold(infos, line)),
        info['score'].turn
    )
    winning_moves = solver.extract_best_winning_moves(infos, line)
    assert [infos[0], info] == winning_moves
    
    info['score'] = PovScore(
        Mate(3),
        info['score'].turn
    )
    assert infos[0]['score'] != info['score']
    winning_moves = solver.extract_best_winning_moves(infos, line)
    assert [info] == winning_moves
    assert winning_moves[0]['score'].relative.is_mate()
    
    assert solver.extract_best_winning_moves([{'depth': 0, 'score': PovScore(Mate(-0), BLACK)}], line) == []
    assert solver.extract_best_winning_moves([{'depth': 0, 'score': PovScore(Mate(-1), WHITE)}], line) == []
    assert solver.extract_best_winning_moves([{'depth': 0, 'score': PovScore(Cp(-500), WHITE)}], line) == []

    
def test_get_next_player_lines(infos):
    line = Line(Board('r2b1r1k/pppq2pn/2npb1Q1/3N1N1p/2B1PP1P/8/PPP5/2K3RR w - - 0 1'))
    engine = mock.Mock()
    engine.analyse.return_value = infos
    solver = Solver(engine)
    assert solver.get_next_player_lines(line)[0].board.fen() == 'r2b1r1k/pppqN1pn/2npb1Q1/5N1p/2B1PP1P/8/PPP5/2K3RR b - - 1 1'
    assert len(solver.get_next_player_lines(line)) == 1


def test_get_next_comp_line(infos):
    line = Line(Board('r2b1r1k/pppq2pn/2npb1Q1/3N1N1p/2B1PP1P/8/PPP5/2K3RR w - - 0 1'))
    engine = mock.Mock()
    engine.analyse.return_value = infos[0]
    solver = Solver(engine)
    assert solver.get_next_comp_line(line)[0].board.fen() == 'r2b1r1k/pppqN1pn/2npb1Q1/5N1p/2B1PP1P/8/PPP5/2K3RR b - - 1 1'
    assert len(solver.get_next_comp_line(line)) == 1


def test_go_deeper(infos):
    # Player move
    line = Line(Board('r2b1r1k/pppq2pn/2npb1Q1/3N1N1p/2B1PP1P/8/PPP5/2K3RR w - - 0 1'))
    engine = mock.Mock()
    engine.analyse.return_value = infos
    solver = Solver(engine, max_number_best_moves=len(infos))
    solver._depth = 41
    solver.extract_best_winning_moves = lambda i, l: i
    solver._open_lines = [line, line]
    new_lines = flatten(solver._go_deeper())
    assert len(new_lines) == 10
    new_lines_fens = [l.board.fen() for l in new_lines]
    expected_fens = [line.make_move(i['pv'][0]).board.fen() for i in infos] * 2
    new_lines_fens.sort()
    expected_fens.sort()
    assert new_lines_fens == expected_fens
    assert solver._depth == 42
    # solver._extract_best_winning_moves = lambda l: []
    # 
    # with pytest.raises(CannotSolve):
    #     new_lines = solver._go_deeper()
    
    # Computer move
    line._player_color = not line._player_color
    engine.analyse.return_value = infos[0]
    solver = Solver(engine)
    solver._open_lines = [line, line]
    new_lines = flatten(solver._go_deeper())
    assert len(new_lines) == 2
    new_lines_fens = [l.board.fen() for l in new_lines]
    expected_fens = [line.make_move(infos[0]['pv'][0]).board.fen()] * 2
    new_lines_fens.sort()
    expected_fens.sort()
    assert new_lines_fens == expected_fens
    assert solver._depth == 1


def test_evaluate_lines():
    engine = mock.Mock()
    solver = Solver(engine)
    lines = [
        Line(Board('r2b1r1k/pppq2pn/2npb1Q1/3N1N1p/2B1PP1P/8/PPP5/2K3RR w - - 0 1')),
        Line(Board('r2b1r1k/pppq2pn/2npb1Q1/3N1N1p/2B1PP1P/8/PPP5/2K3RR w - - 0 1')),
        Line(Board('r2b1r1k/pppq2pn/2npb1Q1/3N1N1p/2B1PP1P/8/PPP5/2K3RR w - - 0 1')),
    ]
    for l in lines:
        l.evaluate = mock.Mock()

    solver._evaluate_lines(lines)

    for l in lines:
        l.evaluate.assert_called_once()
        

def test_remove_repetitions():
    engine = mock.Mock()
    solver = Solver(engine)
    lines = [
        Line(Board('r2b1r1k/pppq2pn/2npb1Q1/3N1N1p/2B1PP1P/8/PPP5/2K3RR w - - 0 1')),
        Line(Board('r2b1r1k/pppq2pn/2npb1Q1/3N1N1p/2B1PP1P/8/PPP5/2K3RR w - - 0 1')),
        Line(Board('r2b1r1k/pppq2pn/2npb1Q1/3N1N1p/2B1PP1P/8/PPP5/2K3RR w - - 0 1')),
    ]
    lines[1].has_repetition = lambda: True
    assert solver.remove_repetitions(lines) == [lines[0], lines[2]]
    

def test_stop_if_broken_line():
    engine = mock.Mock()
    solver = Solver(engine)
    lines = [[1], [2, 3], [4]]
    
    assert solver.stop_if_broken_line(lines) is None
    lines.append([])
    
    with pytest.raises(CannotSolve):
        solver.stop_if_broken_line(lines)
        
    
def test_stop_if_solution_too_long():
    engine = mock.Mock()
    solver = Solver(engine, max_line_length=10)
    lines = [
        [
            Line(Board('r2b1r1k/pppq2pn/2npb1Q1/3N1N1p/2B1PP1P/8/PPP5/2K3RR w - - 0 1')),
        ],
        [

            Line(Board('r2b1r1k/pppq2pn/2npb1Q1/3N1N1p/2B1PP1P/8/PPP5/2K3RR w - - 0 1')),
            Line(Board('r2b1r1k/pppq2pn/2npb1Q1/3N1N1p/2B1PP1P/8/PPP5/2K3RR w - - 0 1')),
        ],
    ]
    lines[0][0].length = lambda: solver.max_line_length 
    assert solver.stop_if_solution_too_long(lines) is None
    lines[1][0].length = lambda: solver.max_line_length + 1
    
    with pytest.raises(CannotSolve):
        solver.stop_if_solution_too_long(lines)


def test_stop_if_too_many_solutions():
    engine = mock.Mock()
    solver = Solver(engine, max_lines_number=10)
    assert solver.stop_if_too_many_solutions() is None
    solver._open_lines.extend([1, 2, 3, 4, 5])
    assert solver.stop_if_too_many_solutions() is None
    solver._closed_lines.extend([1, 2, 3, 4, 5])
    assert solver.stop_if_too_many_solutions() is None
    solver._closed_lines.extend([1])

    with pytest.raises(CannotSolve):
        solver.stop_if_too_many_solutions()
        

def test_stop_if_too_many_good_moves():
    engine = mock.Mock()
    solver = Solver(engine, max_number_best_moves=2)
    lines = [
        [
            Line(Board('r2b1r1k/pppq2pn/2npb1Q1/3N1N1p/2B1PP1P/8/PPP5/2K3RR w - - 0 1')),
        ],
        [

            Line(Board('r2b1r1k/pppq2pn/2npb1Q1/3N1N1p/2B1PP1P/8/PPP5/2K3RR w - - 0 1')),
            Line(Board('r2b1r1k/pppq2pn/2npb1Q1/3N1N1p/2B1PP1P/8/PPP5/2K3RR w - - 0 1')),
        ],
    ]
    assert solver.stop_if_too_many_good_moves(lines) is None
    solver.max_number_best_moves = 1
    
    with pytest.raises(CannotSolve):
        solver.stop_if_too_many_good_moves(lines)
        

def test_filter_winning_material_solutions():
    engine = mock.Mock()
    solver = Solver(engine, max_number_best_moves=2)
    lines = [
        [
            Line(Board('r2b1r1k/pppq2pn/2npb1Q1/3N1N1p/2B1PP1P/8/PPP5/2K3RR w - - 0 1')),
        ],
        [

            Line(Board('r2b1r1k/pppq2pn/2npb1Q1/3N1N1p/2B1PP1P/8/PPP5/2K3RR w - - 0 1')),
            Line(Board('r2b1r1k/pppq2pn/2npb1Q1/3N1N1p/2B1PP1P/8/PPP5/2K3RR w - - 0 1')),
        ],
        [

            Line(Board('r2b1r1k/pppq2pn/2npb1Q1/3N1N1p/2B1PP1P/8/PPP5/2K3RR w - - 0 1')),
            Line(Board('r2b1r1k/pppq2pn/2npb1Q1/3N1N1p/2B1PP1P/8/PPP5/2K3RR w - - 0 1')),
        ],
        [
            Line(Board('r2b1r1k/pppq2pn/2npb1Q1/3N1N1p/2B1PP1P/8/PPP5/2K3RR w - - 0 1')),
            Line(Board('r2b1r1k/pppq2pn/2npb1Q1/3N1N1p/2B1PP1P/8/PPP5/2K3RR w - - 0 1')),
            Line(Board('r2b1r1k/pppq2pn/2npb1Q1/3N1N1p/2B1PP1P/8/PPP5/2K3RR w - - 0 1')),
        ],
    ]
    lines[1][0]._analysis_result.append({
        'score': PovScore(Cp(11), BLACK)
    })
    lines[1][0].close()
    lines[1][1]._analysis_result.append({
        'score': PovScore(Cp(11), BLACK)
    })
    lines[1][1].close()
    
    lines[2][0]._analysis_result.append({
        'score': PovScore(Cp(11), BLACK)
    })
    lines[2][0].close()
    lines[2][1]._analysis_result.append({
        'score': PovScore(Cp(11), BLACK)
    })

    lines[3][0]._analysis_result.append({
        'score': PovScore(Cp(11), BLACK)
    })
    lines[3][0].close()
    lines[3][1]._analysis_result.append({
        'score': PovScore(Cp(11), BLACK)
    })
    lines[3][1].close()
    lines[3][2]._analysis_result.append({
        'score': PovScore(Mate(11), BLACK)
    })
    lines[3][2].close()
    
    assert solver.filter_winning_material_solutions(lines) == [lines[0], lines[2], lines[3]]


def test_is_solved():
    engine = mock.Mock()
    solver = Solver(engine, max_number_best_moves=2)
    assert solver.is_solved()
    solver._open_lines.append(1)
    assert solver.is_solved() is False


def test_to_dict():
    engine = mock.Mock()
    solver = Solver(engine, max_number_best_moves=2)
    solver._closed_lines = [
        Line(Board('r2b1r1k/pppq2pn/2npb1Q1/3N1N1p/2B1PP1P/8/PPP5/2K3RR w - - 0 1')),
        Line(Board('r2b1r1k/pppq2pn/2npb1Q1/3N1N1p/2B1PP1P/8/PPP5/2K3RR w - - 0 1')),
    ]
    solver._fen = 'r2b1r1k/pppq2pn/2npb1Q1/3N1N1p/2B1PP1P/8/PPP5/2K3RR w - - 0 1'
    expected = {
        'fen': 'r2b1r1k/pppq2pn/2npb1Q1/3N1N1p/2B1PP1P/8/PPP5/2K3RR w - - 0 1',
        'is_solved': True,
        'lines': [l.to_dict() for l in solver._closed_lines]
    }
    assert solver.to_dict() == expected


def test_calc_cp_threshold():
    line = mock.Mock()
    engine = mock.Mock()
    solver = Solver(engine, max_number_best_moves=2)
    infos = [
        {'score': PovScore(Cp(360), WHITE)},
        {'score': PovScore(Cp(100), WHITE)}
    ]
    assert abs(solver.calc_cp_threshold(infos, line) - close_score_threshold(Cp(360))) < 0.0003
    infos = [
        {'score': PovScore(Mate(3), WHITE)},
        {'score': PovScore(Cp(100), WHITE)}
    ]
    assert solver.calc_cp_threshold(infos, line) == CP_CLOSE_SCORE


def test_calc_calc_mate_threshold():
    engine = mock.Mock()
    line = mock.Mock()
    solver = Solver(engine, max_number_best_moves=2)
    line.length.return_value = 0

    assert solver.calc_mate_threshold(line) == MATE_CLOSE_SCORE
    line.length.return_value = 1
    assert solver.calc_mate_threshold(line) == MATE_CLOSE_SCORE
    line.length.return_value = 2
    assert solver.calc_mate_threshold(line) == MATE_CLOSE_SCORE - 1
    line.length.return_value = 42
    assert solver.calc_mate_threshold(line) == 0
