from chess import (
    Board,
    Move,
    WHITE,
)

from chess.engine import (
    Cp,
    Mate,
    MateGiven,
    PovScore,
)

from morphy.utils import (
    games_reader,
    white_material,
    black_material,
    is_winning_move,
    moves_are_close,
    extract_best_winning_moves,
    close_score_threshold,
    see,
    one_winning_move,
    is_losing_move,
    one_non_losing_move,
    calculate_close_score_threshold,
)


def test_games_reader(games_pgn):
    games = [g for g in games_reader(games_pgn)]
    assert len(games) == 36
    game_5 = games[5]
    assert '[Event "Barcelona Masters CAT-ARG"]' in game_5
    assert '32. Qg2 1/2-1/2' in game_5
    assert game_5.count('ECO') == 1
    game_26 = games[26]
    assert '1-0' in game_26
    assert '1.' not in game_26


def test_white_material():
    fen = "r7/3kn1p1/p2pq2p/2p1p3/Pp2P3/1Q2B2P/1PP2PP1/R5K1 w - - 0 1"
    board = Board(fen)
    assert board.is_valid()
    assert white_material(board) == 24.5
    
    
def test_black_material():
    fen = "2r2rk1/pR3p1p/3R1p2/2p2q2/Q7/5N2/P4PPP/6K1 b - - 0 1"
    board = Board(fen)
    assert board.is_valid()
    assert black_material(board) == 24.5


def test_is_winning_move():
    # Mate
    assert is_winning_move(Mate(1)) is True
    assert is_winning_move(Mate(12)) is True
    assert is_winning_move(Mate(3)) is True
    assert is_winning_move(MateGiven) is True
    assert is_winning_move(Mate(0)) is False
    assert is_winning_move(Mate(-1)) is False
    assert is_winning_move(Mate(-10)) is False
    
    # CP
    assert is_winning_move(Cp(300), threshold=200) is True
    assert is_winning_move(Cp(200), threshold=200) is True
    assert is_winning_move(Cp(600), threshold=200) is True
    assert is_winning_move(Cp(199), threshold=200) is False
    assert is_winning_move(Cp(0), threshold=200) is False
    assert is_winning_move(Cp(-1), threshold=200) is False
    assert is_winning_move(Cp(-300), threshold=200) is False


def test_is_losing_move():
    # Mate
    assert is_losing_move(-Mate(1)) is True
    assert is_losing_move(-Mate(12)) is True
    assert is_losing_move(-Mate(3)) is True
    assert is_losing_move(-MateGiven) is True
    assert is_losing_move(-Mate(0)) is False
    assert is_losing_move(-Mate(-1)) is False
    assert is_losing_move(-Mate(-10)) is False

    # CP
    assert is_losing_move(-Cp(300), threshold=200) is True
    assert is_losing_move(-Cp(200), threshold=200) is True
    assert is_losing_move(-Cp(600), threshold=200) is True
    assert is_losing_move(-Cp(199), threshold=200) is False
    assert is_losing_move(-Cp(0), threshold=200) is False
    assert is_losing_move(-Cp(-1), threshold=200) is False
    assert is_losing_move(-Cp(-300), threshold=200) is False


