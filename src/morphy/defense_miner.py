import os

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))

import sys
sys.path.insert(0, os.path.join(ROOT_DIR, '..'))

from io import StringIO
import time

import chess.pgn
import chess.engine

from morphy.utils import (
    games_reader,
    is_winning_move,
    score,
    move as move_,
    see,
    one_winning_move,
    is_losing_move,
    one_non_losing_move,
)


ENGINE_PATH = os.environ.get('MORPHY_ENGINE_PATH')


def save_fen(fen, out_file):
    with open(out_file, 'a') as f:
        f.write('{}\n'.format(fen))


def is_good_puzzle(board, engine, nodes, move, prev_boards):
    
    if len(prev_boards) < 3:
        return False
    
    infos = engine.analyse(board, chess.engine.Limit(nodes=nodes), multipv=2)
    best_move = move_(infos[0])
    good_puzzle = one_non_losing_move(infos)
    
    if good_puzzle:
        infos = engine.analyse(
            prev_boards[-3],
            chess.engine.Limit(nodes=nodes),
            multipv=2,
        )
        good_puzzle = good_puzzle and (not one_non_losing_move(infos))

    good_puzzle = good_puzzle and (see(board, best_move) <= 0)

    good_puzzle = good_puzzle and (move != best_move)   
    
    return good_puzzle


def main(pgn_file, out_file):
    
    game_number = 1
    
    for game_str in games_reader(open(pgn_file, 'r')):
        print('Game number: {}'.format(game_number))
        engine = chess.engine.SimpleEngine.popen_uci(ENGINE_PATH)
        game = chess.pgn.read_game(StringIO(game_str))
        board = game.board()
        moves = list(game.mainline_moves())
        prev_boards = [board.copy()]
        
        for move in moves:
            infos = engine.analyse(board, chess.engine.Limit(nodes=10**6), multipv=2)
            
            if one_non_losing_move(infos):
                nodes = 10**6
                
                while nodes < 40 * (10**6):
                    if is_good_puzzle(board, engine, nodes, move, prev_boards):
                        nodes = int(nodes * 1.4)
                        is_puzzle_candidate = True
                    else:
                        is_puzzle_candidate = False
                        break
                
                if is_puzzle_candidate:
                    print('Tactics found: {}'.format(board.fen()))
                    save_fen(board.fen(), out_file)
                    
            board.push(move)
            prev_boards.append(board.copy())

        engine.close()
        game_number += 1
        print('No tactics found :(')
        time.sleep(20)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
