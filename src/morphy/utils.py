import chess
import chess.pgn
from chess.engine import (
    Mate,
    MateGiven,
)

from morphy.constant  import (
    PIECE_VALUES,
)
from morphy.config import settings


def games_reader(pgn_file):
    
    while True:
        offset_before = pgn_file.tell()

        if not chess.pgn.skip_game(pgn_file):
            break
            
        offset_after = pgn_file.tell() - 2
        pgn_file.seek(offset_before)
        
        yield pgn_file.read(offset_after - offset_before)


def _material(color, board, piece_values):
    return sum([piece_values[pt] * len(board.pieces(pt, color)) for pt in chess.PIECE_TYPES[:-1]])


def white_material(board, piece_values=PIECE_VALUES):
    return _material(chess.WHITE, board, piece_values)


def black_material(board, piece_values=PIECE_VALUES):
    return _material(chess.BLACK, board, piece_values)


def is_winning_move(score, threshold=settings.WINNING_SCORE):
    
    if score.is_mate():
        return (score == MateGiven) or score.mate() > 0
    
    
    return score >= chess.engine.Cp(threshold)


def is_losing_move(score, threshold=settings.WINNING_SCORE):
    return is_winning_move(-score, threshold)


def moves_are_close(score_a, score_b, cp_threshold=settings.CP_CLOSE_SCORE, mate_threshold=settings.MATE_CLOSE_SCORE):
    
    if score_a == score_b:
        return True
    
    # Game over
    if score_a.is_mate() and score_a.mate() == 0:
        return False
    
    if score_b.is_mate() and score_b.mate() == 0:
        return False
    
    # Mate
    if score_a.is_mate() and score_b.is_mate():
        
        if score_a.mate() * score_b.mate() < 0:
            return False
        
        return abs(score_a.mate() - score_b.mate()) <= mate_threshold

    # TODO: should we convert mate to score? (mate in 1 == 900*30, mate in 2 == 900*29...)
    if ((score_a.is_mate() and not score_b.is_mate()) or 
        (not score_a.is_mate() and score_b.is_mate())):
        return False
    
    # CP
    return abs(score_a.score() - score_b.score()) <= cp_threshold


def extract_best_winning_moves(scores, threshold=settings.WINNING_SCORE,
                       cp_threshold=settings.CP_CLOSE_SCORE, mate_threshold=settings.MATE_CLOSE_SCORE):
    best_winning_moves = []
    sorted_scores = scores[:]
    sorted_scores.sort(reverse=True)
    sorted_scores = [x for x in sorted_scores if is_winning_move(x, threshold=threshold)]

    if not sorted_scores:
        return best_winning_moves
    
    best_move = sorted_scores[0]
    
    for m in sorted_scores:
        
        if moves_are_close(best_move, m, cp_threshold=cp_threshold, mate_threshold=mate_threshold):
            best_winning_moves.append(m)
    
    return best_winning_moves


def close_score_threshold(max_score, similarity_factor=settings.SIMILARITY_FACTOR):
    assert not max_score.is_mate()
    return abs(max_score.score()) - (abs(max_score.score()) / similarity_factor)


def calculate_close_score_threshold(max_score, similarity_factors):
    assert 0 in [sf[0] for sf in similarity_factors]
    ms = abs(max_score.score())
    sf = sorted([sf for sf in similarity_factors if sf[0] <= ms], key=lambda sf: sf[0])[-1][1]
    return abs(ms) - (abs(ms) / sf)


# def mate_score_to_cp_score(mate_score):
#     assert mate_score.is_mate()

def score(info):
    return info['score'].relative


def move(info):
    return info['pv'][0]


class CannotSolve(Exception):
    pass


def cannot_solve(msg=''):
    raise CannotSolve


def flatten(l):
    flattened_list = []

    for el in l:
        if isinstance(el, list):
            flattened_list += flatten(el)
        else:
            flattened_list += [el]

    return flattened_list


def see(board, move):
    colors_to_material_funcs = {
        chess.WHITE: white_material,
        chess.BLACK: black_material,
    }
    n_board = board.copy()
    n_board.push(move)
    material = colors_to_material_funcs[n_board.turn](board) - colors_to_material_funcs[n_board.turn](n_board)
    attackers = [(s, PIECE_VALUES[n_board.piece_at(s).piece_type]) for s in n_board.attackers(n_board.turn, move.to_square)]
    attackers.sort(key=lambda x: x[1])

    if not attackers or material == 0:
        return material

    return material - see(n_board, chess.Move(attackers[0][0], move.to_square))


def one_winning_move(infos):
    if len(infos) < 2:
        return False

    return is_winning_move(score(infos[0])) and (not is_winning_move(score(infos[1])))


def one_non_losing_move(infos):
    if len(infos) < 2:
        return False

    return not is_losing_move(score(infos[0])) and (is_losing_move(score(infos[1])))