def test_move_are_close():
    # Mate
    assert moves_are_close(Mate(0), Mate(-1), mate_threshold=6) is False
    assert moves_are_close(Mate(0), Mate(0), mate_threshold=6) is True
    assert moves_are_close(MateGiven, MateGiven, mate_threshold=6) is True
    assert moves_are_close(Mate(0), Mate(-6), mate_threshold=6) is False
    assert moves_are_close(Mate(0), Mate(1), mate_threshold=6) is False
    assert moves_are_close(Mate(0), MateGiven, mate_threshold=6) is False
    assert moves_are_close(Mate(2), MateGiven, mate_threshold=6) is False
    assert moves_are_close(Mate(-1), MateGiven, mate_threshold=6) is False
    assert moves_are_close(Mate(-1), Mate(1), mate_threshold=16) is False
    assert moves_are_close(Mate(1), Mate(-1), mate_threshold=16) is False
    assert moves_are_close(Mate(-1), Mate(-4), mate_threshold=3) is True
    assert moves_are_close(Mate(-4), Mate(-1), mate_threshold=3) is True
    assert moves_are_close(Mate(-4), Mate(-4), mate_threshold=3) is True
    assert moves_are_close(Mate(-5), Mate(-1), mate_threshold=3) is False
    assert moves_are_close(Mate(-1), Mate(-5), mate_threshold=3) is False
    assert moves_are_close(Mate(-1), Mate(-2), mate_threshold=3) is True
    assert moves_are_close(Mate(-2), Mate(-1), mate_threshold=3) is True
    assert moves_are_close(Mate(1), Mate(4), mate_threshold=3) is True
    assert moves_are_close(Mate(1), Mate(1), mate_threshold=3) is True
    assert moves_are_close(Mate(4), Mate(1), mate_threshold=3) is True
    assert moves_are_close(Mate(5), Mate(1), mate_threshold=3) is False
    assert moves_are_close(Mate(1), Mate(5), mate_threshold=3) is False
    assert moves_are_close(Mate(1), Mate(2), mate_threshold=3) is True
    assert moves_are_close(Mate(2), Mate(1), mate_threshold=3) is True
    
    # CP
    assert moves_are_close(Cp(50), Cp(-50), cp_threshold=100) is True
    assert moves_are_close(Cp(51), Cp(-50), cp_threshold=100) is False
    assert moves_are_close(Cp(-180), Cp(-200), cp_threshold=100) is True
    assert moves_are_close(Cp(-180), Cp(-180), cp_threshold=100) is True
    assert moves_are_close(Cp(-200), Cp(-100), cp_threshold=100) is True
    assert moves_are_close(Cp(-100), Cp(-201), cp_threshold=100) is False
    assert moves_are_close(Cp(-700), Cp(-201), cp_threshold=100) is False
    assert moves_are_close(Cp(180), Cp(200), cp_threshold=100) is True
    assert moves_are_close(Cp(180), Cp(180), cp_threshold=100) is True
    assert moves_are_close(Cp(200), Cp(100), cp_threshold=100) is True
    assert moves_are_close(Cp(100), Cp(201), cp_threshold=100) is False
    assert moves_are_close(Cp(700), Cp(201), cp_threshold=100) is False
    
    # CP and Mate
    assert moves_are_close(Mate(0), Cp(-1), mate_threshold=1, cp_threshold=1) is False
    assert moves_are_close(MateGiven, Cp(100000000), mate_threshold=1, cp_threshold=1) is False
    assert moves_are_close(Mate(20), Cp(1000000000), mate_threshold=1, cp_threshold=1) is False
    assert moves_are_close(Mate(-20), Cp(-1000000000), mate_threshold=1, cp_threshold=1) is False


def test_extract_best_winning_moves():
    def ebwm(scores):
        return extract_best_winning_moves(
            scores,
            threshold=280,
            cp_threshold=60,
            mate_threshold=3,
            
        )
    assert (ebwm([Mate(1), MateGiven]) == 
            [MateGiven])
    assert (ebwm([Mate(0), MateGiven]) ==
            [MateGiven])
    assert (ebwm([Mate(-1), Mate(1)]) ==
            [Mate(1)])
    assert (ebwm([Mate(3), Mate(1), Mate(5)]) ==
            [Mate(1), Mate(3)])
    assert (ebwm([Mate(5)]) ==
            [Mate(5)])
    assert (ebwm([Mate(-3), Mate(-1), Mate(-5)]) ==
            [])
    assert (ebwm([Cp(300), Cp(900), Mate(50)]) ==
            [Mate(50)])
    assert (ebwm([Cp(-300), Cp(-900), Mate(5)]) ==
            [Mate(5)])
    assert (ebwm([Cp(-300), Cp(-900), Cp(280)]) ==
            [Cp(280)])
    assert (ebwm([Cp(-300), Cp(-900), Cp(-280)]) ==
            [])
    assert (ebwm([Cp(-300), Cp(280), Cp(280)]) ==
            [Cp(280), Cp(280)])
    assert (ebwm([Cp(300), Cp(-300), Cp(280), Cp(280)]) ==
            [Cp(300), Cp(280), Cp(280)])
    assert (ebwm([Cp(900), Cp(300), Cp(-300), Cp(280), Cp(280)]) ==
            [Cp(900)])
    assert (ebwm([Cp(300), Cp(200), Cp(-300), Cp(280), Cp(280)]) ==
            [Cp(300), Cp(280), Cp(280)])
    assert (ebwm([Cp(900)]) ==
            [Cp(900)])
    assert (ebwm([Cp(90), Cp(30), Cp(-300), Cp(270), Cp(270)]) ==
            [])
    assert (ebwm([]) ==
            [])
    
    
def test_close_score_threshold():
    ms = Cp(360)
    assert 40 < close_score_threshold(ms, 1.3) < 84
    ms = Cp(1251)
    assert 155 < close_score_threshold(ms, 1.3) < 289


def test_see():
    board = Board('1k1r4/8/3r4/2Qb4/4B3/2N3B1/8/6K1 w - - 0 1')
    move = Move.from_uci('c3d5')
    assert see(board, move) == 7

    board = Board('1k1r4/8/3r4/2Q5/4B3/2N3B1/8/6K1 w - - 0 1')
    move = Move.from_uci('c3d5')
    assert see(board, move) == 0

    board = Board('1k1r4/ppq5/8/3pN1p1/3pn1Q1/P2KP3/1P6/5RR1 b - -')
    move = Move.from_uci('c7e5')
    assert see(board, move) == 3

    board = Board('1k6/8/3r4/4n3/8/3R4/2P5/1K1R4 b - - 0 1')
    move = Move.from_uci('e5d3')
    assert see(board, move) == -2


def test_one_winning_move(infos):
    assert one_winning_move(infos)
    assert one_winning_move([infos[0]] + infos) is False
    assert one_winning_move(infos[1:]) is False
    assert one_winning_move([infos[0]]) is False


def to_info(score):
    return {
        'score': PovScore(score, WHITE),
    }


def test_one_non_losing_move():
    assert one_non_losing_move([to_info(Cp(-10)), to_info(Mate(-2)), to_info(Mate(-4))])
    assert one_non_losing_move([to_info(Cp(100)), to_info(Mate(-2)), to_info(Mate(-4))])
    assert one_non_losing_move([to_info(Cp(0)), to_info(Mate(-2)), to_info(Mate(-4))])
    assert one_non_losing_move([to_info(Mate(1)), to_info(Mate(-2)), to_info(Mate(-4))])

    assert not one_non_losing_move([to_info(Cp(0)), to_info(Cp(-10)), to_info(Mate(-2)), to_info(Mate(-4))])
    assert not one_non_losing_move([to_info(Cp(300)), to_info(Cp(100)), to_info(Mate(-2)), to_info(Mate(-4))])
    assert not one_non_losing_move([to_info(Cp(0)), to_info(Cp(-30)), to_info(Mate(-2)), to_info(Mate(-4))])
    assert not one_non_losing_move([to_info(Mate(1)), to_info(Mate(2)), to_info(Mate(-2)), to_info(Mate(-4))])


def test_calculate_close_score_threshold():
    similarity_factors = [
        [1800, 1800/900],
        [900, 900/500],
        [500, 500/300],
        [270, 300/270],
        [0, 1],
    ]

    def are_eq(x, y):
        return abs(x - y) <= 0.000001

    ms = Cp(0)
    assert are_eq(
        calculate_close_score_threshold(ms, similarity_factors),
        0,
    )

    ms = Cp(260)
    assert are_eq(
        calculate_close_score_threshold(ms, similarity_factors),
        0,
    )

    ms = Cp(300)
    assert are_eq(
        300 - calculate_close_score_threshold(ms, similarity_factors),
        270,
    )

    ms = Cp(500)
    assert are_eq(
        500 - calculate_close_score_threshold(ms, similarity_factors),
        300,
    )
    ms = Cp(900)
    assert are_eq(
        900 - calculate_close_score_threshold(ms, similarity_factors),
        500,
    )
    ms = Cp(1800)
    assert are_eq(
        1800 - calculate_close_score_threshold(ms, similarity_factors),
        900,
    )
    similarity_factors = [
        [501, 9/5],
        [0, 5/3],
    ]
    ms = Cp(900)
    assert are_eq(
        900 - calculate_close_score_threshold(ms, similarity_factors),
        500,
    )
    ms = Cp(500)
    assert are_eq(
        500 - calculate_close_score_threshold(ms, similarity_factors),
        300,
    )
